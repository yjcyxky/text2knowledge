ENTITY_EXTRACTION_PROMPT_TEMPLATE = """
To ensure the analysis is both comprehensive and accurate, it is crucial to identify and categorize biomedical entities from the text strictly according to the provided categories. Your output should only include entities that fit into the following categories: 'Gene', 'Protein', 'Compound', 'Disease', 'Symptom', 'Pathway', 'Anatomy', 'Metabolite', 'MolecularFunction', 'BiologicalProcess', 'CellularComponent'. Any entities that do not align with these categories must be omitted.

For each identified entity, detail the following in a JSON list format:
- Entity name (it must be a biomedical entity fitting into the provided categories)
- Confidence score from 1 to 5, with 5 being the highest
- The applicable category from the provided list

Please be mindful that accuracy in categorization is paramount, and relevance to the overarching biomedical context is crucial. Non-biomedical entities or entities not fitting the predefined categories should not be included in your output. Here are examples of correctly formatted outputs based on these instructions:

Arguments exist as to the cause of chronic fatigue syndrome (CFS). Some think that it is an example of symptom amplification indicative of functional or psychogenic illness, while our group thinks that some CFS patients may have brain dysfunction. To further pursue our encephalopathy hypothesis, we did spinal taps on 31 women and 13 men fulfilling the 1994 case definition for CFS and on 8 women and 5 men serving as healthy controls. Our outcome measures were white blood cell count, protein concentration in spinal fluid, and cytokines detectable in spinal fluid. We found that significantly more CFS patients had elevations in either protein levels or number of cells than healthy controls (30 versus 0%), and 13 CFS patients had protein levels and cell numbers that were higher than laboratory norms; patients with abnormal fluid had a lower rate of having comorbid depression than those with normal fluid. In addition, of the 11 cytokines detectable in spinal fluid, (i) levels of granulocyte-macrophage colony-stimulating factor were lower in patients than controls, (ii) levels of interleukin-8 (IL-8) were higher in patients with sudden, influenza-like onset than in patients with gradual onset or in controls, and (iii) IL-10 levels were higher in the patients with abnormal spinal fluids than in those with normal fluid or controls. The results support two hypotheses: that some CFS patients have a neurological abnormality that may contribute to the clinical picture of the illness and that immune dysregulation within the central nervous system may be involved in this process.

```
[
    {
        "entity": "Chronic Fatigue Syndrome (CFS)",
        "confidence": "5",
        "category": "Disease"
    },
    {
        "entity": "brain dysfunction",
        "confidence": "4",
        "category": "Symptom"
    },
    {
        "entity": "depression",
        "confidence": "4",
        "category": "Disease"
    },
    {
        "entity": "granulocyte-macrophage colony-stimulating factor",
        "confidence": "4",
        "category": "Protein"
    },
    {
        "entity": "interleukin-8 (IL-8)",
        "confidence": "4",
        "category": "Protein"
    },
    {
        "entity": "IL-10",
        "confidence": "5",
        "category": "Protein"
    },
    {
        "entity": "Neurological abnormality",
        "confidence": "4",
        "category": "Symptom"
    },
    {
        "entity": "Immune dysregulation",
        "confidence": "5",
        "category": "BiologicalProcess"
    },
    {
        "entity": "Central nervous system",
        "confidence": "5",
        "category": "Anatomy"
    }
]
```

Remember, adherence to the category list is non-negotiable. Continuous refinement should be based on aligning strictly with the provided categories, improving the accuracy and relevance of identified entities.
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

Format your output as a list of json. Each element of the list contains a pair of terms and the relation between them, like the following: 
[
   {
       "source_name": "A concept from extracted ontology",
       "source_type": "The type of the concept, one of Gene, Compound, Disease, Symptom, Pathway, Anatomy, Metabolite, MolecularFunction, BiologicalProcess, CellularComponent.",
       "target_name": "A related concept from extracted ontology",
       "target_type": "The type of the concept, one of Gene, Compound, Disease, Symptom, Pathway, Anatomy, Metabolite, MolecularFunction, BiologicalProcess, CellularComponent.",
       "relation_type": "The type of relation between the two concepts, one of BioMedGPS::AssociatedWith::Gene:Disease, BioMedGPS::Modulator::Compound:Gene, BioMedGPS::Interaction::Gene:Gene, BioMedGPS::VirGeneHumGene::Gene:Gene, BioMedGPS::Activator::Compound:Gene, BioMedGPS::Agonist::Compound:Gene, BioMedGPS::AllostericModulator::Compound:Gene, BioMedGPS::Antagonist::Compound:Gene, BioMedGPS::Antibody::Compound:Gene, BioMedGPS::Binder::Compound:Gene, BioMedGPS::Blocker::Compound:Gene, BioMedGPS::Inhibitor::Compound:Gene, BioMedGPS::AssociatedWith::Compound:Gene, BioMedGPS::Carrier::Compound:Gene, BioMedGPS::Interaction::Compound:Compound, BioMedGPS::Treatment::Compound:Disease, BioMedGPS::AtcClassification::Compound:Atc, BioMedGPS::Binder::Gene:Gene, BioMedGPS::Target::Gene:Disease, BioMedGPS::E+::Compound:Gene, BioMedGPS::E-::Compound:Gene, BioMedGPS::E::Compound:Gene, BioMedGPS::E+::Gene:Gene, BioMedGPS::E::Gene:Gene, BioMedGPS::Promotor::Gene:Disease, BioMedGPS::InComplex::Gene:Gene, BioMedGPS::InPathway::Gene:Gene, BioMedGPS::InTax::Gene:Tax, BioMedGPS::Causer::Compound:Disease, BioMedGPS::Causer::Gene:Disease, BioMedGPS::PharmacoKinetics::Compound:Gene, BioMedGPS::Biomarker::Gene:Disease, BioMedGPS::Biomarker::Compound:Disease, BioMedGPS::Influencer::Gene:Gene, BioMedGPS::SideEffect::Compound:Disease, BioMedGPS::Activator::Gene:Gene, BioMedGPS::Risky::Gene:Disease, BioMedGPS::E-::Anatomy:Gene, BioMedGPS::E::Anatomy:Gene, BioMedGPS::E+::Anatomy:Gene, BioMedGPS::SimilarWith::Compound:Compound, BioMedGPS::E-::Disease:Gene, BioMedGPS::LocatedIn::Disease:Anatomy, BioMedGPS::Present::Disease:Symptom, BioMedGPS::SimilarWith::Disease:Disease, BioMedGPS::E+::Disease:Gene, BioMedGPS::Covary::Gene:Gene, BioMedGPS::InBP::Gene:BiologicalProcess, BioMedGPS::InCC::Gene:CellularComponent, BioMedGPS::InMF::Gene:MolecularFunction, BioMedGPS::InPathway::Gene:Pathway, BioMedGPS::InPC::Compound:PharmacologicClass, BioMedGPS::AdpRibosylationReaction::Gene:Gene, BioMedGPS::AssociatedWith::Gene:Gene, BioMedGPS::CleavageReaction::Gene:Gene, BioMedGPS::InLocation::Gene:Gene, BioMedGPS::DePhosphorylationReaction::Gene:Gene, BioMedGPS::Interaction::Compound:Gene, BioMedGPS::PhosphorylationReaction::Gene:Gene, BioMedGPS::ProteinCleavage::Gene:Gene, BioMedGPS::UbiquitinationReaction::Gene:Gene, BioMedGPS::Inbitor::Gene:Gene, BioMedGPS::PostTranslationalMod::Gene:Gene, BioMedGPS::AssociatedWith::Pathway:Disease, BioMedGPS::AssociatedWith::Gene:Symptom, BioMedGPS::Contraindication::Disease:Compound, BioMedGPS::NE::Anatomy:Gene, BioMedGPS::AssociatedWith::BiologicalProcess:Gene, BioMedGPS::AssociatedWith::BiologicalProcess:Exposure, BioMedGPS::AssociatedWith::CellularComponent:Gene, BioMedGPS::AssociatedWith::CellularComponent:Exposure, BioMedGPS::AssociatedWith::MolecularFunction:Gene, BioMedGPS::AssociatedWith::Gene:Pathway, BioMedGPS::AssociatedWith::Gene:Exposure, BioMedGPS::AssociatedWith::MolecularFunction:Exposure, BioMedGPS::AssociatedWith::Exposure:Disease, BioMedGPS::ParentChild::Anatomy:Anatomy, BioMedGPS::ParentChild::BiologicalProcess:BiologicalProcess, BioMedGPS::ParentChild::CellularComponent:CellularComponent, BioMedGPS::ParentChild::Disease:Disease, BioMedGPS::ParentChild::MolecularFunction:MolecularFunction, BioMedGPS::ParentChild::Pathway:Pathway, BioMedGPS::ParentChild::Symptom:Symptom, BioMedGPS::ParentChild::Exposure:Exposure, BioMedGPS::Absent::Disease:Symptom, BioMedGPS::SideEffect::Compound:Symptom, BioMedGPS::Target::Gene:Compound, BioMedGPS::Transporter::Gene:Compound."
       "key_sentence": "relationship between the two concepts, node_1 and node_2 in one or two sentences"
   }, {...}
]
"""
