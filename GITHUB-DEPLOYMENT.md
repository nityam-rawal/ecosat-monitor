# GitHub Deployment Guide for EcoSat Monitor

## 🚀 Quick GitHub Deployment (3 Steps)

### Step 1: Push to GitHub

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: EcoSat Monitor"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/ecosat-monitor.git
git branch -M main
git push -u origin main
```

### Step 2: Enable GitHub Pages (Frontend Auto-Deploy)
1. Go to **Repository Settings** → **Pages**
2. Select **Deploy from a branch**
3. Choose `gh-pages` branch → save
4. Frontend deploys automatically to `https://YOUR_USERNAME.github.io/ecosat-monitor`

### Step 3: Deploy Backend (Free Options)

Choose one of these free deployment services:

#### **Option A: Render.com (Recommended - Easiest)**

```bash
# 1. Sign up at https://render.com (use GitHub login)
# 2. Click "New +" → "Web Service"
# 3. Connect your GitHub repository
# 4. Configure:
#    - Name: ecosat-monitor-backend
#    - Environment: Docker
#    - Build Command: (leave default)
#    - Start Command: (leave default)
#    - Plan: Free
# 5. Add Environment Variables:
#    - DATABASE_URL: (use Render PostgreSQL)
#    - REDIS_URL: (use Render Redis)
#    - GEE_PROJECT_ID, GEE_SERVICE_ACCOUNT_JSON, etc.
# 6. Deploy!
```

**Benefits:**
- Auto-deploys on push to `main`
- Free PostgreSQL + Redis included
- Custom domain available
- Health checks included

#### **Option B: Railway.app**

```bash
# 1. Sign up at https://railway.app (GitHub login)
# 2. Click "New Project" → "Deploy from GitHub repo"
# 3. Select ecosat-monitor
# 4. Add services:
#    - PostgreSQL
#    - Redis
#    - Backend (Dockerfile)
# 5. Set environment variables
# 6. Connect frontend API to Railway URL
```

#### **Option C: Replit (Fastest)**

```bash
# 1. Go to https://replit.com/new
# 2. Select "Import from GitHub"
# 3. Paste: https://github.com/YOUR_USERNAME/ecosat-monitor
# 4. Click "Import"
# 5. It auto-detects backend and deploys instantly!
```

---

## 📊 Deployment Architecture

```
GitHub Repository
    ↓
    ├─→ GitHub Actions (CI/CD)
    │   ├─ Run tests
    │   ├─ Build containers
    │   └─ Deploy jobs
    │
    ├─→ Frontend: GitHub Pages
    │   └─ https://username.github.io/ecosat-monitor
    │
    └─→ Backend: Render/Railway/Replit
        └─ https://ecosat-monitor-backend.onrender.com
```

---

## 🔐 Environment Variables for GitHub

### 1. **Add Secrets to GitHub**

Go to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these:
```
GEE_SERVICE_ACCOUNT_JSON    → Your GEE service account JSON
NASA_EARTHDATA_USER         → (optional)
NASA_EARTHDATA_PASS         → (optional)
RENDER_DEPLOY_HOOK          → (optional, for auto-deploy)
```

### 2. **Use Secrets in Workflow**

```yaml
- name: Deploy
  env:
    GEE_SERVICE_ACCOUNT_JSON: ${{ secrets.GEE_SERVICE_ACCOUNT_JSON }}
  run: ./deploy.sh
```

---

## 🌐 Full Stack Deployment URLs

After deployment, you'll have:

| Service | URL |
|---------|-----|
| **Frontend** | `https://username.github.io/ecosat-monitor` |
| **Backend API** | `https://ecosat-monitor-backend.onrender.com` |
| **API Docs** | `https://ecosat-monitor-backend.onrender.com/api/v1/docs` |
| **Database** | Managed by Render/Railway |
| **Redis** | Managed by Render/Railway |

---

## 🔄 Continuous Deployment Workflow

Every time you push to `main`:

1. **GitHub Actions triggers**
   - Runs tests
   - Lints code
   - Builds Docker images
   - Pushes to registry (optional)

2. **Frontend auto-deploys to GitHub Pages**
   - Built automatically
   - Live in 2-3 minutes

3. **Backend auto-deploys to Render/Railway**
   - Detects changes
   - Rebuilds container
   - Redeploys with zero downtime
   - Live in 5-10 minutes

---

## ✅ Deployment Checklist

- [ ] Created GitHub repository
- [ ] Pushed code to main branch
- [ ] Enabled GitHub Pages
- [ ] Signed up to Render/Railway/Replit
- [ ] Connected backend service
- [ ] Added environment variables
- [ ] Set GEE credentials
- [ ] Updated frontend API URL (production domain)
- [ ] Tested health endpoint
- [ ] Verified frontend loads
- [ ] Created first AOI
- [ ] Checked alerts dashboard

---

## 🔗 Production Frontend Configuration

Update your backend URL in `frontend/vite.config.ts`:

```typescript
// For production
const API_BASE_URL = process.env.VITE_API_BASE_URL || 
  'https://ecosat-monitor-backend.onrender.com'
```

Or set environment variable during build:
```bash
VITE_API_BASE_URL=https://ecosat-monitor-backend.onrender.com npm run build
```

---

## 📈 Monitor Deployments

### GitHub Actions Dashboard
- Repository → Actions tab
- See all workflow runs
- Check logs for errors
- View deployment history

### Render/Railway Dashboard
- Service health checks
- Live logs
- Memory/CPU usage
- Deployment history
- Rollback capability

---

## 🚨 Common Issues

### Frontend not loading data
```bash
# Check CORS in backend
curl -H "Origin: https://username.github.io" \
  https://ecosat-monitor-backend.onrender.com/api/v1/health

# Update CORS_ORIGINS in backend environment
CORS_ORIGINS=https://username.github.io/ecosat-monitor
```

### Backend container crashes
```bash
# Check logs on Render/Railway dashboard
# View database connectivity
# Verify environment variables are set
# Check GEE credentials are valid
```

### Database not connecting
```bash
# Verify DATABASE_URL format:
postgresql://user:pass@host:5432/dbname

# Test connection:
psql $DATABASE_URL -c "SELECT 1"
```

---

## 🎯 Next Steps

1. **Push to GitHub** (if not done)
2. **Choose backend service** (Render recommended)
3. **Deploy** (5-10 minutes)
4. **Configure GEE** (if using live data)
5. **Test endpoints**
6. **Share your dashboard!**

---

## 📞 Support

- GitHub Actions Issues: Check .github/workflows/ logs
- Render/Railway Issues: Check service dashboard
- API Issues: http://your-backend-url/api/v1/docs
- Code Issues: GitHub Issues tab

**You're production-ready! 🚀**
