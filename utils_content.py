from collections import OrderedDict
from os.path import join, dirname

from presets.file_iterators_dicom import CPTAC_CCRCC_Service, TCGA_LIHC_Service
from utils import DATASETS_DIR


tcia_ccrcc_root = join(DATASETS_DIR, "tcia-ccrcc")
tcia_ccrcc_rkt_root = join(DATASETS_DIR, "tcia-ccrcc-rkt")
tcga_lihc = join(DATASETS_DIR, "TCGA-LIHC")


# This dictionary represent a common collection of
# all datasets utilized in studies.
LIVER_DATASETS = OrderedDict({
    "tcga-lihc": {
        "src": {
            "default": tcga_lihc,
            "series_func": lambda: dirname(LIVER_DATASETS["tcga-lihc"]["meta"]["default"]),
        },
        "meta": {
            "default": TCGA_LIHC_Service.metadata_search(tcga_lihc),
            # This classification has been manually added to the resource content and is not a part of the original CPTAC-CCRCC collection.
            "classification-auto": CPTAC_CCRCC_Service.metadata_search(tcga_lihc, template="series-classification"),
        },
    },
    # Page: https://www.cancerimagingarchive.net/collection/cptac-ccrcc/
    # https://www.cancerimagingarchive.net/wp-content/uploads/TCIA-CPTAC-CCRCC_v11_20230818.tcia
    "tcia-ccrcc": {
        "src": {
            # The default root where collection has been downloaded.
            "default": tcia_ccrcc_root,
            # The root for the all series, i.e. where everything has been unpacked.
            "series_func": lambda: dirname(LIVER_DATASETS["tcia-ccrcc"]["meta"]["default"]),
        },
        "meta": {
            "default": CPTAC_CCRCC_Service.metadata_search(tcia_ccrcc_root),
            # This classification has been manually added to the resource content and is not a part of the original CPTAC-CCRCC collection.
            "classification-auto": CPTAC_CCRCC_Service.metadata_search(tcia_ccrcc_root, template="series-classification"),
        },
    },
    # Page: https://www.cancerimagingarchive.net/collection/cptac-ccrcc/
    # Represent additional part of the collection that describes 4 patients.
    "tcia-ccrcc-rkt": {
        "src": {
            # The default root where collection has been downloaded.
            "default": tcia_ccrcc_rkt_root,
            # The root for the all series, i.e. where everything has been unpacked.
            "series_func": lambda: dirname(LIVER_DATASETS["tcia-ccrcc-rkt"]["meta"]),
        },
        "meta": CPTAC_CCRCC_Service.metadata_search(dir_path=tcia_ccrcc_rkt_root),
    },
})

