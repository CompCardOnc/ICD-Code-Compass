from pathlib import Path
import pandas as pd

from icd_code_compass.utils import read

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
    print(df)
    assert df.loc[0, 0] == "1"
    assert df.loc[0, 1] == "3"
    assert df.loc[1, 0] == "2"
    assert df.loc[1, 1] == "4"
