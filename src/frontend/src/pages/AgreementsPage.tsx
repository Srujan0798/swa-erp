import { useState, useEffect, type ReactElement } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAgreements, useCreateAgreement } from "@/hooks/useAgreements";
import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { AgreementForm } from "@/components/agreements/AgreementForm";
import { useToast } from "@/hooks/useToast";
import { useCurrentUser } from "@/hooks/useAuth";
import { canManageCommercial } from "@/lib/permissions";
import { ArrowLeft, ArrowRight, Plus, Search } from "lucide-react";

/**
 * Global Service Agreements inventory — maps to SWA "Service Agreements Sheet".
 */
export function AgreementsPage(): ReactElement {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debounced, setDebounced] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [clientId, setClientId] = useState("");
  const pageSize = 20;
  const { toast } = useToast();
  const { data: user } = useCurrentUser();
  const commercial = canManageCommercial(user);
  const createMutation = useCreateAgreement();

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { data, isLoading, isError, error, refetch } = useAgreements({
    page,
    page_size: pageSize,
    q: debounced || undefined,
  });
  const { data: clientsData } = useQuery({
    queryKey: ["clients-for-agreements"],
    queryFn: () => api.listClients({ page: 1, page_size: 100 }),
    enabled: showCreate,
  });
  const clients = clientsData?.items ?? [];

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize) || 1);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Service Agreements</h1>
          <p className="text-sm text-muted-foreground">
            Excel <span className="font-medium">Service Agreements Sheet</span> — Agreement ID, Client,
            Inquiry, Service Name (e.g. INSUDESIGN), Start/End, Total Tokens, Status, Notes.
          </p>
        </div>
        {commercial && !showCreate ? (
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Agreement
          </Button>
        ) : null}
      </div>

      {showCreate && commercial ? (
        <div className="space-y-3 rounded-lg border p-4">
          <div className="space-y-2">
            <Label htmlFor="sa-client">Client *</Label>
            <select
              id="sa-client"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
            >
              <option value="">Select client…</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} — {c.name}
                </option>
              ))}
            </select>
          </div>
          <AgreementForm
            initialData={{ service_name: "INSUDESIGN" }}
            onSubmit={async (formData) => {
              if (!clientId) {
                toast({ title: "Select a client first", variant: "destructive" });
                return;
              }
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
                setShowCreate(false);
                setClientId("");
                void refetch();
              } catch (err) {
                toast({ title: (err as Error).message, variant: "destructive" });
              }
            }}
            onCancel={() => {
              setShowCreate(false);
              setClientId("");
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
              placeholder="Search by reference ID or service name…"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          {isError && (
            <QueryErrorBanner
              message="Failed to load agreements"
              error={error}
              onRetry={() => void refetch()}
            />
          )}

          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Agreement ID</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Start</TableHead>
                  <TableHead>End</TableHead>
                  <TableHead>Tokens</TableHead>
                  <TableHead>Notes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground">
                      Loading…
                    </TableCell>
                  </TableRow>
                ) : items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="py-8 text-center text-muted-foreground">
                      {debounced ? (
                        <>No agreements match “{debounced}”. Try another reference or service name.</>
                      ) : (
                        <>
                          No service agreements yet. Load sheets with{" "}
                          <code className="rounded bg-muted px-1">make swa-live-local</code>, or open
                          a{" "}
                          <Link className="underline font-medium text-foreground" to="/clients">
                            client
                          </Link>{" "}
                          → Service agreements to add a retainer (e.g. INSUDESIGN).
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((a) => (
                    <TableRow key={a.id} className="hover:bg-muted/40">
                      <TableCell className="font-mono text-xs font-semibold">
                        {a.reference_id}
                      </TableCell>
                      <TableCell>
                        <Link
                          className="text-sm font-medium text-primary underline-offset-2 hover:underline"
                          to={`/clients/${a.client_id}`}
                        >
                          {a.client_name || "Open client"}
                        </Link>
                      </TableCell>
                      <TableCell className="font-medium">{a.service_name}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{a.status}</Badge>
                      </TableCell>
                      <TableCell className="text-sm whitespace-nowrap">{a.start_date}</TableCell>
                      <TableCell className="text-sm whitespace-nowrap">
                        {a.end_date ?? "—"}
                      </TableCell>
                      <TableCell className="tabular-nums">{a.total_tokens ?? "—"}</TableCell>
                      <TableCell className="max-w-[160px] truncate text-xs text-muted-foreground">
                        {a.notes ?? "—"}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              {total} agreement{total !== 1 ? "s" : ""}
            </span>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
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
