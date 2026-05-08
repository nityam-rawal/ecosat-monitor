"""Quick Setup Guide for EcoSat Monitor."""

# EcoSat Monitor - Quick Setup Guide

## 🚀 5-Minute Quick Start

### 1. Prerequisites
- Docker & Docker Compose installed
- Git installed

### 2. Clone & Configure

```bash
# Clone repository
git clone <repo-url> ecosat-monitor
cd ecosat-monitor

# Copy environment template
cp .env.example .env
```

### 3. Google Earth Engine Setup (Optional but Recommended)

To use live satellite data:

```bash
# 1. Go to: https://code.earthengine.google.com/
# 2. Sign in with Google account
# 3. Accept terms and create project
# 4. Create service account:
#    - Go to Google Cloud Console
#    - Create project: "ecosat-monitor"
#    - Enable Earth Engine API
#    - Create Service Account
#    - Generate JSON key
# 5. Download JSON and save to: backend/gee-key.json
# 6. Update .env:
export GEE_SERVICE_ACCOUNT_JSON=$(cat backend/gee-key.json | jq -r .)
```

### 4. Start Services

```bash
# Build and start (this takes 3-5 minutes on first run)
docker-compose up --build -d

# Wait for services to be healthy
docker-compose ps

# Check logs
docker-compose logs -f backend
```

### 5. Access Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/v1/docs
- **Database**: psql -h localhost -U ecosat -d ecosat
- **Redis**: redis-cli -h localhost

### 6. Create Your First AOI (Area of Interest)

Via API:
```bash
curl -X POST http://localhost:8000/api/v1/aois \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Region",
    "geom": {
      "type": "Polygon",
      "coordinates": [[
        [-122.5, 37.5],
        [-122.0, 37.5],
        [-122.0, 38.0],
        [-122.5, 38.0],
        [-122.5, 37.5]
      ]]
    }
  }'
```

Via Frontend:
1. Go to http://localhost:5173
2. Click "+ New AOI" in sidebar
3. Enter name and draw polygon on map

### 7. Verify Data Ingestion

```bash
# Check if data is being ingested
curl http://localhost:8000/api/v1/datasets

# View time-series data
curl "http://localhost:8000/api/v1/timeseries/ndvi?aoi_id=1&start_date=2026-05-01&end_date=2026-05-09"

# View alerts
curl http://localhost:8000/api/v1/alerts
```

## 📊 Available Datasets

| Dataset | Type | Resolution | Latency | Source |
|---------|------|-----------|---------|--------|
| NDVI | Vegetation | 10m | 5-7 days | Sentinel-2 |
| NO₂ | Air Pollution | 7km × 3.5km | 1 day | Sentinel-5P |
| SO₂ | Air Pollution | 7km × 3.5km | 1 day | Sentinel-5P |
| Rainfall | Precipitation | 11km | 4-14 hours | NASA GPM |
| LST | Temperature | 1km | 1 day | MODIS |

## 🔧 Common Commands

```bash
# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Remove everything
docker-compose down -v

# Execute command in container
docker-compose exec backend python -c "from app.db.session import init_db; init_db()"

# Open database shell
docker-compose exec db psql -U ecosat -d ecosat

# Check health
curl http://localhost:8000/api/v1/health | jq
```

## 🐛 Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker ps

# View detailed logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v && docker-compose up --build
```

### Database connection error
```bash
# Wait for database to be ready
docker-compose exec db pg_isready

# Check logs
docker-compose logs db
```

### No data appearing
```bash
# Check if GEE credentials are set
echo $GEE_SERVICE_ACCOUNT_JSON

# Check scheduler logs
docker-compose logs scheduler

# Manually trigger data ingestion
docker-compose exec worker celery -A pipeline.workers.pollution_worker call ingest_pollution 1 "NO2"
```

### Frontend not connecting to backend
```bash
# Check CORS settings
grep CORS_ORIGINS backend/app/config.py

# Update .env
VITE_API_BASE_URL=http://localhost:8000
```

## 📚 Documentation

- **Full README**: [README.md](README.md)
- **API Docs**: http://localhost:8000/api/v1/docs (when running)
- **Architecture**: See README.md Architecture section
- **Deployment Guide**: See Production section in README.md

## 🔐 Security Notes

- **Development Only**: This setup is for local development. For production:
  - Use strong database passwords
  - Set CORS_ORIGINS to your domain
  - Use HTTPS
  - Enable authentication
  - Use managed Redis/PostgreSQL (AWS RDS, etc.)

## 📞 Need Help?

- Check logs: `docker-compose logs -f`
- Review error messages carefully
- Check environment variables: `cat .env`
- Verify GEE credentials are correct
- Ensure ports 5173, 8000, 5432, 6379 are not in use

---

**Happy monitoring! 🌍**
