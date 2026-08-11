"""Generation of synthetic customer batches written out as Parquet."""

from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from typing import Any

import numpy as np

from generator.parquet_writer import write_table_batches

BATCH_SIZE = 250_000

# Bytes-per-row estimate for the physical Parquet columns:
#   customer_id(8) + customer_name string(~15) + customer_segment
#   string(~11) + country_code string(~2) + created_at(8) + ingested_at(4)
#   = ~48 raw bytes/row. Applying the same ~2x snappy compression rule of
# thumb used for orders gives ~24 compressed bytes/row. At 8,000,000
# rows/file that lands ~192MB, inside the 128-256MB target.
MAX_ROWS_PER_FILE = 8_000_000


SEGMENTS = [
    "SMALL_BUSINESS",
    "MID_MARKET",
    "ENTERPRISE"
]


COUNTRIES = [
    "US",
    "CA",
    "GB",
    "DE",
    "FR",
    "JP"
]


def generate_customers(
    count: int,
    output: str,
    ingested_at: date,
    table_name: str = "customers"
) -> None:
    """Generate synthetic customers and write them to Parquet on S3.

    Args:
        count: Total number of customers to generate.
        output: S3 output prefix; customers are written under
            `{output}/{table_name}`.
        ingested_at: Date the generator job ran, stamped onto every row.
        table_name: Table name for the customers dataset; used as the S3
            folder name customers are written under.

    Returns:
        None
    """

    def batches() -> Iterator[dict[str, Any]]:
        """Yield successive batches of customer records.

        Returns:
            Iterator[dict[str, Any]]: Iterator of dicts mapping column
                names to lists/arrays of column values for each batch.
        """
        current = 1

        while current <= count:

            size = min(
                BATCH_SIZE,
                count - current + 1
            )

            ids = np.arange(
                current,
                current + size,
                dtype=np.int64
            )

            yield {

                "customer_id": ids,

                "customer_name": [
                    f"Customer {i}"
                    for i in ids
                ],

                "customer_segment":
                    np.random.choice(
                        SEGMENTS,
                        size=size
                    ),

                "country_code":
                    np.random.choice(
                        COUNTRIES,
                        size=size
                    ),

                "created_at":
                    [
                        datetime.now(UTC)
                        -
                        timedelta(
                            days=int(
                                np.random.randint(
                                    0,
                                    1000
                                )
                            )
                        )
                        for _ in range(size)
                    ],


                "ingested_at":
                    [ingested_at] * size
            }

            current += size

    write_table_batches(
        batches(),
        f"{output}/{table_name}",
        max_rows_per_file=MAX_ROWS_PER_FILE
    )
