"""AOI Manager component."""

import { useState } from "react";
import { useCreateAOI, useDeleteAOI } from "@/hooks";
import { AOI } from "@/types";

interface AOIManagerProps {
  aois: AOI[];
  selectedAoiId: number | null;
  onSelect: (id: number) => void;
}

export default function AOIManager({
  aois,
  selectedAoiId,
  onSelect,
}: AOIManagerProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [newAoiName, setNewAoiName] = useState("");
  const { mutate: createAOI } = useCreateAOI();
  const { mutate: deleteAOI } = useDeleteAOI();

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAoiName.trim()) return;

    // In production, would use map drawing tool to get geometry
    const dummyGeometry = {
      type: "Polygon",
      coordinates: [
        [
          [0, 0],
          [1, 0],
          [1, 1],
          [0, 1],
          [0, 0],
        ],
      ],
    };

    createAOI(
      { name: newAoiName, geometry: dummyGeometry },
      {
        onSuccess: () => {
          setNewAoiName("");
          setIsCreating(false);
        },
      }
    );
  };

  return (
    <div className="aoi-manager">
      <select
        value={selectedAoiId || ""}
        onChange={(e) => onSelect(parseInt(e.target.value))}
        className="aoi-select"
      >
        <option value="">-- Select AOI --</option>
        {aois.map((aoi) => (
          <option key={aoi.id} value={aoi.id}>
            {aoi.name}
          </option>
        ))}
      </select>

      {isCreating ? (
        <form onSubmit={handleCreate} className="aoi-form">
          <input
            type="text"
            placeholder="AOI Name"
            value={newAoiName}
            onChange={(e) => setNewAoiName(e.target.value)}
            className="aoi-input"
          />
          <div className="form-buttons">
            <button type="submit" className="btn-primary">
              Create
            </button>
            <button
              type="button"
              onClick={() => setIsCreating(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <button
          onClick={() => setIsCreating(true)}
          className="btn-primary"
        >
          + New AOI
        </button>
      )}

      {selectedAoiId && (
        <button
          onClick={() => deleteAOI(selectedAoiId)}
          className="btn-danger"
        >
          Delete AOI
        </button>
      )}
    </div>
  );
}
