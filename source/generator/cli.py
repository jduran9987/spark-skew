"""Command-line interface for generating Spark join benchmark datasets."""

import argparse
from datetime import UTC, datetime

from generator.customers import generate_customers
from generator.orders import generate_order_events


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the dataset generator.

    Returns:
        argparse.Namespace: Parsed arguments containing customers,
            order_events, skew, and output values.
    """
    parser = argparse.ArgumentParser(
        description="Generate Spark join benchmark datasets"
    )

    parser.add_argument(
        "--customers",
        type=int,
        required=True,
        help="Number of customers"
    )

    parser.add_argument(
        "--order-events",
        type=int,
        required=True,
        help="Number of order events"
    )

    parser.add_argument(
        "--skew",
        choices=[
            "balance",
            "low",
            "high"
        ],
        required=True
    )

    parser.add_argument(
        "--output",
        required=True,
        help="S3 output prefix"
    )

    parser.add_argument(
        "--glue-database",
        required=True,
        help="Glue database to register order-event partitions in"
    )

    parser.add_argument(
        "--glue-table",
        required=True,
        help="Glue table to register order-event partitions against"
    )

    return parser.parse_args()


def main() -> None:
    """Parse arguments and generate the customer and order event datasets."""
    args = parse_args()

    ingested_at = datetime.now(UTC).date()

    generate_customers(
        count=args.customers,
        output=args.output,
        ingested_at=ingested_at
    )

    generate_order_events(
        count=args.order_events,
        customers=args.customers,
        skew=args.skew,
        output=args.output,
        ingested_at=ingested_at,
        glue_database=args.glue_database,
        glue_table=args.glue_table
    )


if __name__ == "__main__":
    main()
