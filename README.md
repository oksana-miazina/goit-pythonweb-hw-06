# goit-pythonweb-hw-06

База університету: студенти, групи, викладачі, предмети та оцінки. SQLAlchemy, Alembic, PostgreSQL.

## Запуск бази

```bash
docker run --name hw06-postgres -p 5432:5432 -e POSTGRES_PASSWORD=hw06-pass -e POSTGRES_DB=hw06 -d postgres
```

Параметри підключення лежать у `.env` (зразок — `.env.example`).

## Залежності

```bash
uv sync --system-certs
```

## Міграція, наповнення, запити

```bash
uv run alembic upgrade head
uv run python seed.py
uv run python my_select.py
```

## CLI

```bash
uv run python main.py -a create -m Teacher -n "Boris Jonson"
uv run python main.py -a list -m Teacher
uv run python main.py -a update -m Teacher --id 3 -n "Andry Bezos"
uv run python main.py -a remove -m Teacher --id 3
uv run python main.py -a create -m Group -n "AD-101"
```
