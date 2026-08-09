"""Tests for the customer_distribution skew behavior driving the --skew CLI flag."""

import numpy as np
import pytest
from generator.distribution import customer_distribution

SIZE = 200_000
CUSTOMER_COUNT = 1_000


@pytest.fixture(autouse=True)
def _seed_random() -> None:
    """Seed the global numpy RNG so each test's distribution is deterministic."""
    np.random.seed(0)


def _counts_per_customer(customer_ids: np.ndarray, customer_count: int) -> np.ndarray:
    """Return order counts per customer_id, indexed 0 (unused) through customer_count.

    Args:
        customer_ids: Array of customer IDs, one per generated order.
        customer_count: Total number of distinct customers to bucket counts for.

    Returns:
        np.ndarray: Array of length `customer_count` where index `i` holds
            the order count for customer ID `i + 1`.
    """
    return np.bincount(customer_ids, minlength=customer_count + 1)[1:]


def test_balance_distributes_orders_evenly_across_all_customers() -> None:
    """Verify "balance" skew spreads orders uniformly across all customers."""
    result = customer_distribution(SIZE, CUSTOMER_COUNT, "balance")

    assert result.shape == (SIZE,)
    assert result.min() >= 1
    assert result.max() <= CUSTOMER_COUNT

    counts = _counts_per_customer(result, CUSTOMER_COUNT)
    expected_per_customer = SIZE / CUSTOMER_COUNT

    # No customer should be meaningfully hotter or colder than the average.
    assert counts.min() > expected_per_customer * 0.6
    assert counts.max() < expected_per_customer * 1.4
    assert counts.std() / expected_per_customer < 0.15


def test_low_skew_sends_about_90_percent_of_orders_to_40_percent_of_customers() -> None:
    """Verify "low" skew concentrates ~90% of orders on ~40% of customers."""
    result = customer_distribution(SIZE, CUSTOMER_COUNT, "low")

    assert result.shape == (SIZE,)
    assert result.min() >= 1
    assert result.max() <= CUSTOMER_COUNT

    hot_customers = int(CUSTOMER_COUNT * 0.40)
    hot_share = np.count_nonzero(result <= hot_customers) / SIZE

    # ~90% land in the hot pool directly, plus a small spillover from the
    # 10% of orders randomly distributed across every customer.
    assert 0.85 <= hot_share <= 0.97

    cold_share = 1 - hot_share
    assert 0 < cold_share <= 0.15


def test_high_skew_sends_about_90_percent_of_orders_to_1_percent_of_customers() -> None:
    """Verify "high" skew concentrates ~90% of orders on ~1% of customers."""
    result = customer_distribution(SIZE, CUSTOMER_COUNT, "high")

    assert result.shape == (SIZE,)
    assert result.min() >= 1
    assert result.max() <= CUSTOMER_COUNT

    hot_customers = max(1, int(CUSTOMER_COUNT * 0.01))
    hot_share = np.count_nonzero(result <= hot_customers) / SIZE

    assert 0.85 <= hot_share <= 0.97

    cold_share = 1 - hot_share
    assert 0 < cold_share <= 0.15


def test_high_skew_concentrates_orders_more_than_low_skew() -> None:
    """Verify "high" skew packs more orders per hot customer than "low" skew."""
    low_result = customer_distribution(SIZE, CUSTOMER_COUNT, "low")
    high_result = customer_distribution(SIZE, CUSTOMER_COUNT, "high")

    low_hot_customers = int(CUSTOMER_COUNT * 0.40)
    high_hot_customers = max(1, int(CUSTOMER_COUNT * 0.01))

    low_orders_per_hot_customer = (
        np.count_nonzero(low_result <= low_hot_customers) / low_hot_customers
    )
    high_orders_per_hot_customer = (
        np.count_nonzero(high_result <= high_hot_customers) / high_hot_customers
    )

    # "high" packs a similar share of orders into far fewer customers, so
    # its hot customers should each carry a much larger order volume.
    assert high_orders_per_hot_customer > low_orders_per_hot_customer


def test_unsupported_skew_raises_value_error() -> None:
    """Verify an unrecognized skew value raises ValueError."""
    with pytest.raises(ValueError):
        customer_distribution(SIZE, CUSTOMER_COUNT, "bogus")
