import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileText, FolderOpen } from "lucide-react";
import type { DocumentItem, DocumentFolder } from "@/types/document";

export function DocumentsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);

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

  if (!projectId) return null;

  const folders: DocumentFolder[] = foldersData?.items ?? [];
  const documents: DocumentItem[] = data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Documents</h1>
        <Button disabled title="Upload coming soon">
          <Upload className="mr-2 h-4 w-4" />
          Upload
        </Button>
      </div>

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
    </div>
  );
}
