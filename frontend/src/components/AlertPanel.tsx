// Alert panel component.

import { useAlerts, useResolveAlert } from "@/hooks";
import { Alert } from "@/types";

interface AlertPanelProps {
  aoiId: number | null;
}

const SEVERITY_COLORS = {
  low: "#60a5fa",
  medium: "#f59e0b",
  high: "#ef4444",
  critical: "#dc2626",
};

export default function AlertPanel({ aoiId }: AlertPanelProps) {
  const { data: alerts = [] } = useAlerts(aoiId || undefined);
  const { mutate: resolveAlert } = useResolveAlert();

  if (!aoiId) {
    return (
      <div className="alert-panel">
        <p className="empty-state">Select an AOI to view alerts</p>
      </div>
    );
  }

  return (
    <div className="alert-panel">
      <h3>Active Alerts ({alerts.length})</h3>
      {alerts.length === 0 ? (
        <p className="empty-state">No active alerts</p>
      ) : (
        <div className="alerts-list">
          {alerts.map((alert: Alert) => (
            <div
              key={alert.id}
              className="alert-item"
              style={{
                borderLeft: `4px solid ${SEVERITY_COLORS[alert.severity]}`,
              }}
            >
              <div className="alert-header">
                <span className="alert-type">{alert.alert_type}</span>
                <span
                  className="alert-severity"
                  style={{
                    backgroundColor: SEVERITY_COLORS[alert.severity],
                  }}
                >
                  {alert.severity}
                </span>
              </div>
              <p className="alert-description">{alert.description}</p>
              <small className="alert-meta">
                {new Date(alert.detected_at).toLocaleDateString()} •{" "}
                {(alert.confidence_score * 100).toFixed(0)}% confidence
              </small>
              <button
                onClick={() => resolveAlert(alert.id)}
                className="btn-resolve"
              >
                Resolve
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
