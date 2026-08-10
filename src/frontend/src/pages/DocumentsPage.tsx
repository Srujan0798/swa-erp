import { useEffect, useState, type ReactElement } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { FileBrowser } from "@/components/documents/FileBrowser";

/**
 * Global Documents nav: pick a project, then browse/upload via FileBrowser.
 * Document *references* (DRN) live on each Project → Documents tab.
 */
export function DocumentsPage(): ReactElement {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedProjectId, setSelectedProjectId] = useState(
    searchParams.get("project") ?? "",
  );

  useEffect(() => {
    const fromUrl = searchParams.get("project") ?? "";
    if (fromUrl !== selectedProjectId) setSelectedProjectId(fromUrl);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const setProject = (id: string): void => {
    setSelectedProjectId(id);
    if (id) setSearchParams({ project: id }, { replace: true });
    else setSearchParams({}, { replace: true });
  };

  const {
    data: projectsData,
    isError: projectsError,
    error: projectsErr,
    refetch: refetchProjects,
  } = useQuery({
    queryKey: ["projects-for-docs"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });

  const projects = projectsData?.items ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">File documents</h1>
        <p className="text-sm text-muted-foreground">
          Upload and browse project files. For DRN/DBR document references, open a Project →
          Documents tab.
        </p>
      </div>

      {projectsError && (
        <QueryErrorBanner
          message="Failed to load projects"
          error={projectsErr}
          onRetry={() => void refetchProjects()}
        />
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Select project</CardTitle>
        </CardHeader>
        <CardContent>
          {projects.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No projects yet. Import Excel or create one under{" "}
              <Link className="underline" to="/projects">
                Projects
              </Link>
              .
            </p>
          ) : (
            <select
              className="w-full max-w-md rounded border px-3 py-2 text-sm"
              value={selectedProjectId}
              onChange={(e) => setProject(e.target.value)}
            >
              <option value="">— choose project —</option>
              {projects.map((p: { id: string; name: string; code?: string }) => (
                <option key={p.id} value={p.id}>
                  {p.code ? `${p.code} — ` : ""}
                  {p.name}
                </option>
              ))}
            </select>
          )}
        </CardContent>
      </Card>

      {!selectedProjectId ? (
        <div className="rounded-md border border-dashed p-8 text-center text-sm text-muted-foreground">
          Select a project to browse and upload files.
        </div>
      ) : (
        <FileBrowser projectId={selectedProjectId} />
      )}
    </div>
  );
}
