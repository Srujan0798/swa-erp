import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ComplianceDashboard } from "@/components/compliance/ComplianceDashboard";
import { ComplianceChecklist } from "@/components/compliance/ComplianceChecklist";
import { useStandards } from "@/hooks/useCompliance";
import { api } from "@/lib/api";
import { ArrowLeft } from "lucide-react";

/**
 * Global Compliance nav: pick a project, then run NBC/ECBC/IGBC/IS checklists.
 * (Previously required /projects/:id and returned blank from the sidebar link.)
 */
export function CompliancePage() {
  const [projectId, setProjectId] = useState("");
  const [selectedStandard, setSelectedStandard] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const { data: standards = [] } = useStandards();

  const { data: projectsData, isLoading, isError } = useQuery({
    queryKey: ["projects-for-compliance"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

  const handleSelectStandard = (standardName: string) => {
    const std = standards.find((s) => s.name === standardName);
    if (std) {
      setSelectedStandard({ id: std.id, name: std.name });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Compliance</h1>
        <p className="text-sm text-muted-foreground">
          NBC / ECBC / IGBC / IS checklists per project.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Select project</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <p className="text-sm text-muted-foreground">Loading projects…</p>
          )}
          {isError && (
            <p className="text-sm text-destructive">
              Failed to load projects. Check API / login.
            </p>
          )}
          {!isLoading && !isError && projects.length === 0 && (
            <p className="text-sm text-muted-foreground">
              No projects yet.{" "}
              <Link className="underline" to="/projects">
                Create or import projects
              </Link>
              , then return here.
            </p>
          )}
          {projects.length > 0 && (
            <select
              className="w-full max-w-lg rounded-md border bg-background px-3 py-2 text-sm"
              value={projectId}
              onChange={(e) => {
                setProjectId(e.target.value);
                setSelectedStandard(null);
              }}
            >
              <option value="">— choose project —</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.code} — {p.name}
                </option>
              ))}
            </select>
          )}
        </CardContent>
      </Card>

      {projectId && (
        <>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setProjectId("");
                setSelectedStandard(null);
              }}
            >
              <ArrowLeft className="mr-1 h-4 w-4" />
              Change project
            </Button>
            <span className="mx-1">·</span>
            <Link className="hover:underline" to={`/projects/${projectId}`}>
              Open project detail
            </Link>
          </div>

          {selectedStandard ? (
            <ComplianceChecklist
              projectId={projectId}
              standardId={selectedStandard.id}
              standardName={selectedStandard.name}
              onBack={() => setSelectedStandard(null)}
            />
          ) : (
            <ComplianceDashboard
              projectId={projectId}
              onSelectStandard={handleSelectStandard}
            />
          )}
        </>
      )}
    </div>
  );
}
