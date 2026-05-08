# EcoSat Monitor — Live Satellite Environmental Intelligence Platform

A full-stack, open-source web application delivering **live satellite-derived environmental data** with zero infrastructure costs. Real-time monitoring of tree cover, air pollution, rainfall, and heat waves.

## 🌍 Features

- **Real-time Satellite Data**: NDVI (vegetation), NO₂/SO₂/CO/O₃/CH₄ (pollution), Rainfall, LST (heat)
- **Automated Data Ingestion**: Daily/weekly data pipelines via Celery workers
- **Interactive Map**: MapLibre GL JS with dynamic layers, opacity controls, time slider
- **Time-Series Analytics**: Charts and trends for all datasets
- **Anomaly Detection**: Automated alerts for heat waves, deforestation, pollution spikes, floods
- **Zero Infrastructure Costs**: Uses free satellite APIs (ESA Copernicus, NASA, Google Earth Engine)
- **Docker-Ready**: Full local development with Docker Compose

## 📋 Tech Stack

### Backend
- **FastAPI**: Async Python web framework
- **PostgreSQL + PostGIS**: Geospatial database
- **Redis**: Caching and task queue
- **Celery**: Distributed task processing
- **Google Earth Engine API**: Satellite data processing
- **SQLAlchemy**: ORM

### Frontend
- **React 18 + TypeScript**: UI framework
- **Vite**: Build tool
- **MapLibre GL JS**: Interactive maps
- **TanStack Query**: Data fetching and caching
- **Recharts**: Time-series charts
- **Tailwind CSS**: Styling

### Data Sources
- **Sentinel-2 MSI**: Vegetation (NDVI) - ESA Copernicus
- **Sentinel-5P TROPOMI**: Air pollution - ESA Copernicus
- **NASA GPM IMERG**: Rainfall/Precipitation
- **MODIS**: Land Surface Temperature - NASA
- **Landsat 8/9**: Supplementary optical data - USGS

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (if running frontend separately)
- Python 3.11+ (if running backend separately)
- Google Earth Engine account (free for non-commercial use)

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/ecosat-monitor.git
cd ecosat-monitor

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` and set up GEE credentials:

```bash
# Get Google Earth Engine credentials
# 1. Go to https://code.earthengine.google.com/
# 2. Authenticate and create a service account project
# 3. Create and download private key JSON
# 4. Add path to GEE_SERVICE_ACCOUNT_JSON in .env
```

### 3. Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d
```

Services will be available at:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Frontend**: http://localhost:5173
- **Database**: localhost:5432
- **Redis**: localhost:6379

### 4. Create Initial AOI

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/aois \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Region",
    "geom": {
      "type": "Polygon",
      "coordinates": [[
        [0, 0], [1, 0], [1, 1], [0, 1], [0, 0]
      ]]
    }
  }'
```

### 5. Ingest Data

Data ingestion runs automatically on schedule. To manually trigger:

```bash
# Via Celery
celery -A pipeline.scheduler call ingest_pollution 1 "NO2"
```

## 📊 API Endpoints

### Core
- `GET /api/v1/health` - Health check
- `GET /api/v1/datasets` - List available datasets

### AOI Management
- `POST /api/v1/aois` - Create AOI
- `GET /api/v1/aois` - List all AOIs
- `GET /api/v1/aois/{id}` - Get AOI details
- `DELETE /api/v1/aois/{id}` - Delete AOI

### Time-Series Data
- `GET /api/v1/timeseries/{dataset}` - Query time-series data
  - Params: `aoi_id`, `start_date`, `end_date`, `aggregation`
- `GET /api/v1/timeseries/latest/all` - Latest data for all datasets

### Alerts
- `GET /api/v1/alerts` - List active alerts
  - Params: `aoi_id`, `alert_type`, `severity`, `limit`
- `DELETE /api/v1/alerts/{id}` - Resolve alert

### Map Tiles
- `GET /api/v1/tiles/{dataset}/{z}/{x}/{y}.png` - Dynamic map tiles

### Export
- `GET /api/v1/export/geojson?aoi_id={id}` - Export AOI as GeoJSON
- `GET /api/v1/export/csv` - Export time-series as CSV

**Full API Documentation**: http://localhost:8000/api/v1/docs (Swagger UI)

## 🔄 Data Pipeline

### Daily Schedule (Automated)
1. **02:00 UTC** - Pollution (Sentinel-5P TROPOMI) for all pollutants
2. **03:00 UTC** - Rainfall (NASA GPM IMERG)
3. **04:00 UTC** - Heat/LST (MODIS)
4. **05:00 UTC (Sunday)** - Vegetation/NDVI (Sentinel-2, 7-day median)

Each AOI is processed independently. Anomalies trigger alerts.

### Data Retention
- **Hot**: Last 90 days (database)
- **Cold**: Archive older data to S3/cloud storage (optional)
- **Cleanup**: Automated weekly cleanup task

## 🎨 Frontend Usage

### Map Features
- **Layer Switcher**: Select active dataset
- **Opacity Control**: Adjust layer transparency
- **Time Slider**: Animate last 30 days
- **Click on Map**: Fetch point data and show time-series chart
- **Draw AOI**: Create custom polygon regions

### Dashboard
- **Live Status**: Latest satellite pass time per dataset
- **AOI Summary**: Current values for NDVI, NO₂, rainfall, LST
- **Alert Feed**: Real-time anomalies with severity badges
- **Chart Panel**: Interactive time-series visualizations

## 🔐 Security

- No user tracking or cookies (JWT sessions optional)
- All satellite data is public domain (proper attribution in UI)
- API rate limiting: 100 req/min per IP
- CORS configured for frontend domain only
- No API keys exposed in frontend code
- Environment variables for sensitive data

## 📈 Deployment

### Development
```bash
docker-compose up
```

### Production (Free Tier)

**Frontend**: Cloudflare Pages or GitHub Pages
- Connect repository
- Auto-deploy on push
- Free SSL/TLS

**Backend + Database**: Oracle Cloud Free Tier (2x AMD VMs, 1GB RAM each) or Render.com
```bash
# Example: Oracle Cloud Compute
docker-compose -f docker-compose.prod.yml up -d
```

**Storage**: Oracle Cloud Object Storage or Linode S3-compatible
```bash
# Configure in config.py
TILE_STORAGE_PATH = "s3://my-bucket/tiles"
```

**Domain**: Cloudflare free subdomain or GitHub Pages domain

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test

# Type checking
npm run type-check
```

## 📚 Project Structure

```
ecosat-monitor/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # API routes
│   │   ├── core/                 # GEE client, exceptions
│   │   ├── db/                   # Database models, migrations
│   │   ├── models/               # Pydantic schemas
│   │   ├── services/             # Business logic (pollution, rainfall, etc.)
│   │   ├── config.py             # Settings
│   │   └── main.py               # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── hooks/                # Custom React hooks
│   │   ├── services/             # API client
│   │   ├── types/                # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── pipeline/
│   ├── workers/                  # Celery tasks
│   ├── utils/                    # COG, alert utilities
│   └── scheduler.py              # Beat scheduler
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all options. Key variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ecosat

# Google Earth Engine (required)
GEE_PROJECT_ID=your-project-id
GEE_SERVICE_ACCOUNT_JSON=/path/to/service-account-key.json

# NASA/Copernicus credentials (optional, for fallback data sources)
NASA_EARTHDATA_USER=username
COPERNICUS_DSM_USER=username
```

### Database Initialization

The database initializes automatically on backend startup. To manually init:

```bash
docker exec ecosat-backend python -c "from app.db.session import init_db; init_db()"
```

## 📖 Advanced Topics

### Using TiTiler for Dynamic Tile Serving

```bash
# Run TiTiler container
docker run -p 8008:8000 ghcr.io/developmentseed/titiler-cogeo

# Update config
TITILER_URL=http://titiler:8000
```

### Custom Alert Rules

Edit `app/services/alert_engine.py` to add custom anomaly detection logic.

### Adding New Datasets

1. Create service file (e.g., `app/services/new_dataset_service.py`)
2. Create Celery worker (e.g., `pipeline/workers/new_dataset_worker.py`)
3. Add endpoint in `app/api/v1/endpoints/timeseries.py`
4. Update frontend dataset selector

## 🤝 Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the **MIT License** - see LICENSE file for details.

All satellite data sources are public domain:
- ESA Copernicus (Sentinel-2, Sentinel-5P) - CC-BY-4.0
- NASA USGS (Landsat, MODIS) - Public domain
- NASA GPM IMERG - Public domain

Proper attribution included in UI data legends.

## 🙋 Support

- **Documentation**: See README and code comments
- **Issues**: GitHub Issues
- **Community**: Discussions

## 🗺️ Roadmap

- [ ] TiTiler integration for dynamic COG tile serving
- [ ] User authentication and AOI sharing
- [ ] Mobile-optimized version
- [ ] WebRTC for real-time collaboration
- [ ] Custom ML anomaly detection models
- [ ] Sentinel-3 sea surface temperature data
- [ ] Integration with citizen science data (GBIF, iNaturalist)
- [ ] Multi-language UI support

## 📞 Contact

For questions or collaboration:
- Open an issue on GitHub
- Contact project maintainers

---

**Built with ❤️ using open-source satellite data**

Data last updated: **May 9, 2026**
