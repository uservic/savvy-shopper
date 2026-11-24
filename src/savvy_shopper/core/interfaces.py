from abc import ABC, abstractmethod
from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMClient(ABC):
    """Абстракция провайдера LLM (Strategy Pattern для перехода на YandexGPT/GigaChat в Инкременте 5)."""

    @abstractmethod
    async def generate_structured(self, prompt: str, system_prompt: str, response_model: type[T]) -> T:
        """Генерирует строго валидируемый JSON по Pydantic-схеме."""
        pass

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: str) -> str:
        """Генерирует текстовый ответ в формате Markdown."""
        pass


class PriceComparisonStrategy(ABC):
    """Интерфейс ранжирования рыночных предложений (задел под контекстный анализ в Инкременте 3)."""

    @abstractmethod
    def evaluate_and_rank(self, offers: list[dict], context: dict | None = None) -> dict:
        """Возвращает структуру ценового коридора: low, median, high и список очищенных лотов."""
        pass
