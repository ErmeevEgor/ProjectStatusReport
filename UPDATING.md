# Обновление ProjectStatusReport из консоли

Эта инструкция используется для применения подготовленного update bundle, проверки проекта, коммита и выпуска GitHub Release.

## 1. Требования

Нужно установить:
- Git;
- Python 3.11+;
- GitHub CLI (`gh`) — только для создания Release из консоли.

Проверка:

```bash
git --version
python --version
gh --version
```

Для выпуска релиза авторизуйтесь один раз:

```bash
gh auth login
```

## 2. Обновить локальный репозиторий

```bash
cd /path/to/ProjectStatusReport
git status
git switch main
git pull --ff-only origin main
```

`git status` должен быть чистым. Если есть локальные изменения, сначала закоммитьте их или уберите в stash.

## 3. Наложить bundle v0.7.0

Распакуйте `ProjectStatusReport-v0.7.0-update.zip` во временную папку и скопируйте содержимое `repository-overlay` в корень репозитория.

### PowerShell

```powershell
$Repo = "C:\Work\ProjectStatusReport"
$Bundle = "C:\Temp\ProjectStatusReport-v0.7.0-update.zip"
$Tmp = Join-Path $env:TEMP "psr-v070"

Remove-Item $Tmp -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive -Path $Bundle -DestinationPath $Tmp -Force
Copy-Item "$Tmp\repository-overlay\*" $Repo -Recurse -Force
Set-Location $Repo
```

### Bash / Git Bash

```bash
REPO=/path/to/ProjectStatusReport
BUNDLE=/path/to/ProjectStatusReport-v0.7.0-update.zip
TMP=$(mktemp -d)
unzip "$BUNDLE" -d "$TMP"
cp -R "$TMP/repository-overlay/." "$REPO/"
cd "$REPO"
```

## 4. Проверить, что версии синхронизированы

Должно быть `0.7.0` в:
- `pyproject.toml`;
- `src/project_status_report/__init__.py`;
- `portable-skills/project-status-report/release.json`.

## 5. Установить зависимости и запустить тесты

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python -m unittest discover -s tests
```

Затем smoke-test генерации:

```bash
python -m project_status_report.cli examples/sample-report-data.json --out output --name sample-v070
```

Проверьте, что в странице 2 fallback DOCX есть отдельные колонки:
`Код задачи`, `Наименование`, `Задача`, `План начала`, `План завершения`.

## 6. Собрать portable skill

```bash
python scripts/build_portable_skill.py
```

Скрипт синхронизирует `src/project_status_report/*.py` в portable runtime и создаст:
- `release/project-status-report-0.7.0.zip`;
- `release/project-status-report-0.7.0.zip.sha256`.

После сборки снова запустите тесты:

```bash
python -m unittest discover -s tests
```

## 7. Проверить diff

```bash
git status --short
git diff --check
git diff
```

Ожидаемые смысловые изменения v0.7.0:
- previous-first structural continuity в `SKILL.md`;
- fallback таблица задач с отдельными `Код задачи / Наименование / Задача`;
- отдельные `План начала / План завершения`;
- обновленные `README.md`, `USER_GUIDE.md`, internal prompt и `report-structure.md`;
- версия 0.7.0;
- новый тест layout v0.7.

## 8. Коммит и push

```bash
git add -A
git commit -m "Release v0.7.0: preserve previous OSP structure"
git push origin main
```

## 9. Создать тег

```bash
git tag -a v0.7.0 -m "ProjectStatusReport v0.7.0"
git push origin v0.7.0
```

Если тег уже существует, не перезаписывайте его молча. Сначала проверьте:

```bash
git tag --list v0.7.0
git ls-remote --tags origin v0.7.0
```

## 10. Выпустить GitHub Release

```bash
gh release create v0.7.0 \
  release/project-status-report-0.7.0.zip \
  release/project-status-report-0.7.0.zip.sha256 \
  --title "ProjectStatusReport v0.7.0" \
  --notes-file docs/releases/v0.7.0.md
```

Проверка:

```bash
gh release view v0.7.0
```

## 11. Если `gh` не используется

После `git push` и `git push origin v0.7.0` можно открыть GitHub → Releases → Draft a new release, выбрать тег `v0.7.0`, вставить текст из `docs/releases/v0.7.0.md` и приложить два файла из `release/`.

## Что не хранить в репозитории

Не коммитьте реальные договоры, переписки, клиентские ОСП и внешнее состояние конкретных проектов (`report-data.json`, `sources.json`, `source-manifest.json`). Они должны находиться вне репозитория.
