from collections import OrderedDict
from os.path import join

from mmi_kit.series.utils import iter_handled_filepath_series
from mmi_kit.service_os import OsService

from presets.dicom_filters import DicomFilters
from presets.issue87.schemas.v20 import OntologyV20
from presets.issue87.schemas.v21 import OntologyV21
from utils import DATA_DIR, LOCAL_TCIA_NARRATIVES_COLLECTION
from utils_content import LIVER_DATASETS
from utils_dicom_handlers import DICOM_META2CAT_DICT


def __cast_multi_variant(mv):
    if isinstance(mv, str):
        return [mv]
    if mv is None:
        return []
    return list(mv)


def iter_dicom_data(series_dir):
    sr_it = iter_handled_filepath_series(
        series_func=lambda: [
            ("", OsService.iter_dir_filepaths(series_dir))
        ],
        handlers=[
            # for common categories.
            lambda fp: DicomFilters.filter_categorized(
                filepath=fp,
                categories=set(DICOM_default_params) | set(DICOM_relevant_params),
                categories_map=DICOM_META2CAT_DICT,
                cat_cast={
                    "Sequence-Name": lambda v: str(v),
                    "Sequence-Variant": lambda v: __cast_multi_variant(v),
                },
                suppress_wa=True),
        ])

    # Handled data.
    for _, handled_data in sr_it:
        yield handled_data[0]


ISSUE_87_DIR = join(DATA_DIR)


# Predefined set for roots of the collections.
DICOM_ROOTS = {
    "CPTAC-CCRCC": LIVER_DATASETS['tcia-ccrcc']["src"]["series_func"](),
    "CPTAC-CCRCC-rkt": LIVER_DATASETS['tcia-ccrcc-rkt']["src"]["series_func"](),
    "TCGA-LIHC": LIVER_DATASETS['tcga-lihc']["src"]["series_func"](),
}


def create_input_for_model(csv_filename):
    return OrderedDict({
        "collection": {
            # Utilized for obtaining data from the LLM.
            "filepath": join(ISSUE_87_DIR, csv_filename),
            # Initial metadata.
            "metadata": LOCAL_TCIA_NARRATIVES_COLLECTION
        },
    })


MODEL_RESULTS = {
    "llama-3-8b-v20": {
        "predict": "collection-llama-3-8b-instruct_medical.csv",
        "ontology": OntologyV20()
    },
    "llama-3-70b-v20": {
        "predict": "collection-llama-3-70b-instruct_medical.csv",
        "ontology": OntologyV20()
    },

    # ------------
    # T0.1
    # ------------
    # Results that are based on another ontology.
    "chat-gpt-4-v21": {
        "predict": "collection-gpt-4-turbo-2024-04-09_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3-8b-v21": {
        "predict": "collection-llama-3-8b-instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3-70b-v21": {
        "predict": "collection-llama-3-70b-instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "chat-gpt-3-v21": {
        "predict": "collection-gpt-3.5-turbo-0125_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3.2-3b-v21": {
        "predict": "collection-llama-3.2-3B-Instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3.2-1b-v21": {
        "predict": "collection-llama-3.2-1B-Instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    # ------------
    # T0.5
    # ------------
    "llama-3-8b-v21-t05": {
        "predict": "results-t05/collection-llama-3-8b-instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3-70b-v21-t05": {
        "predict": "results-t05/collection-llama-3-70b-instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "chat-gpt-3-v21-t05": {
        "predict": "results-t05/collection-gpt-3.5-turbo-0125_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3.2-3b-v21-t05": {
        "predict": "results-t05/collection-llama-3.2-3B-Instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3.2-1b-v21-t05": {
        "predict": "results-t05/collection-llama-3.2-1B-Instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    # ------------
    # T1.0
    # ------------
    "llama-3-8b-v21-t10": {
        "predict": "results-t10/collection-llama-3-8b-instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3-70b-v21-t10": {
        "predict": "results-t10/collection-llama-3-70b-instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "chat-gpt-3-v21-t10": {
        "predict": "results-t10/collection-gpt-3.5-turbo-0125_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3.2-3b-v21-t10": {
        "predict": "results-t10/collection-llama-3.2-3B-Instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
    "llama-3.2-1b-v21-t10": {
        "predict": "results-t10/collection-llama-3.2-1B-Instruct_medical-v2.1.csv",
        "ontology": OntologyV21()
    },
}

# This field represent a list of collections.
# You have to setup this parameter as this the one utilized in other scripts.
MODEL_TO_TEST = "chat-gpt-4-v21"

# Ontology is picking up automatically depending on the MODEL_TO_TEST.
MODEL_ONTOLOGY_FUNC = lambda model: MODEL_RESULTS[model]["ontology"]

# Input information for handling in scripts.
MODEL_INPUT_FUNC = lambda model: create_input_for_model(csv_filename=MODEL_RESULTS[model]["predict"])

# Setup for the DICOM parameters.
DICOM_default_params = ["Modality", "Patient_ID", "ID-Series", "Patient_Age", "Patient_Weight", "Patient_Sex"]
# NOTE:
# It is being discovered that these parameters serve the most valuable information
# necessary for filling the ontology with the image essence: weighting, plane, acquisition, contrast presence.
DICOM_relevant_params = ["Image-param_Repetition-Time", "Image-param_Echo-Time", "Contrast-Agent",
                         "Image-param_FlipAngle", "Sequence-Name", "Sequence-Variant", "Protocol-Name",
                         "Series-Description", "Photometric-Interpretation", "Echo-Numbers", "Modality"]


FIELD_LOG_HANDLERS = {
    # "weight_is_dwi": lambda data: print(data),
    # "weight_is_adc": lambda data: print(data),
    # "plane_type": lambda data: print(data),
    # "aquisition_echo": lambda data: print(data),
    # "is_fs": lambda data: print(data),
    # "phase_type": lambda data: print(data),
    # "weight_t": lambda data: print(data),
    # "contrast_time": lambda data: print(data),
}


def create_series_header():

    series_header = ([# Weight.
                       "weight_is_dwi",
                       "weight_is_adc",
                       "weight_t",
                       "is_fs",
                       # Contrast.
                       "contrast_time",
                       "is_contrast_agent",
                       # Aquisition mode.
                       "aquisition_echo",
                       "plane_type",
                       # Phase.
                       "phase_type"] +
                     DICOM_default_params +
                     DICOM_relevant_params)

    # Reorder the headers.
    series_header.remove("Patient_ID")
    series_header.insert(0, "Patient_ID")
    series_header.remove("ID-Series")
    series_header.insert(0, "ID-Series")

    return series_header
