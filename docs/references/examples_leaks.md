# Примеры потенциальных утечек по категориям

**Назначение:** словарь типов секретов для диплома, правил детекции и ручной разметки. Проверка документации: 03.10.2026.

**Все значения ниже — искусственные заглушки.** Запись `<SYNTHETIC_...>` показывает место значения и не задаёт точную длину или алфавит токена. Это не действующие ключи и не готовый обучающий датасет. Форматы провайдеров могут меняться; перед реализацией правила сверяются с актуальной документацией.

Категории частично пересекаются: например, строка подключения содержит пароль, а JWT может быть access token. В разметке задаём один `primary_type` и дополнительные теги, чтобы не считать одну находку несколько раз.

## 1. API keys

| Популярный пример | Учебный шаблон | Что учитывать |
|---|---|---|
| Stripe secret API key | `STRIPE_SECRET_KEY=sk_live_<SYNTHETIC_KEY>` | Серверный секрет; контекст переменной и тип ключа важнее одного слова `key`. |
| Stripe test secret key | `STRIPE_SECRET_KEY=sk_test_<SYNTHETIC_KEY>` | Настоящий тестовый ключ тоже даёт доступ к ресурсам тестового окружения; `test` не означает автоматически безопасное значение. |
| Stripe restricted API key | `STRIPE_RESTRICTED_KEY=rk_live_<SYNTHETIC_KEY>` | Ограниченные права не делают ключ публичным. |
| SendGrid API key | `SENDGRID_API_KEY=SG.<SYNTHETIC_PART_1>.<SYNTHETIC_PART_2>` | Кандидат на секрет в коде, `.env`, конфигурации или заголовке авторизации. |
| Google API key | `GOOGLE_API_KEY=AIza<SYNTHETIC_KEY>` | Классификация зависит от API, ограничений и назначения ключа; не всякий такой ключ равен паролю. |

**Контрпримеры:** publishable-ключи Stripe `pk_test_...` / `pk_live_...`; `os.getenv("API_KEY")`; текст `YOUR_API_KEY`. Firebase API keys обычно служат идентификаторами проекта, а не самостоятельной авторизацией; не помечать их как подтверждённые секреты без контекста.

Источники: [Stripe API keys](https://docs.stripe.com/keys), [SendGrid SDK](https://github.com/sendgrid/sendgrid-python), [Firebase API keys](https://firebase.google.com/docs/projects/api-keys).

## 2. Access tokens

| Популярный пример | Учебный шаблон | Где исследовать |
|---|---|---|
| GitHub classic personal access token | `GITHUB_TOKEN=ghp_<SYNTHETIC_TOKEN>` | Скрипты CI, Git-конфигурация, примеры запросов. |
| GitHub fine-grained personal access token | `GITHUB_TOKEN=github_pat_<SYNTHETIC_TOKEN>` | Конфигурация интеграций и автоматизации. |
| GitLab personal access token | `GITLAB_TOKEN=glpat-<SYNTHETIC_TOKEN>` | Переменные окружения и CI-конфигурация. |
| Slack bot token | `SLACK_BOT_TOKEN=xoxb-<SYNTHETIC_TOKEN>` | Настройки бота и интеграций. |
| npm access token | `//registry.npmjs.org/:_authToken=npm_<SYNTHETIC_TOKEN>` | Содержимое `.npmrc` и скрипты публикации. |
| Hugging Face token | `HF_TOKEN=hf_<SYNTHETIC_TOKEN>` | Конфигурация загрузки моделей и датасетов. |

**Контрпримеры:** `${GITHUB_TOKEN}`, названия переменных и маски `***`. Префикс помогает извлечь кандидата, но не доказывает, что токен действующий или имеет определённые права.

Источники: [Gitleaks: правила и тесты провайдеров](https://github.com/gitleaks/gitleaks), [TruffleHog: детекторы](https://github.com/trufflesecurity/trufflehog), [Hugging Face Hub](https://github.com/huggingface/huggingface_hub).

## 3. AWS credentials

| Пример | Учебный шаблон | Правило интерпретации |
|---|---|---|
| Долгосрочный Access Key ID | `AWS_ACCESS_KEY_ID=AKIA<SYNTHETIC_ID>` | Идентификатор — компонент пары, а не секретный ключ. |
| Secret Access Key | `AWS_SECRET_ACCESS_KEY=<SYNTHETIC_SECRET>` | Основная секретная часть пары; учитывать соседний ID. |
| Временный Access Key ID | `AWS_ACCESS_KEY_ID=ASIA<SYNTHETIC_ID>` | Для временных credentials искать также secret key и session token. |
| Session token | `AWS_SESSION_TOKEN=<SYNTHETIC_SESSION_TOKEN>` | Часть временного набора учётных данных. |
| Файл AWS credentials | `[default]` с полями `aws_access_key_id` и `aws_secret_access_key` | Анализировать несколько строк как связанную запись. |

Учебный фрагмент:

```ini
[lab-profile]
aws_access_key_id = AKIA<SYNTHETIC_ID>
aws_secret_access_key = <SYNTHETIC_SECRET>
```

**Контрпримеры:** AWS account ID, ARN роли, имя S3 bucket, регион. Они могут раскрывать структуру инфраструктуры, но сами по себе не являются секретными credentials. Для Pathfinding-сценариев используем искусственные наборы и описание их роли, без обращения к AWS API.

Источники: [AWS access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html), [IAM identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html), [Pathfinding.cloud](https://pathfinding.cloud/).

## 4. Private keys

| Популярный формат | Маркер начала | Что извлекать |
|---|---|---|
| PKCS#8 private key | `-----BEGIN PRIVATE KEY-----` | Весь многострочный блок до соответствующего END. |
| RSA private key | `-----BEGIN RSA PRIVATE KEY-----` | Заголовок, тело, окончание и контекст использования. |
| EC private key | `-----BEGIN EC PRIVATE KEY-----` | Аналогично; не путать с публичной частью. |
| OpenSSH private key | `-----BEGIN OPENSSH PRIVATE KEY-----` | Файлы вроде `id_rsa` / `id_ed25519` и тестовые fixtures. |
| PGP private key | `-----BEGIN PGP PRIVATE KEY BLOCK-----` | Секретный ключевой материал, а не публичный PGP-блок. |
| Encrypted private key | `-----BEGIN ENCRYPTED PRIVATE KEY-----` | Шифрование не превращает приватный ключ в публичный материал. |

Учебный, намеренно неполный блок:

```text
-----BEGIN PRIVATE KEY-----
<SYNTHETIC_BODY_NOT_A_VALID_PRIVATE_KEY>
-----END PRIVATE KEY-----
```

**Контрпримеры:** `BEGIN PUBLIC KEY`, SSH public key, `BEGIN CERTIFICATE`. Для проверки парсинга создаём отдельные структурно корректные локальные ключи, никогда не применяемые для реальных сервисов. Тестовый ключ и действующая утечка должны иметь разные атрибуты происхождения.

Источники: [GitHub generic secret patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns), [pyca/cryptography](https://cryptography.io/en/latest/), [OpenSSH](https://github.com/openssh/openssh-portable).

## 5. Database credentials

| Популярный пример | Учебный фрагмент |
|---|---|
| PostgreSQL | `PGUSER=lab_user` и `PGPASSWORD=<SYNTHETIC_PASSWORD>` |
| MySQL / MariaDB | `MYSQL_USER=lab_user` и `MYSQL_PASSWORD=<SYNTHETIC_PASSWORD>` |
| MongoDB | `MONGO_USER=lab_user` и `MONGO_PASSWORD=<SYNTHETIC_PASSWORD>` |
| Redis | `REDIS_PASSWORD=<SYNTHETIC_PASSWORD>` |
| SQL Server | `DB_USER=lab_user` и `DB_PASSWORD=<SYNTHETIC_PASSWORD>` |

Типичные места: `.env`, JSON/YAML-конфигурации, Docker Compose, параметры подключения в коде. Искать отношения `host — username — password`, но не выводить пароль в отчёт.

**Контрпримеры:** имя пользователя без пароля, `password=os.getenv("DB_PASSWORD")`, пустой пароль в документации. Для непустого значения решение зависит от контекста; слабый пароль не должен пропускаться из-за низкой энтропии.

Источники: [PostgreSQL connection parameters](https://www.postgresql.org/docs/current/libpq-connect.html), [MongoDB connection strings](https://www.mongodb.com/docs/manual/reference/connection-string/), [Redis Python client](https://github.com/redis/redis-py).

## 6. Passwords

| Популярный пример | Учебный фрагмент | Контекст |
|---|---|---|
| Пароль SMTP | `SMTP_PASSWORD=<SYNTHETIC_PASSWORD>` | Конфигурация почтовой отправки. |
| Пароль учётной записи приложения | `admin_password = "<SYNTHETIC_PASSWORD>"` | Код и конфигурация авторизации. |
| Учётные данные `.netrc` | `machine api.example.invalid login lab password <SYNTHETIC_PASSWORD>` | Локальная автоматизация доступа. |
| HTTP Basic Authentication | `Authorization: Basic <BASE64_OF_SYNTHETIC_USER_AND_PASSWORD>` | Сохранённые запросы, тесты, документация. |
| Пароль в настройках сборки | `repository_password: "<SYNTHETIC_PASSWORD>"` | Настройки CI и доступа к артефактам. |

**Важно:** Base64 — не шифрование. Короткие строки могут быть настоящими паролями; высокая энтропия не является обязательным условием. Хеш пароля — отдельный чувствительный объект, не plaintext password и не автоматически безопасный контрпример.

**Контрпримеры:** поле HTML `type="password"`, имя аргумента `password`, строка с инструкцией «введите пароль». Значения из документации размечаются по установленной политике, а не только по наличию слова `example`.

Источники: [GitHub generic and AI-detected patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns), [Python netrc](https://docs.python.org/3/library/netrc.html).

## 7. Connection strings

| Популярный пример | Учебная строка |
|---|---|
| PostgreSQL URI | `postgresql://lab_user:SYNTHETIC_PASSWORD@db.example.invalid:5432/labdb` |
| MySQL URI | `mysql://lab_user:SYNTHETIC_PASSWORD@db.example.invalid:3306/labdb` |
| MongoDB SRV URI | `mongodb+srv://lab_user:SYNTHETIC_PASSWORD@cluster.example.invalid/labdb` |
| Redis URI | `redis://:SYNTHETIC_PASSWORD@cache.example.invalid:6379/0` |
| SQL Server connection string | `Server=db.example.invalid;Database=labdb;User Id=lab_user;Password=SYNTHETIC_PASSWORD;` |
| Azure Storage connection string | `DefaultEndpointsProtocol=https;AccountName=labaccount;AccountKey=<SYNTHETIC_KEY>;EndpointSuffix=core.windows.net` |

Искать секретную часть, а не просто наличие URL. Учитывать URI-кодирование, кавычки и строковую конкатенацию. Для отчёта сохранять замаскированную строку и позицию секретного поля.

**Контрпримеры:** `postgresql://localhost/labdb` без credentials; `${DATABASE_URL}`; публичный URL без секретных параметров. Домены `example.invalid` и все пароли в таблице искусственные.

Источники: [PostgreSQL URI format](https://www.postgresql.org/docs/current/libpq-connect.html), [MongoDB URI format](https://www.mongodb.com/docs/manual/reference/connection-string/), [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy), [Azure Storage connection strings](https://learn.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string), [GitHub supported patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns).

## 8. JWT / authentication tokens

| Популярный пример | Учебный шаблон | Что учитывать |
|---|---|---|
| JWT в формате compact JWS | `<BASE64URL_HEADER>.<BASE64URL_PAYLOAD>.<SIGNATURE>` | Три сегмента; парсинг структуры не подтверждает подлинность. |
| JWT в формате compact JWE | `<HEADER>.<ENCRYPTED_KEY>.<IV>.<CIPHERTEXT>.<TAG>` | Пять сегментов; не ограничивать все JWT правилом «три части». |
| Bearer token | `Authorization: Bearer <SYNTHETIC_TOKEN>` | Может быть JWT либо непрозрачной строкой. |
| Session cookie | `Cookie: sessionid=<SYNTHETIC_SESSION_ID>` | Потенциальный секрет сессии при подтверждённом контексте. |
| OAuth refresh token | `refresh_token: "<SYNTHETIC_REFRESH_TOKEN>"` | Не имеет одного универсального префикса. |

**Контрпримеры:** объяснение JWT-структуры в документации, имя cookie, публичный JWK без секретных параметров. JWT не обязательно является токеном доступа: назначение определяется контекстом. Истечение срока действия не отменяет факта исторического раскрытия; статус активности без внешней проверки остаётся неизвестным.

Локальное декодирование необходимо только для получения признаков и разметки. Не выполнять по найденному токену запросы и не принимать содержимое payload как доверенное.

Источники: [RFC 7519 — JWT](https://www.rfc-editor.org/rfc/rfc7519.html), [PyJWT](https://pyjwt.readthedocs.io/en/stable/), [Authlib](https://github.com/authlib/authlib).

## 9. Other high-entropy secrets

| Популярный пример | Учебный фрагмент | Назначение |
|---|---|---|
| Django SECRET_KEY | `SECRET_KEY = "<SYNTHETIC_RANDOM_SECRET>"` | Секрет приложения для криптографической подписи. |
| Flask SECRET_KEY | `app.config["SECRET_KEY"] = "<SYNTHETIC_RANDOM_SECRET>"` | Секрет конфигурации приложения и подписи сессий. |
| Симметричный ключ шифрования | `ENCRYPTION_KEY=<SYNTHETIC_RANDOM_KEY>` | Значение, используемое при шифровании, а не произвольная случайная строка. |
| HMAC signing key | `HMAC_SECRET=<SYNTHETIC_RANDOM_SECRET>` | Ключ вычисления MAC. |
| Webhook signing secret | `WEBHOOK_SECRET=whsec_<SYNTHETIC_SECRET>` | Например, секрет проверки подписей Stripe webhook; не API key. |
| Ключ Fernet | `FERNET_KEY=<SYNTHETIC_URLSAFE_BASE64_KEY>` | Симметричный ключ; формат и контекст должны соответствовать библиотеке. |

**Контрпримеры:** Git commit hash, UUID, контрольная сумма файла, Base64-картинка, SRI-хеш, случайный идентификатор запроса. Энтропия — только признак, а не доказательство утечки. Base64-представление Kubernetes Secret также требует анализа декодированного значения, а не автоматической метки по имени поля.

Источники: [Django SECRET_KEY](https://docs.djangoproject.com/en/stable/ref/settings/#secret-key), [Flask](https://github.com/pallets/flask), [cryptography](https://cryptography.io/en/latest/), [Stripe webhook secrets](https://docs.stripe.com/keys), [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).

## Политика разметки для всех категорий

Предлагаемые поля: `label = SECRET | NON_SECRET | UNCERTAIN`, `primary_type`, `origin = SYNTHETIC | LAB | PUBLIC`, `usage_context`, `activity_status = UNKNOWN`, `repo_id`, `commit_sha`, `path`, `line_start`, `line_end`, `fingerprint`.

`SECRET` означает, что образец по назначению содержит секретный материал, а не что проверена его действительность. Структурно корректный, самостоятельно созданный и нигде не используемый ключ может быть положительным синтетическим примером. Текстовая заглушка `<YOUR_API_KEY>` — пример документационного не-секрета. Неоднозначные случаи остаются `UNCERTAIN` до ручного решения.

Заглушки из этого файла нельзя просто превратить в положительный класс. Для обучения подготовить разнообразные реалистичные, но не действующие примеры; не давать модели выучить только маркеры `TEST`, `EXAMPLE`, имя папки или источник датасета. Дубликаты, общие шаблоны и связанные репозитории не должны попадать в разные части train / validation / test. В открытых результатах публиковать только искусственные или замаскированные значения.
