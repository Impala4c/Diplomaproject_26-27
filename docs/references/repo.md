# Публичные Git-репозитории для экспериментального корпуса

**Всего: 60 уникальных репозиториев. Проверка публичных страниц и описаний: 03.10.2026.**

Это каталог целей для локального статического исследования, а не перечень организаций с действующими утечками. Репозитории не были клонированы или просканированы при подготовке списка; конкретные секреты и их расположение в истории здесь не подтверждаются. Каждый URL в таблице — прямая ссылка на первичный источник.

В каталоге есть намеренно небезопасные учебные проекты, исследовательские датасеты, тесты сканеров и обычные библиотеки. Для последних указаны предлагаемые области отбора примеров, а не результаты обнаружения. «Контрольный корпус» не означает, что весь репозиторий гарантированно является отрицательным классом.

**Приоритеты:** P1 — 12 источников для пилота; P2 — расширение после работающего прототипа; P3 — резерв или вспомогательный материал. Приоритет отражает предложенный порядок работы команды, а не качество или безопасность проекта. Для каждого источника отдельно проверить лицензию и допустимость перепубликации фрагментов.

## 1. Специализированные лаборатории и датасеты

| № | Публичный репозиторий — прямая ссылка | Что исследовать / роль | Приоритет |
|---:|---|---|:---:|
| 1 | [https://github.com/Plazmaz/leaky-repo](https://github.com/Plazmaz/leaky-repo) | Учебный репозиторий секретов; автор описывает рандомизацию/редактирование значений. Разные типы credentials и многострочные ключи. | P1 |
| 2 | [https://github.com/digininja/leakyrepo](https://github.com/digininja/leakyrepo) | Намеренно небезопасные примеры для изучения раскрытия секретов; источник лабораторных случаев. | P1 |
| 3 | [https://github.com/trufflesecurity/test_keys](https://github.com/trufflesecurity/test_keys) | Публичный тестовый репозиторий ключей. Только статический анализ; действительность значений не проверялась. | P1 |
| 4 | [https://github.com/OWASP/wrongsecrets](https://github.com/OWASP/wrongsecrets) | Учебные задания по ошибкам хранения секретов. Анализировать код и конфигурации; не подключаться к внешним ресурсам. | P1 |
| 5 | [https://github.com/setu1421/SecretBench](https://github.com/setu1421/SecretBench) | Исследовательский артефакт и данные для secret detection. Проверить условия получения конкретной версии; не считать готовым набором Git-историй. | P1 |
| 6 | [https://github.com/Samsung/CredData](https://github.com/Samsung/CredData) | Датасет и разметка credentials; источник положительных и отрицательных примеров после проверки лицензии и происхождения. | P1 |

## 2. Сканеры и их тестовые примеры

| № | Публичный репозиторий — прямая ссылка | Что исследовать / роль | Приоритет |
|---:|---|---|:---:|
| 7 | [https://github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | Правила и тесты поиска секретов; основной внешний baseline. Его fixtures выделить из независимого контрольного набора. | P1 |
| 8 | [https://github.com/trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) | Провайдерские детекторы и тесты; второй baseline только с отключённой сетевой верификацией. | P2 |
| 9 | [https://github.com/Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) | Плагины, тесты энтропии, ключевых слов и фильтров. Дополнительное сравнение снимков файлов. | P1 |
| 10 | [https://github.com/Skyscanner/whispers](https://github.com/Skyscanner/whispers) | Поиск секретов в структурированных текстах; примеры конфигураций и контекстных правил. | P1 |
| 11 | [https://github.com/awslabs/git-secrets](https://github.com/awslabs/git-secrets) | AWS-oriented правила и тестовые случаи; разграничение ID и секретной части credentials. | P2 |
| 12 | [https://github.com/secretlint/secretlint](https://github.com/secretlint/secretlint) | Правила и тесты secret linting; примеры совпадений и исключений. | P2 |
| 13 | [https://github.com/GitGuardian/ggshield](https://github.com/GitGuardian/ggshield) | Исходный код и тесты клиентского инструмента; использовать как корпус, не отправлять найденные данные в SaaS. | P2 |
| 14 | [https://github.com/SonarSource/sonar-text](https://github.com/SonarSource/sonar-text) | Анализ текста и секретов; правила, тестовые случаи и фильтры ложных срабатываний. | P2 |
| 15 | [https://github.com/Checkmarx/2ms](https://github.com/Checkmarx/2ms) | Сканер секретов и его тестовые случаи; дополнительный источник шаблонов и форматов. | P2 |
| 16 | [https://github.com/praetorian-inc/noseyparker](https://github.com/praetorian-inc/noseyparker) | Детекция секретов в текстах и Git-данных; правила, тесты и идеи дедупликации. | P2 |
| 17 | [https://github.com/aquasecurity/trivy](https://github.com/aquasecurity/trivy) | Тестовые данные подсистемы secret scanning. Остальные проверки безопасности не входят в тему. | P3 |
| 18 | [https://github.com/bridgecrewio/checkov](https://github.com/bridgecrewio/checkov) | IaC-конфигурации и тесты проверок; контекст конфигурационных credentials. Не считать специализированным Git-history benchmark. | P3 |
| 19 | [https://github.com/semgrep/semgrep-rules](https://github.com/semgrep/semgrep-rules) | Статические правила и тесты; выбирать случаи hard-coded credentials. Проверить отдельные условия лицензии правил. | P2 |
| 20 | [https://github.com/deepfence/SecretScanner](https://github.com/deepfence/SecretScanner) | Сканер секретов файловой системы и контейнеров; использовать правила/тесты, не запускать чужие образы. | P3 |
| 21 | [https://github.com/microsoft/DevSkim](https://github.com/microsoft/DevSkim) | Правила security linting и тесты; дополнительный материал по строковым литералам и небезопасной конфигурации. | P3 |

## 3. AWS-сценарии, учебные приложения и исследовательские артефакты

| № | Публичный репозиторий — прямая ссылка | Что исследовать / роль | Приоритет |
|---:|---|---|:---:|
| 22 | [https://github.com/DataDog/pathfinding.cloud](https://github.com/DataDog/pathfinding.cloud) | Основная сценарная методология для AWS IAM. Код лабораторий и описание ролей credentials; это не датасет Git-утечек. | P2 |
| 23 | [https://github.com/setu1421/AssetHarvester](https://github.com/setu1421/AssetHarvester) | Связь секретов с ресурсами в статическом анализе; исследовательская реализация контекстного подхода. | P2 |
| 24 | [https://github.com/nafiurahman00/Secret-Breach-Prevention-In-Software-Issue-Reports](https://github.com/nafiurahman00/Secret-Breach-Prevention-In-Software-Issue-Reports) | LLM-исследование secret detection в issues. Вспомогательный материал; домен отличается от истории кода. | P3 |
| 25 | [https://github.com/WebGoat/WebGoat](https://github.com/WebGoat/WebGoat) | Учебное Java-приложение; отбор примеров авторизации, паролей и конфигурации из исходного кода. | P3 |
| 26 | [https://github.com/digininja/DVWA](https://github.com/digininja/DVWA) | Учебное PHP-приложение; настройки базы данных и примерные credentials. | P2 |
| 27 | [https://github.com/OWASP/NodeGoat](https://github.com/OWASP/NodeGoat) | Учебное Node.js-приложение; MongoDB, конфигурация и контекст авторизации. | P2 |
| 28 | [https://github.com/appsecco/dvna](https://github.com/appsecco/dvna) | Учебное Node.js-приложение; переменные окружения и конфигурационные параметры. | P2 |
| 29 | [https://github.com/OWASP/crAPI](https://github.com/OWASP/crAPI) | Учебное API-приложение; конфигурации, токены и контекст аутентификации. | P2 |
| 30 | [https://github.com/RhinoSecurityLabs/cloudgoat](https://github.com/RhinoSecurityLabs/cloudgoat) | AWS-лаборатории; статический анализ Terraform и сценариев. Развёртывать облачные ресурсы для дипломного MVP не требуется. | P2 |
| 31 | [https://github.com/madhuakula/kubernetes-goat](https://github.com/madhuakula/kubernetes-goat) | Kubernetes-лаборатории; YAML, переменные окружения и объекты Secret. | P2 |
| 32 | [https://github.com/bridgecrewio/terragoat](https://github.com/bridgecrewio/terragoat) | Намеренно небезопасные Terraform-конфигурации; контекст IaC и значения-заглушки. | P2 |
| 33 | [https://github.com/bridgecrewio/cfngoat](https://github.com/bridgecrewio/cfngoat) | Учебные CloudFormation-конфигурации; параметры доступа и настройки облачной инфраструктуры. | P2 |
| 34 | [https://github.com/juice-shop/juice-shop](https://github.com/juice-shop/juice-shop) | Учебное веб-приложение OWASP Juice Shop; код авторизации, тесты и конфигурации. | P2 |
| 35 | [https://github.com/OWASP-Benchmark/BenchmarkJava](https://github.com/OWASP-Benchmark/BenchmarkJava) | Java security benchmark; выбирать относящиеся к credentials/криптографии случаи. Не является специализированным датасетом Git-утечек. | P3 |

## 4. Криптография, JWT, OAuth и конфигурационные библиотеки

| № | Публичный репозиторий — прямая ссылка | Что исследовать / роль | Приоритет |
|---:|---|---|:---:|
| 36 | [https://github.com/pyca/cryptography](https://github.com/pyca/cryptography) | Криптографические тесты и векторы: приватные/публичные ключи, сертификаты. Размечать по назначению и происхождению. | P2 |
| 37 | [https://github.com/jpadilla/pyjwt](https://github.com/jpadilla/pyjwt) | JWT-код, тесты и примеры; различать токены, ключи подписи и публичный материал. | P1 |
| 38 | [https://github.com/auth0/node-jsonwebtoken](https://github.com/auth0/node-jsonwebtoken) | JWT и ключевые fixtures в Node.js; контекст подписи и проверки токенов. | P2 |
| 39 | [https://github.com/golang-jwt/jwt](https://github.com/golang-jwt/jwt) | Go-реализация JWT; тестовые токены, ключи и несекретные структурные элементы. | P2 |
| 40 | [https://github.com/lcobucci/jwt](https://github.com/lcobucci/jwt) | PHP-реализация JWT; примерные токены и ключевые данные в тестах. | P2 |
| 41 | [https://github.com/authlib/authlib](https://github.com/authlib/authlib) | OAuth, OIDC, JWK и JWT; контекст токенов и ключевых параметров. | P2 |
| 42 | [https://github.com/requests/requests-oauthlib](https://github.com/requests/requests-oauthlib) | OAuth-примеры и тесты запросов; access/refresh tokens и заглушки. | P2 |
| 43 | [https://github.com/oauthlib/oauthlib](https://github.com/oauthlib/oauthlib) | OAuth-тесты и модели авторизации; вспомогательный материал по контексту токенов. | P2 |
| 44 | [https://github.com/paramiko/paramiko](https://github.com/paramiko/paramiko) | SSH-код и тестовые ключи; различать приватную часть, публичную часть и known-hosts. | P2 |
| 45 | [https://github.com/openssh/openssh-portable](https://github.com/openssh/openssh-portable) | SSH-код и регрессионные тесты; форматы ключей. Большую историю включать после пилота. | P3 |
| 46 | [https://github.com/motdotla/dotenv](https://github.com/motdotla/dotenv) | Парсинг .env: литералы, переменные и заглушки; материал для ручного отбора сложных отрицательных примеров. | P1 |
| 47 | [https://github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv) | Python-парсер .env; тесты интерполяции и строковых значений. | P2 |

## 5. SDK, базы данных и веб-фреймворки — контрольный корпус

| № | Публичный репозиторий — прямая ссылка | Что исследовать / роль | Приоритет |
|---:|---|---|:---:|
| 48 | [https://github.com/boto/boto3](https://github.com/boto/boto3) | AWS SDK: примеры вызовов и конфигурации credentials. Объединять с botocore в одну группу при разделении данных. | P2 |
| 49 | [https://github.com/boto/botocore](https://github.com/boto/botocore) | Провайдеры credentials, подпись запросов и тестовые данные AWS; контекст ID/secret/session token. | P1 |
| 50 | [https://github.com/stripe/stripe-python](https://github.com/stripe/stripe-python) | Stripe SDK; контекст secret и publishable API keys, примеры и тестовые значения. | P2 |
| 51 | [https://github.com/sendgrid/sendgrid-python](https://github.com/sendgrid/sendgrid-python) | SendGrid SDK; API key в примерах интеграции и тестах. | P2 |
| 52 | [https://github.com/twilio/twilio-python](https://github.com/twilio/twilio-python) | Twilio SDK; различие Auth Token и Account SID, тестовые запросы. | P2 |
| 53 | [https://github.com/sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) | Форматы DB URL и конфигурации подключения; пароль в URI и варианты без credentials. | P2 |
| 54 | [https://github.com/psycopg/psycopg](https://github.com/psycopg/psycopg) | PostgreSQL DSN, параметры пользователя и пароля в тестовом коде. | P2 |
| 55 | [https://github.com/mongodb/mongo-python-driver](https://github.com/mongodb/mongo-python-driver) | MongoDB URI и тесты аутентификации; литералы и ссылки на окружение. | P2 |
| 56 | [https://github.com/redis/redis-py](https://github.com/redis/redis-py) | Redis URL, параметры пароля и тесты подключения. | P2 |
| 57 | [https://github.com/django/django](https://github.com/django/django) | SECRET_KEY, пароли и настройки в тестах/документации; большой репозиторий для расширенного этапа. | P3 |
| 58 | [https://github.com/pallets/flask](https://github.com/pallets/flask) | SECRET_KEY, конфигурации сессий и тестовые приложения. | P2 |
| 59 | [https://github.com/huggingface/huggingface_hub](https://github.com/huggingface/huggingface_hub) | Обработка токенов и тестовые конфигурации; не считать упоминание HF_TOKEN утечкой. | P2 |
| 60 | [https://github.com/firebase/firebase-admin-python](https://github.com/firebase/firebase-admin-python) | Service-account credentials и примеры конфигурации; отличать приватный ключ от публичного идентификатора. | P2 |

## Как использовать каталог до декабря

**Начало:** взять 12 источников P1, но не смешивать их роли. SecretBench/CredData используются как источники размеченных образцов и протокола; лаборатории — для контролируемых случаев; библиотеки и тесты — для ручного отбора контекстных примеров. Для проверки поиска по коммитам создать дополнительные собственные Git-истории с известной разметкой. Все 60 репозиториев не обязательно скачивать одновременно.

**Фиксация корпуса:** для каждого реально взятого источника заполнить `repo_url`, `retrieval_date`, `commit_sha`, `fetched_refs`, `family_id`, `license`, `corpus_role`, `scan_status`. Значения commit SHA здесь намеренно не придуманы: они фиксируются после получения репозитория. В отчёте указывать фактическое число просканированных проектов, а не размер этого каталога.

**История Git:** анализировать объекты, достижимые из полученных веток и тегов, включая начальный коммит и файлы, позже удалённые из текущего дерева. Не использовать shallow clone для исследования полной доступной истории. Недостижимые удалённые коммиты, чужие форки, скрытые refs, LFS-объекты и submodules не считать автоматически полученными; ограничения отражать в протоколе. Основа обхода: [Git rev-list](https://git-scm.com/docs/git-rev-list) и [Git cat-file](https://git-scm.com/docs/git-cat-file).

**Разделение данных:** связанные репозитории, форки, одинаковые значения и общие шаблоны группировать до train / validation / test. Например, boto3 и botocore не распределять независимо. Тестовые примеры сравниваемого сканера не использовать как единственный независимый test set: это даёт ему преимущество. Синтетический набор проверяет функциональность, а результаты на нём не заменяют оценку переноса на независимые данные.

## Собственные истории коммитов для проверки сканера

| Сценарий | Что должно быть известно заранее |
|---|---|
| Добавление и последующее удаление секрета | Секрет отсутствует в HEAD, но известны коммит и файл его появления. |
| Секрет уже в начальном коммите | Проверяется, что сканер не обходит только последующие diff. |
| Переименование файла с секретом | Известны исходный и новый путь; дубликат не считается новой уникальной утечкой без установленного правила. |
| Секрет в отдельной ветке и merge | Известны refs и граф коммитов; проверяется охват не только основной ветки. |
| Многострочный приватный ключ | Известны начало и конец блока; построчное правило не должно терять объект. |
| Повтор одного значения в нескольких файлах | Отдельно считаются уникальный секрет и его появления. |
| Документационный placeholder рядом с секретом | Известны положительный и отрицательный примеры с похожим контекстом. |
| AWS ID, secret key и session token в соседних полях | Известен состав набора; ID не подменяет секретную часть. |

Значения в собственных историях — искусственные и нигде не используемые для реального доступа. Они должны быть разнообразными; метка не должна определяться словом TEST или именем файла.

## Ограничения обращения с находками

Не использовать найденные значения, не выполнять вход в аккаунты и не проверять credentials через API провайдеров. Отключить верификацию у сканеров и сетевой доступ на этапе локального анализа. Код исследуемых проектов, hooks и workflow не запускать. Не публиковать чужие секреты; в результатах оставлять замаскированный контекст, commit/path и HMAC-отпечаток. Неоднозначные случаи передавать на ручную разметку, а не объявлять подтверждённой действующей утечкой.
