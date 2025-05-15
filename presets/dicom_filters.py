import math

from mmi_kit.service_dict import DictionaryService
from mmi_kit.service_pydicom import PyDicomService


class DicomFilters(object):

    @staticmethod
    def filter_categorized(filepath, categories=None, categories_map=None, **kwargs):
        assert (isinstance(categories, set) or categories is None)
        assert (isinstance(categories_map, dict) or categories_map is None)

        patient_data = {}
        m_data_dict = PyDicomService.get_metadata_dict(filepath, **kwargs)
        for k, v in m_data_dict.items():

            if categories_map is not None and k not in categories_map:
                continue

            cat = categories_map[k] if categories_map is not None else k

            if categories is not None and cat not in categories:
                continue

            # Setup optional type casting.
            type_casting = DictionaryService.try_get(kwargs, path=["cat_cast", cat], default=lambda val: val)

            # Assign value with the type casting.
            patient_data[cat] = type_casting(v)

        return patient_data

