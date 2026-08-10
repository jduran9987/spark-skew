# Infrastructure

Terraform-managed AWS infrastructure for spark-skew. This directory does not
contain application code — it provisions the storage and cataloging layer
that the Spark jobs read from.

## What this provisions

- **S3 (`s3.tf`)** — a bucket (`spark-skew-7472`) that acts as the data lake.
  Datasets are written to it as Parquet files, partitioned by dataset/table.
  This bucket is the durable source of truth for all data used in the project.

- **Glue Data Catalog** — sits on top of the S3 bucket and catalogs the Parquet
  files as queryable tables (schema, partitions, file locations). This lets
  Spark (and other engines, e.g. Athena) resolve a table name to its
  underlying S3 data without hardcoding paths or schemas.

- **Terraform (`provider.tf`, `versions.tf`)** — all AWS resources are defined
  and applied via Terraform. Nothing in this environment should be created or
  changed manually through the AWS console; changes go through `.tf` files
  and `terraform plan`/`apply`.

## Data flow

```
Parquet files --> S3 bucket (spark-skew-7472) --> Glue Data Catalog --> Spark jobs
```

Spark jobs treat the Glue Catalog as their table metastore and the S3 bucket
as their input source. This infrastructure's job is to make sure that data
exists, is organized, and is discoverable — the Spark application logic
itself lives elsewhere in the repo.

## Usage

```
terraform init
terraform plan
terraform apply
```
