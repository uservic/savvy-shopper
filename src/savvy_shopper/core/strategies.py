import statistics
from savvy_shopper.core.interfaces import PriceComparisonStrategy


class BasicPriceStrategy(PriceComparisonStrategy):
    """Базовая стратегия ранжирования строго по цене (Инкремент 1 / MVP)."""

    def evaluate_and_rank(self, offers: list[dict], context: dict | None = None) -> dict:
        if not offers:
            return {"low": None, "median": None, "high": None, "offers": []}

        sorted_offers = sorted(offers, key=lambda x: x["price_rub"])
        prices = [item["price_rub"] for item in sorted_offers]
        median_price = statistics.median(prices)

        # Находим ближайший лот к медианной цене
        median_offer = min(sorted_offers, key=lambda x: abs(x["price_rub"] - median_price))

        return {
            "low": sorted_offers[0],
            "median": median_offer,
            "high": sorted_offers[-1],
            "offers": sorted_offers,
        }
