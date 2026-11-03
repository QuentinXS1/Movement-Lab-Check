# Texting Performance Analysis

This repository contains an aggregate analysis exercise built from a texting-program export. It focuses on reproducible data loading, SQL-ready modeling, and program-level performance reporting. The included code reports only aggregate outcomes; it does not expose individual contact records.

## Contents

| File | Purpose |
| --- | --- |
| [`load_to_sqlite.py`](load_to_sqlite.py) | Loads the Projects, Waves, and Parts exports into SQLite with typed fields and indexes on the join keys. |
| [`texting_performance_report.py`](texting_performance_report.py) | Produces a weighted engagement report by department, aggregator, or another available dimension. |
| [`sms_dashboard.html`](sms_dashboard.html) | Interactive dashboard for exploring the exercise outputs. |

## Run the aggregate report

```bash
python texting_performance_report.py "Copy of Hiring exercise - texting dataset - shared - Parts.csv" --group-by department --output department_summary.csv
```

The report calculates reply and opt-out rates from total messages and contacts, avoiding the distortion that comes from averaging row-level percentages.

## Load the data into SQLite

```bash
python load_to_sqlite.py --data-dir . --db movement_labs.db
```

After loading, the `projects`, `waves`, and `parts` tables can be queried with standard SQLite tools.

