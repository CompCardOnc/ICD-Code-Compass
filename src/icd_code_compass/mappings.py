#!/usr/bin/env python3
import argparse
from collections import OrderedDict
from typing import List, Union
from utils import *

def read_mappings(path: str,
                  from_column: Union[int, str],
                  to_column: Union[int, str],
                  header: List[str] = None,
                  attributes: List[str] = [],
                  delimiter: str = None,
                  sheet: Union[int, str] = 0,
                  encoding: str = "utf-8") -> List[Row]:
    """
    Read a mapping table from CSV or Excel into a list of row dictionaries.

    The function extracts two key columns (`from_code` and `to_code`)
    and collects additional attributes into a nested dictionary.
    All values are returned as strings with blanks converted to None.

    If either `from_column` or `to_column` is specified as an integer,
    the file is assumed to have no header row and columns are resolved
    by positional index (0-based). Otherwise, columns are matched by name.

    Parameters
    ----------
    path : str
        Path or URL to the CSV or Excel file.
    from_column : int or str
        Name of column for the source code.
    to_column : int or str
        Name of column for the target code.
    header : List[str], optional
        List with column names. If None, first line is assumed to be the header.
    attributes : list of str, , default []
        Additional columns to include in the output.
    delimiter : str, default None
        Delimiter to use for CSV files. If None, defaults to pandas will attempt to infer the delimiter.
    sheet : int or str, default 0
        Sheet index (int) or name (str) for Excel files. Ignored for CSV.
    encoding : str, default "utf-8"
        Encoding to use when reading CSV files. Ignored for Excel.

    Returns
    -------
    list of dict
        Each element represents a row with the structure:
        {
            "from_code": str or None,
            "to_code": str or None,
            "attributes": {attr_name: str, ...} or None
        }

    Raises
    ------
    KeyError
        If a referenced column does not exist in the file.
    ValueError
        If a column index is out of range.
    """
    
    df = read(path=path,
              header=header,
              delimiter=delimiter,
              sheet=sheet,
              encoding=encoding)
    
    # Rename columns
    df = df.rename(columns={
        from_column: "from_code",
        to_column: "to_code"
    })
    
    # Normalize codes
    df["from_code"] = df.apply(lambda row: normalize_icd(row["from_code"]), axis=1)
    df["to_code"] = df.apply(lambda row: normalize_icd(row["to_code"]), axis=1)
    
    # Collect attributes
    if attributes is not None:
        df["attributes"] = df.apply(lambda row: {a: row[a] for a in attributes}, axis=1)
    else:
        attributes = {}

    return df[["from_code", "to_code", "attributes"]]


def write_compact_json(path: str, data: dict):
    """
    Write a JSON file where "sources" is pretty-printed and "mappings" is compact.

    The output format is tailored for mixed readability and compactness:
    - The "sources" field is indented with multiple lines (human-readable).
    - The "mappings" field is written as a JSON array, one object per line,
      with keys sorted and no extra whitespace.

    Parameters
    ----------
    path : str
        Path to the output JSON file. Parent directories must already exist.
    data : dict
        Dictionary with at least the keys:
        - "sources": a JSON-serializable object (dict or list).
        - "mappings": a list of JSON-serializable objects (dicts).

    Returns
    -------
    None
        Writes the formatted JSON directly to the specified file.

    """

    with Path(path).open("w", encoding="utf-8") as f:
        f.write("{\n")

        # write "sources" normal intentation
        f.write('  "sources": ')
        src = json.dumps(data["sources"], ensure_ascii=False, indent=2)
        # Indent every line by 2 spaces for alignment
        src = src.replace("\n", "\n  ")
        f.write(src)
        f.write(",\n")

        key_order = ["from_icd", "from_code", "to_icd", "to_code", "attributes", "source"]
        sort_order = [k for k in key_order if k != "attributes"]

        mappings_sorted = sorted(
            data["mappings"],
            key=lambda r: tuple(r.get(k) for k in  sort_order)
        )

        # write "mappings" in compact one-line style
        f.write('  "mappings": [\n')
        for i, obj in enumerate(mappings_sorted):
            line = "    "
            ordered = OrderedDict((k, obj.get(k)) for k in key_order if k in obj)
            line += json.dumps(ordered, ensure_ascii=False)
            if i < len(mappings_sorted) - 1:
                line += ","
            f.write(line + "\n")
        f.write("  ]\n")

        f.write("}\n")
        

def main():
    """
    Command-line entry point for generating ICD code mappings.

    This function parses command-line arguments, loads a YAML configuration
    file, reads mapping definitions, and writes the combined results to
    a JSON file.

    Command-line Arguments
    ----------------------
    --config : File path
        Path to the YAML config file that defines sources and mappings.
    --output : File path
        Path where the output JSON file will be written.
    """

    parser = argparse.ArgumentParser(
        description="Generate ICD codes mappings",
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
    mappings = config["mappings"]
    
    data = {
        "sources": sources,
        "mappings": []
    }

    for m in mappings:
        source = sources[m["source"]]

        # read rows from file
        df = read_mappings(
            path = source["path"],
            from_column = m["from_column"],
            to_column = m["to_column"],
            header = m.get("header"),
            attributes = m.get("attributes", []),
            delimiter = m.get("delimiter", None),
            sheet = m.get("sheet", 0),
            encoding = m.get("encoding", "utf8"))

        df["source"] = m["source"]
        df["from_icd"] = m["from_icd"]
        df["to_icd"] = m["to_icd"]
        data["mappings"].extend(df.to_dict("records"))

    # write to file
    write_compact_json(args.output, data)


if __name__ == "__main__":
    main()
