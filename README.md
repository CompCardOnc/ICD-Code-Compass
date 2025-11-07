# ICD-Code-Compass

> A tool for exploring, downloading, and publishing ICD mapping files.

<div align="center">

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Build](https://img.shields.io/badge/CI-pytest-informational)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-3776AB)
![Tests](https://img.shields.io/badge/tests-passing-success)

</div>

## ✨ What is this?

**ICD-Code-Compass** is a Python toolkit and service for working with ICD codes (lookup, mapping, and publishing).

The service allows user to explore, filter, and export ICD mapping files intended for use in registry-based research, with the objective of speeding up and increasing the reproducability and transparency of registry-based studies.

Try out the service now: [ICD-Code-Compass](https://compcardonc.github.io/ICD-Code-Compass/)

---

## 🤝 Contributing
Contributing to the project is easy. Simply open up an [issue](https://github.com/CompCardOnc/ICD-Code-Compass/issues) to:
- Report bugs
- Request new features
- Request the addition of new files to provide additional mappings or labels

---

## 🗂️ Project layout

```
ICD-Code-Compass/
├─ src/icd_code_compass/      # package code (public API lives here)
├─ tests/                     # pytest suite
├─ scripts/                   # runnable scripts
├─ data/                      # reference data
├─ config/                    # configuration files
├─ docs/                      # website
├─ requirements.txt
├─ pytest.ini
└─ LICENSE (MIT)
```
---

## Installation

```bash
# clone the repo
git clone https://github.com/CompCardOnc/ICD-Code-Compass.git
cd ICD-Code-Compass

# (optional) create a venv
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# install deps
pip install -r requirements.txt
```

---

## Running scripts
To generate a new mappings file, run:
```bash
./scripts/generate-mappings.sh
```

To generate a new labels file, run:
```bash
./scripts/generate-labels.sh
```

---

## 📄 License

**MIT** — see [`LICENSE`](./LICENSE).

---

## Citation

### APA
```
Keskisärkkä, R., Hubbert, L., & Singull, M. (2026). Systematic Mapping of ICD Codes for Epidemiological Studies. JOURNAL, VOLUME(ISSUE), PAGES. DOI
```

### Bibtex
```bibtex
@article{Keskisarkka2026ICDMapping,
  title   = {{Systematic Mapping of ICD Codes for Epidemiological Studies}},
  author  = {Keskisärkkä, Robin and Hubbert, Laila and Singull, Martin},
  journal = {},
  year    = {2026},
  volume  = {},
  number  = {},
  pages   = {},
  doi     = {}
}
```
