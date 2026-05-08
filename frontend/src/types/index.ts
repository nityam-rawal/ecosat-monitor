"""Frontend types and interfaces."""

// API Response Types
export interface AOI {
  id: number;
  name: string;
  geom: GeoJSONPolygon;
  created_at: string;
}

export interface TimeseriesData {
  date: string;
  mean: number;
  min: number;
  max: number;
  stddev: number;
  source: string;
}

export interface Alert {
  id: number;
  aoi_id: number;
  alert_type: string;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  detected_at: string;
  satellite_source: string;
  confidence_score: number;
  geom: GeoJSONPoint;
}

export interface DatasetMetadata {
  name: string;
  data_type: string;
  source: string;
  description: string;
  temporal_resolution: string;
  spatial_resolution: string;
  unit: string;
  last_update: string | null;
  color_scheme: Record<string, string>;
}

export interface HealthCheckResponse {
  status: "healthy" | "degraded" | "unhealthy";
  version: string;
  database: string;
  cache: string;
}

// GeoJSON Types
export interface GeoJSONPoint {
  type: "Point";
  coordinates: [number, number]; // [lon, lat]
}

export interface GeoJSONPolygon {
  type: "Polygon";
  coordinates: [[[number, number]]]; // [[[lon, lat], ...]]
}

export interface GeoJSONFeature {
  type: "Feature";
  geometry: GeoJSONPoint | GeoJSONPolygon;
  properties: Record<string, unknown>;
}

// UI State Types
export interface MapLayer {
  id: string;
  name: string;
  type: "raster" | "vector";
  visible: boolean;
  opacity: number;
  source: string;
  paint?: Record<string, unknown>;
  layout?: Record<string, unknown>;
}

export interface TimeSliderState {
  currentDate: string;
  startDate: string;
  endDate: string;
  isPlaying: boolean;
}

export interface SelectedAOI {
  id: number | null;
  name: string;
  geometry: GeoJSONPolygon | null;
}

export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    fill: boolean;
  }>;
}

// API Query Parameters
export interface TimeseriesQueryParams {
  aoi_id?: number;
  lat?: number;
  lon?: number;
  dataset: string;
  start_date: string;
  end_date: string;
  aggregation?: "day" | "week" | "month";
}

export interface AlertQueryParams {
  aoi_id?: number;
  alert_type?: string;
  severity?: string;
  limit?: number;
}
