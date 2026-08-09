"""Utilities for writing batches of records to partitioned Parquet files."""

from collections.abc import Iterable
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
import s3fs

TARGET_SIZE_BYTES = (
    160 * 1024 * 1024
)


def write_table_batches(
    batches: Iterable[dict[str, Any]],
    path: str,
    partition_column: str | None = None
) -> None:
    """Buffer record batches and flush them to Parquet files once large enough.

    Args:
        batches: Iterable of record batches, where each batch is a dict
            mapping column names to lists of column values.
        path: S3 output prefix to write Parquet files under.
        partition_column: Optional column name to partition output by.

    Returns:
        None
    """
    fs = s3fs.S3FileSystem()

    buffer = []

    buffer_size = 0

    file_index = 0

    for batch in batches:

        table = pa.Table.from_pydict(
            batch
        )

        buffer.append(table)

        buffer_size += (
            table.nbytes
        )

        if buffer_size >= TARGET_SIZE_BYTES:

            combined = pa.concat_tables(
                buffer
            )

            write_parquet(
                fs,
                combined,
                path,
                file_index
            )

            file_index += 1

            buffer.clear()
            buffer_size = 0

    if buffer:

        combined = pa.concat_tables(
            buffer
        )

        write_parquet(
            fs,
            combined,
            path,
            file_index
        )


def write_parquet(
    fs: s3fs.S3FileSystem,
    table: pa.Table,
    path: str,
    index: int
) -> None:
    """Write a single Arrow table to a Parquet file on S3.

    Args:
        fs: S3 filesystem handle used to open the destination file.
        table: Arrow table to write.
        path: S3 output prefix the file will be written under.
        index: Sequential file index used to build the output filename.

    Returns:
        None
    """
    file_path = (
        f"{path}/part-{index:05d}.parquet"
    )

    with fs.open(
        file_path,
        "wb"
    ) as f:

        pq.write_table(
            table,
            f,
            compression="snappy"
        )
