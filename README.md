# Retail Analytics Data Engineering Pipeline

An end-to-end portfolio project for a retail analytics use case. It demonstrates a repeatable ETL workflow with Python/Pandas, PostgreSQL, SQL analytics, data-quality reporting, and optional PySpark processing.

## What this project demonstrates

- **Extract:** read a raw retail transactions CSV and validate the expected columns.
- **Transform:** normalize data types, calculate revenue/profit fields, remove duplicate order-line IDs, and reject invalid records.
- **Load:** create PostgreSQL analytics tables and incrementally upsert records (safe to rerun; no table truncation).
- **Data quality:** write a JSON quality summary and a CSV of rejected rows.
- **Observability:** structured console/file logs and an ETL run log in PostgreSQL.
- **Analytics:** SQL queries for sales KPIs, product performance, and trends.
- **Tests:** automated tests for transformations and quality rules.
- **Optional extensions:** PySpark, AWS S3 upload, and an Airflow DAG example.

The bundled sample data is **synthetic** and includes deliberately invalid rows so quality checks can be demonstrated.

## Architecture

```text
Raw CSV
  |
  v
Extract + schema validation
  |
  v
Pandas transformations + data-quality rules ------> Rejected rows + quality report
  |
  v
Cleaned snapshot
  |
  v
PostgreSQL staging/upsert (incremental and repeatable)
  |
  v
Analytics SQL / KPI reporting
```

## Project structure

```text
retail_data_engineering_final/
├── data/raw/retail_transactions.csv
├── data/processed/                 # generated outputs (ignored by Git)
├── dags/retail_pipeline_dag.py     # optional Airflow example
├── logs/                           # generated logs (ignored by Git)
├── reports/                        # generated quality reports (ignored by Git)
├── scripts/
│   ├── run_spark_transform.py
│   └── upload_processed_to_s3.py
├── sql/
│   ├── schema.sql
│   └── analytics_queries.sql
├── src/retail_pipeline/
│   ├── config.py
│   ├── extract.py
│   ├── transform.py
│   ├── quality.py
│   ├── load.py
│   ├── pipeline.py
│   ├── spark_transform.py
│   └── s3_storage.py
├── tests/
├── .env.example
├── requirements.txt
└── run_pipeline.py
```

## 1. Requirements

For the **core pipeline**:
- Python 3.10+
- PostgreSQL 14+ (local install or Docker)
- VS Code recommended

The core ETL uses Python/Pandas and PostgreSQL. You do **not** need Spark, AWS, or Airflow to run it.

## 2. Set up Python

Open this project folder in VS Code and open a terminal at the project root.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. This changes the policy only for that terminal session.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure PostgreSQL

Create a database named `retail_analytics` in pgAdmin or `psql`:

```sql
CREATE DATABASE retail_analytics;
```

Copy `.env.example` to `.env`, then set your own local PostgreSQL credentials. In PowerShell:

```powershell
Copy-Item .env.example .env
```

Example `.env` values:

```env
PGHOST=localhost
PGPORT=5432
PGDATABASE=retail_analytics
PGUSER=postgres
PGPASSWORD=your_local_password
```

**Never commit `.env` or put database passwords, AWS keys, or other secrets in source code.** The `.gitignore` excludes `.env`.

## 4. Run the ETL pipeline

Ensure PostgreSQL is running and the `.venv` is active, then run:

```bash
python run_pipeline.py
```

The pipeline:
1. Reads `data/raw/retail_transactions.csv`.
2. Validates the input schema and normalizes data.
3. Removes duplicate order-line IDs and rejects invalid records.
4. Writes `reports/data_quality_report.json` and, when needed, `reports/rejected_rows.csv`.
5. Writes a cleaned CSV snapshot to `data/processed/retail_transactions_clean.csv`.
6. Creates and upserts rows into PostgreSQL.
7. Records execution metrics in `etl_run_log` and writes logs to `logs/pipeline.log`.

The sample dataset contains 156 input rows: one duplicate is removed, five invalid rows are rejected, and 150 rows are accepted. These counts are for the bundled synthetic data.

**Incremental behavior:** `order_line_id` is used as a key. Rerunning the pipeline inserts new rows and updates matching rows without truncating the target tables. Existing database rows are not deleted merely because they are absent from a later input file.

## 5. Verify the results in pgAdmin

Open `sql/analytics_queries.sql` and execute the queries after the pipeline succeeds. For a quick row-count check:

```sql
SELECT COUNT(*) FROM fact_sales;
SELECT * FROM etl_run_log ORDER BY started_at DESC;
```

The sample run should load 150 valid order lines into `fact_sales` for a clean, newly created database.

## 6. Run automated tests

```bash
python -m pytest -q
```

These tests validate transformation and data-quality behavior; they do not require PostgreSQL credentials.

## 7. Optional: PySpark transformation

PySpark is an optional extension. Java 17 or newer is required. In the active virtual environment:

```bash
pip install -r requirements-spark.txt
python scripts/run_spark_transform.py
```

The script uses Spark DataFrames to parse dates/numeric columns, remove duplicates, filter invalid records, and calculate gross revenue, net revenue, and profit. Output goes to `data/processed/spark_output/`.

**Windows note:** local Hadoop file writes can require a separate `winutils.exe` utility. For this small demo, the script uses a Windows-specific Pandas/PyArrow output path to avoid that dependency. On Linux/macOS it uses Spark's Parquet writer. For large-scale production workloads, run on Linux/WSL or a managed Spark platform and retain distributed Parquet writes rather than collecting results to Pandas.

## 8. Optional: AWS S3

Install the optional dependency:

```bash
pip install -r requirements-aws.txt
```

Configure AWS credentials using your normal AWS CLI profile or environment configuration, set `S3_BUCKET`, and run:

```bash
python scripts/upload_processed_to_s3.py
```

The processed CSV must exist first, so run the core pipeline before the upload script. Do not hardcode AWS access keys in source files. S3 upload incurs cloud costs if you use paid AWS resources.

## 9. Optional: Airflow

`dags/retail_pipeline_dag.py` is an example DAG and requires a separately installed/configured Airflow environment. It uses `RETAIL_PROJECT_DIR` to locate the project. Airflow is not required for the core pipeline.

## Data model

- `dim_customers`: customer attributes
- `dim_products`: product and category attributes
- `fact_sales`: order-line facts, quantity, unit price, discount, revenue, and profit
- `etl_run_log`: per-run input/accepted/rejected counts and status

## Publish this project to GitHub

1. Extract the project ZIP and open the `retail_data_engineering_final` folder in VS Code.
2. Check that your `.env` file is not included. Commit `.env.example`, not `.env`.
3. Create a new **empty** repository on GitHub, for example `retail-data-engineering-pipeline`.
4. From the project root, run the following commands, replacing the URL with your repository URL:

```bash
git init
git add .
git status
git commit -m "Build retail analytics data engineering pipeline"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/retail-data-engineering-pipeline.git
git push -u origin main
```

If Git is not configured on this laptop yet, set your Git name/email once before committing. Review `git status` before `git commit` and confirm `.env`, `.venv`, logs, and generated output files are not staged.

## Resume-ready project description

**Retail Analytics Data Engineering Pipeline | Python, Pandas, PostgreSQL, SQL, PySpark**

- Built a repeatable ETL pipeline to validate and transform retail transaction data and incrementally upsert analytics records into PostgreSQL.
- Implemented data-quality reporting, rejected-record handling, structured logging, automated transformation tests, and analytical SQL queries.
- Added an optional PySpark transformation with Parquet output and examples for S3 storage and Airflow scheduling.

Only claim optional technologies such as PySpark, AWS, and Airflow as hands-on skills after you have run the respective extension and can explain how it works in an interview.
