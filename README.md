# Информационная безопасность — лабораторная работа № 1

Защищённый REST API на Python 3.12+, Flask, SQLAlchemy и SQLite.

## API

| Метод | URL | Назначение | Доступ |
|---|---|---|---|
| `POST` | `/auth/register` | Регистрация пользователя и выдача JWT | Открытый |
| `POST` | `/auth/login` | Аутентификация и выдача JWT | Открытый |
| `GET` | `/api/data` | Получение списка данных | Только с JWT |

Тело запросов регистрации и входа:

```json
{
  "login": "alice",
  "password": "correct-horse"
}
```

Успешная регистрация или аутентификация возвращает:

```json
{
  "token": "<JWT>",
  "token_type": "Bearer"
}
```

## Запуск

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:JWT_SECRET = (python -c "import secrets; print(secrets.token_urlsafe(32))")
python run.py
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
export JWT_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python run.py
```

`JWT_SECRET` — обязательная переменная окружения: приложение не запустится,
если её нет или секрет короче 32 байт. Он передаётся только текущему процессу
терминала и не хранится в файлах проекта. `JWT_EXPIRATION_SECONDS` можно
установить отдельно для изменения времени жизни токена; по умолчанию это 3600
секунд. После запуска API будет доступен на `http://127.0.0.1:8080`.


## Реализованные меры защиты

- SQL-инъекции: все обращения к БД выполняются через ORM SQLAlchemy и
  параметризованные выражения, SQL не собирается конкатенацией строк.
- XSS: строки из БД экранируются функцией Flask `markupsafe.escape`;
- Broken Authentication: пароли хранятся только как bcrypt-хэши с солью;
  секрет подписи JWT передаётся через переменную окружения и не хранится в репозитории;
  после входа выдаётся подписанный JWT с ограниченным временем жизни;
  middleware `jwt_required` проверяет схему Bearer, подпись, алгоритм и срок
  действия JWT на защищённом endpoint.

## Скриншоты отчётов

![Bandit SAST report](docs/img/bandit.png)

## Отчёты последнего запуска CI

- [Bandit SAST — HTML-отчёт](reports/bandit.html)
- [Snyk SCA — JSON-отчёт](reports/snyk.json)
