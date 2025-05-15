from collections import Counter
from os.path import join

from mmi_kit.service_dict import DictionaryService
from mmi_kit.service_os import OsService
from tqdm import tqdm

from core.service_txt import TextService
from core.utils import iter_to_iterator
from issue87_2_series_classification_llm import do_handle_llm_responses
from issue87_2_series_classification_manual import do_handle_manual
from presets.issue87.utils import MODEL_INPUT_FUNC, MODEL_TO_TEST, MODEL_ONTOLOGY_FUNC, ISSUE_87_DIR


def iter_series(h, ontology, force_params_dict):
    errors = Counter()
    total = Counter()
    data_it = [h(**p | {"ctr_errors": errors, "ctr_total": total, "register_dicom": False,
                        "ontology": ontology, "force_params_dict": force_params_dict})
               for p in MODEL_INPUT_FUNC(MODEL_TO_TEST).values()]
    return data_it, total, errors


def handle_line(line, params, results, meta, meta_params_func):
    """ Performs results collection from line according to the list of given parameters.
    """
    assert (isinstance(results, dict))

    for param in params:
        if param in line:

            # Save original results.
            related_results = DictionaryService.register_path(results, path=[param], value_if_not_exist=[])
            related_results.append(line[param])

            # Save meta-information.
            meta_results = DictionaryService.register_path(meta, path=[param], value_if_not_exist=[])
            meta_results.append(":".join([line[x] for x in meta_params_func(param)]))


def do_analysis(k):

    # get labels
    labels = ontology.get_ontology_labels(key=k, keep_unknown=False)

    if labels is not None:
        # preparing results.
        y_true = gold_results.get(k, [])
        y_pred = predict_results.get(k, [])

        # metadata.
        m_true = gold_meta.get(k)
        m_pred = predict_meta.get(k, [])

        for i in range(len(y_true)):

            if y_pred[i] == y_true[i]:
                continue

            pred_text = m_pred[i].replace('\n', " ")

            yield f"{i}: `{m_true[i]}` ({y_true[i]}) predicted as `{y_pred[i]}`"
            yield f"\tResponse: {pred_text}"


if __name__ == '__main__':

    ontology = MODEL_ONTOLOGY_FUNC(MODEL_TO_TEST)

    manual_meta = ["Study Description", "Series Description"]

    manual_it, manual_t, manual_e = iter_series(
        do_handle_manual, ontology=ontology,
        force_params_dict={p: f"_{p}" for p in manual_meta})

    llm_it, llm_t, llm_e = iter_series(
        do_handle_llm_responses, ontology=ontology,
        force_params_dict={p: f"_{p}" for p in ontology.get_header()})

    # Actual results.
    gold_results = dict()
    predict_results = dict()

    # Meta-data for analysis.
    gold_meta = dict()
    predict_meta = dict()

    entries_total = 0
    for gold_line, predict_line in tqdm(zip(iter_to_iterator(manual_it), iter_to_iterator(llm_it)), desc=MODEL_TO_TEST):

        # For such parameters which values are defined both in gold annotation and predict annotation.
        known_gold_params = [k for k in ontology.iter_ontology_keys() if gold_line[k] != ontology.UNKN_VALUE]

        # Collecting the results.
        handle_line(line=gold_line, params=known_gold_params, results=gold_results,
                    meta_params_func=lambda _: [f"_{p}" for p in manual_meta], meta=gold_meta)
        # Predicted.
        handle_line(line=predict_line, params=known_gold_params, results=predict_results,
                    meta_params_func=lambda p: [f"_{p}"], meta=predict_meta)

        entries_total += 1

    # Setup target dir.
    target_dir = join(ISSUE_87_DIR, ontology.Name)
    OsService.create_dir_if_not_exists(target_dir, is_dir=True)

    # Log the output.
    for k in ontology.iter_ontology_keys():
        TextService.write_list(target=join(target_dir, f"analysis-{MODEL_TO_TEST}-{k}.txt"),
                               list_data=do_analysis(k))
