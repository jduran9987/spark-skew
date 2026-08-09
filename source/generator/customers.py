"""Generation of synthetic customer batches written out as Parquet."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np

from generator.parquet_writer import write_table_batches

BATCH_SIZE = 250_000


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
    output: str
) -> None:
    """Generate synthetic customers and write them to Parquet on S3.

    Args:
        count: Total number of customers to generate.
        output: S3 output prefix; customers are written under
            `{output}/customers`.

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
                    ]
            }

            current += size

    write_table_batches(
        batches(),
        f"{output}/customers"
    )
