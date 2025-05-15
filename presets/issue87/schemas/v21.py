from presets.issue87.schemas.base import BaseOntology
from presets.issue87.schemas.fields import PLANE_TYPE_AXIAL, CONTRAST_TIMING_PRE, \
    CONTRAST_TIMING_PORTAL, CONTRAST_TIMING_DELAYED, CONTRAST_NO, WEIGHTING_T1, CONTRAST_YES, FS_YES, WEIGHTING_T2, \
    PLANE_TYPE_CORONAL, PLANE_TYPE_SAGITTAL, CONTRAST_TIMING_ARTERIAL
from presets.issue87.schemas.v20 import OntologyV20


class OntologyV21(BaseOntology):

    WEIGHTING_DWI = "DWI"
    WEIGHTING_ADC = "ADC"

    @property
    def Name(self):
        return "ontology-v21"

    def __init__(self):
        super().__init__(ontology_dict=self._ONTOLOGY_PARSERS)
        pass

    _ONTOLOGY_PARSERS = {
        # "what's weight type: T1 or T2?"
        "weight_t": {
            "llm": {
                "pattern_tree": {
                    "__init__":
                        OntologyV20._ONTOLOGY_PARSERS["weight_t"]["llm"]["pattern_tree"]["__init__"][:-1] +
                        [(["dwi"], WEIGHTING_DWI)] +
                        [(["adc"], WEIGHTING_ADC)] +
                        [(None, BaseOntology.UNKN_VALUE)]
                }
            },
            "manual": {
                "while_not_true":
                    OntologyV20._ONTOLOGY_PARSERS["weight_t"]["manual"]["while_not_true"][:-1] +
                    OntologyV20._create_dwi_manual(label=WEIGHTING_DWI) +
                    OntologyV20._create_adc_manual(label=WEIGHTING_ADC) +
                    [(lambda _: True, BaseOntology.UNKN_VALUE)]
            },
            # Utilized for evaluation purposes.
            "labels": OntologyV20._ONTOLOGY_PARSERS["weight_t"]["labels"][:-1] +
                      [WEIGHTING_DWI, WEIGHTING_ADC] +
                      [BaseOntology.UNKN_VALUE]
        },
        # "is series has: arterial, portal, delayed or delayed time?"
        "contrast_time": {
            # Parsing response from LLM.
            "llm": {
                "pattern_tree": {
                    "__init__":
                        OntologyV20._ONTOLOGY_PARSERS["contrast_time"]["llm"]["pattern_tree"]["__init__"][:-1] +
                        [(["not applicable"], BaseOntology.UNKN_VALUE),
                         (["not-applicable"], BaseOntology.UNKN_VALUE)] +
                        [(None, BaseOntology.UNKN_VALUE)]
                }
            },
            # Parsing response manually.
            "manual": {
                "while_not_true":
                    OntologyV20._ONTOLOGY_PARSERS["contrast_time"]["manual"]["while_not_true"][:-1] +
                    [(lambda _: True, BaseOntology.UNKN_VALUE)]
            },
            "labels": OntologyV20._ONTOLOGY_PARSERS["contrast_time"]["labels"][:-1] +
                      [BaseOntology.UNKN_VALUE]
        },
        "is_contrast_agent": OntologyV20._ONTOLOGY_PARSERS["is_contrast_agent"],
        "is_fs": OntologyV20._ONTOLOGY_PARSERS["is_fs"],
        "aquisition_echo": OntologyV20._ONTOLOGY_PARSERS["aquisition_echo"],
        "plane_type": OntologyV20._ONTOLOGY_PARSERS["plane_type"],
        "phase_type": OntologyV20._ONTOLOGY_PARSERS["phase_type"],
    }

    def ontology_series_mapping(self):
        return {
            # Weighting
            "axial-adc":
                lambda p_series: [s for s in p_series if
                                  s["weight_t"] == self.WEIGHTING_ADC and s["plane_type"] == PLANE_TYPE_AXIAL],
            "axial-dwi":
                lambda p_series: [s for s in p_series if
                                  s["weight_t"] == self.WEIGHTING_DWI and s["plane_type"] == PLANE_TYPE_AXIAL],
            # T1
            "axial-t1-fs-cont-del":
                lambda p_series: [s for s in p_series if
                                  s["plane_type"] == PLANE_TYPE_AXIAL and
                                  s["weight_t"] == WEIGHTING_T1 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_TIMING_PORTAL and
                                  s["contrast_time"] == CONTRAST_TIMING_DELAYED],
            "axial-t1-fs-cont-port":
                lambda p_series: [s for s in p_series if
                                  s["plane_type"] == PLANE_TYPE_AXIAL and
                                  s["weight_t"] == WEIGHTING_T1 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_TIMING_PORTAL and
                                  s["contrast_time"] == CONTRAST_TIMING_PRE],
            "axial-t1-fs-cont-art":
                lambda p_series: [s for s in p_series if
                                  s["plane_type"] == PLANE_TYPE_AXIAL and
                                  s["weight_t"] == WEIGHTING_T1 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_TIMING_ARTERIAL and
                                  s["contrast_time"] == CONTRAST_TIMING_PRE],
            "axial-t1-fs-cont-pre":
                lambda p_series: [s for s in p_series if
                                  s["plane_type"] == PLANE_TYPE_AXIAL and
                                  s["weight_t"] == WEIGHTING_T1 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_YES and
                                  s["contrast_time"] == CONTRAST_TIMING_PRE],
            "axial-t1-fs":
                lambda p_series: [s for s in p_series if
                                  s["weight_t"] == WEIGHTING_T1 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_NO and s["plane_type"] == PLANE_TYPE_AXIAL],
            "axial-t1":
                lambda p_series: [s for s in p_series if
                                  s["weight_t"] == WEIGHTING_T1 and s.get("is_fs", None) != FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_NO and s["plane_type"] == PLANE_TYPE_AXIAL],
            # T2
            "axial-t2-fs-cont-del":
                lambda p_series: [s for s in p_series if
                                  s["plane_type"] == PLANE_TYPE_AXIAL and
                                  s["weight_t"] == WEIGHTING_T2 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_TIMING_PORTAL and
                                  s["contrast_time"] == CONTRAST_TIMING_DELAYED],
            "axial-t2-fs-cont-port":
                lambda p_series: [s for s in p_series if
                                  s["plane_type"] == PLANE_TYPE_AXIAL and
                                  s["weight_t"] == WEIGHTING_T2 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_TIMING_PORTAL and
                                  s["contrast_time"] == CONTRAST_TIMING_PRE],
            "axial-t2-fs-cont-art":
                lambda p_series: [s for s in p_series if
                                  s["plane_type"] == PLANE_TYPE_AXIAL and
                                  s["weight_t"] == WEIGHTING_T2 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_TIMING_ARTERIAL and
                                  s["contrast_time"] == CONTRAST_TIMING_PRE],
            "axial-t2-fs-cont-pre":
                lambda p_series: [s for s in p_series if
                                  s["plane_type"] == PLANE_TYPE_AXIAL and
                                  s["weight_t"] == WEIGHTING_T2 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_YES and
                                  s["contrast_time"] == CONTRAST_TIMING_PRE],
            "axial-t2-fs":
                lambda p_series: [s for s in p_series if
                                  s["weight_t"] == WEIGHTING_T2 and s.get("is_fs", None) == FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_NO and s["plane_type"] == PLANE_TYPE_AXIAL],
            "axial-t2":
                lambda p_series: [s for s in p_series if
                                  s["weight_t"] == WEIGHTING_T2 and s.get("is_fs", None) != FS_YES and
                                  s["is_contrast_agent"] == CONTRAST_NO and s["plane_type"] == PLANE_TYPE_AXIAL],
            # Timing
            'coronal':
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_CORONAL],
            'sagittal':
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_SAGITTAL]
        }

    def ontology_mapping_header(self):
        return [
            # DWI / ADC
            # Weighting
            "ax-adc", "ax-dwi",
            # t-weighted series with- or w/o contrast
            "ax-t1-fs-pre", "ax-t1-fs-art", "ax-t1-fs-port", "ax-t1-fs-del", "ax-t1-fs", "ax-t1",
            "ax-t2-fs-pre", "ax-t2-fs-art", "ax-t2-fs-port", "ax-t2-fs-del", "ax-t2-fs", "ax-t2",
            # Other
            "cor", "sag"
        ]

    def get_header(self):
        return [
            "weight_t",
            "is_fs",
            "is_contrast_agent",
            "contrast_time",
            "aquisition_echo",
            "plane_type",
            "phase_type",
        ]