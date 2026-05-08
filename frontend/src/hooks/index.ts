"""React hooks for data fetching and state management."""

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/services/api";

// AOI Hooks
export function useAOIs() {
  return useQuery({
    queryKey: ["aois"],
    queryFn: () => api.getAOIs(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useAOI(aoiId: number | null) {
  return useQuery({
    queryKey: ["aoi", aoiId],
    queryFn: () => (aoiId ? api.getAOI(aoiId) : null),
    enabled: !!aoiId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateAOI() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ name, geometry }: { name: string; geometry: object }) =>
      api.createAOI(name, geometry),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["aois"] });
    },
  });
}

export function useDeleteAOI() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (aoiId: number) => api.deleteAOI(aoiId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["aois"] });
    },
  });
}

// Timeseries Hooks
export function useTimeseries(
  dataset: string,
  aoiId: number | null,
  startDate: string,
  endDate: string
) {
  return useQuery({
    queryKey: ["timeseries", dataset, aoiId, startDate, endDate],
    queryFn: () =>
      api.getTimeseries({
        dataset,
        aoi_id: aoiId || undefined,
        start_date: startDate,
        end_date: endDate,
      }),
    enabled: !!(aoiId && startDate && endDate),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useLatestData() {
  return useQuery({
    queryKey: ["latest-data"],
    queryFn: () => api.getLatestData(),
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
}

// Alerts Hooks
export function useAlerts(aoiId?: number, alertType?: string) {
  return useQuery({
    queryKey: ["alerts", aoiId, alertType],
    queryFn: () =>
      api.getAlerts({
        aoi_id: aoiId,
        alert_type: alertType,
        limit: 50,
      }),
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
}

export function useResolveAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (alertId: number) => api.resolveAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}

// Datasets Hooks
export function useDatasets() {
  return useQuery({
    queryKey: ["datasets"],
    queryFn: () => api.getDatasets(),
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}

// Map Hooks
export function useMapInstance() {
  const [map, setMap] = useState<unknown>(null);

  return { map, setMap };
}

// Export Hooks
export function useExportGeoJSON() {
  return useMutation({
    mutationFn: async (id: number) => {
      const geojson = await api.exportGeoJSON(id);
      const element = document.createElement("a");
      element.setAttribute(
        "href",
        "data:text/plain;charset=utf-8," + encodeURIComponent(geojson)
      );
      element.setAttribute("download", `aoi_${id}.geojson`);
      element.style.display = "none";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    },
  });
}

export function useExportCSV() {
  return useMutation({
    mutationFn: async ({
      aoiId,
      dataset,
      startDate,
      endDate,
    }: {
      aoiId: number;
      dataset: string;
      startDate: string;
      endDate: string;
    }) => {
      const blob = await api.exportCSV(aoiId, dataset, startDate, endDate);
      const element = document.createElement("a");
      element.setAttribute("href", URL.createObjectURL(blob));
      element.setAttribute("download", `${dataset}_${startDate}_${endDate}.csv`);
      element.style.display = "none";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    },
  });
}
