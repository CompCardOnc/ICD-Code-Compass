import json
from pathlib import Path
import re
from urllib.parse import urlparse
from typing import List, Dict, Optional, Union, Any
import pandas as pd
import yaml

Row = Dict[str, Optional[str]]


def normalize_icd(code: Optional[str]) -> Optional[str]:
    """
    Normalize ICD code formatting for consistency:
    - Remove decimal points and commas.
    - Convert all letters to uppercase.
    - Strip leading/trailing whitespace.

    Parameters
    ----------
    code : str or None
        ICD code to normalize.

    Returns
    -------
    str or None
        Normalized ICD code, or None if input was None/empty.
    """
    if not code:
        return None
    
    code = code.strip()

    if code == "":
        return None

    code = re.sub(r"[,\.]", "", code)
    code = code.upper()
    return code


def read(path: str,
         sheet: Union[int, str] = 0,
         header: List[str] = None,
         delimiter: str = None,
         encoding: str = "utf-8") -> pd.DataFrame:
    """
    Read a CSV or Excel file into a pandas DataFrame with all values as strings.

    Parameters
    ----------
    path : str
        Path or URL to the input file.
    headers : List[str]
        Use as column names. If None, use the first row as column headers.
    delimiter : str
        Delimiter to use for CSV files. If None, pandas will try to
        infer the delimiter automatically.
    sheet : int or str
        Sheet index or name to read from for Excel files. Ignored for CSV.
    encoding : str
        Encoding to use when reading CSV files. Ignored for Excel.

    Returns
    -------
    pandas.DataFrame
        DataFrame with string-typed values. If `no_header` is False,
        column names are stripped of surrounding whitespace.
    """
    parsed = urlparse(path)
    
    header_row = 0 if header is None else None

    # Pick file extension
    ext = Path(parsed.path).suffix.lower()
    if ext in {".xlsx", ".xls"}:
        df = pd.read_excel(path,
                           sheet_name=sheet,
                           dtype=str,
                           header=header_row,
                           names=header)
    else:
        df = pd.read_csv(path,
                         sep=delimiter,
                         dtype=str,
                         encoding=encoding,
                         header=header_row,
                         names=header,
                         engine="python",
                         escapechar="\\")

    # Normalize column names
    df.columns = [str(c).strip() for c in df.columns]

    df = df.where(df.notna(), None)
    return df


def resolve(df: pd.DataFrame,
            col_sel: Union[int, str]) -> str:
    """
    Resolve a column selector into an actual DataFrame column label.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame whose columns are being resolved.
    col_sel : int or str
        Column selector:
        - int: column position (0-based index).
        - str: column name (whitespace is stripped).

    Returns
    -------
    str
        The resolved column label.

    Raises
    ------
    ValueError
        If an integer index is out of range.
    KeyError
        If a string name does not exist in the DataFrame columns.
    """
    if col_sel is None or col_sel == "":
        raise KeyError(
            f"'{col_sel}' is not a valid column name. "
            f"Available columns: {list(df.columns)}"
        )

    if isinstance(col_sel, int):
        if col_sel < 0 or col_sel >= len(df.columns):
            raise ValueError(
                f"Column index {col_sel} is out of range (0..{len(df.columns)-1}). "
                f"Available columns: {list(df.columns)}"
            )
        return df.columns[col_sel]

    col_name = str(col_sel).strip()
    if col_name not in df.columns:
        raise KeyError(
            f"Column '{col_name}' not found in DataFrame. "
            f"Available columns: {list(df.columns)}"
        )
    return col_name


def sub(df: pd.DataFrame,
        column: str,
        replacements: Optional[List[Dict[str, str]]]) -> pd.DataFrame:
    """
    Apply a sequence of regex-based substitution rules to the "code" column
    of a pandas DataFrame.

    Each replacement rule is a dictionary with the keys:
    - "pattern": a regex pattern (string) to match.
    - "replace": a replacement string. Can include backreferences such as \1.

    The rules are applied sequentially in the order they appear in the list.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame that must contain a "code" column.
    replacements : list of dict or None
        A list of replacement rules of the form
        {"pattern": str, "replace": str}. If None, the DataFrame
        is returned unchanged.

    Returns
    -------
    pandas.DataFrame
        The same DataFrame with the "code" column modified in-place
        according to the replacement rules.
    """
    if column not in df.columns:
        raise KeyError(f"Required column '{column}' not found. Columns: {list(df.columns)}")
    
    if replacements is None or len(replacements) == 0:
        return df

    for rule in replacements:
        pattern = rule["pattern"]
        replace = rule["replace"]
        df[column] = df[column].str.replace(pattern, replace, regex=True)

    return df


def write_json_array(path: Path,
                     data: List[Row]) -> None:
    """
    Write a list of dictionaries to a JSON file with UTF-8 encoding.

    Parameters
    ----------
    path : Path
        Path to the output JSON file. Parent directories must exist.
    data : list of dict
        Sequence of row dictionaries to write. Each row should be JSON
        serializable (keys must be strings; values must be of a JSON-
        compatible type such as str, int, float, bool, None, list, or dict).

    Returns
    -------
    None
        This function does not return a value. The result is written
        directly to the file at `path`.
    """
    with Path(path).open("w", encoding="utf-8") as f:
        f.write("[\n")
        for i, obj in enumerate(data):
            line = json.dumps(obj, ensure_ascii=False)
            suffix = ",\n" if i < len(data) - 1 else "\n"
            f.write("  " + line + suffix)
        f.write("]\n")


def load_yaml(path: str) -> Dict[str, Any]:
    """
    Load a YAML file safely into a Python dictionary.

    Parameters
    ----------
    path : str
        Path to the YAML file to load. The file is expected to be encoded
        in UTF-8.

    Returns
    -------
    dict
        A dictionary containing the parsed YAML data. If the file is
        empty or only contains comments, an empty dictionary is returned.

    Raises
    ------
    FileNotFoundError
        If the file at `path` does not exist.
    yaml.YAMLError
        If the file contains invalid YAML and cannot be parsed.
    """
    text = Path(path).read_text(encoding="utf-8")
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML at {path}: {e}") from e

