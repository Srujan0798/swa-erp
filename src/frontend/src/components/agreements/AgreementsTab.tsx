import { useState } from "react";
import { useAgreements, useCreateAgreement, useDeleteAgreement } from "@/hooks/useAgreements";
import { useToast } from "@/hooks/useToast";
import { AgreementForm } from "@/components/agreements/AgreementForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, Trash2 } from "lucide-react";

interface AgreementsTabProps {
  clientId: string;
}

export function AgreementsTab({ clientId }: AgreementsTabProps) {
  const [showForm, setShowForm] = useState(false);
  const { toast } = useToast();
  const { data, isLoading } = useAgreements({ client_id: clientId, page_size: 100 });
  const createMutation = useCreateAgreement();
  const deleteMutation = useDeleteAgreement();

  const agreements = data?.items ?? [];

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle>Service Agreements</CardTitle>
        {!showForm && (
          <Button size="sm" onClick={() => setShowForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Agreement
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {showForm && (
          <AgreementForm
            onSubmit={async (formData) => {
              try {
                await createMutation.mutateAsync({
                  client_id: clientId,
                  service_name: formData.service_name,
                  start_date: formData.start_date,
                  end_date: formData.end_date || undefined,
                  total_tokens: formData.total_tokens,
                  status: formData.status,
                  notes: formData.notes,
                });
                toast({ title: "Agreement created" });
                setShowForm(false);
              } catch (err) {
                toast({ title: (err as Error).message, variant: "destructive" });
              }
            }}
            onCancel={() => setShowForm(false)}
            isLoading={createMutation.isPending}
          />
        )}

        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading agreements...</p>
        ) : agreements.length === 0 ? (
          <p className="text-sm text-muted-foreground">No agreements yet for this client.</p>
        ) : (
          <div className="space-y-2">
            {agreements.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between border rounded-md p-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-semibold">{a.reference_id}</span>
                    <Badge variant="secondary">{a.status}</Badge>
                  </div>
                  <div className="text-sm font-medium">{a.service_name}</div>
                  <div className="text-xs text-muted-foreground">
                    {a.start_date}
                    {a.end_date ? ` → ${a.end_date}` : " (open-ended)"}
                    {a.total_tokens != null ? ` · ${a.total_tokens} tokens planned` : ""}
                  </div>
                </div>
                <Button
                  size="icon"
                  variant="ghost"
                  disabled={deleteMutation.isPending}
                  onClick={() => {
                    if (confirm(`Delete agreement ${a.reference_id}?`)) {
                      deleteMutation.mutate(a.id);
                    }
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
