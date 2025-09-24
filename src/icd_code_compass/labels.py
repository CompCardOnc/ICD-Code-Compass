#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from typing import List, Dict, Optional, Union
from collections import defaultdict
from utils import *

Row = Dict[str, Optional[str]]


def read_labels(path: str,
                code_column: Union[int, str],
                label_column: Union[int, str],
                filter: str = None,
                delimiter: str = None,
                sheet: Union[int, str] = 0,
                encoding: str = "utf-8") -> List[Row]:
    """
    Read a table of codes and labels from a file (CSV/TSV/Excel) and return
    them as a list of rows (dict-like).

    - If `code_column` or `label_column` is given as an integer, it is treated
      as a positional index and the file is read with no header row.
    - If given as a string, it must match a column name in the input.
    - The `sheet` argument applies only to Excel input and may be an index (int)
      or sheet name (str).
    - Codes are normalized using `normalize_icd`.
    - Blank or missing labels are dropped.
    - If `filter` is provided, only codes matching the regex pattern are kept.

    Parameters
    ----------
    path : str
        Path to the input file (CSV, TSV, Excel, etc.).
    code_column : int or str
        Column index or column name containing the ICD codes.
    label_column : int or str
        Column index or column name containing the labels.
    filter : str, optional
        Regex pattern to filter codes; only matching codes are included.
    delimiter : str, optional
        Field delimiter for CSV/TSV files. Ignored for Excel.
    sheet : int or str, default 0
        Sheet index or name for Excel files. Ignored for CSV/TSV.
    encoding : str, default "utf-8"
        Text encoding for CSV/TSV files.

    Returns
    -------
    List[Row]
        A list of rows (dict-like) with keys:
        - "code"  : normalized ICD code
        - "label" : corresponding label (non-null)
    """
    # If either selector is positional, assume the file has no header row
    no_header = isinstance(code_column, int) or isinstance(label_column, int)
    
    df = read(path=path,
              no_header=no_header,
              delimiter=delimiter,
              sheet=sheet,
              encoding=encoding)
    
    code_col = resolve(df, code_column)
    label_col = resolve(df, label_column)
    
    # Rename columns
    df = df.rename(columns={code_col: "code"})
    df = df.rename(columns={label_col: "label"})

    # Normalize codes
    df["code"] = df["code"].apply(normalize_icd)

    # Skip lines?
    if filter != None:
        df = df[df["code"].str.match(filter, na=False)]
    
    # Drop missing labels
    df = df[df["label"].notna()]
    
    return df[["code", "label"]]


def main():
    """"
    Command-line entry point for generating ICD code labels.

    CLI arguments
    -------------
    --config : Path to config file
    --output : Path to output file

    Example
    -------
    $ python -m icd_code_compass.labels \
        --config config.yml \
        --output labels.json
    """
    parser = argparse.ArgumentParser(
        description="Generate ICD codes labels",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--config",
                        type=Path,
                        required=True,
                        default=argparse.SUPPRESS,
                        help="Path to the config file")
    parser.add_argument("--output",
                        type=Path,
                        required=True,
                        default=argparse.SUPPRESS,
                        help="Path to the output file")

    args = parser.parse_args()
    config = load_yaml(args.config)
    
    sources = config["sources"]
    labels = config["labels"]
    
    data = {
        "sources": sources,
        "labels": defaultdict(tree)
    }
    
    for l in labels:
        source = sources[l["source"]]
         
        # read rows from file
        df = read_labels(
            path=source["path"],
            delimiter=l.get("delimiter"),
            sheet=l.get("sheet", 0),
            encoding=l.get("encoding", "utf8"),
            filter=l.get("filter"),
            code_column=l["code_column"],
            label_column=l["label_column"])

        df = sub(df, "code", l.get("replacements"))

        for row in df.to_dict("records"):
            icd = l["icd"]
            lang = l["lang"]
            code = row["code"]
            label = row["label"]
            data["labels"][icd][code][lang] = label

    # write to file
    with Path(args.output).open("w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))

def tree():
    return defaultdict(tree)


if __name__ == "__main__":
    main()
