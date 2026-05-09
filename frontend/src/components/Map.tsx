// Map component with MapLibre GL JS.

import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useDatasets, useLatestData } from "@/hooks";
import { api } from "@/services/api";

interface MapProps {
  selectedAoiId: number | null;
  activeDataset: string;
}

export default function Map({ selectedAoiId, activeDataset }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [zoom, setZoom] = useState(5);
  const { data: datasets } = useDatasets();
  const { data: latestData = {} } = useLatestData();

  useEffect(() => {
    if (!mapContainer.current) return;

    // Initialize map
    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://demotiles.maplibre.org/style.json",
      center: [0, 20],
      zoom: zoom,
    });

    // Add navigation control
    map.current.addControl(new maplibregl.NavigationControl());
    map.current.on("moveend", () => {
      setZoom(Number(map.current?.getZoom().toFixed(1) || 0));
    });

    return () => {
      map.current?.remove();
    };
  }, []);

  useEffect(() => {
    if (!map.current || !activeDataset || !datasets) return;

    const dataset = datasets.find((d) => d.data_type === activeDataset);
    if (!dataset) return;

    // Remove existing raster layer
    const existingLayers = map.current.getStyle().layers || [];
    existingLayers.forEach((layer) => {
      if (layer.id.startsWith("raster-")) {
        map.current?.removeLayer(layer.id);
      }
    });

    // Remove existing sources
    const existingSources = map.current.getStyle().sources || {};
    Object.keys(existingSources).forEach((sourceId: string) => {
      if (sourceId.startsWith("raster-")) {
        map.current?.removeSource(sourceId);
      }
    });

    // Add new raster layer
    const sourceId = `raster-${activeDataset}`;
    map.current.addSource(sourceId, {
      type: "raster",
      tiles: [
        api.getTileUrl(activeDataset, "{z}", "{x}", "{y}"),
      ],
      tileSize: 256,
    });

    const beforeLayer = existingLayers.some((layer) => layer.id === "water")
      ? "water"
      : undefined;

    map.current.addLayer(
      {
        id: `raster-${activeDataset}`,
        type: "raster",
        source: sourceId,
        paint: {
          "raster-opacity": 0.7,
        },
      },
      beforeLayer
    );
  }, [activeDataset, datasets]);

  return (
    <div className="map-container">
      <div ref={mapContainer} className="map" />
      <div className="map-info">
        {latestData && activeDataset && (
          <div className="latest-info">
            Latest {activeDataset}: {(latestData as any)[activeDataset]?.date || "N/A"}
            {selectedAoiId ? ` | AOI ${selectedAoiId}` : ""} | Zoom {zoom}
          </div>
        )}
      </div>
    </div>
  );
}
