from collections import Counter
from os.path import join

import argparse
from mmi_kit.service_dict import DictionaryService
from mmi_kit.service_os import OsService
from sklearn.metrics import f1_score
from tqdm import tqdm

from core.service_seaborn import SeabornService
from core.service_spreadsheet import SpreadsheetService
from core.utils import iter_to_iterator
from issue87_2_series_classification_llm import do_handle_llm_responses
from issue87_2_series_classification_manual import do_handle_manual
from presets.issue87.schemas.base import BaseOntology
from presets.issue87.utils import MODEL_INPUT_FUNC, ISSUE_87_DIR, MODEL_RESULTS, MODEL_TO_TEST


def show_log(total, errors):
    for k, v in errors.most_common():
        print(k, ":", "%.2f" % (100 * round(float(v) / total[k], 2)), "%")


def iter_series(h, ontology, m_name):
    errors = Counter()
    total = Counter()
    data_it = [h(**p | {"ctr_errors": errors, "ctr_total": total, "register_dicom": False, "ontology": ontology})
               for p in MODEL_INPUT_FUNC(m_name).values()]
    return data_it, total, errors


def handle_line(line, params, results):
    """ Performs results collection from line according to the list of given parameters.
    """
    assert (isinstance(results, dict))
    for param in params:
        if param in line:
            related_results = DictionaryService.register_path(results, path=[param], value_if_not_exist=[])
            related_results.append(line[param])


def do_eval(gold_results, predict_results, entries_total, ontology,
            show_amount=True, show_amount_p=True, save_f1_visual_func=None):
    assert (isinstance(ontology, BaseOntology))

    amount_d = {}
    res_eval = {}
    res_missed = {}
    for k in ontology.iter_ontology_keys():

        # get labels
        labels = ontology.get_ontology_labels(key=k, keep_unknown=False)
        if labels is None:
            continue

        # preparing results.
        y_true = gold_results.get(k, [])
        y_pred = predict_results.get(k, [])

        # For debugging purposes: exploiting actual labels set.
        actual_labels = [label for label in labels if label in y_pred or label in y_true]

        # This is for the case when
        if len(labels) == 1:
            # Calculating accuracy.
            r_type = 'ACC'
            result = sum([1 for i in range(len(y_true)) if y_true[i] == y_pred[i]]) / len(y_true)
        else:
            # Calculating F-measure.
            r_type = "F1"
            result = f1_score(y_true=y_true, y_pred=y_pred, average="macro", labels=labels, zero_division=0.0)

        # Logging results.
        amount = len(y_true)

        # Formatting evaluated output.
        res_line = "{r_type}({key}) ({actual_labels}): {value} [checked: {amount}/{entries_total}, {percentage}%]".format(
            r_type=r_type, key=k, actual_labels=actual_labels, value="%.2f" % result, amount=amount,
            entries_total=entries_total, percentage="%.2f" % (100 * float(amount) / entries_total))

        print(res_line)

        # Register result in dictionary.
        res_eval[k] = result

        # Logging the percentage of the missed results.
        res_missed[k] = sum([1 for v in y_pred if v == ontology.UNKN_VALUE]) / len(y_pred)

        # Register the total amount.
        amount_d[k] = y_true

        # Evaluation for confusion matrix
        if save_f1_visual_func is not None:

            fig_size = {
                1: (1.8, 1.44),
                2: (2.0, 1.6),
                3: (2.2, 1.76),
                4: (2.4, 1.92),
            }

            x_captions = {
                "weight_t": "Weighting",
                "contrast_time": "Contrast Timing",
                "is_contrast_agent": "Contrast Presence",
                "aquisition_echo": "Technique",
                "plane_type": "Plane",
            }

            SeabornService.confusion_heatmap_2d(true_list=y_true, predict_list=y_pred,
                                                # We compose matrix by using all the class values including UNKN value.
                                                classes_list=actual_labels + [ontology.UNKN_VALUE],
                                                # We display only known values.
                                                classes_list_visual=actual_labels,
                                                do_normalize=True,
                                                save_png_path=save_f1_visual_func(k),
                                                # We pick only first 3 letters.
                                                handle_visual_func=lambda text: text[:3].upper(),
                                                x_caption=x_captions[k] if k in x_captions else k,
                                                figsize=fig_size[len(actual_labels)])

    header = ontology.get_header()

    # Print in format accessible for pasting in Google Spreadsheet.
    print(SpreadsheetService.format_line([round(res_eval.get(v, -1), 2) for v in header]))
    print(SpreadsheetService.format_line([round(res_missed.get(v, -1), 2) for v in header]))

    # Print in format accessible for pasting in Google Spreadsheet.
    if show_amount:
        print(SpreadsheetService.format_line([str(len(amount_d.get(v, []))) for v in header]))
    if show_amount_p:
        print(SpreadsheetService.format_line(["%.1f" % (100 * float(len(amount_d.get(v, []))) / entries_total) for v in header]))


if __name__ == '__main__':
    """ This script is related to evaluation code implementation for automatically classified 
        medical reports by means of Large Language Model / GenAI / Machine learning in general.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('--model', dest='model', type=str, nargs="?", default=MODEL_TO_TEST)

    args = parser.parse_args()

    ontology = MODEL_RESULTS[args.model]["ontology"]

    manual_it, manual_t, manual_e = iter_series(do_handle_manual, ontology=ontology, m_name=args.model)
    llm_it, llm_t, llm_e = iter_series(do_handle_llm_responses, ontology=ontology, m_name=args.model)

    gold_results = dict()
    predict_results = dict()
    entries_total = 0
    for gold_line, predict_line in tqdm(zip(iter_to_iterator(manual_it), iter_to_iterator(llm_it)), desc=args.model):

        # For such parameters which values are defined both in gold annotation and predict annotation.
        known_gold_params = [k for k in ontology.iter_ontology_keys() if gold_line[k] != ontology.UNKN_VALUE]

        # Collecting the results.
        handle_line(line=gold_line, params=known_gold_params, results=gold_results)
        # Predicted.
        handle_line(line=predict_line, params=known_gold_params, results=predict_results)

        entries_total += 1

    print("=============")
    print("ERROR SUMMARY")
    print("=============")
    print(f"Ontology: {type(ontology)}")
    print("-------------")
    for k in manual_t.keys():
        print("----------------")
        print(f"Collection: {k}")
        print("----------------")
        show_log(total=manual_t[k], errors=manual_e[k])
    print("=============")
    show_log(total=llm_t, errors=llm_e)
    print("=============")

    print("OUTPUT")
    print("------")
    print(gold_results)
    print(predict_results)

    print("EVALUATION")
    print("----------")

    # Target dir.
    target_dir = join(ISSUE_87_DIR, ontology.Name)
    OsService.create_dir_if_not_exists(target_dir, is_dir=True)

    do_eval(gold_results=gold_results, predict_results=predict_results, entries_total=entries_total, ontology=ontology,
            show_amount=False, show_amount_p=False,
            save_f1_visual_func=lambda cat: join(target_dir, f"{args.model}-{cat}.png"))
