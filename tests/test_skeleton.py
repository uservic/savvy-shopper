from savvy_shopper.config import load_domain_config
from savvy_shopper.core.strategies import BasicPriceStrategy


def test_load_smartphones_domain_inheritance():
    """Проверяет наследование smartphones.yaml от _base_electronics.yaml (ADR-002)."""
    cfg = load_domain_config("smartphones")
    assert cfg["domain_id"] == "smartphones"
    assert "4pda.to" in cfg["trusted_forums"]
    assert "youtube.com" in cfg["blacklisted_domains"]
    assert cfg["pricing_rules"]["min_budget_ratio"] == 0.60


def test_basic_price_strategy_corridor():
    """Проверяет расчет точек Низ — Середина — Верх на каркасе (US-004)."""
    offers = [
        {"title": "Lot A", "price_rub": 50000},
        {"title": "Lot B", "price_rub": 60000},
        {"title": "Lot C", "price_rub": 70000},
    ]
    strategy = BasicPriceStrategy()
    result = strategy.evaluate_and_rank(offers)

    assert result["low"]["price_rub"] == 50000
    assert result["median"]["price_rub"] == 60000
    assert result["high"]["price_rub"] == 70000
