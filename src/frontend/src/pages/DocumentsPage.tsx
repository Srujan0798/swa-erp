import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileText, FolderOpen } from "lucide-react";
import type { DocumentItem, DocumentFolder } from "@/types/document";

/**
 * Global Documents nav: pick a project, then browse file documents.
 * Document *references* (DRN) live on each Project → Documents tab.
 */
export function DocumentsPage() {
  const { projectId: routeProjectId } = useParams<{ projectId: string }>();
  const [selectedProjectId, setSelectedProjectId] = useState<string>(routeProjectId ?? "");
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);

  const projectId = routeProjectId || selectedProjectId;

  const { data: projectsData } = useQuery({
    queryKey: ["projects-for-docs"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
    enabled: !routeProjectId,
  });

  const { data, isLoading } = useQuery({
    queryKey: ["documents", projectId, selectedFolderId],
    queryFn: () => api.listDocuments(projectId!, { folder_id: selectedFolderId ?? undefined }),
    enabled: !!projectId,
  });

  const { data: foldersData } = useQuery({
    queryKey: ["folders", projectId, selectedFolderId],
    queryFn: () => api.listFolders(projectId!, selectedFolderId ?? undefined),
    enabled: !!projectId,
  });

  const projects = projectsData?.items ?? [];
  const folders: DocumentFolder[] = foldersData?.items ?? [];
  const documents: DocumentItem[] = data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">File documents</h1>
          <p className="text-sm text-muted-foreground">
            Uploaded files per project. For DRN/DBR document references, open a Project → Documents.
          </p>
        </div>
        <Button disabled title="Open a project and use the project Documents area for file uploads">
          <Upload className="mr-2 h-4 w-4" />
          Upload (via project)
        </Button>
      </div>

      {!routeProjectId && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Select project</CardTitle>
          </CardHeader>
          <CardContent>
            {projects.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No projects yet. Import Excel projects or create one under{" "}
                <Link className="underline" to="/projects">
                  Projects
                </Link>
                .
              </p>
            ) : (
              <select
                className="w-full max-w-md rounded border px-3 py-2 text-sm"
                value={selectedProjectId}
                onChange={(e) => {
                  setSelectedProjectId(e.target.value);
                  setSelectedFolderId(null);
                }}
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
      )}

      {!projectId ? null : (
        <div className="grid grid-cols-4 gap-6">
          <div className="col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Folders</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                <button
                  type="button"
                  className={`flex w-full items-center gap-2 rounded px-2 py-1 text-sm ${
                    selectedFolderId === null ? "bg-accent" : "hover:bg-accent/50"
                  }`}
                  onClick={() => setSelectedFolderId(null)}
                >
                  <FolderOpen className="h-4 w-4" />
                  All Documents
                </button>
                {folders.map((folder) => (
                  <button
                    key={folder.id}
                    type="button"
                    className={`flex w-full items-center gap-2 rounded px-2 py-1 text-sm ${
                      selectedFolderId === folder.id ? "bg-accent" : "hover:bg-accent/50"
                    }`}
                    onClick={() => setSelectedFolderId(folder.id)}
                  >
                    <FolderOpen className="h-4 w-4" />
                    {folder.name}
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="col-span-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Files</CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <p className="text-sm text-muted-foreground">Loading...</p>
                ) : documents.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No documents in this folder.</p>
                ) : (
                  <div className="space-y-2">
                    {documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="flex items-center justify-between rounded border p-3"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <div className="text-sm font-medium">{doc.name}</div>
                            <div className="text-xs text-muted-foreground">
                              {doc.content_type} · {(doc.file_size / 1024).toFixed(1)} KB
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
