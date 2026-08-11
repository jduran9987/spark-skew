"""Utilities for writing batches of records to partitioned Parquet files on S3."""

import itertools
from collections.abc import Iterable
from typing import Any

import pyarrow as pa
import pyarrow.dataset as ds

# PyArrow's dataset writer limits file size by row count, not bytes, so
# callers convert their own "target file size" into a row count using a
# schema-specific bytes-per-row estimate (see orders.py / customers.py).
DEFAULT_MAX_ROWS_PER_FILE = 5_000_000


def write_table_batches(
    batches: Iterable[dict[str, Any]],
    path: str,
    partition_column: str | None = None,
    max_rows_per_file: int = DEFAULT_MAX_ROWS_PER_FILE
) -> dict[str, str]:
    """Stream record batches to Parquet files on S3 via PyArrow's dataset writer.

    Args:
        batches: Iterable of record batches, where each batch is a dict
            mapping column names to lists of column values.
        path: S3 output prefix to write Parquet files under, e.g.
            "s3://bucket/prefix".
        partition_column: Optional column name to Hive-partition output by
            (e.g. "event_date" produces "event_date=YYYY-MM-DD/" folders).
        max_rows_per_file: Maximum rows to write into a single Parquet file
            before rolling over to the next one.

    Returns:
        dict[str, str]: Mapping of partition value (e.g. "2026-01-01") to
            its S3 location, for every partition a file was written to.
            Empty if `partition_column` is None.
    """
    filesystem, base_path = pa.fs.FileSystem.from_uri(path)

    record_batches = (
        pa.RecordBatch.from_pydict(batch)
        for batch in batches
    )

    try:
        first_batch = next(record_batches)
    except StopIteration:
        return {}

    reader = pa.RecordBatchReader.from_batches(
        first_batch.schema,
        itertools.chain(
            [first_batch],
            record_batches
        )
    )

    partition_locations: dict[str, str] = {}

    def file_visitor(written_file: Any) -> None:
        """Record the S3 location of each partition a file was written to."""
        if not partition_column:
            return

        relative = written_file.path[len(base_path):].strip("/")

        for segment in relative.split("/"):

            if segment.startswith(f"{partition_column}="):

                value = segment.split("=", 1)[1]

                partition_locations[value] = (
                    f"{path.rstrip('/')}/{segment}/"
                )

                break

    ds.write_dataset(
        reader,
        base_dir=base_path,
        filesystem=filesystem,
        format="parquet",
        partitioning=[partition_column] if partition_column else None,
        partitioning_flavor="hive" if partition_column else None,
        basename_template="part-{i}.parquet",
        existing_data_behavior="overwrite_or_ignore",
        max_rows_per_file=max_rows_per_file,
        max_rows_per_group=min(max_rows_per_file, 1_000_000),
        file_options=ds.ParquetFileFormat().make_write_options(
            compression="snappy"
        ),
        file_visitor=file_visitor
    )

    return partition_locations
