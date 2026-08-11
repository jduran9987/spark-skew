"""Utilities for registering S3 Parquet partitions in the Glue Data Catalog."""

import boto3

# BatchCreatePartition accepts at most 100 partitions per call.
MAX_PARTITIONS_PER_BATCH = 100


def register_partitions(
    database: str,
    table: str,
    partition_locations: dict[str, str]
) -> None:
    """Register newly written S3 partitions with the Glue Data Catalog.

    Reuses the target table's existing StorageDescriptor (columns, file
    format, SerDe) for each partition, overriding only its S3 location.

    Args:
        database: Glue database the table lives in.
        table: Glue table to register partitions against.
        partition_locations: Mapping of partition value (e.g. "2026-01-01")
            to its S3 location, as returned by `write_table_batches`.

    Returns:
        None
    """
    if not partition_locations:
        return

    client = boto3.client("glue")

    storage_descriptor = client.get_table(
        DatabaseName=database,
        Name=table
    )["Table"]["StorageDescriptor"]

    partition_inputs = [
        {
            "Values": [value],
            "StorageDescriptor": {
                **storage_descriptor,
                "Location": location
            }
        }
        for value, location in partition_locations.items()
    ]

    for batch_start in range(
        0,
        len(partition_inputs),
        MAX_PARTITIONS_PER_BATCH
    ):

        batch = partition_inputs[
            batch_start:batch_start + MAX_PARTITIONS_PER_BATCH
        ]

        response = client.batch_create_partition(
            DatabaseName=database,
            TableName=table,
            PartitionInputList=batch
        )

        errors = [
            error
            for error in response.get("Errors", [])
            if error["ErrorDetail"]["ErrorCode"] != "AlreadyExistsException"
        ]

        if errors:
            raise RuntimeError(
                f"Failed to register partitions in Glue: {errors}"
            )
