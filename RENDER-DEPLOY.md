# Deploy to Render.com (Easiest & Fastest)

## ⏱️ Total Time: ~10 minutes

Render.com is the **recommended free option** - it handles everything automatically.

---

## 📋 Prerequisites

- GitHub account with your `ecosat-monitor` repository pushed
- Render.com account (free, no credit card)
- Google Earth Engine service account (optional, for live data)

---

## 🚀 Step-by-Step Deployment

### Step 1: Sign Up to Render.com

1. Go to https://render.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize and sign in
5. ✅ You're in!

### Step 2: Deploy PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**

```
Name: ecosat-db
Database: ecosat
User: ecosat
Password: (auto-generated, copy it)
Region: Choose closest to you
Plan: Free
```

2. Click **"Create Database"**
3. ⏳ Wait 2-3 minutes for database to be ready
4. Copy the connection string that appears

**Save this:**
```
DATABASE_URL = postgresql://user:password@host:5432/ecosat
```

### Step 3: Deploy Redis Cache

1. Click **"New +"** → **"Redis"**

```
Name: ecosat-redis
Plan: Free
Region: Same as database
```

2. Click **"Create Redis"**
3. ⏳ Wait 2-3 minutes
4. Copy the connection string

**Save this:**
```
REDIS_URL = redis://user:password@host:6379
```

### Step 4: Deploy Backend API

1. Click **"New +"** → **"Web Service"**
2. Select your `ecosat-monitor` GitHub repository
3. Configure:

```
Name: ecosat-monitor-api
Environment: Docker
Build Command: (leave blank - auto-detected)
Start Command: (leave blank - auto-detected)
Plan: Free
```

4. Click **"Create Web Service"**
5. Now add **Environment Variables**:

Click the **"Environment"** tab and add:

```
DATABASE_URL = (paste from Step 2)
REDIS_URL = (paste from Step 3)
DEBUG = false
GEE_PROJECT_ID = your-gee-project-id
GEE_SERVICE_ACCOUNT_JSON = (paste full JSON from GEE service account)
```

6. ⏳ Backend automatically deploys (5-10 min)
7. Once running, copy the URL: `https://ecosat-monitor-api.onrender.com`

### Step 5: Deploy Frontend

1. Click **"New +"** → **"Static Site"**
2. Select your `ecosat-monitor` GitHub repository
3. Configure:

```
Name: ecosat-monitor-web
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/dist
Plan: Free
```

4. Click **"Create Static Site"**
5. ⏳ Frontend deploys automatically (3-5 min)
6. Get the URL: `https://ecosat-monitor-web.onrender.com`

### Step 6: Connect Frontend to Backend

1. Go to **"Static Site"** settings
2. Add **Environment Variable**:

```
VITE_API_BASE_URL = https://ecosat-monitor-api.onrender.com
```

3. **Redeploy** (auto-triggers)
4. ✅ Frontend now connects to backend!

---

## ✅ Verify Deployment

```bash
# Test API health
curl https://ecosat-monitor-api.onrender.com/api/v1/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "cache": "connected"
}
```

---

## 🌐 Your Live URLs

After deployment, you have:

| Service | URL |
|---------|-----|
| **Frontend** | `https://ecosat-monitor-web.onrender.com` |
| **Backend API** | `https://ecosat-monitor-api.onrender.com` |
| **API Docs** | `https://ecosat-monitor-api.onrender.com/api/v1/docs` |
| **Health Check** | `https://ecosat-monitor-api.onrender.com/api/v1/health` |

---

## 🔄 Auto-Deployment

Every time you push to GitHub:

1. Render.com detects the change
2. Rebuilds the containers
3. Deploys automatically
4. Zero downtime! ✨

---

## 🛠️ Troubleshooting

### Backend container keeps crashing

**Check logs:**
1. Go to Backend service
2. Click **"Logs"** tab
3. Look for error messages

**Common fixes:**
```bash
# Database connection error
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# GEE authentication error
# Make sure GEE_SERVICE_ACCOUNT_JSON is valid JSON

# Redis connection error
REDIS_URL=redis://user:pass@host:6379
```

### Frontend shows "Cannot connect to API"

1. Check Backend is running (green "Live" status)
2. Verify `VITE_API_BASE_URL` is correct
3. Check CORS settings in backend
4. Redeploy frontend

### Database not initializing

1. SSH into backend service
2. Run:
```bash
psql $DATABASE_URL -f init.sql
```

---

## 💾 Backups

Render.com automatically backs up PostgreSQL:
- Daily backups (7 day retention)
- Manual backups available
- Downloadable as SQL dump

---

## 📊 Monitoring

### View Service Status
1. Render Dashboard → Services
2. See CPU, Memory, Request count
3. View error logs in real-time

### Performance Metrics
- Response time
- Error rate
- Database query time
- Cache hit ratio

---

## 🚀 Next Features to Deploy

```bash
# After basic deployment works:

1. Configure custom domain
   - Settings → Custom Domains

2. Enable HTTPS (automatic)
   - Render provides free SSL

3. Set up alerts
   - Services → Alert Settings
   - Get notified of failures

4. Scale resources (paid)
   - Upgrade from Free to Starter
   - Higher concurrency
   - More memory
```

---

## 💰 Cost

**Total Cost: $0/month** (Free tier includes)

- 750 hours/month web service
- Unlimited static sites
- PostgreSQL database (free tier)
- Redis cache (free tier)
- SSL certificates (automatic)
- Email support

**Upgrade when:**
- Free tier exhausted
- Need more than 4GB database
- Want 24/7 uptime guarantee
- Production traffic exceeds limits

---

## 📞 Need Help?

- **Render Documentation**: https://render.com/docs
- **GitHub Integration**: https://render.com/docs/github
- **Deployment Issues**: Check service logs
- **API Issues**: http://your-backend-url/api/v1/docs

---

## ✨ You're Live!

Share your dashboard with the world:

```
Frontend: https://ecosat-monitor-web.onrender.com
API Docs: https://ecosat-monitor-api.onrender.com/api/v1/docs
```

**Congratulations! 🎉**
