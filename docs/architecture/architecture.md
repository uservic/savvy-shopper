# Архитектура системы SavvyShopper (КТ-2)
**Дата актуализации:** 24.11.2026  
**Статус:** Утверждено для КТ-2

---

## 1. Контекстная диаграмма (C4 Context)
Описывает границы системы и взаимодействие с внешним окружением.

```mermaid
graph LR
    User["Покупатель (Веб-браузер)"]
    System["SavvyShopper (Конвейер исследования товаров)"]
    Forums["Доверенные форумы (4PDA, iXBT, Reddit) [NFR-004]"]
    Search["Поисковый движок (DuckDuckGo Dorking) [NFR-006]"]
    Markets["Торговые площадки (DNS, Ситилинк, Ozon, Я.Маркет)"]

    User <-->|"1. Свободный запрос и справка .md [NFR-007, NFR-008]"| System
    System -->|"2. Запросы по Whitelist [NFR-004]"| Search
    Search -.->|"3. Сниппеты цен и ссылки"| Markets
    System <-->|"4. Чтение веток обсуждений [NFR-006]"| Forums
```

---

## 2. Диаграмма контейнеров и развёртывания (C4 Containers & Deployment)
Описывает распределение сервисов по Docker-контейнерам и взаимодействие с локальным GPU.

```mermaid
graph TD
    subgraph Host ["Хост-машина (Ubuntu/WSL2, RTX 4090 24GB VRAM)"]
        Ollama["Ollama Engine (Модель qwen2.5:14b) [NFR-001, NFR-002: ≤12GB VRAM]"]
        
        subgraph Docker ["Контур Docker Compose (savvy-network)"]
            UI["Frontend: Streamlit (:8501) (Zero-Config UI)"]
            API["Backend: FastAPI (:8000) (Очередь FIFO) [NFR-003, NFR-007]"]
            Configs["YAML-профили (configs/domains/) [ADR-002]"]
            DB[("PostgreSQL 15 (:5432) (Volume: postgres_data)")]
        end
    end

    UI <-->|"REST API / JSON [NFR-007: ≤200ms]"| API
    API <-->|"SQLAlchemy asyncpg"| DB
    Configs -.->|"Правила домена и RegEx [NFR-004]"| API
    API <-->|"HTTP localhost:11434 [NFR-001: 0 внешних LLM API]"| Ollama
```

---

## 3. Модель данных (ER-диаграмма)
Описывает структуру единственной таблицы MVP с архитектурным заделом под авторизацию (Инкремент 4).

```mermaid
erDiagram
    RESEARCH_SESSIONS {
        UUID id PK "Первичный ключ сессии"
        UUID user_id "Задел под Инкремент 4 (NULL в MVP)"
        VARCHAR domain "Профиль домена (smartphones)"
        TEXT user_query "Исходный запрос покупателя"
        VARCHAR status "PENDING | PROCESSING | COMPLETED | FAILED [NFR-003]"
        VARCHAR current_step "Текущий этап для UI [NFR-007]"
        JSONB chat_history "История уточняющего диалога"
        JSONB price_corridor "Точки Низ-Середина-Верх [NFR-005]"
        TEXT result_markdown "Итоговая справка .md [NFR-008]"
        TEXT error_message "Причина сбоя при отказе [NFR-006]"
        TIMESTAMPTZ created_at "Время создания задачи"
        TIMESTAMPTZ updated_at "Время обновления статуса"
    }
```

---

## 4. Последовательность ключевого сценария и ветки отказа (Sequence Diagram)
Описывает штатное прохождение запроса по конвейеру и обработку сетевого сбоя.

```mermaid
sequenceDiagram
    autonumber
    actor U as Покупатель
    participant UI as Streamlit UI
    participant API as FastAPI + Queue [NFR-003]
    participant DB as PostgreSQL
    participant LLM as Ollama (Qwen2.5-14B) [NFR-001]
    participant Web as Поиск / Форумы

    U->>UI: Вводит запрос ("флагман самсунг в подарок")
    UI->>API: POST /api/v1/sessions
    API->>DB: INSERT (status=PENDING)
    API-->>UI: 201 Created (session_id) [NFR-007: ≤200ms]

    Note over API,LLM: Захват gpu_semaphore(1) [NFR-002, NFR-003]
    API->>DB: UPDATE status=PROCESSING
    API->>Web: Поиск веток форумов + RegEx-антиспам [NFR-004]

    alt Штатный сценарий (Данные получены)
        Web-->>API: Очищенные тексты форумов
        API->>LLM: Экстракция чек-листа рисков (JSON)
        LLM-->>API: JSON-список рисков
        API->>Web: Доркинг цен по площадкам [ADR-003]
        Web-->>API: Сырые карточки товаров
        API->>LLM: Нормализация SKU (RAM/ROM) [NFR-005]
        LLM-->>API: Валидные конфигурации + BasicPriceStrategy
        API->>DB: UPDATE status=COMPLETED, result_markdown [NFR-008]
        UI->>API: GET /api/v1/sessions/{id}
        API-->>UI: Отчет .md + график ценового коридора
    else Ветка отказа (Таймаут сети / HTTP 403-429) [NFR-006]
        Web--xAPI: ConnectionError / HTTP 429
        API->>DB: UPDATE status=FAILED, error_message [NFR-006]
        UI->>API: GET /api/v1/sessions/{id}
        API-->>UI: Уведомление об ошибке без падения сервера
    end
```

---

## 5. Легенда и привязка к требованиям
* **Сплошные стрелки (`-->`):** Синхронные и асинхронные потоки передачи данных и управления.
* **Пунктирные стрелки (`-.->`):** Загрузка декларативных правил конфигурации (`configs/domains/*.yaml`).
* **Блоки `alt / else`:** Ветвление алгоритма при штатной работе и при сбоях внешнего окружения.
* **Теги `[NFR-XXX]`:** Явная трассировка архитектурных ограничений на реестр нефункциональных требований (`docs/requirements/nfr.md`).
