#!/usr/bin/env python3
"""
Load the Movement Labs texting dataset (Projects, Waves, Parts CSVs) into a SQLite database.

Usage:
    python load_to_sqlite.py [--data-dir DIR] [--db PATH]

Defaults assume the three CSVs sit in the data dir with their original
"Copy of Hiring exercise - texting dataset - shared - <Table>.csv" names.

Creates three tables: projects, waves, parts — with proper types,
parsed ISO dates/timestamps, and indexes on the join keys
(project_airtable_id, wave_airtable_id).
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

FILES = {
    "projects": "Copy of Hiring exercise - texting dataset - shared - Projects.csv",
    "waves": "Copy of Hiring exercise - texting dataset - shared - Waves.csv",
    "parts": "Copy of Hiring exercise - texting dataset - shared - Parts.csv",
}

DATE_COLS = ["send_date_earliest"]
TS_COLS = ["message_sent_earliest", "message_sent_latest"]

INT_COLS = [
    "part_id", "contacts", "contacts_opted_out",
    "outgoing_messages", "incoming_messages",
    "sms_segments", "sms_incoming_segments", "sms_outgoing_segments",
    "mms_segments", "mms_incoming_segments", "mms_outgoing_segments",
]

FLOAT_COLS = ["delivery_rate", "reply_rate", "opt_out_rate"]


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    # Parse dates/timestamps to ISO strings (SQLite-friendly, sortable)
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%m/%d/%Y", errors="coerce").dt.strftime("%Y-%m-%d")
    for col in TS_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

    # Coerce numerics (bad/blank values -> NULL)
    for col in INT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    for col in FLOAT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=".", help="Directory containing the three CSVs")
    ap.add_argument("--db", default="movement_labs.db", help="Output SQLite database path")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    db_path = Path(args.db)

    con = sqlite3.connect(db_path)
    try:
        for table, filename in FILES.items():
            csv_path = data_dir / filename
            df = load_csv(csv_path)
            df.to_sql(table, con, if_exists="replace", index=False)
            print(f"Loaded {len(df):>6,} rows -> {table}  ({csv_path.name})")

        # Indexes on join keys
        cur = con.cursor()
        cur.executescript("""
            CREATE INDEX IF NOT EXISTS idx_waves_project ON waves(project_airtable_id);
            CREATE INDEX IF NOT EXISTS idx_parts_project ON parts(project_airtable_id);
            CREATE INDEX IF NOT EXISTS idx_parts_wave    ON parts(wave_airtable_id);
            CREATE INDEX IF NOT EXISTS idx_parts_agg     ON parts(aggregator);
        """)
        con.commit()

        # Quick sanity check
        for table in FILES:
            n = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"Verified: {table} has {n:,} rows")
    finally:
        con.close()

    print(f"\nDone -> {db_path.resolve()}")


if __name__ == "__main__":
    main()
