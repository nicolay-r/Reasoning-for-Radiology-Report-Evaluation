# Reasoning for Radiology Report Evaluation
![](https://img.shields.io/badge/Python-3.10-brightgreen.svg)

<p align="center">
    <img src="https://github.com/user-attachments/assets/ac78b035-1ef7-43a5-ad08-94d5df2aff15" width="800" height="auto"/>
</p>
<p align="center">
  <a href="https://www.dropbox.com/scl/fi/ixo08df4nzfco5e52a7b8/AniNex_CASA_2025_Poster_Print_2_Pages_Version.pdf?rlkey=ksc5q7mretnnvr8iuhjp7m083&st=zuqxe037&dl=1">👉<b>poster</b>👈</a>
</p>

This repository represent a code for a poster paper 
[Using Large Language Models for Evaluation of Radiological Textual Reports
](https://www.dropbox.com/scl/fi/ixo08df4nzfco5e52a7b8/AniNex_CASA_2025_Poster_Print_2_Pages_Version.pdf?rlkey=ksc5q7mretnnvr8iuhjp7m083&st=zuqxe037&dl=1) 
at 
[AniNex / CASA-2025 Workshop](https://casa2025.sciencesconf.org).


## Experiment Organization

### [📦 Link to utilized resources](./utils_content.py)
> Requires downloaded `DICOM` files for accessing patient-related parameters from [TCIA](https://www.cancerimagingarchive.net/).

## Usage

1. Install project dependencies:
```bash
pip install -r dependencies.txt
```
2. Launch scripts, for example.
```bash
python issue87_2_series_classification_llm.py
```

## Resources

### [✍️ Link to the series narratives dataset **PSN-tcia**](./datasets/tcia_series_narratives/collection.csv)

### [🤖 Link to the LLM responses](./data/collection-gpt-4-turbo-2024-04-09_medical-v2.1.csv)


## Organizations

This work has been accomplished as a part of Research Fellow position @ Bournemouth University.
<p><img src="org.png"/></p>
