"""
Rank_Phenotypes Test Script

Author: Angel Nugroho, NCATS intern 2020
"""

import rank_phenotypes
import random

canavan_disease = {"Macrocephaly":0.545, "Hearing impairment":0.545, "Visual impairmen":0.545, "Blindness":0.545,
"Optic atrophy":0.895, "Abnormality of visual evoked potentials":0.545, "Seizures":0.17, "Muscular hypotonia::0.545,
Global developmental delay:0.895, Hypertonia:0.545, Flexion contracture:0.17, Gastroesophageal reflux: 0.545,
EEG abnormality:0.895, Developmental regression: 0.17, Reduced consciousness/confusion: .895,
Abnormality of retinal pigmentation: .17, Feeding difficulties in infancy: .895, Cognitive impairment: .895}


example_dict = {"HP:000123" : .70 , "HP:000555" : .03}

def generate_patient(phen_dict):
    """
    Returns a list of the phenotypes the patient has.

    Parameters:
    phen_dict: A dictionary of the diseases phenotypes and corresponding prevalences
    """
    patient_phenotypes = []
    for key in phen_dict.keys():
        num = random.randint(1,100)
        if num/100 <= phen_dict[key]:
            patient_phenotypes.append(key)
    return patient_phenotypes


def test_ranks(trials, phen_dict):
    """
    Runs rank_phenotypes for the given number of patients and disease dictionary
    Returns the accuracy of the results (Percentage of trials that gave the correct disease in the top five rankings)
    Parameters:
    trials: A int of the desired number of patient sets to run on
    """
    successes = 0
    for trial in range(trials):
        ex_name = "GARD:000123"
        example = generate_patient(phen_dict)
        rank_list = rank_phenotypes.rank_phenotypes_weighted_tfidf(example)
        top_ranks = []
        if len(rank_list) > 5:
            for entry in rank_list[:5]:
                top_ranks.append(entry[1]["id"])
        else:
            for entry in rank_list:
                top_ranks.append(entry[1]["id"])
        if ex_name in top_5:
            successes += 1
    return successes/trials
