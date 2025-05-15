from os.path import join

from collections import Counter

from mmi_kit.service_os import OsService
from source_iter.service_csv import CsvService
from tqdm import tqdm

from core.utils import iter_to_iterator

from presets.issue87.llm_matching_while import do_while_not_true
from presets.issue87.llm_matching_tree import do_pattern_tree_matching
from presets.issue87.schemas.base import BaseOntology
from presets.issue87.utils import iter_dicom_data, FIELD_LOG_HANDLERS, MODEL_INPUT_FUNC, create_series_header, \
    MODEL_TO_TEST, MODEL_ONTOLOGY_FUNC, DICOM_ROOTS, ISSUE_87_DIR


def handle_line(line, ctr_errors, ctr_total, ontology, register_dicom=True, force_params_dict=None, **kwargs):
    assert (isinstance(ontology, BaseOntology))
    assert (isinstance(force_params_dict, dict) or force_params_dict is None)

    # Provide DICOM data.
    dicom_params = {}
    series_dir = join(DICOM_ROOTS[line["Collection"]], line["File Location"])
    for data in iter_dicom_data(series_dir):
        dicom_params.update(data)

    # Initialize output dictionary.
    if force_params_dict is not None:
        processed = {v: line[k] for k, v in force_params_dict.items()}
    else:
        processed = {}

    for field_name, parsing_methods in ontology.iter_ontology_parsers(parser_type="llm"):

        # There might be different version of files utilized in evaluation.
        # Therefore, we consider to skip such parameters that are not presented in line.
        if field_name not in line:
            continue

        text_to_parse = line[field_name].lower()

        parsing_method_collection = {
            "pattern_tree": do_pattern_tree_matching,
            "while_not_true": do_while_not_true,
        }

        for method_name, params in parsing_methods.items():
            field_logger = FIELD_LOG_HANDLERS[field_name] if field_name in FIELD_LOG_HANDLERS else None
            result = parsing_method_collection[method_name](text_to_parse, params, field_logger)
            processed[field_name] = result if result is not None else ontology.UNKN_VALUE

        if field_name in processed and processed[field_name] == ontology.UNKN_VALUE:
            ctr_errors[field_name] += 1

        ctr_total[field_name] += 1

    if register_dicom:
        processed = processed | dicom_params

    return processed


def do_handle_llm_responses(filepath, **handler_args):
    llm_responses = CsvService.read(src=filepath, skip_header=True, as_dict=True, delimiter=",")
    return map(lambda line: handle_line(line=line, **handler_args), llm_responses)


if __name__ == '__main__':

    # Setup error counters.
    errors = Counter()
    total = Counter()

    ontology = MODEL_ONTOLOGY_FUNC(MODEL_TO_TEST)

    # Dump everything into jsonl
    items_it = [do_handle_llm_responses(**p | {"ctr_errors": errors, "ctr_total": total, "ontology": ontology})
                for p in MODEL_INPUT_FUNC(MODEL_TO_TEST).values()]

    dict_it = iter_to_iterator(items_it=items_it)

    series_header = create_series_header()

    # Target dir.
    target_filepath = join(ISSUE_87_DIR, ontology.Name, f'{MODEL_TO_TEST}.csv')
    OsService.create_dir_if_not_exists(target_filepath, is_dir=False)

    # Saving in accessible format.
    CsvService.write(
        target=target_filepath,
        header=create_series_header(),
        data2col_func=lambda data: data,
        data_it=map(lambda row: [row[c] if c in row else "None" for c in series_header],
                    tqdm(dict_it)))

    print("=============")
    print("ERROR SUMMARY")
    print("=============")
    print(f"Ontology: {type(ontology)}")
    print(total.most_common())
    for k, v in errors.most_common():
        print(k, ":", "%.2f" % (100*round(float(v) / total[k], 2)), "%")
    print("=============")
