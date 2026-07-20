import { useState } from "react";
import { useTokens, useCreateToken, useDeleteToken } from "@/hooks/useTokens";
import { useToast } from "@/hooks/useToast";
import { TokenForm } from "@/components/tokens/TokenForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, Trash2 } from "lucide-react";

interface TokensListProps {
  agreementId: string;
}

export function TokensList({ agreementId }: TokensListProps) {
  const [showForm, setShowForm] = useState(false);
  const { toast } = useToast();
  const { data, isLoading } = useTokens({ agreement_id: agreementId, page_size: 100 });
  const createMutation = useCreateToken();
  const deleteMutation = useDeleteToken();

  const tokens = data?.items ?? [];

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle>Tokens</CardTitle>
        {!showForm && (
          <Button size="sm" onClick={() => setShowForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Token
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {showForm && (
          <TokenForm
            onSubmit={async (formData) => {
              try {
                await createMutation.mutateAsync({
                  agreement_id: agreementId,
                  token_date: formData.token_date,
                  token_type: formData.token_type,
                  description: formData.description,
                  token_status: formData.token_status,
                  tokens_used: formData.tokens_used,
                  client_employee_name: formData.client_employee_name,
                  project_id: formData.project_id || undefined,
                });
                toast({ title: "Token created" });
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
          <p className="text-sm text-muted-foreground">Loading tokens...</p>
        ) : tokens.length === 0 ? (
          <p className="text-sm text-muted-foreground">No tokens yet for this agreement.</p>
        ) : (
          <div className="space-y-2">
            {tokens.map((t) => (
              <div
                key={t.id}
                className="flex items-center justify-between border rounded-md p-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-base font-bold">{t.reference_id}</span>
                    <Badge variant="secondary">{t.token_status}</Badge>
                    <span className="text-xs text-muted-foreground">×{t.tokens_used}</span>
                  </div>
                  <div className="text-sm">
                    {t.token_type ?? "Token"} · {t.token_date}
                    {t.client_employee_name ? ` · ${t.client_employee_name}` : ""}
                  </div>
                  {t.description && (
                    <div className="text-xs text-muted-foreground line-clamp-1">{t.description}</div>
                  )}
                </div>
                <Button
                  size="icon"
                  variant="ghost"
                  disabled={deleteMutation.isPending}
                  onClick={() => {
                    if (confirm(`Delete token ${t.reference_id}?`)) {
                      deleteMutation.mutate(t.id);
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
