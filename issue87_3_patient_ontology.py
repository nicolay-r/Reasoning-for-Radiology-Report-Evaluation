from os.path import join

from mmi_kit.service_dict import DictionaryService
from mmi_kit.service_os import OsService
from tqdm import tqdm
from collections import Counter

from source_iter.service_csv import CsvService

from presets.issue87.utils import MODEL_INPUT_FUNC, DICOM_default_params, ISSUE_87_DIR, MODEL_ONTOLOGY_FUNC, MODEL_TO_TEST

from core.utils import iter_to_iterator

from issue87_2_series_classification_llm import do_handle_llm_responses


def group_in_memory_iter(dict_it, col_id):
    """ This method performs grouping of the elements.
    """

    buffer = {}
    for dict_data in dict_it:
        target = DictionaryService.register_path(buffer, path=[dict_data[col_id]], value_if_not_exist=[])
        target.append(dict_data)

    for content in buffer.values():
        yield content


def series_to_patients(series_group_it, cols_mapping, default_cols):

    for patient_series in series_group_it:
        assert (isinstance(patient_series, list))

        patient_data = {}

        for col, h in cols_mapping.items():
            patient_data[col] = len(h(patient_series))

        # Keep default columns by fetching the value from the first row.
        for col in default_cols:
            if col in patient_series[0]:
                patient_data[col] = patient_series[0][col]

        yield patient_data


if __name__ == '__main__':

    # Setup error counters.
    errors = Counter()
    total = Counter()

    ontology = MODEL_ONTOLOGY_FUNC(MODEL_TO_TEST)

    # Dump everything into jsonl
    items_it = [do_handle_llm_responses(**p | {"ctr_errors": errors, "ctr_total": total, "ontology": ontology})
                for p in MODEL_INPUT_FUNC(MODEL_TO_TEST).values()]

    series_it = iter_to_iterator(items_it=items_it)

    aligned_patients_it = series_to_patients(
        series_group_it=group_in_memory_iter(dict_it=tqdm(series_it), col_id="Patient_ID"),
        cols_mapping=ontology.ontology_series_mapping(),
        default_cols=DICOM_default_params)

    header = (ontology.ontology_mapping_header() +
              DICOM_default_params)

    # Reorder the headers.
    header.remove("Patient_ID")
    header.insert(0, "Patient_ID")
    header.remove("ID-Series")
    header.remove("Modality")

    # Target filepath.
    target = join(ISSUE_87_DIR, ontology.Name, f"patient-ontology-{MODEL_TO_TEST}.csv")
    OsService.create_dir_if_not_exists(target, is_dir=False)

    # Saving in accessible format.
    CsvService.write(
        target=target,
        header=header,
        data2col_func=lambda data: data,
        data_it=map(lambda row: [row[c] if c in row else "None" for c in header],
                    aligned_patients_it))
