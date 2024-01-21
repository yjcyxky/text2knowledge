ENTITY_EXTRACTION_PROMPT_TEMPLATE = """
Your task is to extract the key concepts (and non-personal entities) mentioned in the given context. 
Extract only the most important and atomistic concepts, if needed break the concepts down to simpler concepts.
Categorize the concepts in one of the following categories: 
[Gene, Compound, Disease, Symptom, Pathway, Anatomy, Metabolite, MolecularFunction, BiologicalProcess, CellularComponent]

Format your output as a list of JSON with the following format:

[
   {
       "entity": "The Concept",
       "importance": "The contextual importance of the concept on a scale of 1 to 5 (5 being the highest)",
       "category": "The Type of Concept"
   },
   { },
]
"""

RELATION_EXTRACTION_PROMPT_TEMPLATE = """
You are a network graph maker who extracts terms and their relations from a given context. 
You are provided with a context chunk (delimited by ```) Your task is to extract the ontology 
of terms mentioned in the given context. These terms should represent the key concepts as per the context.

Thought 1: While traversing through each sentence, Think about the key terms mentioned in it.
    Terms may include object, entity, location, organization, person, 
    condition, acronym, documents, service, concept, etc.
    Terms should be as atomistic as possible

Thought 2: Think about how these terms can have one on one relation with other terms.
    Terms that are mentioned in the same sentence or the same paragraph are typically related to each other.
    Terms can be related to many other terms

Thought 3: Find out the relation between each such related pair of terms. 

The type of relation between two terms can be one of the following:
[associated_with, upregulated_in, downregulated_in, activated_by, inhibited_by, reduced_by, increased_by, alleviated_by, induced_by, unknown]

Format your output as a list of json. Each element of the list contains a pair of terms and the relation between them, like the following: 
[
   {
       "source_name": "A concept from extracted ontology",
       "source_type": "The type of the concept, e.g. Gene, Compound, Disease, Symptom, Pathway, Anatomy, Metabolite, MolecularFunction, BiologicalProcess, CellularComponent, etc.",
       "target_name": "A related concept from extracted ontology",
       "target_type": "The type of the concept, e.g. Gene, Compound, Disease, Symptom, Pathway, Anatomy, Metabolite, MolecularFunction, BiologicalProcess, CellularComponent, etc.",
       "relation_type": "The type of relation between the two concepts."
       "key_sentence": "relationship between the two concepts, node_1 and node_2 in one or two sentences"
   }, {...}
]
"""
