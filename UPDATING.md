# Обновление и выпуск ProjectStatusReport

Используйте текущую версию из `portable-skills/project-status-report/release.json`.

```powershell
cd D:\ProjectStatusReport
git switch main
git pull --ff-only origin main
git status

python -m pip install -r requirements.txt
python -m pip install -e .
python -m unittest discover -s tests
python scripts/build_portable_skill.py

git diff --check
git status
git diff
```

После проверки:

```powershell
git add -A
git commit -m "Release vX.Y.Z: <description>"
git push origin main

git tag -a vX.Y.Z -m "ProjectStatusReport vX.Y.Z"
git push origin vX.Y.Z

gh release create vX.Y.Z `
  release\project-status-report-X.Y.Z.zip `
  release\project-status-report-X.Y.Z.zip.sha256 `
  --title "ProjectStatusReport vX.Y.Z" `
  --notes-file docs\releases\vX.Y.Z.md
```

Commit + tag do not create GitHub Release automatically.
