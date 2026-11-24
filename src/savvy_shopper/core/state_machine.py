import asyncio
import uuid
from sqlalchemy import select
from savvy_shopper.config import load_domain_config
from savvy_shopper.core.strategies import BasicPriceStrategy
from savvy_shopper.db.database import async_session_maker
from savvy_shopper.db.models import ResearchSession

# Глобальный семафор для защиты видеопамяти (NFR-003: строго <= 1 активного инференса)
gpu_semaphore = asyncio.Semaphore(1)


async def run_research_pipeline(session_id: uuid.UUID) -> None:
    """Каркас детерминированного конечного автомата (ADR-001)."""
    async with gpu_semaphore:
        async with async_session_maker() as db:
            result = await db.execute(select(ResearchSession).where(ResearchSession.id == session_id))
            session = result.scalar_one_or_none()
            if not session:
                return

            try:
                domain_cfg = load_domain_config(session.domain)
                session.status = "PROCESSING"

                # Шаг 1: Анализ запроса
                session.current_step = "Шаг 1/4: Анализ параметров запроса (Агент-интервьюер)"
                await db.commit()
                await asyncio.sleep(0.5)

                # Шаг 2: Поиск по форумам
                session.current_step = f"Шаг 2/4: Поиск на форумах {domain_cfg.get('trusted_forums')}"
                await db.commit()
                await asyncio.sleep(0.5)

                # Шаг 3: Извлечение рисков
                session.current_step = "Шаг 3/4: Динамическая генерация чек-листа рисков"
                await db.commit()
                await asyncio.sleep(0.5)

                # Шаг 4: Оценка ценового коридора (заглушка для проверки каркаса КТ-2)
                session.current_step = "Шаг 4/4: Нормализация SKU и расчет ценового коридора"
                await db.commit()

                mock_offers = [
                    {"title": "Samsung Galaxy S26 12/256GB (UAE)", "price_rub": 74900, "url": "https://ozon.ru"},
                    {"title": "Samsung Galaxy S26 12/256GB (CAU)", "price_rub": 82500, "url": "https://dns-shop.ru"},
                    {"title": "Samsung Galaxy S26 12/256GB (Официальный ритейл)", "price_rub": 89990, "url": "https://mvideo.ru"},
                ]
                strategy = BasicPriceStrategy()
                corridor = strategy.evaluate_and_rank(mock_offers)

                session.price_corridor = corridor
                session.result_markdown = (
                    f"# Аналитическая справка SavvyShopper (Каркас)\n\n"
                    f"**Запрос:** {session.user_query}\n\n"
                    f"### Ценовой коридор (12/256 ГБ)\n"
                    f"- **Низ рынка:** {corridor['low']['price_rub']} ₽ — [{corridor['low']['title']}]({corridor['low']['url']})\n"
                    f"- **Золотая середина:** {corridor['median']['price_rub']} ₽ — [{corridor['median']['title']}]({corridor['median']['url']})\n"
                    f"- **Верх рынка:** {corridor['high']['price_rub']} ₽ — [{corridor['high']['title']}]({corridor['high']['url']})\n\n"
                    f"> *{domain_cfg['pricing_rules']['disclaimer']}*"
                )
                session.status = "COMPLETED"
                session.current_step = "Готово"
                await db.commit()

            except Exception as exc:
                session.status = "FAILED"
                session.error_message = str(exc)
                session.current_step = "Ошибка выполнения"
                await db.commit()
