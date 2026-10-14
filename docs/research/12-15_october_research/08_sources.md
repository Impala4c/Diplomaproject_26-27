# Источники и происхождение сведений

**Этап:** 12–15 октября 2026 года. **Повторная проверка веб-источников для этого пакета:** 11.10.2026.

Это реестр источников, а не заявление о скачивании датасетов или воспроизведении экспериментов. Ссылки на изменяемые README и документацию не фиксируют версию программы. Версии инструментов и ревизии наборов данных предстоит записать при реализации.

Обозначения: **P** — материалы команды; **S01–S10** — исходные десять референсов; **A** — дополнительные первичные источники для определений, безопасности и оценки. Дополнительные документы не подменяют исходные десять работ/ресурсов.

## Материалы команды

<a id="p0"></a>
### [P0] roadmap 1.pdf
**Где:** С. 1: тема, цель, основа, этап 12–15 октября; с. 2: оценка и ограничения.
**Роль:** Главная основа этапа. Копия вложена без правок.
**Доступный файл проекта:** [roadmap 1.pdf](../../planning/roadmap%201.pdf). Ссылка обновлена 14.10.2026: указанной ранее папки `basis/` в исходном комплекте нет. Совпадение с исторической копией этим не подтверждается.

<a id="p1"></a>
### [P1] Уточнение команды в переписке
**Где:** Сообщение: «нас двое те кто пишут».
**Роль:** Подтверждает двух авторов; имена и утверждённые личные роли не сообщены.
**Доступ:** исходный материал в переписке; отдельной копии в этом пакете нет.

<a id="p2"></a>
### [P2] ref.md
**Где:** Разделы [1]–[10].
**Роль:** Исходный список референсов. Копия вложена; проверенные сведения раскрыты в S01–S10.
**Доступный файл проекта:** [ref.md](../../references/ref.md). Ссылка обновлена 14.10.2026: указанной ранее папки `basis/` в исходном комплекте нет. Совпадение с исторической копией этим не подтверждается.

<a id="p3"></a>
### [P3] examples_leaks.md
**Где:** Девять категорий и «Политика разметки для всех категорий».
**Роль:** Сохранены названия категорий. Искусственные строки из прежнего файла здесь не размножались.
**Доступ:** исходный материал в переписке; отдельной копии в этом пакете нет.

<a id="p4"></a>
### [P4] req.md
**Где:** Инструменты, эксперименты, ограничения MVP.
**Роль:** В старом файле указаны три участника; это положение не переносится как актуальное.
**Доступ:** исходный материал в переписке; отдельной копии в этом пакете нет.

<a id="p5"></a>
### [P5] read.me
**Где:** Разделы 4, 5, 7, 11, 14 и 15.
**Роль:** Ранее предложенные формулировки и отмеченные несогласованности. Не доказательство выполненных работ.
**Доступ:** исходный материал в переписке; отдельной копии в этом пакете нет.

## Основные десять референсов

<a id="s01"></a>
### [S01] Pathfinding.cloud
**Авторы / организация:** Seth Art / Datadog; проект Pathfinding.cloud.
**Год / версия:** Обновляемый веб-ресурс; просмотр 11.10.2026.
**Проверенные разделы:** About pathfinding.cloud; Getting Started / Prerequisites.
**Что обосновывает и чего не доказывает:** Источник AWS IAM-сценариев. Не основание для утверждения, что существует датасет утечек Git или готовый ML-детектор.
**Главная страница:** https://pathfinding.cloud/
**Labs: Getting Started:** https://pathfinding.cloud/labs/getting-started/

<a id="s02"></a>
### [S02] How Bad Can It Git? Characterizing Secret Leakage in Public GitHub Repositories
**Авторы / организация:** Michael Meli; Matthew R. McNiece; Bradley Reaves.
**Год / версия:** NDSS 2019.
**Проверенные разделы:** Abstract; I. Introduction; первая страница PDF сверена визуально.
**Что обосновывает и чего не доказывает:** Историческое эмпирическое исследование раскрытия секретов на GitHub. Его наблюдения не являются статистикой 2026 года.
**Страница публикации:** https://www.ndss-symposium.org/ndss-paper/how-bad-can-it-git-characterizing-secret-leakage-in-public-github-repositories/
**Полный текст PDF:** https://www.ndss-symposium.org/wp-content/uploads/2019/02/ndss2019_04B-3_Meli_paper.pdf

<a id="s03"></a>
### [S03] SecretBench: A Dataset of Software Secrets
**Авторы / организация:** Setu Kumar Basak; Lorenzo Neil; Bradley Reaves; Laurie Williams.
**Год / версия:** MSR 2023, Data and Tool Showcase Track; arXiv:2303.06729v1, 12.03.2023.
**Проверенные разделы:** II. Data Extraction, Steps 6–7; III-C. Data Storage; VI. Ethics; VII. Threats to Validity. README: How to Use; Ethics.
**Что обосновывает и чего не доказывает:** Кандидаты, ручная разметка, происхождение данных и условия доступа. Публичная статья не равна открытому доступу ко всем данным.
**Метаданные и аннотация:** https://arxiv.org/abs/2303.06729v1
**Полный текст HTML:** https://arxiv.org/html/2303.06729v1
**Репозиторий авторов:** https://github.com/setu1421/SecretBench

<a id="s04"></a>
### [S04] AssetHarvester: A Static Analysis Tool for Detecting Secret-Asset Pairs in Software Artifacts
**Авторы / организация:** Setu Kumar Basak; K. Virgil English; Ken Ogura; Vitesh Kambara; Bradley Reaves; Laurie Williams.
**Год / версия:** На arXiv указано принятие в ICSE 2025; использована версия arXiv:2403.19072v2 от 20.11.2024.
**Проверенные разделы:** Abstract; V. AssetHarvester; IX. Threats to Validity.
**Что обосновывает и чего не доказывает:** Статические связи между секретом и ресурсом; ограничения полноты эталонного набора. Это не результат нашей ML-модели.
**Метаданные и аннотация:** https://arxiv.org/abs/2403.19072v2
**Полный текст HTML:** https://arxiv.org/html/2403.19072v2

<a id="s05"></a>
### [S05] Detecting Hard-Coded Credentials in Software Repositories via LLMs
**Авторы / организация:** Chidera Biringa; Gokhan Kul.
**Год / версия:** arXiv:2506.13090v1 от 16.06.2025; на странице указано принятие в ACM Digital Threats: Research and Practice.
**Проверенные разделы:** 3. Approach, 3.1–3.2; 4. Evaluation; 5. Limitations.
**Что обосновывает и чего не доказывает:** Векторные представления credentials и классификатор. Выводы не доказывают эффективность TF-IDF или наших моделей; том, номер и страницы журнала не добавлялись.
**Метаданные и аннотация:** https://arxiv.org/abs/2506.13090v1
**Полный текст HTML:** https://arxiv.org/html/2506.13090v1

<a id="s06"></a>
### [S06] Secret Leak Detection in Software Issue Reports using LLMs: A Comprehensive Evaluation
**Авторы / организация:** Sadif Ahmed; Md Nafiu Rahman; Zahin Wahab; Gias Uddin; Rifat Shahriyar.
**Год / версия:** arXiv:2410.23657v4 от 16.04.2026; на странице указано принятие в MSR 2026.
**Проверенные разделы:** 3. Methodology; 5.2. Impact of Context Window Length; 6.3. Effectiveness of Model on Real World Repositories.
**Что обосновывает и чего не доказывает:** Работа про issue reports. В §6.3 тоже оцениваются issue reports из репозиториев, а не обход истории файлов.
**Метаданные и аннотация:** https://arxiv.org/abs/2410.23657v4
**Полный текст HTML:** https://arxiv.org/html/2410.23657v4

<a id="s07"></a>
### [S07] Gitleaks — README и документация
**Авторы / организация:** Gitleaks project.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** Warning в начале README; Usage; Commands / Git; Creating a baseline; Configuration.
**Что обосновывает и чего не доказывает:** Документированные возможности инструмента. Версия исполняемого файла не выбрана; запуск в рамках этого этапа не выполнялся.
**Официальный репозиторий:** https://github.com/gitleaks/gitleaks

<a id="s08"></a>
### [S08] TruffleHog — README и документация
**Авторы / организация:** Truffle Security.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** CLI help: no-verification, results, no-update; git source.
**Что обосновывает и чего не доказывает:** Различие обнаружения и верификации. Флаг отключения проверки не является доказательством отсутствия любых сетевых обращений.
**Официальный репозиторий:** https://github.com/trufflesecurity/trufflehog

<a id="s09"></a>
### [S09] detect-secrets — README и документация
**Авторы / организация:** Yelp; участники проекта.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** Введение; Examples / Quickstart; baseline; audit.
**Что обосновывает и чего не доказывает:** Проверка новых изменений и аудит кандидатов. Полный исторический обход нельзя приписывать инструменту по аналогии с Gitleaks.
**Официальный репозиторий:** https://github.com/Yelp/detect-secrets

<a id="s10"></a>
### [S10] GitHub Docs — Secret scanning
**Авторы / организация:** GitHub.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** How secret scanning protects your code; Pattern categories; Supported generic patterns; What are secrets.
**Что обосновывает и чего не доказывает:** Функциональные классы секретов, Git-история и отдельная функция validity checks. Документация сервиса не является независимой разметкой.
**Secret scanning:** https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning
**Supported secret scanning patterns:** https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns
**Secret leakage risks:** https://docs.github.com/en/code-security/concepts/secret-security/secret-leakage-risks

## Дополнительные первичные источники

CredData вынесен сюда: он указан в roadmap, но не был самостоятельным пунктом исходного ref.md. Остальные документы уточняют определения и протокол; это не дополнительные «найденные утечки».

<a id="a01"></a>
### [A01] CWE-798: Use of Hard-coded Credentials
**Авторы / организация:** MITRE CWE.
**Год / версия:** Обновляемая запись; просмотр 11.10.2026.
**Проверенные разделы:** Description; Extended Description; Detection Methods.
**Что обосновывает и чего не доказывает:** Термин hard-coded credentials. Не доказывает наличие эксплуатируемой уязвимости у каждого найденного кандидата.
**Определение слабости:** https://cwe.mitre.org/data/definitions/798.html

<a id="a02"></a>
### [A02] git-rev-list Documentation
**Авторы / организация:** Git project.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** DESCRIPTION; --all; --objects; EXAMPLES.
**Что обосновывает и чего не доказывает:** Достижимость коммитов и объектов из заданных ссылок. Не обещает восстановление удалённых недостижимых объектов сервера.
**Описание обхода истории:** https://git-scm.com/docs/git-rev-list

<a id="a03"></a>
### [A03] Metrics and scoring; precision_recall_fscore_support
**Авторы / организация:** scikit-learn developers.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** Precision, recall and F-measures; параметры average, pos_label, zero_division; Notes.
**Что обосновывает и чего не доказывает:** Определения метрик. Численные значения будущего дипломного эксперимента из документации не заимствуются.
**Метрики и формулы:** https://scikit-learn.org/stable/modules/model_evaluation.html
**Функция метрик и случаи деления на ноль:** https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html

<a id="a04"></a>
### [A04] Common pitfalls and recommended practices
**Авторы / организация:** scikit-learn developers.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** Data leakage; How to avoid data leakage.
**Что обосновывает и чего не доказывает:** Разделение данных до обучения преобразований; test не участвует в fit. Это утечка информации при обучении, не утечка credentials.
**Data leakage:** https://scikit-learn.org/stable/common_pitfalls.html#data-leakage

<a id="a05"></a>
### [A05] Cross-validation: evaluating estimator performance
**Авторы / организация:** scikit-learn developers.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** Cross-validation iterators for grouped data; Group K-fold.
**Что обосновывает и чего не доказывает:** Разделение связанных наблюдений по группам. Что считать семейством репозиториев и дубликатов, определяет наш протокол, а не библиотека.
**Групповая проверка:** https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data

<a id="a06"></a>
### [A06] CredData (Credential Dataset)
**Авторы / организация:** Samsung; участники проекта.
**Год / версия:** Обновляемый репозиторий; просмотр 11.10.2026.
**Проверенные разделы:** Ground Rules for Labeling Suspected Credential Information; Obfuscation; License.
**Что обосновывает и чего не доказывает:** Нужно сохранить исходные метки и учитывать преобразование значений. Лицензии исходных файлов проверяются отдельно.
**README и условия:** https://github.com/Samsung/CredData

<a id="a07"></a>
### [A07] API keys
**Авторы / организация:** Stripe.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** Protect your keys; Publishable keys; Restricted or secret API keys.
**Что обосновывает и чего не доказывает:** Различие publishable и секретных API-ключей. Нельзя объявлять любой API key конфиденциальным.
**Типы ключей и ограничения:** https://docs.stripe.com/keys

<a id="a08"></a>
### [A08] Learn about and manage API keys for Firebase
**Авторы / организация:** Firebase / Google.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** Обзор; Use separate, restricted API keys for any non-Firebase service.
**Что обосновывает и чего не доказывает:** Ключи для Firebase обычно не требуют секретности; для других Google Cloud API действуют дополнительные оговорки.
**Назначение ключей Firebase:** https://firebase.google.com/docs/projects/api-keys

<a id="a09"></a>
### [A09] Access keys и временные credentials AWS
**Авторы / организация:** Amazon Web Services.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** IAM: состав access key; STS Credentials: AccessKeyId, SecretAccessKey, SessionToken, Expiration.
**Что обосновывает и чего не доказывает:** Отличие идентификатора от секретного материала и состав временных credentials. Их действительность в проекте не проверяется.
**IAM access keys:** https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
**STS Credentials:** https://docs.aws.amazon.com/STS/latest/APIReference/API_Credentials.html

<a id="a10"></a>
### [A10] The OAuth 2.0 Authorization Framework: Bearer Token Usage
**Авторы / организация:** M. Jones; D. Hardt; IETF.
**Год / версия:** RFC 6750, октябрь 2012.
**Проверенные разделы:** Abstract; 1.2. Terminology; 2.1. Authorization Request Header Field.
**Что обосновывает и чего не доказывает:** Понятие bearer token. Детальное воспроизведение OAuth-протокола не входит в этап.
**Стандарт RFC 6750:** https://www.rfc-editor.org/rfc/rfc6750.html
**Полный текст в IETF Datatracker:** https://datatracker.ietf.org/doc/html/rfc6750

<a id="a11"></a>
### [A11] JSON Web Token (JWT)
**Авторы / организация:** M. Jones; J. Bradley; N. Sakimura; IETF.
**Год / версия:** RFC 7519, май 2015.
**Проверенные разделы:** 2. Terminology; 3. JWT Overview; 7.2. Validating a JWT.
**Что обосновывает и чего не доказывает:** JWT — формат claims в JWS/JWE; распознавание формата не равно доверенной проверке токена.
**Стандарт RFC 7519:** https://www.rfc-editor.org/rfc/rfc7519.html

<a id="a12"></a>
### [A12] Database Connection Control Functions
**Авторы / организация:** PostgreSQL Global Development Group.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** Connection URIs; Parameter Key Words: user, password, host, dbname.
**Что обосновывает и чего не доказывает:** Строка подключения может содержать пароль, но пароль не обязателен в каждом URI.
**Параметры и строки подключения:** https://www.postgresql.org/docs/current/libpq-connect.html

<a id="a13"></a>
### [A13] Settings: SECRET_KEY
**Авторы / организация:** Django Software Foundation; участники проекта.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** SECRET_KEY.
**Что обосновывает и чего не доказывает:** Секрет приложения для криптографической подписи; подтверждённый пример категории Other high-entropy secrets.
**Назначение SECRET_KEY:** https://docs.djangoproject.com/en/stable/ref/settings/#secret-key

<a id="a14"></a>
### [A14] Key Serialization
**Авторы / организация:** pyca/cryptography contributors.
**Год / версия:** Обновляемая документация; просмотр 11.10.2026.
**Проверенные разделы:** PEM; OpenSSH; загрузка private/public keys.
**Что обосновывает и чего не доказывает:** Различие форматов закрытых и открытых ключей. Успешный разбор не подтверждает использование ключа в каком-либо сервисе.
**Сериализация ключей:** https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/

## Как использовать ссылки в тексте диплома

Ссылки [Sxx] в рабочих файлах ведут к записи реестра. Для диплома переносите автора, название, год/версию и адрес, затем оформляйте по требованиям кафедры. Эти требования команде ещё предстоит предоставить; неизвестные DOI, номера выпусков, страницы или даты доступа не добавлены.

Научные результаты авторов описаны как результаты их работ. Выводы для нашего проекта отдельно названы применением или предложением. Просмотр документации не подтверждает работоспособность команды запуска в вашей среде.

## Контроль исходных файлов

SHA-256 позволяет проверить, что использованы именно доступные в этой переписке версии. Это контроль файлов, не проверка научной достоверности их содержимого.

`roadmap 1.pdf`
`71f7d8b38a6c40291ffd0922886d4871108475709f54658dae70c9d46c6c20c0`

`ref.md`
`11a9e2f0b5327f2fb4a707856b9a3a7733e8268fb894cca4c2e596fb80067591`

`examples_leaks.md`
`60cea12e966ff93e36c5d671f66f6c524926597edddbadb967704195e65f2512`

`req.md`
`655b2e572c55f6b521c23d5b2b0e4f13e64f998989458c5556b7fae1f55f2f69`

`read.me`
`bc6835481dc17d020b150846b86feb89f3a97f7323e4a8770302f76ecd2a3d7e`
