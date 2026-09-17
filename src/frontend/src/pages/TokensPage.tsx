import { useState, useEffect, type ReactElement } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { TokenForm } from "@/components/tokens/TokenForm";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/useToast";
import { useCurrentUser } from "@/hooks/useAuth";
import { canManageCommercial } from "@/lib/permissions";
import { useCreateToken } from "@/hooks/useTokens";
import { ArrowLeft, ArrowRight, Plus, Search } from "lucide-react";

/**
 * Global Tokens inventory — maps to SWA "Tokens Sheet".
 */
export function TokensPage(): ReactElement {
  const [searchParams] = useSearchParams();
  const projectFilter = searchParams.get("project") ?? undefined;
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debounced, setDebounced] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [agreementId, setAgreementId] = useState("");
  const pageSize = 20;
  const { toast } = useToast();
  const { data: user } = useCurrentUser();
  const commercial = canManageCommercial(user);
  const createMutation = useCreateToken();

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["tokens-global", page, debounced, projectFilter],
    queryFn: () =>
      api.listTokens({
        page,
        page_size: pageSize,
        q: debounced || undefined,
        project_id: projectFilter,
      }),
  });

  const { data: agreementsData } = useQuery({
    queryKey: ["agreements-for-tokens"],
    queryFn: () => api.listAgreements({ page: 1, page_size: 100 }),
    enabled: showCreate,
  });
  const agreements = agreementsData?.items ?? [];

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize) || 1);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Tokens</h1>
          <p className="text-sm text-muted-foreground">
            Excel <span className="font-medium">Tokens Sheet</span> — Date, Token ID, Agreement ID,
            Type, Description, Status, Tokens Used, SWA employee, Project owner, Client employee.
          </p>
        </div>
        {commercial && !showCreate ? (
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Token
          </Button>
        ) : null}
      </div>

      {showCreate && commercial ? (
        <div className="space-y-3 rounded-lg border p-4">
          <div className="space-y-2">
            <Label htmlFor="tkn-agreement">Agreement *</Label>
            <select
              id="tkn-agreement"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={agreementId}
              onChange={(e) => setAgreementId(e.target.value)}
            >
              <option value="">Select agreement…</option>
              {agreements.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.reference_id} — {a.service_name} ({a.client_name || "client"})
                </option>
              ))}
            </select>
          </div>
          <TokenForm
            onSubmit={async (formData) => {
              if (!agreementId) {
                toast({ title: "Select an agreement first", variant: "destructive" });
                return;
              }
              try {
                await createMutation.mutateAsync({
                  agreement_id: agreementId,
                  token_date: formData.token_date,
                  token_type: formData.token_type,
                  description: formData.description,
                  token_status: formData.token_status,
                  tokens_used: formData.tokens_used,
                  swa_employee_name: formData.swa_employee_name || undefined,
                  project_owner_name: formData.project_owner_name || undefined,
                  client_employee_name: formData.client_employee_name,
                  project_id: formData.project_id || undefined,
                });
                toast({ title: "Token created" });
                setShowCreate(false);
                setAgreementId("");
                void refetch();
              } catch (err) {
                toast({ title: (err as Error).message, variant: "destructive" });
              }
            }}
            onCancel={() => {
              setShowCreate(false);
              setAgreementId("");
            }}
            isLoading={createMutation.isPending}
          />
        </div>
      ) : null}

      <Card>
        <CardContent className="pt-6">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              className="pl-10"
              placeholder="Search by token ID or description…"
              aria-label="Search tokens by token ID or description"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          {isError && (
            <QueryErrorBanner
              message="Failed to load tokens"
              error={error}
              onRetry={() => void refetch()}
            />
          )}
          {projectFilter ? (
            <p className="mb-3 text-xs text-muted-foreground">
              Filtered to project from quick link.{" "}
              <Link className="underline" to="/tokens">
                Show all tokens
              </Link>
            </p>
          ) : null}

          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Token ID</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Agreement ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Used</TableHead>
                  <TableHead>SWA employee</TableHead>
                  <TableHead>Project owner</TableHead>
                  <TableHead>Client emp.</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Project</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={11} className="text-center text-muted-foreground">
                      Loading…
                    </TableCell>
                  </TableRow>
                ) : items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={11} className="py-8 text-center text-muted-foreground">
                      {debounced || projectFilter ? (
                        <>
                          No tokens match this filter.{" "}
                          <Link className="underline font-medium text-foreground" to="/tokens">
                            Clear filters
                          </Link>
                          .
                        </>
                      ) : (
                        <>
                          No tokens yet. Load sheets with{" "}
                          <code className="rounded bg-muted px-1">make swa-live-local</code>, or open
                          a{" "}
                          <Link className="underline font-medium text-foreground" to="/clients">
                            client
                          </Link>{" "}
                          → agreement to issue the first token.
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((t) => (
                    <TableRow key={t.id} className="hover:bg-muted/40">
                      <TableCell className="font-mono text-xs font-semibold">
                        {t.reference_id}
                      </TableCell>
                      <TableCell className="text-sm whitespace-nowrap">{t.token_date}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {t.agreement_reference_id || "—"}
                      </TableCell>
                      <TableCell>{t.token_type ?? "—"}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{t.token_status}</Badge>
                      </TableCell>
                      <TableCell className="tabular-nums">×{t.tokens_used}</TableCell>
                      <TableCell className="text-sm">
                        {t.swa_employee_name || "—"}
                      </TableCell>
                      <TableCell className="text-sm">
                        {t.project_owner_name || "—"}
                      </TableCell>
                      <TableCell className="text-sm">
                        {t.client_employee_name || "—"}
                      </TableCell>
                      <TableCell className="max-w-[180px] truncate text-sm">
                        {t.description ?? "—"}
                      </TableCell>
                      <TableCell>
                        {t.project_id ? (
                          <Button variant="outline" size="sm" asChild>
                            <Link to={`/projects/${t.project_id}`}>Project</Link>
                          </Button>
                        ) : (
                          "—"
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              {total} token{total !== 1 ? "s" : ""}
            </span>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                aria-label="Previous page"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                aria-label="Next page"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
