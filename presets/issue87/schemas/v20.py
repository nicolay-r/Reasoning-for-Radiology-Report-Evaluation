from presets.issue87.llm_matching_while import do_while_not_true
from presets.issue87.schemas.base import BaseOntology
from presets.issue87.schemas.fields import CONTRAST_NO, CONTRAST_YES, \
    CONTRAST_TIMING_PRE, CONTRAST_TIMING_ARTERIAL, CONTRAST_TIMING_PORTAL, CONTRAST_TIMING_DELAYED, ECHO_GRADIENT, \
    ECHO_SPIN, PLANE_TYPE_AXIAL, PLANE_TYPE_SAGITTAL, PLANE_TYPE_CORONAL, WEIGHTING_T1, WEIGHTING_T2, FS_YES, \
    PHASE_IN, PHASE_OUT
from presets.issue87.schemas.utils import manual_terms_split


class OntologyV20(BaseOntology):

    #####
    # ADC
    DWI_YES = "+"
    DWI_NO = "."

    #####
    # ADC
    ADC_YES = "+"
    ADC_NO = "."

    def __init__(self):
        super().__init__(ontology_dict=self._ONTOLOGY_PARSERS)
        pass

    @property
    def Name(self):
        return "ontology-v20"

    @staticmethod
    def _create_dwi_manual(label):
        return [
            # DWI is only supported for MR images.
            (lambda line: "MR" not in line["Modality"], BaseOntology.UNKN_VALUE),
            # Filtering rules.
            (lambda line: "Series-Description" in line and "dwi" in manual_terms_split(line["Series-Description"].lower()), label),
            (lambda line: "Series-Description" in line and "b50" in manual_terms_split(line["Series-Description"].lower()) and
                                                           "adc" not in line["Series-Description"].lower(), label),
            (lambda line: "Series-Description" in line and "edwi" in manual_terms_split(line["Series-Description"].lower()), label),
            (lambda line: "Series-Description" in line and "diffusion" in line["Series-Description"].lower() and
                                                           "apparent" not in line["Series-Description"].lower() and
                                                           "coefficient" not in line["Series-Description"].lower(), label),
        ]

    @staticmethod
    def _create_adc_manual(label):
        # DWI is only supported for MR images.
        return [
            (lambda line: "MR" not in line["Modality"], BaseOntology.UNKN_VALUE),
            # Filtering rules.
            (lambda line: "Series-Description" in line and "adc" in manual_terms_split(line["Series-Description"].lower()), label),
            (lambda line: "Series-Description" in line and line["Series-Description"].endswith('ADC'), label),
            (lambda line: "Series-Description" in line and "apparent" in line["Series-Description"].lower() and 
                                                           "diffusion" in line["Series-Description"].lower() and
                                                           "coefficient" in line["Series-Description"].lower(), label),
        ]

    @staticmethod
    def _contrast_timing_manual():
        return [
            # Contrast agent is supported for any modality.
            (lambda line: "MR" not in line["Modality"] and "CT" not in line["Modality"], BaseOntology.UNKN_VALUE),
            # Timing stage.
            (lambda line: "Series-Description" in line and "pre" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_PRE),
            (lambda line: "Series-Description" in line and "arterial" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_ARTERIAL),
            (lambda line: "Series-Description" in line and "art" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_ARTERIAL),
            (lambda line: "Series-Description" in line and "late art." in line["Series-Description"].lower(), CONTRAST_TIMING_ARTERIAL),
            # Portal stage.
            (lambda line: "Series-Description" in line and "portal" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_PORTAL),
            # In several cases there might be misspellings.
            # Usually varies in between: 60-120 sec.
            (lambda line: "Series-Description" in line and "porotal" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_PORTAL),
            (lambda line: "Series-Description" in line and "venous" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_PORTAL),
            (lambda line: "Series-Description" in line and "p.venous" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_PORTAL),
            # Delayed stage. (might not be contrast there).
            # Usually: 3-5 minutes. Might be even more.
            # (lambda line: "Series-Description" in line and "3min" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_DELAYED),
            # (lambda line: "Series-Description" in line and "3 min" in line["Series-Description"].lower(), CONTRAST_TIMING_DELAYED),
            # (lambda line: "Series-Description" in line and "5min" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_DELAYED),
            # (lambda line: "Series-Description" in line and "5 min" in line["Series-Description"].lower(), CONTRAST_TIMING_DELAYED),
            (lambda line: "Series-Description" in line and "10 min" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_DELAYED),
            (lambda line: "Series-Description" in line and "15 min" in line["Series-Description"].lower(), CONTRAST_TIMING_DELAYED),
            (lambda line: "Series-Description" in line and "20min" in manual_terms_split(line["Series-Description"].lower()), CONTRAST_TIMING_DELAYED),
            (lambda line: "Series-Description" in line and "20 min" in line["Series-Description"].lower(), CONTRAST_TIMING_DELAYED),
            (lambda line: "Series-Description" in line and "delay" in line["Series-Description"].lower(), CONTRAST_TIMING_DELAYED),
            (lambda _: True, BaseOntology.UNKN_VALUE)
        ]

    @staticmethod
    def get_contrast_timing_manual(line):
        return do_while_not_true(line, params=OntologyV20._contrast_timing_manual())

    _ONTOLOGY_PARSERS = {
        # "is series represent Diffusion Weighted (DWI)?"
        "weight_is_dwi": {
            # Parsing response from LLM.
            "llm": {
                "while_not_true": [
                    (lambda text: "yes" in text.lower(), DWI_YES),
                    (lambda text: "no" in text.lower(), DWI_NO),
                ]
            },

            # Parsing response manually.
            "manual": {
                "while_not_true": _create_dwi_manual(label=DWI_YES) +
                                  [(lambda _: True, DWI_NO)]
            },
            "labels": [DWI_YES, DWI_NO, BaseOntology.UNKN_VALUE]
        },
        # "is series represent Apparent Diffusion Coefficient (ADC) mapping?"
        "weight_is_adc": {
            # Parsing response from LLM.
            "llm": {
                "while_not_true": [
                    (lambda text: "yes" in text.lower(), ADC_YES),
                    (lambda text: "no" in text.lower(), ADC_NO),
                ]
            },
            # Parsing response manually.
            "manual": {
                "while_not_true": _create_adc_manual(label=ADC_YES) +
                                  [(lambda _: True, ADC_NO)]
            },
            "labels": [ADC_YES, ADC_NO, BaseOntology.UNKN_VALUE]
        },
        # "is series has contrast agent?"
        "is_contrast_agent": {
            # Parsing response from LLM.
            "llm": {
                "while_not_true": [
                    (lambda text: "yes" in text.lower(), CONTRAST_YES),
                    (lambda text: "no" in text.lower(), CONTRAST_NO),
                ]
            },
            "manual": {
                "while_not_true": [
                    # Contrast agent is supported for any modality.
                    (lambda line: "MR" not in line["Modality"] and "CT" not in line["Modality"], BaseOntology.UNKN_VALUE),
                    # Rely on Series Description field.
                    (lambda line: "Series-Description" in line and "non-contrast" in line["Series-Description"].lower(), CONTRAST_NO),
                    (lambda line: "Series-Description" in line and "non contrast" in line["Series-Description"].lower(), CONTRAST_NO),
                    (lambda line: "Series-Description" in line and "no contrast" in line["Series-Description"].lower(), CONTRAST_NO),
                    (lambda line: "Series-Description" in line and "contrast routine" in line["Series-Description"].lower(), CONTRAST_YES),
                    # mentioning that contrast agent is presented.
                    (lambda line: OntologyV20.get_contrast_timing_manual(line) in [CONTRAST_TIMING_PORTAL, CONTRAST_TIMING_ARTERIAL], CONTRAST_YES),
                    (lambda _: True, BaseOntology.UNKN_VALUE)
                ]
            },
            "manual_meta": {
                "while_not_true": [
                    (lambda line: "Contrast-Agent" in line and line["Contrast-Agent"].lower() == "yes", CONTRAST_YES),
                    (lambda line: "Contrast-Agent" in line and line["Contrast-Agent"].lower() == "applied", CONTRAST_YES),
                    (lambda line: "Contrast-Agent" in line and line["Contrast-Agent"].lower() != "none" and len(line["Contrast-Agent"]) > 0, CONTRAST_YES),
                    (lambda _: True, BaseOntology.UNKN_VALUE)
                ]
            },
            "labels": [CONTRAST_YES, CONTRAST_NO, BaseOntology.UNKN_VALUE]
        },
        # "is series has: arterial, portal, delayed or delayed time?"
        "contrast_time": {
            # Parsing response from LLM.
            "llm": {
                "pattern_tree": {
                    "__init__": [
                        "choice",
                        # Before administration of the contrast agent.
                        (['pre-contrast'], CONTRAST_TIMING_PRE),
                        (['arterial'], CONTRAST_TIMING_ARTERIAL),
                        (['portal'], CONTRAST_TIMING_PORTAL),
                        (['delayed'], CONTRAST_TIMING_DELAYED),
                        # Anything else means we don't know.
                        (None, BaseOntology.UNKN_VALUE)
                    ],
                }
            },
            # Parsing response manually.
            "manual": {
                "while_not_true": _contrast_timing_manual()
            },
            "labels": [CONTRAST_TIMING_PRE, CONTRAST_TIMING_ARTERIAL, CONTRAST_TIMING_PORTAL, CONTRAST_TIMING_DELAYED, BaseOntology.UNKN_VALUE]
        },
        # "is series acquisition is spin echo or gradient echo?"
        "aquisition_echo": {
            # Parsing response from LLM.
            "llm": {
                "pattern_tree": {
                    "__init__": [
                        "choice",
                        (["spin echo", "spin-echo"], ECHO_SPIN),
                        (["gradient"], ECHO_GRADIENT),
                        # Anything else means we don't know
                        (None, BaseOntology.UNKN_VALUE)
                    ],
                },
            },
            # Parsing response manually.
            "manual": {
                "while_not_true": [
                    # DWI is only supported for MR images.
                    (lambda line: "MR" not in line["Modality"], BaseOntology.UNKN_VALUE),
                    # Fast Gre common entry.
                    (lambda line: "Series-Description" in line and "ssfse" in manual_terms_split(line["Series-Description"].lower()), ECHO_SPIN),
                    (lambda line: "Series-Description" in line and "frfse" in manual_terms_split(line["Series-Description"].lower()), ECHO_SPIN),
                    (lambda line: "Series-Description" in line and "fse" in manual_terms_split(line["Series-Description"].lower()), ECHO_SPIN),
                    (lambda line: "Series-Description" in line and "fgre" in manual_terms_split(line["Series-Description"].lower()), ECHO_GRADIENT),
                    # Three-dimensional T1-weighted GRADIENT RECALL ECHO (3D T1W GRE) volumetric interpolated breath-hold examination (VIBE).
                    (lambda line: "Series-Description" in line and "vibe" in manual_terms_split(line["Series-Description"].lower()), ECHO_GRADIENT),
                    # HASTE T2 weighted image (T2WI) half-Fourier acquired single turbo spin-echo (HASTE)
                    (lambda line: "Series-Description" in line and "haste" in manual_terms_split(line["Series-Description"].lower()), ECHO_SPIN),
                    # BLADE: uses a Turbo Spin Echo(TSE) sequence to reduce motion artifacts
                    (lambda line: "Series-Description" in line and "blade" in manual_terms_split(line["Series-Description"].lower()), ECHO_SPIN),
                    # Anything else means we don't know.
                    (lambda _: True, BaseOntology.UNKN_VALUE)
                ]
            },
            "labels": [ECHO_SPIN, ECHO_GRADIENT, BaseOntology.UNKN_VALUE]
        },
        # "what's the plane type: axial, coronal, sagittal?"
        "plane_type": {
            "llm": {
                "pattern_tree": {
                    "__init__": [
                        "choice",
                        (["axial", "transverse"], PLANE_TYPE_AXIAL),
                        (["sagittal"], PLANE_TYPE_SAGITTAL),
                        (["coronal"], PLANE_TYPE_CORONAL),
                        # Anything else means we don't know.
                        (None, BaseOntology.UNKN_VALUE)
                    ],
                },
            },
            # Parsing response manually.
            "manual": {
                "while_not_true": [
                    # Contrast agent is supported for any modality.
                    (lambda line: "MR" not in line["Modality"] and "CT" not in line["Modality"], BaseOntology.UNKN_VALUE),
                    # Seeking for the related value.
                    (lambda line: "Series-Description" in line and "axial" in manual_terms_split(line["Series-Description"].lower()), PLANE_TYPE_AXIAL),
                    (lambda line: "Series-Description" in line and "ax" in manual_terms_split(line["Series-Description"].lower()), PLANE_TYPE_AXIAL),
                    (lambda line: "Series-Description" in line and "sagittal" in manual_terms_split(line["Series-Description"].lower()), PLANE_TYPE_SAGITTAL),
                    (lambda line: "Series-Description" in line and "sag" in manual_terms_split(line["Series-Description"].lower()), PLANE_TYPE_SAGITTAL),
                    (lambda line: "Series-Description" in line and "cor" in manual_terms_split(line["Series-Description"].lower()), PLANE_TYPE_CORONAL),
                    (lambda line: "Series-Description" in line and "coronal" in manual_terms_split(line["Series-Description"].lower()), PLANE_TYPE_CORONAL),
                    # Anything else means we don't know.
                    (lambda _: True, BaseOntology.UNKN_VALUE)
                ]
            },
            # Utilized for evaluation purposes.
            "labels": [PLANE_TYPE_AXIAL, PLANE_TYPE_SAGITTAL, PLANE_TYPE_CORONAL, BaseOntology.UNKN_VALUE]
        },
        # "what's weight type: T1 or T2?"
        "weight_t": {
            "llm": {
                "pattern_tree": {
                    "__init__": [
                        "choice",
                        (["**t1**", "t1"], WEIGHTING_T1),
                        (["**t2**", "t2"], WEIGHTING_T2),
                        # Anything else means we don't know.
                        (None, BaseOntology.UNKN_VALUE)
                    ],
                }
            },
            "manual": {
                "while_not_true": [
                    # DWI is only supported for MR images.
                    (lambda line: "MR" not in line["Modality"], BaseOntology.UNKN_VALUE),
                    # Direct mention of the related weighting.
                    (lambda line: "Series-Description" in line and "t1" in manual_terms_split(line["Series-Description"].lower()), WEIGHTING_T1),
                    (lambda line: "Series-Description" in line and "t-1" in manual_terms_split(line["Series-Description"].lower()), WEIGHTING_T1),
                    (lambda line: "Series-Description" in line and "t2" in manual_terms_split(line["Series-Description"].lower()), WEIGHTING_T2),
                    (lambda line: "Series-Description" in line and "t-2" in manual_terms_split(line["Series-Description"].lower()), WEIGHTING_T2),
                    (lambda line: "Series-Description" in line and "post-t2" in manual_terms_split(line["Series-Description"].lower()), WEIGHTING_T2),
                    # Indirect. VIBE: Three-dimensional T1-weighted gradient recall echo (3D T1W GRE) volumetric interpolated breath-hold examination (VIBE).
                    # According to the related paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC6209485/
                    (lambda line: "Series-Description" in line and "vibe" in manual_terms_split(line["Series-Description"].lower()), WEIGHTING_T1),
                    # Indirect. HASTE: T2 weighted image (T2WI) half-Fourier acquired single turbo spin-echo (HASTE).
                    # According to the related paper: https://pubmed.ncbi.nlm.nih.gov/8835965/
                    (lambda line: "Series-Description" in line and "haste" in manual_terms_split(line["Series-Description"].lower()), WEIGHTING_T2),
                    # Anything else means we don't know.
                    (lambda _: True, BaseOntology.UNKN_VALUE)
                ]
            },
            # Utilized for evaluation purposes.
            "labels": [WEIGHTING_T1, WEIGHTING_T2, BaseOntology.UNKN_VALUE]
        },
        # Fat suppressed.
        "is_fs": {
            "llm": {
                "while_not_true": [
                    (lambda text: "yes" in text.lower(), FS_YES),
                    # NOTE: we use UNKN_VALUE because it is not a part of the evaluation, but at the same time we
                    # don't want count it as an error of non-recognized value.
                    (lambda text: "no" in text.lower(), BaseOntology.UNKN_VALUE),
                ]
            },
            "manual": {
                "while_not_true": [
                    # DWI is only supported for MR images.
                    (lambda line: "MR" not in line["Modality"], BaseOntology.UNKN_VALUE),
                    # https://radiopaedia.org/articles/fat-suppressed-imaging
                    (lambda line: "Series-Description" in line and "SPAIR" in line["Series-Description"], FS_YES),
                    # Fat suppression is commonly used in magnetic resonance imaging (MRI) imaging to suppress the signal from adipose tissue or detect adipose tissue
                    (lambda line: "Series-Description" in line and "SPIR" in line["Series-Description"], FS_YES),
                    (lambda line: "Series-Description" in line and "STIR" in line["Series-Description"], FS_YES),
                    # FS mentions inside or by the beginning or at the end of the line.
                    (lambda line: "Series-Description" in line and " FS " in line["Series-Description"] or line["Series-Description"].startswith("FS ") or line["Series-Description"].endswith(" FS"), FS_YES),
                    (lambda line: "Series-Description" in line and " fs " in line["Series-Description"] or line["Series-Description"].startswith("fs ") or line["Series-Description"].endswith(" fs"), FS_YES),
                    # The Fat-Sat technique is the most widely used method for fat suppression.
                    # https://mriquestions.com/fat-sat-pulses.html#/
                    (lambda line: "Series-Description" in line and "fatsat" in line["Series-Description"].lower(), FS_YES),
                    (lambda line: "Series-Description" in line and "fat sat" in line["Series-Description"].lower(), FS_YES),
                    (lambda _: True, BaseOntology.UNKN_VALUE)
                ]
            },
            # Utilized for evaluation purposes.,
            "labels": [FS_YES, BaseOntology.UNKN_VALUE]
        },
        # "{response} and echo type `{aquisition_echo}` is series represent: in-phase or out-of-phase image?"
        "phase_type": {
            "llm": {
                "pattern_tree": {
                    "__init__": [
                        "if-else",
                        (["represents both"], 'in-out'),
                        "single"
                    ],
                    "single": [
                        "choice",
                        (["in-phase"], PHASE_IN),
                        (["out-of-phase"], PHASE_OUT),
                        # Anything else means we don't know
                        (None, BaseOntology.UNKN_VALUE)
                    ]
                },
            },
            "manual": {
                "while_not_true": [
                    # DWI is only supported for MR images.
                    (lambda line: "MR" not in line["Modality"], BaseOntology.UNKN_VALUE),
                    # Value selection.
                    (lambda line: "Series-Description" in line and "inphase" in manual_terms_split(line["Series-Description"].lower()), PHASE_IN),
                    (lambda line: "Series-Description" in line and
                                  "in" in manual_terms_split(line["Series-Description"].lower()) and
                                  "phase" in manual_terms_split(line["Series-Description"].lower()), PHASE_IN),
                    (lambda line: "Series-Description" in line and "outphase" in manual_terms_split(line["Series-Description"].lower()), PHASE_OUT),
                    (lambda line: "Series-Description" in line and
                                  "out" in manual_terms_split(line["Series-Description"].lower()) and
                                  "phase" in manual_terms_split(line["Series-Description"].lower()), PHASE_OUT),
                    (lambda _: True, BaseOntology.UNKN_VALUE)
                ]
            },
            # Utilized for evaluation purposes.
            "labels": [PHASE_IN, PHASE_OUT, BaseOntology.UNKN_VALUE]
        }
    }

    # This is a mapping schema from series towards the patient-related data.
    def ontology_series_mapping(self):
        return {
            # Phased
            "axial-phased-in":
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_AXIAL and s["phase_type"] == PHASE_IN],
            "axial-phased-out":
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_AXIAL and s["phase_type"] == PHASE_OUT],
            "axial-phased-in-out":
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_AXIAL and s["phase_type"] == 'in-out'],
            "axial-phased-none":
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_AXIAL and s["phase_type"] == '.'],
            # Timing
            'axial-time-pre':
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_AXIAL and s["contrast_time"] == CONTRAST_TIMING_PRE],
            'axial-time-portal':
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_AXIAL and s["contrast_time"] == CONTRAST_TIMING_PORTAL],
            'axial-time-del':
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_AXIAL and s["contrast_time"] == CONTRAST_TIMING_DELAYED],
            'axial-time-none':
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_AXIAL and s["contrast_time"] == CONTRAST_NO],
            # Weighting
            "axial-adc":
                lambda p_series: [s for s in p_series if s["weight_is_adc"] == self.ADC_YES and s["plane_type"] == PLANE_TYPE_AXIAL],
            "axial-dwi":
                lambda p_series: [s for s in p_series if s["weight_is_dwi"] == self.DWI_YES and s["plane_type"] == PLANE_TYPE_AXIAL],
            # T1
            "t1-cont-fs":
                lambda p_series: [s for s in p_series if s["weight_t"] == WEIGHTING_T1 and s.get("is_fs", None) == FS_YES and s["is_contrast_agent"] == CONTRAST_YES and s["plane_type"] == PLANE_TYPE_AXIAL],
            "t1-cont":
                lambda p_series: [s for s in p_series if s["weight_t"] == WEIGHTING_T1 and s.get("is_fs", None) != FS_YES and s["is_contrast_agent"] == CONTRAST_YES and s["plane_type"] == PLANE_TYPE_AXIAL],
            "t1-fs":
                lambda p_series: [s for s in p_series if s["weight_t"] == WEIGHTING_T1 and s.get("is_fs", None) == FS_YES and s["is_contrast_agent"] == CONTRAST_NO and s["plane_type"] == PLANE_TYPE_AXIAL],
            "t1":
                lambda p_series: [s for s in p_series if s["weight_t"] == WEIGHTING_T1 and s["is_contrast_agent"] == CONTRAST_NO and s["plane_type"] == PLANE_TYPE_AXIAL],
            # T2
            "t2-cont-fs":
                lambda p_series: [s for s in p_series if s["weight_t"] == WEIGHTING_T2 and s.get("is_fs", None) == FS_YES and s["is_contrast_agent"] == CONTRAST_YES and s["plane_type"] == PLANE_TYPE_AXIAL],
            "t2-cont":
                lambda p_series: [s for s in p_series if s["weight_t"] == WEIGHTING_T2 and s.get("is_fs", None) != FS_YES and s["is_contrast_agent"] == CONTRAST_YES and s["plane_type"] == PLANE_TYPE_AXIAL],
            "t2-fs":
                lambda p_series: [s for s in p_series if s["weight_t"] == WEIGHTING_T2 and s.get("is_fs", None) == FS_YES and s["is_contrast_agent"] == CONTRAST_NO and s["plane_type"] == PLANE_TYPE_AXIAL],
            "t2":
                lambda p_series: [s for s in p_series if s["weight_t"] == WEIGHTING_T2 and s["is_contrast_agent"] == CONTRAST_NO and s["plane_type"] == PLANE_TYPE_AXIAL],
            # Other
            'coronal':
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_CORONAL],
            'sagittal':
                lambda p_series: [s for s in p_series if s["plane_type"] == PLANE_TYPE_SAGITTAL],
        }

    def ontology_mapping_header(self):
        return [
           # DWI / ADC
           # Phased
           "axial-phased-in", "axial-phased-out", "axial-phased-in-out", "axial-phased-none",
           # Timing.
           'axial-time-pre', 'axial-time-portal', 'axial-time-del', 'axial-time-none',
           # Weighting
           "axial-adc", "axial-dwi",
           "t1-cont-fs", "t1-cont", "t1-fs", "t1",
           "t2-cont-fs", "t2-cont", "t2-fs", "t2",
           # Other
           "coronal", "sagittal"
        ]
    
    def get_header(self):
        return ["weight_is_adc", "weight_is_dwi", "weight_t", "is_fs", "is_contrast_agent", "contrast_time",
                "aquisition_echo", "plane_type", "phase_type"]