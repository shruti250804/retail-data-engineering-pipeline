"""Optional PySpark ETL for the sample retail CSV.

On Linux/macOS, Spark writes a Parquet dataset directly. On Windows, this
small demo collects the result to Pandas and uses PyArrow to write a single
Parquet file, avoiding the winutils.exe dependency in local Hadoop writes.
For large production datasets, run Spark on Linux, WSL, or a managed Spark
platform and use Spark's distributed Parquet writer.
"""
from pathlib import Path
import os


def transform_csv_with_spark(input_path, output_path):
    """Clean retail records with Spark and write Parquet output."""
    from pyspark.sql import SparkSession, functions as F

    spark = (
        SparkSession.builder
        .appName("RetailPipelineTransform")
        .config("spark.sql.ansi.enabled", "false")
        .getOrCreate()
    )
    try:
        df = (
            spark.read.option("header", True)
            .option("inferSchema", True)
            .csv(str(input_path))
        )

        # try_cast returns NULL for malformed values (e.g. "not-a-date") rather
        # than failing the entire Spark job during its lazy evaluation/write.
        cleaned = (
            df.withColumn("order_date", F.expr("try_cast(order_date AS DATE)"))
            .withColumn("quantity", F.expr("try_cast(quantity AS INT)"))
            .withColumn("unit_price", F.expr("try_cast(unit_price AS DOUBLE)"))
            .withColumn("discount", F.expr("try_cast(discount AS DOUBLE)"))
            .withColumn("unit_cost", F.expr("try_cast(unit_cost AS DOUBLE)"))
            .dropDuplicates(["order_line_id"])
            .filter(
                F.col("order_line_id").isNotNull()
                & F.col("order_date").isNotNull()
                & F.col("quantity").isNotNull()
                & (F.col("quantity") > 0)
                & F.col("unit_price").isNotNull()
                & (F.col("unit_price") >= 0)
                & F.col("discount").between(0, 1)
                & F.col("unit_cost").isNotNull()
                & (F.col("unit_cost") >= 0)
            )
            .withColumn(
                "gross_revenue",
                F.round(F.col("quantity") * F.col("unit_price"), 2),
            )
            .withColumn(
                "net_revenue",
                F.round(
                    F.col("quantity") * F.col("unit_price") * (1 - F.col("discount")),
                    2,
                ),
            )
            .withColumn(
                "profit",
                F.round(
                    F.col("quantity")
                    * (
                        F.col("unit_price") * (1 - F.col("discount"))
                        - F.col("unit_cost")
                    ),
                    2,
                ),
            )
        )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if os.name == "nt":
            # Local Windows Hadoop often requires winutils.exe to write files.
            # For this small sample only, write via Pandas/PyArrow instead.
            import pandas as pd  # noqa: F401 - explicit dependency check

            output_path.mkdir(parents=True, exist_ok=True)
            pandas_df = cleaned.toPandas()
            pandas_df.to_parquet(output_path / "part-00000.parquet", index=False)
        else:
            cleaned.write.mode("overwrite").parquet(str(output_path))

        print(f"PySpark output written to: {output_path}")
        print(f"Accepted rows: {cleaned.count()}")
    finally:
        spark.stop()
