## UA Law LLM Telegram Bot

Система для пошуку по законодавству України та генерації відповідей через LLM, з доступом через Telegram‑бота.

### Структура проекту

- **backend**: FastAPI‑бекенд, PostgreSQL‑моделі, сервіси парсингу, пошуку та інтеграції з LLM.
- **bot**: Telegram‑бот на `aiogram`, який звертається до бекенду.
- **scripts**: утиліти для ініціалізації БД та оновлення бази законів.

### Швидкий старт локально

1. Встановіть Python 3.11+ та PostgreSQL (якщо не використовуєте `docker-compose`).
2. Встановіть залежності:

```bash
pip install -r requirements.txt
```

3. Створіть `.env` на основі `.env.example`:

```bash
cp .env.example .env
```

та заповніть:

- `OPENAI_API_KEY` — ваш ключ OpenAI;
- `TELEGRAM_BOT_TOKEN` — токен Telegram‑бота;
- `DATABASE_URL` — рядок підключення до PostgreSQL (або залиште значення з `docker-compose`).

4. Ініціалізуйте базу даних:

```bash
python scripts/init_db.py
```

5. Запустіть бекенд:

```bash
uvicorn backend.app.main:app --reload
```

6. Запустіть бота:

```bash
python -m bot.main
```

Тепер бот повинен відповідати в Telegram, звертаючись до ендпоінта `POST /api/ask`.

### Оновлення бази законів

- Одноразове оновлення (ручний запуск):

```bash
python scripts/run_update.py
```

- Для автоматичного щотижневого оновлення на VPS налаштуйте `cron`, наприклад:

```cron
0 3 * * 1  /usr/bin/python /path/to/project/scripts/run_update.py >> /var/log/ua_law_update.log 2>&1
```

або запустіть окремо планувальник:

```bash
python -m backend.app.scheduler
```

### Використання Docker

1. Побудувати та запустити сервіс:

```bash
docker compose up --build
```

2. Бекенд буде доступний на `http://localhost:8000`, бот — як окремий сервіс (працює всередині контейнера).

### Важливі зауваження

- Проект орієнтований **лише на законодавство України**.
- Відповіді бота є **інформаційними** і не замінюють професійну юридичну консультацію.
- Парсер `backend/app/services/parser.py` містить каркас, який потрібно адаптувати під фактичний формат ZIP‑архіву з `data.gov.ua` (XML/JSON/CSV з метаданими і повними текстами актів).

