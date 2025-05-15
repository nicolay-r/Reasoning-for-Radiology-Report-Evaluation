import os
from os.path import dirname, realpath, join

current_dir = dirname(realpath(__file__))
DATA_DIR = join(current_dir, "data")
TEST_DIR = join(DATA_DIR, "test")
CACHE_DIR = join(DATA_DIR, ".cache")

# This is a default folder for all datasets
home_dir = os.path.expanduser("~")
DATASETS_DIR = join(home_dir, "datasets")

# See issue 106.
LOCAL_DATASETS_DIR = join(current_dir, "datasets")
LOCAL_TCIA_NARRATIVES_COLLECTION = join(LOCAL_DATASETS_DIR, "tcia_series_narratives", "collection.csv")
LOCAL_TCIA_NARRATIVES_LANG_CHECK = join(LOCAL_DATASETS_DIR, "tcia_series_narratives", "collection-llama-3-70b-instruct_translation.csv")
