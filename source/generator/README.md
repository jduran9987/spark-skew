# generator

## Description

`generator` creates synthetic customer and order-event datasets for
benchmarking Spark join performance under different data skew conditions.
It writes both datasets as partitioned Parquet files to an S3 prefix.

## Usage

Run the CLI as a module, with `source/` on your `PYTHONPATH`:

```bash
PYTHONPATH=source python -m generator.cli \
    --customers 1000000 \
    --order-events 50000000 \
    --skew high \
    --output s3://my-bucket/spark-skew
```

This generates `--customers` customer records and `--order-events` order
events, and writes them under `s3://my-bucket/spark-skew/customers` and
`s3://my-bucket/spark-skew/orders` respectively.

## CLI Arguments

| Flag              | Type | Required | Description                                                  |
|-------------------|------|----------|----------------------------------------------------------------|
| `--customers`     | int  | yes      | Number of customer records to generate.                      |
| `--order-events`  | int  | yes      | Number of order event records to generate.                    |
| `--skew`          | str  | yes      | Order-to-customer distribution pattern. One of `balance`, `low`, `high`. |
| `--output`        | str  | yes      | S3 output prefix that datasets are written under.             |

### `--skew` behavior

`--skew` controls how order events' `customer_id` values are distributed
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
