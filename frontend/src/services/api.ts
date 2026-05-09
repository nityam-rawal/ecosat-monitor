// Frontend API client service.

import axios, { AxiosInstance } from "axios";
import {
  AOI,
  Alert,
  AlertQueryParams,
  DatasetMetadata,
  HealthCheckResponse,
  TimeseriesData,
  TimeseriesQueryParams,
} from "@/types";

const API_BASE_URL = ((import.meta as any).env.VITE_API_BASE_URL as string | undefined) || "http://localhost:8000";

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  // Health & Status
  async healthCheck(): Promise<HealthCheckResponse> {
    const { data } = await this.client.get("/health");
    return data;
  }

  // Datasets
  async getDatasets(): Promise<DatasetMetadata[]> {
    const { data } = await this.client.get("/datasets");
    return data;
  }

  async getDataset(datasetId: string): Promise<DatasetMetadata> {
    const { data } = await this.client.get(`/datasets/${datasetId}`);
    return data;
  }

  // AOIs
  async getAOIs(): Promise<AOI[]> {
    const { data } = await this.client.get("/aois");
    return data;
  }

  async getAOI(aoiId: number): Promise<AOI> {
    const { data } = await this.client.get(`/aois/${aoiId}`);
    return data;
  }

  async createAOI(name: string, geometry: object): Promise<AOI> {
    const { data } = await this.client.post("/aois", {
      name,
      geom: geometry,
    });
    return data;
  }

  async deleteAOI(aoiId: number): Promise<void> {
    await this.client.delete(`/aois/${aoiId}`);
  }

  // Time-series Data
  async getTimeseries(params: TimeseriesQueryParams): Promise<TimeseriesData[]> {
    const { dataset, ...queryParams } = params;
    const { data } = await this.client.get(`/timeseries/${dataset}`, {
      params: queryParams,
    });
    return data;
  }

  async getLatestData(): Promise<Record<string, unknown>> {
    const { data } = await this.client.get("/timeseries/latest/all");
    return data;
  }

  // Alerts
  async getAlerts(params?: AlertQueryParams): Promise<Alert[]> {
    const { data } = await this.client.get("/alerts", { params });
    return data;
  }

  async getAlert(alertId: number): Promise<Alert> {
    const { data } = await this.client.get(`/alerts/${alertId}`);
    return data;
  }

  async resolveAlert(alertId: number): Promise<void> {
    await this.client.delete(`/alerts/${alertId}`);
  }

  // Export
  async exportGeoJSON(aoiId: number): Promise<string> {
    const { data } = await this.client.get("/export/geojson", {
      params: { aoi_id: aoiId },
    });
    return JSON.stringify(data);
  }

  async exportCSV(
    aoiId: number,
    dataset: string,
    startDate: string,
    endDate: string
  ): Promise<Blob> {
    const { data } = await this.client.get("/export/csv", {
      params: {
        aoi_id: aoiId,
        dataset,
        start_date: startDate,
        end_date: endDate,
      },
      responseType: "blob",
    });
    return data;
  }

  // Tiles
  getTileUrl(
    dataset: string,
    z: number | string,
    x: number | string,
    y: number | string
  ): string {
    return `${API_BASE_URL}/api/v1/tiles/${dataset}/${z}/${x}/${y}.png`;
  }

  getTileMetadata(dataset: string): Promise<Record<string, unknown>> {
    return this.client
      .get(`/tiles/${dataset}/preview`)
      .then(({ data }) => data);
  }
}

export const api = new APIClient();
