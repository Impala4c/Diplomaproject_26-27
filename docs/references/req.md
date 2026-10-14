# Инструменты и требования по категориям

**Период:** октябрь — декабрь 2026. **Команда:** 3 человека. Документация проверена 03.10.2026.

**Основной стек:** Python + Git CLI + Gitleaks + TruffleHog + pandas / NumPy + scikit-learn + pytest. Основная модель работает локально. Платный API, GPU и развёртывание AWS для декабрьского прототипа не требуются.

## 1. Среда разработки и зависимости

| Инструмент | Для чего используем | Источник |
|---|---|---|
| Python | Сканер, обработка данных, ML и отчёты. Начальная целевая версия — 3.12; совместимость выбранных пакетов подтверждаем пилотным запуском. | https://www.python.org/ |
| Git CLI | Получение публичных репозиториев и чтение истории объектов. | https://git-scm.com/docs |
| uv | Изолированная среда и воспроизводимый lock-файл зависимостей. | https://docs.astral.sh/uv/ |
| Git-репозиторий команды | Код, конфигурации, тесты и история изменений дипломного проекта; без чужих секретов и сырых чувствительных данных. | https://git-scm.com/docs |

Использовать Linux либо WSL2; весь конвейер должен запускаться командной строкой. Окончательные версии записать в `uv.lock` и журнал окружения после smoke-test, а не объявлять совместимыми заранее. Версии бинарных сканеров и их конфигурации фиксировать отдельно.

## 2. Получение и анализ Git-истории

| Инструмент | Задача | Источник |
|---|---|---|
| Git CLI: clone / fetch | Получить разрешённые публичные refs; не использовать shallow-историю для основного эксперимента. | https://git-scm.com/docs/git-clone |
| Git CLI: rev-list | Обойти коммиты, достижимые из полученных refs; не ограничиваться HEAD основной ветки. | https://git-scm.com/docs/git-rev-list |
| Git CLI: ls-tree / cat-file | Читать версии файлов и многострочные объекты без выполнения кода целевого проекта. | https://git-scm.com/docs/git-ls-tree ; https://git-scm.com/docs/git-cat-file |
| Python subprocess / pathlib | Управлять Git-процессами, тайм-аутами и локальными путями. Передавать аргументы списком, без shell=True. | https://docs.python.org/3/library/subprocess.html |

Сканировать уникальные blob-объекты, сохраняя связь с commit/path. Учитывать начальный коммит, переименования, ветки, merge и последующее удаление файла. Фиксировать пропуски из-за размера, кодировки, бинарного формата, LFS или отсутствующих submodules. GitPython / PyDriller не обязательны: для MVP достаточно Git CLI и Python.

## 3. Извлечение кандидатов и baseline

| Инструмент / метод | Роль | Источник |
|---|---|---|
| Python re + math + collections | Собственные шаблоны, длина, состав символов, энтропия и признаки контекста. | https://docs.python.org/3/library/re.html |
| Gitleaks | Основной внешний baseline по Git-истории. | https://github.com/gitleaks/gitleaks |
| TruffleHog | Второй внешний baseline; отключить сетевую проверку credentials и фиксировать параметры запуска. | https://github.com/trufflesecurity/trufflehog |
| detect-secrets | Дополнительное сравнение снимков; полная история требует отдельной обвязки. | https://github.com/Yelp/detect-secrets |

Собственный baseline: regex + энтропия + контекстные признаки без ML. Оценить извлечение кандидатов отдельно: классификатор не сможет вернуть секрет, который не был извлечён. Сопоставлять инструменты на одинаковом охвате истории и одинаковой единице учёта находок.

## 4. Инструменты для девяти категорий секретов

| Категория | Что используем в собственном методе | Важное ограничение |
|---|---|---|
| API keys | Провайдерские regex, имя переменной, окружающий код; затем ML-фильтр. | Публичный API identifier не равен секретному API key. |
| Access tokens | Regex и анализ полей токенов, заголовков, CI-конфигураций. | Не определять действительность или права токена по одному префиксу. |
| AWS credentials | Regex + связывание соседних полей ID / secret / session; INI / JSON / YAML. | Access Key ID отдельно не заменяет секретный ключ. |
| Private keys | Многострочное извлечение, маркеры PEM/OpenSSH; cryptography для локальной проверки поддерживаемых форматов. | Поддержку PGP и других форматов отмечать отдельно; один парсер не покрывает всё. |
| Database credentials | Контекст полей password/user/host; configparser, json, PyYAML. | Не помечать одно имя пользователя как утечку пароля. |
| Passwords | Ключевые слова, контекст присваивания и ML; не только энтропия. | Слабые и короткие пароли также могут быть секретами. |
| Connection strings | urllib.parse, разбор параметров и контекст DB URL. | URL без credentials не считать положительным по умолчанию. |
| JWT / authentication tokens | Ограниченный разбор структуры и Base64url; PyJWT для локальных JWS-fixtures. | Декодирование без проверки подписи не подтверждает подлинность; JWE выделить отдельно. |
| Other high-entropy secrets | math / collections + контекст назначения + ML. | Хеши, UUID и кодированные файлы могут иметь высокую энтропию без секрета. |

Документация: [поддерживаемые типы GitHub](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns), [cryptography](https://cryptography.io/en/latest/), [PyJWT](https://pyjwt.readthedocs.io/en/stable/), [urllib.parse](https://docs.python.org/3/library/urllib.parse.html), [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation).

Парсить недоверенные файлы с ограничением размера и времени; для YAML использовать безопасную загрузку. Не импортировать и не выполнять анализируемый Python/JavaScript-код.

## 5. Данные, разметка и хранение

| Инструмент / формат | Задача | Источник |
|---|---|---|
| pandas / NumPy | Таблицы кандидатов, признаки, статистика классов и объединение разметки. | https://pandas.pydata.org/docs/ ; https://numpy.org/doc/ |
| JSONL / CSV + SQLite | Локальное хранение метаданных, результатов и связей commit/file/finding. | https://docs.python.org/3/library/sqlite3.html |
| Python hmac / hashlib | HMAC-отпечатки для дедупликации без открытого сохранения значения в отчётах. Ключ HMAC хранить отдельно. | https://docs.python.org/3/library/hmac.html |
| CSV-форма разметки | Два независимых разметчика; третий участник разрешает расхождения. | Собственный протокол команды. |

Сохранять `repo_id`, `family_id`, `commit_sha`, `path`, диапазон строк, категорию, признаки, метку, происхождение и маскированный контекст. Полные значения и окружающий текст при необходимости остаются в ограниченном локальном хранилище, не в публичном Git. Простой хеш слабого пароля не использовать как надёжную анонимизацию.

Разделить train / validation / test по группам репозиториев и дубликатов до обучения. Не использовать `repo_id`, имя автора или готовую метку baseline как замену независимым признакам. `UNCERTAIN` разрешать вручную либо учитывать отдельно, не превращая молча в отрицательный класс.

## 6. Машинное обучение

| Инструмент / модель | Как используем | Источник |
|---|---|---|
| scikit-learn: LogisticRegression | Первая модель: числовые признаки и ограниченное TF-IDF-представление контекста. | https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression |
| scikit-learn: RandomForestClassifier | Второй кандидат на компактных числовых и контекстных признаках. | https://scikit-learn.org/stable/modules/ensemble.html#forest |
| TfidfVectorizer / ColumnTransformer / Pipeline | Преобразования обучаются только на train; единый путь обработки новых данных. | https://scikit-learn.org/stable/modules/compose.html |
| GroupShuffleSplit / GroupKFold | Разделение и кросс-валидация с учётом родственных репозиториев и дубликатов. | https://scikit-learn.org/stable/modules/cross_validation.html |
| joblib | Сохранение собственной модели и pipeline; не загружать чужие недоверенные pickle/joblib-файлы. | https://joblib.readthedocs.io/ |

Проверяем гипотезу: контекст уменьшает ложные срабатывания при сопоставимом recall. Это ожидаемый эффект, а не заранее известный результат. Порог и гиперпараметры выбирать на validation; test открыть после фиксации решения. Выход модели называть `model_score`; не выдавать его за откалиброванную вероятность действующей утечки.

## 7. Лабораторные сценарии и тесты

| Инструмент | Задача | Источник |
|---|---|---|
| Pathfinding.cloud | Основная методология выбора AWS-сценариев и описания контекста credentials. | https://pathfinding.cloud/ ; https://pathfinding.cloud/labs/getting-started/ |
| Собственные Git-fixtures | Добавление/удаление, начальный коммит, ветки, merge, переименование, повтор и многострочные ключи. | Сценарии перечислены в repo.md. |
| cryptography / PyJWT | Самостоятельно созданные локальные ключи и токены, нигде не используемые для реального доступа. | https://cryptography.io/en/latest/ ; https://pyjwt.readthedocs.io/en/stable/ |
| pytest | Автоматическая проверка извлечения и ожидаемых находок. | https://docs.pytest.org/en/stable/ |
| Ruff / pre-commit | Ruff проверяет собственный код; pre-commit запускает настроенный Gitleaks-hook перед коммитом. | https://docs.astral.sh/ruff/ ; https://pre-commit.com/ |

Облачные лаборатории не запускаем автоматически. Корректность истории проверяем на искусственных данных, качество переноса модели — отдельно на независимом размеченном наборе. Строки с `<SYNTHETIC_...>` из examples_leaks.md являются иллюстрациями, а не готовыми положительными обучающими примерами.

## 8. Эксперименты и отчёты

| Инструмент | Результат | Источник |
|---|---|---|
| sklearn.metrics | Precision, recall, F1, confusion matrix, FPR и результаты по категориям. | https://scikit-learn.org/stable/modules/model_evaluation.html |
| matplotlib | Сравнительные графики и матрица ошибок. | https://matplotlib.org/stable/ |
| time.perf_counter | Время сканирования при одинаковых ограничениях и окружении. | https://docs.python.org/3/library/time.html#time.perf_counter |
| CSV / JSON / Markdown | Машиночитаемый отчёт, сводка эксперимента и инструкция повторного запуска. | Форматы собственных артефактов проекта. |

Отдельно показывать полноту извлечения кандидатов и end-to-end результат; находки в HEAD и только в истории; уникальные секреты и количество появлений. Для неизвестного ground truth не заявлять полный recall. Сохранять версии, random seed, состав test set и реально измеренные результаты — без заранее придуманных процентов.

## 9. Распределение между участниками

| Участник | Основные инструменты и результат |
|---|---|
| 1 — Git / Data | Git CLI, subprocess, pandas, SQLite: коллектор истории, manifest, датасет и разметка. |
| 2 — Detection / AI | re, NumPy, scikit-learn, Gitleaks, TruffleHog: извлечение, baseline, признаки и модель. |
| 3 — System / Evaluation | Pathfinding.cloud, pytest, Ruff, matplotlib: сценарии, интеграция, независимые тесты и отчёты. |

Все участвуют в разметке, проверке результатов и написании диплома; третий участник отвечает не только за оформление.

## 10. Минимальный перечень Python-пакетов

```text
numpy
pandas
scikit-learn
matplotlib
joblib
PyYAML
cryptography
PyJWT
pytest
ruff
pre-commit
```

Это перечень зависимостей, не готовый зафиксированный `requirements.txt`. Git, Gitleaks, TruffleHog и uv устанавливаются отдельно. `subprocess`, `pathlib`, `re`, `math`, `collections`, `json`, `csv`, `sqlite3`, `hmac`, `hashlib`, `configparser`, `urllib.parse`, `time` входят в стандартную библиотеку Python.

**За пределами обязательного MVP:** GPU/LLM, XGBoost/LightGBM, веб-интерфейс, Docker-развёртывание лабораторий, облачный AWS-стенд и коммерческие SaaS-сканеры. Добавлять только после воспроизводимого результата основного конвейера.
