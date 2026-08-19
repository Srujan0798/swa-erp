import { useState } from "react";
import { useDocumentReferences, useCreateDocumentReference, useDeleteDocumentReference } from "@/hooks/useDocumentReferences";
import { useToast } from "@/hooks/useToast";
import { DocumentReferenceForm } from "@/components/documentRefs/DocumentReferenceForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useCurrentUser } from "@/hooks/useAuth";
import { canWrite } from "@/lib/permissions";
import { Plus, Trash2 } from "lucide-react";

interface DocumentReferenceListProps {
  projectId: string;
  tokenId?: string;
}

export function DocumentReferenceList({ projectId, tokenId }: DocumentReferenceListProps) {
  const [showForm, setShowForm] = useState(false);
  const { toast } = useToast();
  const { data: user } = useCurrentUser();
  const write = canWrite(user);
  const { data, isLoading } = useDocumentReferences({
    project_id: projectId,
    token_id: tokenId,
    page_size: 100,
  });
  const createMutation = useCreateDocumentReference();
  const deleteMutation = useDeleteDocumentReference();

  const docs = data?.items ?? [];

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle>Document References {tokenId ? "(filtered by Token)" : ""}</CardTitle>
        {!showForm && write ? (
          <Button size="sm" onClick={() => setShowForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Document Reference
          </Button>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-4">
        {showForm && write ? (
          <DocumentReferenceForm
            projectId={projectId}
            initialData={tokenId ? { token_id: tokenId } : undefined}
            onSubmit={async (formData) => {
              try {
                await createMutation.mutateAsync({
                  project_id: projectId,
                  token_id: formData.token_id || tokenId || undefined,
                  doc_date: formData.doc_date,
                  document_type: formData.document_type,
                  type: formData.type,
                  user_ref: formData.user_ref,
                  description: formData.description,
                  revision: formData.revision,
                  status: formData.status,
                  remarks: formData.remarks,
                });
                toast({ title: "Document reference created" });
                setShowForm(false);
              } catch (err) {
                toast({ title: (err as Error).message, variant: "destructive" });
              }
            }}
            onCancel={() => setShowForm(false)}
            isLoading={createMutation.isPending}
          />
        ) : null}

        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading document references...</p>
        ) : docs.length === 0 ? (
          <p className="text-sm text-muted-foreground">No document references yet.</p>
        ) : (
          <div className="space-y-2">
            {docs.map((d) => (
              <div
                key={d.id}
                className="flex items-center justify-between border rounded-md p-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-semibold">{d.reference_id}</span>
                    <Badge variant="secondary">{d.document_type}</Badge>
                    <Badge variant="outline">{d.revision}</Badge>
                    <Badge>{d.status}</Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {d.doc_date}
                    {d.user_ref ? ` · ${d.user_ref}` : ""}
                    {d.type ? ` · ${d.type}` : ""}
                  </div>
                  {d.description && (
                    <div className="text-sm line-clamp-1">{d.description}</div>
                  )}
                </div>
                {write ? (
                  <Button
                    size="icon"
                    variant="ghost"
                    disabled={deleteMutation.isPending}
                    aria-label={`Delete document reference ${d.reference_id}`}
                    onClick={() => {
                      if (confirm(`Delete document reference ${d.reference_id}?`)) {
                        deleteMutation.mutate(d.id);
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
