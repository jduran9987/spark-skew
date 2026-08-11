"""Generation of synthetic order event batches written out as Parquet."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from collections.abc import Iterator
from typing import Any

import numpy as np

from generator.distribution import customer_distribution
from generator.glue import register_partitions
from generator.parquet_writer import write_table_batches

BATCH_SIZE = 250_000

# Bytes-per-row estimate for the physical Parquet columns (event_date is
# dropped from the file since it's the Hive partition column):
#   order_id(8) + customer_id(8) + product_id(8) + order_timestamp(8)
#   + quantity(8) + unit_price decimal128(16) + event_type string(~14)
#   + ingested_at(4) = ~74 raw bytes/row. Snappy roughly halves mixed
# numeric/decimal/low-cardinality-string data like this, so ~37
# compressed bytes/row. At 5,000,000 rows/file that lands ~185MB,
# comfortably inside the 128-256MB target.
MAX_ROWS_PER_FILE = 5_000_000


EVENT_TYPES = [
    "ORDER_CREATED",
    "ORDER_UPDATED",
    "ORDER_CANCELLED"
]


def generate_order_events(
    count: int,
    customers: int,
    skew: str,
    output: str,
    ingested_at: date,
    glue_database: str,
    glue_table: str,
    table_name: str = "orders"
) -> None:
    """Generate synthetic order events, write them to Parquet on S3, and
    register the resulting `event_date` partitions in Glue.

    Args:
        count: Total number of order events to generate.
        customers: Total number of distinct customers to assign orders to.
        skew: Customer distribution skew pattern to apply (see
            `customer_distribution`).
        output: S3 output prefix; orders are written under
            `{output}/{table_name}`.
        ingested_at: Date the generator job ran, stamped onto every row.
        glue_database: Glue database the orders table lives in.
        glue_table: Glue table to register new `event_date` partitions
            against.
        table_name: Table name for the orders dataset; used as the S3
            folder name order events are written under.

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
                    ],


                "ingested_at":
                    [ingested_at] * size
            }

            current += size

    partition_locations = write_table_batches(
        batches(),
        f"{output}/{table_name}",
        partition_column="event_date",
        max_rows_per_file=MAX_ROWS_PER_FILE
    )

    register_partitions(
        database=glue_database,
        table=glue_table,
        partition_locations=partition_locations
    )
