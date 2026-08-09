"""Generation of synthetic order event batches written out as Parquet."""

from datetime import datetime, timedelta
from decimal import Decimal
from collections.abc import Iterator
from typing import Any

import numpy as np

from generator.distributions import customer_distribution
from generator.parquet_writer import write_table_batches

BATCH_SIZE = 250_000


EVENT_TYPES = [
    "ORDER_CREATED",
    "ORDER_UPDATED",
    "ORDER_CANCELLED"
]


def generate_order_events(
    count: int,
    customers: int,
    skew: str,
    output: str
) -> None:
    """Generate synthetic order events and write them to Parquet on S3.

    Args:
        count: Total number of order events to generate.
        customers: Total number of distinct customers to assign orders to.
        skew: Customer distribution skew pattern to apply (see
            `customer_distribution`).
        output: S3 output prefix; orders are written under
            `{output}/orders`.

    Returns:
        None
    """

    def batches() -> Iterator[dict[str, Any]]:
        """Yield successive batches of order event records.

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

            timestamps = [
                datetime(2026, 1, 1)
                +
                timedelta(
                    seconds=int(
                        np.random.randint(
                            0,
                            90 * 24 * 60 * 60
                        )
                    )
                )
                for _ in range(size)
            ]

            yield {

                "order_id":
                    np.arange(
                        current,
                        current + size,
                        dtype=np.int64
                    ),


                "customer_id":
                    customer_distribution(
                        size,
                        customers,
                        skew
                    ),


                "product_id":
                    np.random.randint(
                        1,
                        100000,
                        size=size
                    ),


                "order_timestamp":
                    timestamps,


                "quantity":
                    np.random.randint(
                        1,
                        10,
                        size=size
                    ),


                "unit_price":
                    [
                        Decimal(
                            str(
                                round(
                                    np.random.uniform(
                                        1,
                                        500
                                    ),
                                    2
                                )
                            )
                        )
                        for _ in range(size)
                    ],


                "event_type":
                    np.random.choice(
                        EVENT_TYPES,
                        size=size
                    ),


                "event_date":
                    [
                        timestamp.date()
                        for timestamp in timestamps
                    ]
            }

            current += size

    write_table_batches(
        batches(),
        f"{output}/orders"
    )
