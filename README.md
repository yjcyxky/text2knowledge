## Text to Knolwedge Graph

### Introduction

A new solution to convert text to knowledge graph

1. `Extract` all biomedical entities from the text by using a large language model (e.g. ChatGPT4, Vicuna, etc.)
2. Convert all preset ontology items to `embeddings`
3. `Map` all extracted entities to the ontology items by computing the similarity between the embeddings, and then pick up the top N similar ontology items for each entity
4. Use a more precise method to `re-rank` the top N similar ontology items for each entity and pick up the top 1
5. `Generate questions` from the mapped ontology items. If we have ten entities, we can generate **_C(10, 2) = 10! / [2!(10-2)!] = (10 _ 9) / (2 _ 1) = 45_** questions. We can reduce the number of questions based on our needs, such as we only care about the specific entities.
6. `Pick up the answer for each question` from the text by using a large language model (e.g. ChatGPT4, Vicuna, etc.)

### Improvement plan

1. Fine-tune embedding algorithm for biomedical entities
2. Select the most suitable similarity algorithm
3. Select a suitable re-ranking algorithm
4. Improve the prompts for generating questions based on the characteristics of the large language model
