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
        "--customers-tablename",
        default="customers",
        help=(
            "Table name for the customers dataset. Used as the S3 "
            "folder name customers are written under, i.e. "
            "'{output}/{customers-tablename}'. Defaults to 'customers'."
        )
    )

    parser.add_argument(
        "--orders-tablename",
        default="orders",
        help=(
            "Table name for the orders dataset. Used as the S3 "
            "folder name order events are written under, i.e. "
            "'{output}/{orders-tablename}'. Defaults to 'orders'."
        )
    )

    return parser.parse_args()


def main() -> None:
    """Parse arguments and generate the customer and order event datasets."""
    args = parse_args()

    ingested_at = datetime.now(UTC).date()

    generate_customers(
        count=args.customers,
        output=args.output,
        ingested_at=ingested_at,
        table_name=args.customers_tablename
    )

    generate_order_events(
        count=args.order_events,
        customers=args.customers,
        skew=args.skew,
        output=args.output,
        ingested_at=ingested_at,
        glue_database=args.glue_database,
        glue_table=args.orders_tablename,
        table_name=args.orders_tablename
    )


if __name__ == "__main__":
    main()
