"""Utilities for generating customer ID distributions with configurable skew."""

import numpy as np


def customer_distribution(
    size: int,
    customer_count: int,
    skew: str
) -> np.ndarray:
    """Generate an array of customer IDs following the requested skew pattern.

    Args:
        size: Number of customer IDs to generate.
        customer_count: Total number of distinct customers to choose from.
        skew: Distribution pattern to apply. One of "balance" (uniform
            across all customers), "low" (40% of customers receive 90%
            of orders), or "high" (1% of customers receive 90% of orders).

    Returns:
        np.ndarray: Array of length `size` containing customer IDs in the
            range [1, customer_count].
    """
    if skew == "balance":

        return np.random.randint(
            1,
            customer_count + 1,
            size=size,
            dtype=np.int64
        )

    if skew == "low":

        hot_customers = int(
            customer_count * 0.40
        )

        hot_orders = int(
            size * 0.90
        )

        normal_orders = (
            size - hot_orders
        )

        return np.concatenate(
            [
                np.random.randint(
                    1,
                    hot_customers + 1,
                    size=hot_orders
                ),
                np.random.randint(
                    1,
                    customer_count + 1,
                    size=normal_orders
                )
            ]
        )

    if skew == "high":

        hot_customers = max(
            1,
            int(customer_count * 0.01)
        )

        hot_orders = int(
            size * 0.90
        )

        normal_orders = (
            size - hot_orders
        )

        return np.concatenate(
            [
                np.random.randint(
                    1,
                    hot_customers + 1,
                    size=hot_orders
                ),
                np.random.randint(
                    1,
                    customer_count + 1,
                    size=normal_orders
                )
            ]
        )

    raise ValueError(
        f"Unsupported skew: {skew}"
    )
