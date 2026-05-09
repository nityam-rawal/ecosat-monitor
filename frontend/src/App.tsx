// Main React App component.

import { useState } from "react";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import Map from "@/components/Map";
import Sidebar from "@/components/Sidebar";
import AlertPanel from "@/components/AlertPanel";
import "./App.css";

const queryClient = new QueryClient();

export default function App() {
  const [selectedAoiId, setSelectedAoiId] = useState<number | null>(null);
  const [activeDataset, setActiveDataset] = useState<string>("ndvi");

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app-container">
        <Sidebar
          selectedAoiId={selectedAoiId}
          onAoiSelect={setSelectedAoiId}
          activeDataset={activeDataset}
          onDatasetChange={setActiveDataset}
        />
        <div className="main-content">
          <Map
            selectedAoiId={selectedAoiId}
            activeDataset={activeDataset}
          />
          <AlertPanel aoiId={selectedAoiId} />
        </div>
      </div>
    </QueryClientProvider>
  );
}
