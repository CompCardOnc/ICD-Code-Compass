from pathlib import Path
import pandas as pd
import pytest
import yaml

from icd_code_compass.utils import *

def test_read_csv_with_header(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("A ,B\n1,2\n3,4\n", encoding="utf-8")
    df = read(str(p), delimiter=",")
    assert list(df.columns) == ["A", "B"]
    assert df.iloc[0].to_dict() == {"A": "1", "B": "2"}
    assert df.iloc[1].to_dict() == {"A": "3", "B": "4"}

def test_read_csv_sniff_delimiter(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("A \tB\n1\t2\n3\t4\n", encoding="utf-8")
    df = read(str(p))
    assert list(df.columns) == ["A", "B"]
    assert df.iloc[0].to_dict() == {"A": "1", "B": "2"}
    assert df.iloc[1].to_dict() == {"A": "3", "B": "4"}


def test_read_csv_no_header(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("1,2\n3,4\n", encoding="utf-8")
    df = read(str(p), no_header=True, delimiter=",")
    assert list(df.columns) == [0, 1]
    assert df.iloc[0].to_dict() == {0: "1", 1: "2"}


def test_read_excel_with_header(tmp_path: Path):
    p = tmp_path / "data.xlsx"
    pd.DataFrame({"A ": ["1", "3"], "B": ["2", "4"]}).to_excel(p, index=False)
    df = read(str(p), no_header=False, sheet=0, encoding="utf-8")
    assert df.loc[0, "A"] == "1"
    assert df.loc[1, "A"] == "3"
    assert df.loc[0, "B"] == "2"
    assert df.loc[1, "B"] == "4"


def test_read_excel_no_header(tmp_path: Path):
    p = tmp_path / "data.xlsx"
    pd.DataFrame([["1", "3"], ["2", "4"]]).to_excel(p, index=False, header=False)
    df = read(str(p), no_header=True)
    assert df.loc[0, 0] == "1"
    assert df.loc[0, 1] == "3"
    assert df.loc[1, 0] == "2"
    assert df.loc[1, 1] == "4"


def test_normalize_icd():
    assert normalize_icd(None) is None
    assert normalize_icd("") is None
    assert normalize_icd("   ") is None
    assert normalize_icd("a10.2") == "A102"
    assert normalize_icd(" C34,1 ") == "C341"
    assert normalize_icd(" 123.4 ") == "1234"


def test_resolve_by_valid_index():
    df = pd.DataFrame(columns=["alpha", "beta", "gamma"])
    assert resolve(df, 0) == "alpha"
    assert resolve(df, 2) == "gamma"


def test_resolve_by_valid_name():
    df = pd.DataFrame(columns=["alpha", "beta"])
    assert resolve(df, "alpha") == "alpha"
    assert resolve(df, " beta ") == "beta"


def test_resolve_invalid_index_or_name():
    df = pd.DataFrame(columns=["a", "b"])
    with pytest.raises(KeyError):
        resolve(df, "c")
    with pytest.raises(KeyError):
        resolve(df, None)
    with pytest.raises(KeyError):
        resolve(df, "")
    with pytest.raises(ValueError):
        resolve(df, -1)
    with pytest.raises(ValueError):
        resolve(df, 2)


def test_sub_applies_replacements():
    df = pd.DataFrame({"code": ["A,10", "10.B"]})
    rules = [
        {"pattern": r"([0-9]+)\.([A-Z]+)", "replace": r"\2\1"},
        {"pattern": r",", "replace": ""}
    ]
    result = sub(df, "code", rules)
    assert result["code"].tolist() == ["A10", "B10"]


def test_sub_applies_empty_replacements():
    df = pd.DataFrame({"code": ["A10", "B10"]})
    rules = []
    result = sub(df, "code", rules)
    assert result["code"].tolist() == ["A10", "B10"]


def test_sub_invalid_name():
    df = pd.DataFrame({})
    rules = [ ]
    with pytest.raises(KeyError):
        sub(df, "code", rules)


def test_load_yaml_valid(tmp_path: Path):
    path = tmp_path / "config.yaml"
    path.write_text("a: 1\nb: test\n", encoding="utf-8")

    data = load_yaml(str(path))
    assert data == {"a": 1, "b": "test"}


def test_load_yaml_empty_returns_dict(tmp_path: Path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")

    data = load_yaml(str(path))
    assert data == {}


def test_load_yaml_file_not_found(tmp_path: Path):
    path = tmp_path / "missing.yaml"
    with pytest.raises(FileNotFoundError):
        load_yaml(str(path))


def test_load_yaml_invalid_yaml(tmp_path: Path):
    path = tmp_path / "broken.yaml"
    # Invalid YAML: key without value
    path.write_text("a: 1\nb:\n  - c: 2\n  - d\n  : e", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        load_yaml(str(path))