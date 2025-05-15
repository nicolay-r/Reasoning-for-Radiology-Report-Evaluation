import random

from tqdm import tqdm

from core.utils import iter_to_iterator
from issue87_2_series_classification_manual import do_handle_manual
from issue87_4_evaluation import iter_series, handle_line, do_eval
from presets.issue87.utils import MODEL_ONTOLOGY_FUNC, MODEL_TO_TEST


def get_baseline_line(keep_unknown, ontology):

    line = {}

    for k in ontology.iter_ontology_keys():
        labels = ontology.get_ontology_labels(k, keep_unknown=keep_unknown)
        predict = random.randint(0, len(labels) - 1)
        line[k] = labels[predict]

    return line


def calc(manual_it, ontology):

    entries_total = 0
    gold_results = dict()
    predict_results = dict()
    for gold_line in tqdm(desc="Baseline [Random] evaluation", iterable=iter_to_iterator(manual_it)):

        predict_line = get_baseline_line(keep_unknown=False, ontology=ontology)

        # For such parameters which values are defined both in gold annotation and predict annotation.
        known_params = [k for k in ontology.iter_ontology_keys() if gold_line[k] != ontology.UNKN_VALUE]

        # Collecting the results.
        handle_line(line=gold_line, params=known_params, results=gold_results)
        handle_line(line=predict_line, params=known_params, results=predict_results)

        entries_total += 1

    return gold_results, predict_results, entries_total


if __name__ == '__main__':
    """ This script is related to evaluation code implementation for automatically classified 
        medical reports by means of Large Language Model / GenAI / Machine learning in general.
    """

    random.seed(42)

    # Select proper ontology for evaluation.
    ontology = MODEL_ONTOLOGY_FUNC(MODEL_TO_TEST)

    print("Results for RANDOM w/o UNK-VALUE [Assign only known values.]")
    manual_it, manual_t, manual_e = iter_series(h=do_handle_manual, ontology=ontology, m_name=MODEL_TO_TEST)
    g, p, e = calc(manual_it=manual_it, ontology=ontology)
    do_eval(gold_results=g, predict_results=p, entries_total=e, ontology=ontology)
