// Sidebar component with controls and charts.

import { useAOIs, useTimeseries, useDatasets } from "@/hooks";
import TimeseriesChart from "@/components/TimeseriesChart";
import AOIManager from "@/components/AOIManager";

interface SidebarProps {
  selectedAoiId: number | null;
  onAoiSelect: (id: number) => void;
  activeDataset: string;
  onDatasetChange: (dataset: string) => void;
}

export default function Sidebar({
  selectedAoiId,
  onAoiSelect,
  activeDataset,
  onDatasetChange,
}: SidebarProps) {
  const { data: aois = [] } = useAOIs();
  const { data: datasets = [] } = useDatasets();
  const today = new Date().toISOString().split("T")[0];
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split("T")[0];

  const { data: timeseriesData } = useTimeseries(
    activeDataset,
    selectedAoiId,
    thirtyDaysAgo,
    today
  );

  return (
    <div className="sidebar">
      <div className="sidebar-section">
        <h2>EcoSat Monitor</h2>
        <p className="subtitle">Live Satellite Environmental Intelligence</p>
      </div>

      <div className="sidebar-section">
        <h3>Area of Interest</h3>
        <AOIManager
          aois={aois}
          selectedAoiId={selectedAoiId}
          onSelect={onAoiSelect}
        />
      </div>

      <div className="sidebar-section">
        <h3>Dataset</h3>
        <select
          value={activeDataset}
          onChange={(e) => onDatasetChange(e.target.value)}
          className="dataset-select"
        >
          {datasets.map((ds) => (
            <option key={ds.data_type} value={ds.data_type}>
              {ds.name}
            </option>
          ))}
        </select>
        {datasets.find((d) => d.data_type === activeDataset) && (
          <div className="dataset-info">
            <p>
              {
                datasets.find((d) => d.data_type === activeDataset)
                  ?.description
              }
            </p>
            <small>
              Resolution:{" "}
              {
                datasets.find((d) => d.data_type === activeDataset)
                  ?.spatial_resolution
              }
            </small>
          </div>
        )}
      </div>

      {selectedAoiId && timeseriesData && (
        <div className="sidebar-section">
          <h3>Time-Series Chart</h3>
          <TimeseriesChart
            data={timeseriesData}
            title={activeDataset.toUpperCase()}
          />
        </div>
      )}

      <div className="sidebar-footer">
        <small>
          Data sources: ESA Copernicus, NASA USGS, WHO GDAC, Powered by Google
          Earth Engine
        </small>
      </div>
    </div>
  );
}
