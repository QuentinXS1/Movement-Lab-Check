#!/usr/bin/env python3
"""Summarize a texting-program export without exposing individual contacts.

The script reads the supplied Parts CSV and produces an aggregate report by the
requested field (department by default). It calculates weighted reply and
opt-out rates, rather than averaging row-level percentages.

Usage:
    python texting_performance_report.py "Copy of Hiring exercise - texting dataset - shared - Parts.csv"
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"contacts", "incoming_messages", "contacts_opted_out"}


def summarize(frame: pd.DataFrame, group_by: str) -> pd.DataFrame:
    """Return weighted engagement metrics for one program dimension."""
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {', '.join(sorted(missing))}")
    if group_by not in frame.columns:
        raise ValueError(f"Group-by column '{group_by}' was not found in the input.")

    work = frame.copy()
    for column in REQUIRED_COLUMNS:
        work[column] = pd.to_numeric(work[column], errors="coerce").fillna(0)
    work[group_by] = work[group_by].fillna("Unknown").astype(str)

    report = work.groupby(group_by, as_index=False).agg(
        contacts=("contacts", "sum"),
        replies=("incoming_messages", "sum"),
        opt_outs=("contacts_opted_out", "sum"),
    )
    report["reply_rate"] = (report["replies"] / report["contacts"].where(report["contacts"] > 0) * 100).round(2)
    report["opt_out_rate"] = (report["opt_outs"] / report["contacts"].where(report["contacts"] > 0) * 100).round(2)
    return report.sort_values("contacts", ascending=False, kind="stable")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an aggregate texting performance report.")
    parser.add_argument("input", type=Path, help="Parts CSV export")
    parser.add_argument("--group-by", default="department", help="Column used to group the report")
    parser.add_argument("--output", type=Path, help="Optional CSV output path")
    args = parser.parse_args()

    report = summarize(pd.read_csv(args.input), args.group_by)
    rendered = report.to_csv(index=False)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {len(report)} aggregate rows to {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()

