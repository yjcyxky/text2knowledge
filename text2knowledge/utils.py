from transformers import AutoModel, AutoConfig
from transformers import AutoTokenizer
from transformers import PreTrainedTokenizer
from transformers import PreTrainedModel
import transformers_embedder as tre
from pathlib import Path
import pandas as pd
import torch
import torch.nn.functional as F
import pickle
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


def load_model(model_name: str | Path) -> PreTrainedModel:
    """Load model from HuggingFace.

    Args:
        model_name (str): Model name.

    Returns:
        AutoModel: Model.
    """
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, config=config)

    return model


def load_tokenizer(
    model_name: str | Path, use_fast: bool = False
) -> PreTrainedTokenizer:
    """Load tokenizer from HuggingFace.

    Args:
        model_name (str): Model name.

    Returns:
        AutoTokenizer: Tokenizer.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=use_fast)

    return tokenizer  # type: ignore

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


def gen_word_embedding(
    word: str,
    model_name: str = "",
    tokenizer: tre.Tokenizer | None = None,
    model: tre.TransformersEmbedder | None = None,
    subword_pooling_strategy: str = "sparse",
    layer_pooling_strategy: str = "mean",
):
    """Convert model to word embedding."""
    if not tokenizer:
        if model_name:
            t = tre.Tokenizer(model_name)
        else:
            raise ValueError("Model name is None.")
    else:
        t = tokenizer

    if not model:
        if model_name:
            m = tre.TransformersEmbedder(
                model_name,
                subword_pooling_strategy=subword_pooling_strategy,
                layer_pooling_strategy=layer_pooling_strategy,
            )
        else:
            raise ValueError("Model name is None.")
    else:
        m = model

    if t and m:
        inputs = t(word, return_tensors=True)
        outputs = m(**inputs)
        # Remove [CLS] and [SEP]
        return outputs.word_embeddings[0, 1, :]
    else:
        raise ValueError("Model or tokenizer is None.")


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


def vectorized_similarity(
    query_embedding: torch.Tensor, embeddings: List[torch.Tensor]
):
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
    raw_name: str


def batch_similarity(
    query_item: str,
    embeddings_dict: Dict[str, Dict[str, Any]],
    model_name: str,
    use_vectorized: bool = False,
) -> List[Score]:
    all_results: List[Score] = []
    embeddings = [m.get("embedding", []) for m in embeddings_dict.values()]
    metadata = pd.DataFrame([m.get("metadata") for m in embeddings_dict.values()])
    query_embedding = gen_word_embedding(query_item, model_name=model_name)
    if use_vectorized:
        results = vectorized_similarity(query_embedding, embeddings)
    else:
        results = similarity(query_embedding, embeddings)

    for i, result in enumerate(results):
        label = metadata.iloc[i]["label"]
        name = metadata.iloc[i]["name"]
        r = Score(
            score=result,
            category=label,
            name=name,
            raw_name=query_item,
        )
        all_results.append(r)

        # print("Batch similarity done. %s, %s" % (query_item, r))

    return all_results


def get_topk_items(
    results: List[Score], k: int = 3, min_score: float = 0.5
) -> List[Score]:
    results.sort(key=lambda x: x.score, reverse=True)
    results = [r for r in results if r.score > min_score]
    return results[:k]


def read_ontology(filepath, sep="\t") -> pd.DataFrame:
    ontology = pd.read_csv(filepath, delimiter=sep)
    return ontology


def gen_embeddings4ontology(
    ontology: pd.DataFrame,
    model_name: str = "",
    tokenizer: tre.Tokenizer | None = None,
    model: tre.TransformersEmbedder | None = None,
) -> Dict[str, Dict[str, Any]]:
    embeddings = {}
    for item in ontology.iterrows():
        label = item[1]["label"]
        name = item[1]["name"]
        embedding = gen_word_embedding(
            name,
            model_name=model_name,
            tokenizer=tokenizer,
            model=model,
            subword_pooling_strategy="sparse",
            layer_pooling_strategy="mean",
        )
        metadata = item[1].to_dict()
        embeddings[name] = {
            "embedding": embedding,
            "metadata": metadata,
            "label": label,
        }

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
    print("Load passage embeddings...")

    final_results: List[List[Score]] = []
    for item in items:
        results = batch_similarity(
            item, embeddings, model_name=model_name, use_vectorized=use_vectorized
        )

        final_results.append(get_topk_items(results, topk, min_score=min_score))

    return final_results
