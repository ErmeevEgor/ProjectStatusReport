# Project Status Report

`ProjectStatusReport` — переносимый LLM-скилл для подготовки и последовательного обновления **Отчёта о состоянии проекта (ОСП)**.

Начиная с **v0.9.0**, канонический сценарий один: **веб-нейросеть (например, ChatGPT) + Google Drive + предыдущий Confluence Storage Format XML**.

Скилл читает проектные материалы, постоянное состояние проекта и предыдущий ОСП, актуализирует факты без выдумывания данных, пересчитывает прогресс/риски/оплаты, обновляет state-файлы в Google Drive и возвращает новый Storage Format XML для ручной вставки в Confluence.

## Канонический workflow v0.9.0

### Вход

Пользователь передаёт:

1. ссылку на папку проекта в Google Drive;
2. проектные файлы и контекст в этой папке;
3. дополнительные файлы и ссылки с изменениями проекта, если они находятся вне папки;
4. `report-data.json` и `sources.json` в папке проекта, если состояние уже существует;
5. предыдущий ОСП в **Confluence Storage Format XML/XHTML**.

Предыдущий Storage Format — обязательный структурный шаблон обычного повторного запуска.

### Выход

В ту же папку Google Drive:

- обновлённый `report-data.json`;
- обновлённый `sources.json`.

В ответ пользователю:

- `ОСП_<N>_Confluence_Storage_Format.xml`.

XML предназначен для ручной вставки в Confluence Source Editor и **по умолчанию не загружается в Google Drive**.

## Что больше не является основным сценарием

В v0.9.0 portable skill не использует:

- DOCX как выход или промежуточный формат;
- working/clean DOCX;
- правило «ровно четыре страницы»;
- `source-manifest.json` в веб-сценарии;
- автоматическую публикацию в Confluence;
- локального агента как отдельную основную ветку.

Старый Python runtime может временно оставаться в репозитории для совместимости/истории, но он не является частью канонического portable-skill workflow v0.9.0 и не включается в portable release archive.

## Основные принципы

### Previous-first

Предыдущий Storage Format используется одновременно как:

- источник номера и даты предыдущего ОСП;
- continuity для незакрытых рисков, вопросов и действий;
- структурный шаблон следующей страницы;
- источник существующих Confluence macros и Handy Status IDs.

Структура не проектируется заново без необходимости.

### Long-lived state

`report-data.json` и `sources.json` — **постоянное состояние проекта**, а не одноразовые артефакты запуска.

Если файлы уже существуют в целевой папке Drive, они обновляются **на месте по Drive file ID**, без создания `report-data (1).json` и подобных дублей.

Если запись в Drive не удалась, LLM не должна утверждать обратное: обновлённые JSON возвращаются пользователю как fallback-файлы.

### Confluence-native output

Storage Format формируется напрямую, без DOCX-конвертации.

Dedicated dates сохраняются нативно:

```xml
<time datetime="2026-10-07" />
```

Handy Status numeric IDs не придумываются. Можно использовать только ID, обнаруженные в предыдущем XML и безопасно сопоставленные нужному semantic domain/status.

### Статусы работ

Видимая модель строго из четырёх статусов:

| Статус | Коэффициент |
|---|---:|
| Не начато | 0% |
| В работе | 50% |
| На согласовании | 90% |
| Выполнено | 100% |

Прогресс считается по договорному бюджету без parent/child double count.

Платежные и риск-статусы — отдельные модели.

## Структура portable skill

```text
portable-skills/project-status-report/
├── SKILL.md
├── USER_GUIDE.md
├── release.json
├── agents/
│   └── openai.yaml
├── prompts/
│   └── REPORT_GENERATION_PROMPT.md
├── references/
│   ├── web-workflow.md
│   ├── confluence-storage-format.md
│   ├── external-state.md
│   ├── source-priority.md
│   ├── progress-calculation.md
│   ├── risk-identification.md
│   ├── status-rules.md
│   └── traceability.md
└── schema/
    └── report-data.schema.json
```

## Рекомендуемый пользовательский запрос

```text
Используй актуальный скилл project-status-report из репозитория
https://github.com/ErmeevEgor/ProjectStatusReport.

Сформируй актуальный ОСП.

Папка проекта в Google Drive:
<ССЫЛКА_НА_ПАПКУ>

В папке находятся проектные материалы, report-data.json и sources.json.
Дополнительные изменения проекта могут быть приложены к сообщению или указаны ссылками.

Предыдущий ОСП приложен в Confluence Storage Format XML.
Используй его как основной структурный шаблон следующего ОСП.
Сохрани таблицы, колонки, группировку, макросы, native dates и Handy Status.
Не используй DOCX.

На выходе:
1. обнови report-data.json в той же папке Google Drive;
2. обнови sources.json в той же папке Google Drive;
3. верни в чат файл ОСП_<номер>_Confluence_Storage_Format.xml для ручной вставки в Confluence.

Сам XML в Google Drive не загружай.
```

Подробности: [`portable-skills/project-status-report/USER_GUIDE.md`](portable-skills/project-status-report/USER_GUIDE.md).

## Выпуск новой версии

Инструкция по применению overlay-архива, commit/push/tag/release: [`UPDATING.md`](UPDATING.md).
