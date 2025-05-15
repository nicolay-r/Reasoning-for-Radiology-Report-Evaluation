# List of the parameters related to the IMAGE-based DICOM files
DICOM_META2CAT_DICT = {
    # Patient related data.
    "Patient ID": "Patient_ID",
    # DICOM file ID
    "SOP Instance UID": "ID",
    "Series Instance UID": "ID-Series",
    # Patients info.
    "Patient's Sex": "Patient_Sex",
    "Patient's Age": "Patient_Age",
    "Patient's Weight": "Patient_Weight",
    # Modality of images.
    "Modality": "Modality",
    # Images parameters.
    "Slice Thickness": "Image-param_Slice-Thickness",
    "Spacing Between Slices": "Image-param_Slice-Thickness",
    "Slice Location": "Image-param_Slice-Location",
    "Repetition Time": "Image-param_Repetition-Time",
    "Pixel Spacing": "Image-param_Pixel-Spacing",
    "Echo Time": "Image-param_Echo-Time",
    # Position and orientation.
    "Image Position (Patient)": "Image-info_Position",
    "Image Orientation (Patient)": "Image-info_Orientation",
    # Contrast/Bolus Agent.
    "Contrast/Bolus Agent": "Contrast-Agent",
    "Contrast/Bolus Volume": "Contrast-Volume",
    "Contrast/Bolus Total Dose": "Contrast-Total-Dose",
    "Contrast/Bolus Ingredient": "Contrast-Ingredient",
    "Contrast/Bolus Ingredient Concentration": "Contrast-Ingredient-Concentration",
    # MR-related parameters.
    "Flip Angle": "Image-param_FlipAngle",
    "Magnetic Field Strength": "Image-param_Magnetic-Field-Strength",
    # Date.
    "Studies Date": "Date-Studies",
    "Series Date": "Date-Series",
    "Acquisition Date": "Date-Acquisition",
    "Content Date": "Date-Content",
    "Date Of Last Calibration": "Date-OfLastCalibration",
    # Sequence related info
    "Sequence Name": "Sequence-Name",
    "Sequence Variant": "Sequence-Variant",
    # Information shares In-Out Phase related parameters in the case of MRI images.
    "Protocol Name": "Protocol-Name",
    # Series Description narratives.
    "Series Description": "Series-Description",
    # Others
    "Photometric Interpretation": "Photometric-Interpretation",
    "Echo Number(s)": "Echo-Numbers",
    "Gradient Echo Train Length": "Gradient-Echo-Train-Length",
    "Multiple Spin Echo": "Multiple-Spin-Echo"
}