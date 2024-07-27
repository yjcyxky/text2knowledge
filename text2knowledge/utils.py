from transformers import AutoModelForCausalLM, AutoModel
from transformers import AutoTokenizer
from transformers import PreTrainedTokenizer
from transformers import PreTrainedModel
import transformers_embedder as tre
from pathlib import Path
import pandas as pd
import torch
import os
import logging
import torch.nn.functional as F
import pickle
from typing import List, Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass
import cohere


def init_logger(name):
    logger = logging.getLogger(name)
    # Set the logging format, only print the message
    formatter = logging.Formatter("%(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


class EmbeddingGenerator:
    """Embedding generator."""

    def __init__(self, model_name: str, word_mode: bool = False):
        """Initialize the embedding generator.

        Args:
            model_name (str): Model name.
        """
        self.model_name = model_name
        self.word_mode = word_mode
        if self.word_mode:
            self.tokenizer, self.model = self.load_tokenizer_and_model(model_name)
        else:
            self.model = self.load_model(model_name)
            self.tokenizer = self.load_tokenizer(model_name, use_fast=True)

    @staticmethod
    def load_model(model_name: Union[str, Path]) -> PreTrainedModel:
        """Load model from HuggingFace.

        Args:
            model_name (str | Path): Model name or path.

        Returns:
            AutoModel: Model.
        """
        print(
            "Loading model into the %s..."
            % ("mps" if torch.backends.mps.is_available() else "cpu")
        )
        device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        model = AutoModel.from_pretrained(model_name).to(device)

        return model

    @staticmethod
    def load_tokenizer(
        model_name: Union[str, Path], use_fast: bool = False
    ) -> PreTrainedTokenizer:
        """Load tokenizer from HuggingFace.

        Args:
            model_name (str | Path): Model name or path.

        Returns:
            AutoTokenizer: Tokenizer.
        """
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=use_fast)

        return tokenizer  # type: ignore

    @staticmethod
    def load_tokenizer_and_model(
        model_name: str,
        use_fast: bool = True,
        subword_pooling_strategy: str = "sparse",
        layer_pooling_strategy: str = "mean",
    ) -> Tuple[tre.Tokenizer, tre.TransformersEmbedder]:
        """Load tokenizer and model from HuggingFace.

        Args:
            model_name (str): Model name.

        Returns:
            AutoTokenizer: Tokenizer.
        """
        tokenizer = tre.Tokenizer(model_name, use_fast=use_fast)
        model = tre.TransformersEmbedder(
            model_name,
            subword_pooling_strategy=subword_pooling_strategy,
            layer_pooling_strategy=layer_pooling_strategy,
        )

        return tokenizer, model

    def gen_text_embedding(self, text: str) -> torch.Tensor:
        """Convert model to text embedding.

        Args:
            text (str): Text.

        Returns:
            torch.Tensor: Word embedding.

        Raises:
            ValueError: If model or tokenizer is None.
        """
        if not self.tokenizer or not self.model:
            raise ValueError("Failed to load model or tokenizer.")

        if self.word_mode:
            inputs = self.tokenizer(text, return_tensors="pt")
            outputs = self.model(**inputs)
            # Remove [CLS] and [SEP]
            return outputs.word_embeddings[0, 1, :]
        else:
            # print("Device: ", self.model.device)
            inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
            # print(text, inputs)
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                # print(embeddings.shape)
                return embeddings[0]

    @staticmethod
    def similarity(query_embedding: torch.Tensor, embeddings: List[torch.Tensor]):
        """Get similarity between query and passage embeddings.

        Args:
            query (numpy array): Query embedding.
            embedding (numpy array): Passage embedding.

        Returns:
            float: Similarity scores.
        """

        def cosine(query_embedding: torch.Tensor, embedding: torch.Tensor):
            return F.cosine_similarity(query_embedding, embedding, dim=0).item()

        # Compute cosine similarity between two tensors
        return [cosine(query_embedding, embedding) for embedding in embeddings]

    @staticmethod
    def vectorized_similarity(
        query_embedding: torch.Tensor, embeddings: List[torch.Tensor]
    ):
        """Get similarity between query and passage embeddings using vectorized operations.

        Args:
            query_embedding (torch.Tensor): Query embedding.
            embeddings (List[torch.Tensor]): Passage embeddings.

        Returns:
            List[float]: Similarity scores.
        """
        # Convert the query_embedding and embeddings to torch tensors
        query_embedding = torch.tensor(query_embedding)
        t_embeddings = torch.stack(embeddings)

        # Normalize the query_embedding and embeddings
        query_embedding = F.normalize(query_embedding, p=2, dim=0)
        t_embeddings = F.normalize(t_embeddings, p=2, dim=1)

        # Calculate the cosine similarities using torch's matrix multiplication
        similarity_scores = torch.matmul(query_embedding, t_embeddings.t())

        # Convert the result to a list of float values
        return similarity_scores.tolist()


@dataclass
class Score:
    score: float
    category: str
    name: str
    target_text: str
    query: str


@dataclass
class Metadata:
    label: str  # category
    name: str  # name for showing in the results, if we don't see a text, we will use the name as the text to generate embedding
    text: Optional[str] = None  # text to generate embedding
    pmid: Optional[str] = None
    filename: Optional[str] = None
    model_name: Optional[str] = None


@dataclass
class Embedding:
    embedding: torch.Tensor
    metadata: Metadata


def batch_similarity(
    query_embedding: Tuple[str, torch.Tensor],
    embeddings_dict: Dict[str, Embedding],
    use_vectorized: bool = False,
) -> List[Score]:
    """Batch similarity between query and passage embeddings.

    Args:
        query_embedding (str): Query item.
        embeddings_dict (Dict[str, Dict[str, Any]]): Passage embeddings.
        use_vectorized (bool): Use vectorized operations.

    Returns:
        List[Score]: Similarity scores.
    """
    all_results: List[Score] = []
    embeddings = [m.embedding for m in embeddings_dict.values()]
    metadata = pd.DataFrame([m.metadata for m in embeddings_dict.values()])

    print("Query: ", query_embedding[0], query_embedding[1])

    if use_vectorized:
        results = EmbeddingGenerator.vectorized_similarity(
            query_embedding[1], embeddings
        )
    else:
        results = EmbeddingGenerator.similarity(query_embedding[1], embeddings)

    for embedding in embeddings_dict.values():
        print("Embedding: ", embedding.metadata.name, embedding.embedding)

    for i, result in enumerate(results):
        label = metadata.iloc[i]["label"]
        name = metadata.iloc[i]["name"]
        text = metadata.iloc[i]["text"]
        r = Score(
            score=result,
            category=label,
            name=name,
            target_text=text if text else name,
            query=query_embedding[0],
        )
        all_results.append(r)

        # print("Batch similarity done. %s, %s" % (query_item, r))

    return all_results


def get_topk_items(
    results: List[Score], k: int = 3, min_score: float = 0.5
) -> List[Score]:
    """Get top k items based on similarity scores.

    Args:
        results (List[Score]): Similarity scores.
        k (int): Number of top items.
        min_score (float): Minimum similarity score.

    Returns:
        List[Score]: Top k items.
    """
    results.sort(key=lambda x: x.score, reverse=True)
    results = [r for r in results if r.score > min_score]
    return results[:k]


def read_ontology(filepath, sep="\t") -> pd.DataFrame:
    """Read ontology file.

    Args:
        filepath (str): File path.
        sep (str): Separator.

    Returns:
        pd.DataFrame: Ontology.
    """
    ontology = pd.read_csv(filepath, delimiter=sep)
    return ontology


def gen_embeddings4ontology(
    ontology: pd.DataFrame,
    model_name: str,
) -> Dict[str, Embedding]:
    """Generate embeddings for ontology.

    Args:
        ontology (pd.DataFrame): Ontology.
        model_name (str): Model name.
        tokenizer (Optional[tre.Tokenizer]): Tokenizer.
        model (Optional[tre.TransformersEmbedder]): Model.

    Returns:
        Dict[str, Dict[str, Any]]: Embeddings.
    """
    embeddings: Dict[str, Embedding] = {}
    embedding_generator = EmbeddingGenerator(model_name, word_mode=True)
    for item in ontology.iterrows():
        name = item[1]["name"]
        embedding = embedding_generator.gen_text_embedding(name)
        metadata = item[1].to_dict()
        metadata.update({"model_name": model_name})
        metadata = Metadata(**metadata)
        embeddings[name] = Embedding(embedding=embedding, metadata=metadata)

    return embeddings


def gen_embeddings4pubtext(
    pubtext: pd.DataFrame,
    embedding_generator: EmbeddingGenerator,
    save_file: str | None = None,
) -> Dict[str, Embedding]:
    """Generate embeddings for pubtext.

    Args:
        pubtext (pd.DataFrame): Pubtext.
        embedding_generator (EmbeddingGenerator): Embedding generator.
        save_file (str): Save file.

    Returns:
        Dict[str, Metadata]: Embeddings.
    """
    expected_columns = ["label", "name", "text"]
    # name is an id, like <pubmed_id>:<title>
    # label is the category

    if not all(col in pubtext.columns for col in expected_columns):
        raise ValueError(
            "Pubtext columns are not valid, expected columns: %s" % expected_columns
        )

    embeddings_dict: Dict[str, Dict[str, Embedding]] = {}
    if save_file and os.path.exists(save_file):
        with open(save_file, "rb") as handle:
            embeddings_dict = pickle.load(handle)

    embeddings = embeddings_dict[embedding_generator.model_name] if embeddings_dict else {}

    for idx, (_, row) in enumerate(pubtext.iterrows()):
        id = row["name"]
        text = row["text"]

        if id in embeddings:
            print("%s. Embedding for %s already exists." % (idx, id))
            continue

        print("%s. Generate embedding for %s..." % (idx, id))
        embedding = embedding_generator.gen_text_embedding(text)
        metadata = row.to_dict()
        metadata.update({"model_name": embedding_generator.model_name})
        metadata = Metadata(**metadata)
        embeddings[id] = Embedding(embedding=embedding, metadata=metadata)

        # 每10个数据项保存一次，但跳过第0个数据项
        if save_file and idx % 10 == 0 and idx != 0:
            embeddings_dict[embedding_generator.model_name] = embeddings
            save(embeddings_dict, save_file)

    if save_file:
        embeddings_dict[embedding_generator.model_name] = embeddings
        save(embeddings_dict, save_file)

    return embeddings


def save(obj, filepath):
    with open(filepath, "wb") as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


def get_valid_entities(
    items: List[str],
    model_name: str,
    embeddings,
    topk: int = 3,
    min_score: float = 0.5,
    use_vectorized: bool = False,
) -> List[List[Score]]:
    """Get valid entities.

    Args:
        items (List[str]): Items.
        model_name (str): Model name.
        embeddings: Embeddings.
        topk (int): Number of top items.
        min_score (float): Minimum similarity score.
        use_vectorized (bool): Use vectorized operations.

    Returns:
        List[List[Score]]: Valid entities.
    """
    print("Load passage embeddings...")
    embedding_generator = EmbeddingGenerator(model_name, word_mode=True)

    final_results: List[List[Score]] = []
    for item in items:
        query_embedding = embedding_generator.gen_text_embedding(item)
        results = batch_similarity(
            (item, query_embedding),
            embeddings,
            use_vectorized=use_vectorized,
        )

        final_results.append(get_topk_items(results, topk, min_score=min_score))

    return final_results


def find_topn_text_chunks(
    query_text: str,
    text_chunks_file: str,
    model_name: str,
    topn: int = 3,
    min_score: float = 0.5,
    use_vectorized: bool = False,
    use_cohere: bool = False,
) -> List[Dict[str, Any]]:
    """Find top n text chunks.

    Args:
        query_text (str): Query text.
        text_chunks_file (str): Text chunks file.
        model_name (str): Model name.
        topn (int): Number of top items.
        min_score (float): Minimum similarity score.
        use_vectorized (bool): Use vectorized operations.

    Returns:
        List[List[Score]]: Top n text chunks.
    """
    pubtext = pd.read_json(text_chunks_file, lines=False)
    print(f"Number of text chunks: {len(pubtext)}")
    print("Generate embeddings for pubtext...", pubtext.shape)
    embedding_generator = EmbeddingGenerator(model_name, word_mode=False)

    pubtext_embeddings_file = os.path.join(
        os.path.dirname(text_chunks_file), "pubtext_embeddings.pkl"
    )
    embeddings = gen_embeddings4pubtext(
        pubtext, embedding_generator, save_file=pubtext_embeddings_file
    )

    # print(
    #     "Embeddings are generated for pubtext: %s"
    #     % [len(embedding.embedding) for embedding in embeddings.values()]
    # )

    print("Get top n text chunks...")
    results = batch_similarity(
        (query_text, embedding_generator.gen_text_embedding(query_text)),
        embeddings,
        use_vectorized=use_vectorized,
    )

    if use_cohere:
        print("Get top %s items with min score %s..." % (topn * 5, min_score))
        topk_items = get_topk_items(results, topn * 5, min_score=min_score)
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY is not set.")

        documents = [item.target_text for item in topk_items]
        # print("Documents: ", documents[:5])

        co = cohere.Client(api_key)
        results = co.rerank(
            query=query_text,
            documents=documents,
            top_n=topn,
            return_documents=True,
            model="rerank-english-v3.0",
        )

        # print("Results: ", results.results)
        result_dict = {}
        for idx, r in enumerate(results.results):
            print(r.__dict__)
            text = r.document.text if r.document else None
            score = r.relevance_score if r.relevance_score else None
            result_dict[text] = score

        print("Use cohere to rerank the results...")
        for item in topk_items:
            item.__dict__.update({"score": result_dict.get(item.target_text, None)})

        topk_items = list(filter(lambda x: x.score is not None, topk_items))
    else:
        topk_items = get_topk_items(results, topn, min_score=min_score)

    if len(topk_items) == 0:
        print("No top text chunks found.")
        return []

    print("Found top %s text chunks." % len(topk_items))
    print("Update the top n text chunks with pmid and filename...")
    item_dicts = []
    for item in topk_items:
        r = pubtext[pubtext["name"] == item.name]
        print(item.__dict__, r.to_dict(orient="records"))

        item.__dict__.update(
            {
                "pmid": r["pmid"].values[0],
                "filename": r["filename"].values[0],
            }
        )

        item_dicts.append(item.__dict__)

    return item_dicts
