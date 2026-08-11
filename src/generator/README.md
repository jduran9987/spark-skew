# Customer and Orders Data Generator

## Description

This package creates synthetic customer and order-event datasets for
benchmarking Spark join performance under different data skew conditions.
It writes both datasets as Parquet files to an S3 prefix.

## Partitioning

Order events are partitioned in S3 by `event_date`, a `YYYY-MM-DD` date
derived from each row's `order_timestamp`. Every row also gets an
`ingested_at` column stamped with the date the generator job ran, which is
constant across a single run and useful for tracking which generator
invocation produced a given file.

The writer (`parquet_writer.write_table_batches`) uses PyArrow's dataset
writer to lay these out as Hive-style partition folders under
`{output}/{orders-tablename}/` (`{output}/orders/` by default), e.g.:

```
s3://my-bucket/spark-skew/orders/event_date=2026-01-01/part-00000.parquet
s3://my-bucket/spark-skew/orders/event_date=2026-01-02/part-00000.parquet
...
```

`event_date` is the physical partition column and is not duplicated as a
column inside the Parquet files themselves — it's encoded only in the
folder path, standard Hive convention. Customer records are not
partitioned; they're written as a flat set of files under
`{output}/{customers-tablename}/` (`{output}/customers/` by default).

After the orders write completes, the generator registers every
`event_date` partition it just wrote against the Glue Data Catalog (via
`generator.glue.register_partitions`, using the Glue `BatchCreatePartition`
API) so the new S3 folders are immediately queryable through Spark/Athena
without a separate crawler run or `MSCK REPAIR TABLE`. Registration is
idempotent — rerunning the generator against partitions that already exist
in the catalog is a no-op rather than an error.

## Schema

### `customers`

Not partitioned; written as a flat set of files under
`{output}/{customers-tablename}`.

| Column              | Type                    | Notes                                                        |
|---------------------|-------------------------|---------------------------------------------------------------|
| `customer_id`       | `int64`                 | Sequential, starting at 1.                                    |
| `customer_name`     | `string`                | `"Customer {customer_id}"`.                                   |
| `customer_segment`  | `string`                | One of `SMALL_BUSINESS`, `MID_MARKET`, `ENTERPRISE`.           |
| `country_code`      | `string`                | One of `US`, `CA`, `GB`, `DE`, `FR`, `JP`.                     |
| `created_at`        | `timestamp[us, tz=UTC]` | Random timestamp within the last 1000 days of the job's run time. |
| `ingested_at`       | `date32` (`YYYY-MM-DD`) | Derived. Date the generator job ran; constant across the run.  |

### `orders`

Partitioned in S3 by `event_date`. Written under
`{output}/{orders-tablename}/event_date=YYYY-MM-DD/`.

| Column            | Type                     | Notes                                                                 |
|-------------------|--------------------------|-------------------------------------------------------------------------|
| `order_id`        | `int64`                  | Sequential, starting at 1.                                              |
| `customer_id`     | `int64`                  | Assigned per the `--skew` distribution; references `customers.customer_id`. |
| `product_id`      | `int64`                  | Random, `1`–`99999`.                                                    |
| `order_timestamp` | `timestamp[us]`          | Random timestamp within a fixed 90-day window starting 2026-01-01 (not tied to the job's real run time — see [order_timestamp source](#order_timestamp-source) in Behavior). |
| `quantity`        | `int64`                  | Random, `1`–`9`.                                                        |
| `unit_price`      | `decimal128(5, 2)`       | Random, `1.00`–`500.00`.                                                |
| `event_type`      | `string`                 | One of `ORDER_CREATED`, `ORDER_UPDATED`, `ORDER_CANCELLED`.             |
| `event_date`      | `date` (`YYYY-MM-DD`)    | **Partition column.** Derived from `order_timestamp`. Not physically stored as a column inside the Parquet files — encoded only in the `event_date=YYYY-MM-DD/` folder path (standard Hive convention). |
| `ingested_at`     | `date32` (`YYYY-MM-DD`)  | Derived. Date the generator job ran; constant across the run.           |

## Behavior

### `order_timestamp` source

`order_timestamp` is generated from a fixed anchor (`2026-01-01 00:00:00`)
plus a random offset of 0–90 days — it does **not** depend on when the
script is actually run. This means every generator run produces order
events (and therefore `event_date` partitions) spread across the same
`2026-01-01`–`2026-03-31` window, and rerunning the generator overwrites
files within those same partition folders rather than creating new ones.

### `skew` behavior

The `--skew` cli arg controls how order events' `customer_id` values are distributed
across the generated customers. The total number of orders and customers
is unchanged by this flag — only how orders are spread across customers
changes.

- **`balance`** — Orders are distributed evenly across all customers, so
  each customer receives approximately the same number of orders. This
  represents a healthy join baseline with even Spark partition workloads.
- **`low`** — ~90% of orders go to 40% of customers, with the remaining
  10% spread randomly across all customers. This produces moderate skew.
- **`high`** — ~90% of orders go to 1% of customers, with the remaining
  10% spread randomly across all customers. This produces severe skew,
  which can cause Spark join partition imbalance and straggler tasks.

## Usage

Run the CLI via the `generate-source-data` script entry point:

```bash
uv run generate-source-data \
    --customers 1000000 \
    --order-events 50000000 \
    --skew high \
    --output s3://my-bucket/spark-skew \
    --glue-database sparkskew_db \
    --customers-tablename customers_v3 \
    --orders-tablename orders_v3
```

This generates `--customers` customer records and `--order-events` order
events, and writes them under `s3://my-bucket/spark-skew/customers_v3` and
`s3://my-bucket/spark-skew/orders_v3` respectively. `--customers-tablename`
and `--orders-tablename` are optional and default to `customers` and
`orders`. `--orders-tablename` also doubles as the Glue table name that
`event_date` partitions are registered against.

## CLI Arguments

| Flag                      | Type | Required | Description                                                  |
|---------------------------|------|----------|----------------------------------------------------------------|
| `--customers`             | int  | yes      | Number of customer records to generate.                      |
| `--order-events`          | int  | yes      | Number of order event records to generate.                    |
| `--skew`                  | str  | yes      | Order-to-customer distribution pattern. One of `balance`, `low`, `high`. |
| `--output`                | str  | yes      | S3 output prefix that datasets are written under.             |
| `--glue-database`         | str  | yes      | Glue database to register order-event `event_date` partitions in. |
| `--customers-tablename`   | str  | no       | Table name for the customers dataset; used as the S3 folder name customers are written under (`{output}/{customers-tablename}`). Defaults to `customers`. |
| `--orders-tablename`      | str  | no       | Table name for the orders dataset; used as the S3 folder name order events are written under (`{output}/{orders-tablename}`), and as the Glue table `event_date` partitions are registered against. Defaults to `orders`. |
