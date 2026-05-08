# EcoSat Monitor - GitHub Quick Start

Status: ready for first GitHub push after local verification.

## 1. Create an Empty GitHub Repository

Go to https://github.com/new and create a repository.

Recommended settings:

```text
Repository name: ecosat-monitor
Visibility: Public or Private
Initialize with README: No
Add .gitignore: No
Add license: Optional
```

## 2. Push This Project

From this folder:

```powershell
cd "C:\Users\DELL\OneDrive\Desktop\Tatvagreens"
python github-setup.py
```

Or manually:

```powershell
git init
git add .
git commit -m "Initial commit: EcoSat Monitor"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ecosat-monitor.git
git push -u origin main
```

Note: `.env`, `node_modules`, build output, and local data are ignored by `.gitignore`.

## 3. GitHub Pages Frontend

The workflow at `.github/workflows/deploy.yml` builds `frontend/` and publishes `frontend/dist` to the `gh-pages` branch.

After the first push:

1. Open your GitHub repository.
2. Go to `Settings -> Pages`.
3. Select `Deploy from a branch`.
4. Choose branch `gh-pages` and folder `/root`.
5. Save.

Frontend URL:

```text
https://YOUR_USERNAME.github.io/ecosat-monitor/
```

## 4. Render Backend

Follow `RENDER-DEPLOY.md`.

Important Render backend settings:

```text
Service type: Web Service
Environment: Docker
Root directory: backend
Dockerfile path: backend/Dockerfile, if Render asks from repo root
Health check path: /api/v1/health
```

Environment variables:

```text
DATABASE_URL=your_render_postgres_url
REDIS_URL=your_render_redis_url
DEBUG=false
CORS_ORIGINS=["https://YOUR_USERNAME.github.io","https://YOUR_USERNAME.github.io/ecosat-monitor"]
GEE_PROJECT_ID=your_project_id_optional
GEE_SERVICE_ACCOUNT_JSON=your_service_account_json_optional
```

Backend URL example:

```text
https://ecosat-monitor-api.onrender.com
```

## 5. Connect Frontend to Backend

For GitHub Actions, add this repository secret:

```text
VITE_API_BASE_URL=https://ecosat-monitor-api.onrender.com
```

If you use Render Static Site instead of GitHub Pages, add the same value as a Render frontend environment variable.

## 6. Verify

Check:

```text
https://ecosat-monitor-api.onrender.com/api/v1/health
https://ecosat-monitor-api.onrender.com/api/v1/docs
https://YOUR_USERNAME.github.io/ecosat-monitor/
```

If GitHub Actions fails, open the `Actions` tab and check the failing step.
