import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { INCIDENTS } from "@/lib/incidents-data";
import { useLiveIncidents } from "@/lib/api/useLiveIncidents";
import { TopBar } from "@/components/dashboard/TopBar";
import { IncidentSidebar } from "@/components/dashboard/IncidentSidebar";
import { IncidentMainStage } from "@/components/dashboard/IncidentMainStage";
import { BobInspector } from "@/components/dashboard/BobInspector";
import { AnnotateProvider } from "@/components/dashboard/annotate-context";
import { AnnotateOverlay } from "@/components/dashboard/AnnotateOverlay";

export const Route = createFileRoute("/")({
  component: DashboardPage,
  head: () => ({
    meta: [
      { title: "Boogle — Security Incident Console" },
      { name: "description", content: "Tactical incident triage with attack path, Bob AI remediation, and correlated evidence." },
    ],
  }),
});

function DashboardPage() {
  const { incidents, newIds, status, scanning, triggerScan, clearAll } = useLiveIncidents(INCIDENTS);
  const [selectedId, setSelectedId] = useState(INCIDENTS[0].id);
  const incident = incidents.find((i) => i.id === selectedId) ?? incidents[0];

  return (
    <AnnotateProvider>
      <div className="flex flex-col h-screen w-full bg-background text-foreground">
        <TopBar />
        <div className="flex flex-1 min-h-0">
          <IncidentSidebar
            incidents={incidents}
            selectedId={selectedId}
            onSelect={setSelectedId}
            newIds={newIds}
            status={status}
            scanning={scanning}
            onScan={(path) => triggerScan(path)}
            onClear={clearAll}
          />
          <main className="flex-1 flex flex-col min-w-0">
            {incident && <IncidentMainStage incident={incident} />}
          </main>
        </div>
        <BobInspector />
        <AnnotateOverlay />
      </div>
    </AnnotateProvider>
  );
}
