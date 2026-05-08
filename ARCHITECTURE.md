"""Architecture overview document."""

# EcoSat Monitor - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ React 18 + TypeScript + Vite                                    │   │
│  │ ├─ Map Component (MapLibre GL JS)                               │   │
│  │ ├─ Sidebar with Layer Controls                                  │   │
│  │ ├─ Time-Series Charts (Recharts)                                │   │
│  │ ├─ Alert Panel                                                  │   │
│  │ └─ AOI Manager (Draw & Manage Regions)                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              (Port: 5173)                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             API GATEWAY LAYER                            │
│  FastAPI + Uvicorn (Port: 8000)                                         │
│  ├─ Health & Status Endpoints                                           │
│  ├─ AOI Management API                                                  │
│  ├─ Time-Series Query API                                               │
│  ├─ Alert API                                                           │
│  ├─ Tile Serving API                                                    │
│  └─ Data Export API (GeoJSON, CSV)                                      │
└─────────────────────────────────────────────────────────────────────────┘
                    │                    │                    │
         ┌──────────┴────────────────────┴────────────────────┴──────────┐
         │                                                                 │
         ▼                                                                 ▼
┌─────────────────────────────────┐                   ┌───────────────────────┐
│   DATA PROCESSING PIPELINE      │                   │  DATA ACCESS LAYER    │
│  (Celery Workers + Scheduler)   │                   │                       │
│                                 │                   │ ┌─────────────────┐   │
│ ┌─ Pollution Worker             │                   │ │  PostgreSQL     │   │
│ ├─ Rainfall Worker              │                   │ │  + PostGIS      │   │
│ ├─ Heat Worker                  │                   │ │                 │   │
│ ├─ Vegetation Worker            │                   │ │ Tables:         │   │
│ └─ Scheduler (Beat)             │                   │ │ ├─ AOIs          │   │
│                                 │                   │ │ ├─ TimeSeries    │   │
│ ┌─ Anomaly Detection            │                   │ │ ├─ Alerts        │   │
│ ├─ COG Generation               │                   │ │ └─ IngestionLogs │   │
│ └─ Data Validation              │                   │ └─────────────────┘   │
│                                 │                   │        (Port: 5432)   │
│ (Redis Queue & Broker)          │                   │                       │
└─────────────────────────────────┘                   └───────────────────────┘
         │                                                    │
         └────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL DATA SOURCES                               │
│  (No Cost - Free Tier APIs)                                             │
│                                                                         │
│  Google Earth Engine (GEE)                                              │
│  ├─ Sentinel-2 (ESA Copernicus) → NDVI                                  │
│  ├─ Sentinel-5P TROPOMI (ESA) → Pollution (NO₂, SO₂, CO, O₃, CH₄)      │
│  ├─ MODIS (NASA) → Land Surface Temperature                             │
│  ├─ Landsat 8/9 (USGS) → Supplementary                                  │
│  └─ NASA GPM IMERG → Rainfall                                           │
│                                                                         │
│  Alternative Sources (Fallback)                                         │
│  ├─ Copernicus Data Space API                                           │
│  ├─ NASA DAAC                                                           │
│  ├─ OpenAQ (Ground truth air quality)                                   │
│  └─ GBIF (Biodiversity data)                                            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Live Data Request Flow

```
User Query
    ↓
Frontend API Call
    ↓
FastAPI Endpoint
    ↓
Check Redis Cache
    ├─ Cache Hit → Return cached data
    └─ Cache Miss
        ↓
    Query PostgreSQL
        ↓
    Format Response (GeoJSON)
        ↓
    Cache Result (5-30 min TTL)
        ↓
    Return to Frontend
```

### 2. Data Ingestion Flow (Automated)

```
Celery Beat Scheduler (Daily/Weekly)
    ↓
Schedule Worker Tasks
    ├─ Pollution Worker (Daily 02:00 UTC)
    ├─ Rainfall Worker (Daily 03:00 UTC)
    ├─ Heat Worker (Daily 04:00 UTC)
    └─ Vegetation Worker (Weekly 05:00 UTC Sunday)
    ↓
Worker Retrieves Data
    ├─ Query Google Earth Engine
    ├─ Filter by AOI geometry
    ├─ Cloud masking & median compositing
    └─ Calculate statistics
    ↓
Store in PostgreSQL
    ├─ TimeseriesStats table
    ├─ Create ingestion log
    └─ Index spatially
    ↓
Anomaly Detection
    ├─ Z-score analysis
    ├─ Threshold comparison
    └─ Create alerts if anomaly detected
    ↓
Optional: Generate COG Tiles
    └─ Export to Cloud Storage
```

### 3. Alert Generation Flow

```
New Data Ingested
    ↓
Calculate Baseline (30-90 day historical)
    ↓
Compare Current vs Baseline
    ├─ If NDVI ↓ 0.2+ → Deforestation Alert
    ├─ If NO₂ > 2σ → Pollution Spike Alert
    ├─ If LST > 90th percentile → Heat Wave Alert
    └─ If Rainfall > 95th percentile → Flood Risk Alert
    ↓
Set Confidence Score
    └─ Based on statistical significance
    ↓
Create Alert Record
    ├─ Store in Alerts table
    ├─ Emit to frontend via WebSocket (future)
    └─ Log severity level
    ↓
Frontend Displays Alert
    └─ User can resolve or archive
```

## Technology Decisions

### Why These Technologies?

| Component | Technology | Reason |
|-----------|-----------|--------|
| Frontend | React + TypeScript | Industry standard, large ecosystem |
| Map Library | MapLibre GL JS | Open-source, no API key required |
| Backend | FastAPI | Fast, async, auto-generated docs |
| Database | PostgreSQL + PostGIS | Mature, spatialgeometry support |
| Task Queue | Celery + Redis | Distributed, handles large workloads |
| Satellite API | Google Earth Engine | Most comprehensive free satellite data |
| Build Tool | Vite | Fast, modern, zero-config |
| Styling | Tailwind CSS | Utility-first, small bundle size |
| Charts | Recharts | React-native, composable |

### Zero-Cost Strategy

- **Frontend**: GitHub Pages or Cloudflare Pages (free deployment)
- **Backend**: Oracle Cloud Free Tier or Render.com
- **Database**: Oracle Cloud Object Storage or self-hosted
- **Satellite Data**: All free/public domain sources
- **CDN**: Cloudflare free tier
- **DNS**: Cloudflare or free services

## Scalability Considerations

### Current Setup (Single VM)
- Handles ~1000 concurrent users
- ~100 AOIs with daily updates
- All data in hot storage (PostgreSQL)

### Scaling Up (Multi-Instance)
1. **Horizontal Backend Scaling**
   - Deploy multiple FastAPI instances
   - Load balance with nginx or cloud provider
   - Share Redis and PostgreSQL

2. **Database Optimization**
   - Partitioning by date for timeseries
   - Read replicas for queries
   - Archive old data to S3

3. **Caching Strategy**
   - Redis for recent tiles (24h TTL)
   - CDN for static assets
   - ElastiCache for distributed cache

4. **Celery Scaling**
   - Multiple worker pods
   - Priority queues (hot data first)
   - Task routing by resource needs

## Security Architecture

```
┌─────────────────────────────────────┐
│       WAF / DDoS Protection         │ (Cloudflare)
└────────────────────┬────────────────┘
                     ↓
┌─────────────────────────────────────┐
│      API Rate Limiting              │ (FastAPI)
│      100 req/min per IP             │
└────────────────────┬────────────────┘
                     ↓
┌─────────────────────────────────────┐
│      CORS Policy                    │ (Frontend domain only)
└────────────────────┬────────────────┘
                     ↓
┌─────────────────────────────────────┐
│      Request Validation             │ (Pydantic)
│      SQL Injection Protection       │ (SQLAlchemy)
└────────────────────┬────────────────┘
                     ↓
┌─────────────────────────────────────┐
│      PostgreSQL Encryption          │ (TLS + SSL)
│      Redis Password Protection      │
└─────────────────────────────────────┘
```

## Monitoring & Observability

### Current Implementation
- Health check endpoint: `/api/v1/health`
- Application logs: Docker logs
- Database logs: PostgreSQL logs
- Task logs: Celery worker logs

### Future Enhancements
- Prometheus metrics
- Grafana dashboards
- ELK stack for centralized logging
- Sentry for error tracking
- NewRelic/Datadog for APM

## Disaster Recovery

### Backup Strategy
```
Daily:
├─ Database backup to S3
├─ Configuration backup
└─ Tile cache backup (optional)

Weekly:
└─ Full system snapshot

Monthly:
└─ Archive to cold storage
```

### Recovery Procedures
1. Database failure: Restore from daily backup (< 24h data loss)
2. Tile cache loss: Regenerate from PostgreSQL stats
3. Container failure: Auto-restart via Docker Compose
4. Service failure: Manual failover to backup instance

---

See [README.md](README.md) for deployment and architecture details.
