from collections import Counter
from os.path import join

from mmi_kit.service_dict import DictionaryService
from mmi_kit.service_os import OsService
from source_iter.service_csv import CsvService
from tqdm import tqdm

from core.service_spreadsheet import SpreadsheetService
from core.utils import iter_to_iterator
from presets.issue87.llm_matching_while import do_while_not_true
from presets.issue87.schemas.base import BaseOntology
from presets.issue87.schemas.v21 import OntologyV21
from presets.issue87.utils import MODEL_INPUT_FUNC, iter_dicom_data, create_series_header, FIELD_LOG_HANDLERS, \
    DICOM_ROOTS, ISSUE_87_DIR, MODEL_TO_TEST


def handle_line(line, ctr_errors, ctr_total, ontology, register_dicom=True, force_params_dict=None, **kwargs):
    assert (isinstance(ontology, BaseOntology))
    assert (isinstance(force_params_dict, dict) or force_params_dict is None)

    # Provide DICOM data.
    dicom_params = {}
    collection_name = line["Collection"]
    series_dir = join(DICOM_ROOTS[collection_name], line["File Location"])
    for data in iter_dicom_data(series_dir):
        dicom_params.update(data)

    # Initialize output dictionary.
    if force_params_dict is not None:
        processed = {v: line[k] for k, v in force_params_dict.items()}
    else:
        processed = {}

    for field_name, parsing_methods in ontology.iter_ontology_parsers(parser_type="manual"):

        parsing_method_collection = {
            "while_not_true": do_while_not_true,
        }

        for method_name, params in parsing_methods.items():
            field_logger = FIELD_LOG_HANDLERS[field_name] if field_name in FIELD_LOG_HANDLERS else None
            result = parsing_method_collection[method_name](dicom_params, params, field_logger)
            processed[field_name] = result if result is not None else ontology.UNKN_VALUE

        # Registering information in total.
        ctr_collection_total = DictionaryService.register_path(ctr_total, path=[collection_name], value_if_not_exist=Counter())
        ctr_collection_total[field_name] += 1
        # Register information per field.
        ctr_collection_total[f"{field_name}:{processed[field_name]}"] += 1

        if field_name in processed and processed[field_name] == ontology.UNKN_VALUE:
            # Registering found errors.
            ctr_collection_e = DictionaryService.register_path(ctr_errors, path=[collection_name], value_if_not_exist=Counter())
            ctr_collection_e[field_name] += 1

    if register_dicom:
        processed = processed | dicom_params

    return processed


def do_handle_manual(metadata, **handler_args):
    csv_metadata = CsvService.read(src=metadata, skip_header=True, as_dict=True, delimiter=",")
    return map(lambda line: handle_line(line=line, **handler_args), csv_metadata)


if __name__ == '__main__':

    # Setup dictionaries for errors stat and total stat.
    errors = {}
    total = {}

    ontology = OntologyV21()

    # Dump everything into jsonl
    items_it = [do_handle_manual(**p | {"ctr_errors": errors, "ctr_total": total, "ontology": ontology})
                for p in MODEL_INPUT_FUNC(MODEL_TO_TEST).values()]

    dict_it = iter_to_iterator(items_it=items_it)

    series_header = create_series_header()

    # Target dir.
    target_filepath = join(ISSUE_87_DIR, ontology.Name, "series-results-manual.csv")
    OsService.create_dir_if_not_exists(target_filepath, is_dir=False)

    # Saving in accessible format.
    CsvService.write(
        target=target_filepath,
        header=create_series_header(),
        data2col_func=lambda data: data,
        data_it=map(lambda row: [row[c] if c in row else "None" for c in series_header],
                    tqdm(dict_it)))

    header = ontology.get_header()

    for k, v_err in errors.items():
        print(SpreadsheetService.format_line([k] + [round(total[k][h] - v_err[h], 1) for h in header]))
        print(SpreadsheetService.format_line(["%"] + [round(100 * (total[k][h] - v_err[h]) / total[k][h], 2)
                                                      for h in header]))

    print("-----------------")
    print("Total statistics:")
    print("-----------------")

    ds_stat_ctr = Counter()
    for ctr in total.values():
        ds_stat_ctr += ctr

    for h in header:
        # output header stat. we keep only known amount of values.
        total_per_concept = ds_stat_ctr[h] - ds_stat_ctr[h + ":" + ontology.UNKN_VALUE]
        print(h, total_per_concept)
        for k, value in ds_stat_ctr.items():
            if k.startswith(h + ":") and not k.endswith(ontology.UNKN_VALUE):
                print("\t",
                      k.split(':')[1][:3].ljust(5, " "),
                      #value,
                      f"{round(100 * value / total_per_concept, 2)}%")
