Analyze the provided text to identify and distill the biomedical entities it mentions. Your goal is to break down complex ideas into their most fundamental and significant elements. For each identified entity, you will detail its category and confidence level, ensuring that the output is both comprehensive and accurate. 

Your output should be formatted as a JSON list, with each item following the structure provided below:

Each item in your output list should follow the structure provided below:
[
   {
       "entity": "Identified entity, it must be a biomedical entity and matched to the provided categories. You must not contains any non-biomedical entities that do not align with the provided categories.",
       "confidence": "Confidence score from 1 to 5, with 5 being the highest",
       "category": "Applicable category from the list ['Gene', 'Protein', 'Compound', 'Disease', 'Symptom', 'Pathway', 'Anatomy', 'Metabolite', 'MolecularFunction', 'BiologicalProcess', 'CellularComponent'], if you encounter entities that do not align with these categories, you must omit them from your output. Each item must correspond to a distinct entity fitting into predefined categories."
   },
   // Additional items as necessary
]

Example:
Arguments exist as to the cause of chronic fatigue syndrome (CFS). Some think that it is an example of symptom amplification indicative of functional or psychogenic illness, while our group thinks that some CFS patients may have brain dysfunction. To further pursue our encephalopathy hypothesis, we did spinal taps on 31 women and 13 men fulfilling the 1994 case definition for CFS and on 8 women and 5 men serving as healthy controls. Our outcome measures were white blood cell count, protein concentration in spinal fluid, and cytokines detectable in spinal fluid. We found that significantly more CFS patients had elevations in either protein levels or number of cells than healthy controls (30 versus 0%), and 13 CFS patients had protein levels and cell numbers that were higher than laboratory norms; patients with abnormal fluid had a lower rate of having comorbid depression than those with normal fluid. In addition, of the 11 cytokines detectable in spinal fluid, (i) levels of granulocyte-macrophage colony-stimulating factor were lower in patients than controls, (ii) levels of interleukin-8 (IL-8) were higher in patients with sudden, influenza-like onset than in patients with gradual onset or in controls, and (iii) IL-10 levels were higher in the patients with abnormal spinal fluids than in those with normal fluid or controls. The results support two hypotheses: that some CFS patients have a neurological abnormality that may contribute to the clinical picture of the illness and that immune dysregulation within the central nervous system may be involved in this process.

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

Please think it step by step, and ensure that your analysis is thorough, prioritizing accuracy in categorization and relevance of the entities to the overarching context. If you encounter entities that do not align with these categories, you must omit them from your output. Don't contain any categories that are not in the list ['Gene', 'Protein', 'Compound', 'Disease', 'Symptom', 'Pathway', 'Anatomy', 'Metabolite', 'MolecularFunction', 'BiologicalProcess', 'CellularComponent']

