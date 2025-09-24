# ICD-Code-Compass

> A tool for exploring, creating, and publishing ICD mapping files.

<div align="center">

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Build](https://img.shields.io/badge/CI-pytest-informational)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-3776AB)
![Tests](https://img.shields.io/badge/tests-passing-success)

</div>

## ✨ What is this?

**ICD-Code-Compass** is a Python toolkit and service for working with ICD codes (lookup, mapping, and validation).

The service allows user to explore, filter, and export ICD mapping files intended for the use in registry-based research.

Try out the service now: [ICD-Code-Compass](https://compcardonc.github.io/ICD-Code-Compass/)

> MIT-licensed. Made for research & production pipelines.

---

## 📦 Features (at a glance)

- **Lookup & search:** query or filter existing ICD mappings.
- **Mappings:** assemble and download mapping files to translate across ICD versions.
- **Reproducablity:** upload new mapping files from studies to increase reproducability and transparency in registry-based studies.

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
python3 scripts/generate-mappings.sh
```

To generate a new labels file, run:
```bash
python3 scripts/generate-labels.sh
```

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

## 🤝 Contributing

Issues and PRs are welcome! Opening an [issue](https://github.com/CompCardOnc/ICD-Code-Compass/issues) to:
- Report bugs
- Propose new features
- Request addition of new mappings or labels

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
