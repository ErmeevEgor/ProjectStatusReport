# Обновление и выпуск ProjectStatusReport

Эта инструкция актуальна для **v0.9.0+**, где portable skill ориентирован на Web LLM + Google Drive + Confluence Storage Format.

## 1. Что представляет собой update archive

Архив обновления — это **overlay корня репозитория**, а не отдельный Git-репозиторий.

Его не нужно коммитить как `.zip`.

Правильный процесс:

1. клонировать/обновить репозиторий;
2. распаковать содержимое overlay-архива **поверх корня репозитория** с заменой файлов;
3. удалить перечисленные legacy-файлы portable skill;
4. проверить `git diff`;
5. сделать commit и push;
6. при выпуске релиза — собрать portable archive, поставить tag и создать GitHub Release.

## 2. Применение overlay в PowerShell

Пример, если репозиторий находится в `D:\ProjectStatusReport`, а архив скачан в `Downloads`.

```powershell
cd D:\ProjectStatusReport

git switch main
git pull --ff-only origin main
git status
```

Рабочее дерево перед обновлением должно быть чистым.

Распакуйте overlay во временную папку:

```powershell
$zip = "$HOME\Downloads\ProjectStatusReport_v0.9.0_repo_overlay.zip"
$tmp = "$env:TEMP\ProjectStatusReport_v0.9.0"

Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive -Path $zip -DestinationPath $tmp -Force
```

Скопируйте содержимое поверх репозитория:

```powershell
Copy-Item "$tmp\*" "D:\ProjectStatusReport" -Recurse -Force
```

## 3. Удаление legacy portable-skill файлов

Начиная с v0.9.0 portable release больше не должен содержать DOCX/runtime ветку.

Удалите из `portable-skills/project-status-report`:

```powershell
Remove-Item .\portable-skills\project-status-report\runtime -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\portable-skills\project-status-report\scripts -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\portable-skills\project-status-report\references\report-structure.md -Force -ErrorAction SilentlyContinue
Remove-Item .\portable-skills\project-status-report\references\confluence.md -Force -ErrorAction SilentlyContinue
```

Корневой `src/`, `tests/` и другие legacy runtime-файлы пока можно сохранить в репозитории для истории/совместимости. Новый `scripts/build_portable_skill.py` их в portable release не добавляет.

## 4. Проверка изменений

```powershell
git status
git diff --check
git diff
```

Проверьте минимум:

- `README.md` описывает только канонический web workflow;
- `SKILL.md` не предлагает DOCX fallback;
- `USER_GUIDE.md` соответствует Google Drive + XML workflow;
- `release.json` содержит `0.9.0`;
- `agents/openai.yaml` не упоминает DOCX;
- `prompts/REPORT_GENERATION_PROMPT.md` не переключает output mode;
- удалены legacy portable `runtime/`, `scripts/`, `report-structure.md`, `confluence.md`.

Быстрый поиск старых формулировок:

```powershell
git grep -n -E "working\.docx|clean\.docx|4 A4|четырехстранич|DOCX mode|fallback DOCX" -- README.md UPDATING.md portable-skills/project-status-report
```

Совпадений в активной документации быть не должно, кроме явно обозначенного исторического/legacy контекста.

## 5. Commit и push

```powershell
git add -A
git status
git commit -m "Release v0.9.0: web Drive and Confluence Storage workflow"
git push origin main
```

Проверить последний commit:

```powershell
git log -1 --oneline
```

## 6. Сборка portable release archive

Новый builder архивирует portable skill как есть и не синхронизирует туда legacy Python runtime.

```powershell
python scripts\build_portable_skill.py
```

Ожидаемые файлы:

```text
release\project-status-report-0.9.0.zip
release\project-status-report-0.9.0.zip.sha256
```

Проверить содержимое:

```powershell
python -c "import zipfile; z=zipfile.ZipFile(r'release\project-status-report-0.9.0.zip'); print('\n'.join(z.namelist()))"
```

В архиве не должно быть `runtime/` и portable `scripts/`.

## 7. Tag и GitHub Release

После успешного push:

```powershell
git tag -a v0.9.0 -m "ProjectStatusReport v0.9.0"
git push origin v0.9.0
```

Если установлен GitHub CLI (`gh`):

```powershell
gh release create v0.9.0 `
  release\project-status-report-0.9.0.zip `
  release\project-status-report-0.9.0.zip.sha256 `
  --title "ProjectStatusReport v0.9.0" `
  --notes-file docs\releases\v0.9.0.md
```

Commit и tag сами по себе GitHub Release не создают.

## 8. Если хотите сделать через GitHub Web без Git CLI

Можно загрузить изменённые файлы вручную через веб-интерфейс, но для удаления старых каталогов и контроля diff это менее удобно.

Для v0.9.0 рекомендуемый вариант — локальный `git clone` + overlay + `git add -A` + `git commit` + `git push`.
