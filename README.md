# Investigating Skew In Spark Joins

This project investigates how data skew in join keys affects Spark join
performance, using a synthetic dataset and a controllable skew parameter
to compare join behavior under balanced and skewed conditions.

## Sources

The datasets used in this project — `customers` and `orders` — are
synthetic data produced by the [generator](src/generator/README.md)
package, written as partitioned Parquet on S3 and cataloged in Glue.

- **`customers`** is the dimension side of the join: one row per customer,
  with `customer_id` as the join key.
- **`orders`** is the fact side: one row per order event, each referencing
  a `customer_id`. This is the table we scale up to a large row count to
  produce a realistic join workload against `customers`.

We use the generator's `--skew` flag to control how order events are
distributed across customers, which lets us run the same
`orders JOIN customers ON customer_id` query under different conditions
and compare Spark's join performance:

1. **Baseline (`--skew balance`)** — orders are spread evenly across all
   customers, so every customer contributes roughly the same order volume.
   This produces balanced Spark partitions on the join key and establishes
   the "healthy" performance baseline everything else is compared against.
2. **Introducing skew (`--skew low` / `--skew high`)** — order volume is
   concentrated onto a shrinking share of customers, while the total order
   and customer counts stay fixed. This reproduces the classic Spark join
   symptom: a small number of hot keys end up with outsized partitions,
   causing partition imbalance and straggler tasks that slow the join well
   past what the baseline predicts.

Because table sizes stay the same across skew levels, skew is the only
variable changing between runs, which is what makes it possible to
attribute join performance differences to skew rather than data volume.

See [`src/generator/README.md`](src/generator/README.md) for the
full schema and CLI reference for both tables.

## Infrastructure

All datasets live in a single S3 bucket, with each table variant (e.g.
`orders_v1`, `orders_v2`, `orders_v3` for the different skew levels, plus
`customers_v1`/`v2`/`v3`) written to its own prefix within that bucket.
Every variant is cataloged as its own Glue table in a shared Glue database,
so they're all independently queryable via Spark/Athena while sharing one
underlying bucket.

Terraform (`infrastructure/`) owns the durable catalog resources: the S3
bucket, the Glue database, and the Glue table definitions (schema, S3
location, and partition keys) for each table variant. The `generator`
package owns the data itself — writing Parquet files to S3 and, for
partitioned tables, registering each new `event_date` partition against
the corresponding Glue table via the Glue `BatchCreatePartition` API. In
other words, Terraform defines the tables' shape and where they live;
the generator fills them with data and keeps the partition metadata in
sync as new data is written.
