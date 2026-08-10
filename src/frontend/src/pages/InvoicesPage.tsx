"use client";

import { useEffect, useState, type ReactElement } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { InvoiceCreateForm } from "@/components/financials/InvoiceCreateForm";
import { useCurrentUser } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import type { Invoice } from "@/types/financial";
import { Plus } from "lucide-react";

const STATUS_BADGE: Record<
  string,
  { label: string; variant: "default" | "secondary" | "destructive" | "outline" }
> = {
  draft: { label: "Draft", variant: "outline" },
  sent: { label: "Sent", variant: "default" },
  paid: { label: "Paid", variant: "secondary" },
  cancelled: { label: "Cancelled", variant: "destructive" },
};

export function InvoicesPage(): ReactElement {
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const [projectId, setProjectId] = useState(searchParams.get("project") ?? "");
  const [status, setStatus] = useState("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const { data: user } = useCurrentUser();
  const canCreate = user?.role !== "viewer";

  useEffect(() => {
    const fromUrl = searchParams.get("project") ?? "";
    if (fromUrl !== projectId && fromUrl) {
      setProjectId(fromUrl);
    }
    // Sync when URL changes (e.g. project quick-link)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const setProject = (id: string): void => {
    setProjectId(id);
    if (id) setSearchParams({ project: id }, { replace: true });
    else setSearchParams({}, { replace: true });
  };

  const {
    data: projectsData,
    isError: projectsError,
    error: projectsErr,
    refetch: refetchProjects,
  } = useQuery({
    queryKey: ["projects-for-invoices"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["invoices", projectId, status],
    enabled: !!projectId,
    queryFn: async () =>
      api.listProjectInvoices(projectId, {
        page: 1,
        page_size: 100,
        status: status === "all" ? undefined : status,
      }),
  });

  const { data: detail } = useQuery({
    queryKey: ["invoice", selectedId],
    enabled: !!selectedId,
    queryFn: async () => api.getInvoice(selectedId as string),
  });

  const rows = (data as { items?: Invoice[] } | undefined)?.items ?? [];
  const statuses = Object.keys(STATUS_BADGE);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Invoices</h1>
          <p className="text-sm text-muted-foreground">
            Billing per project (GST fields on invoice record).
          </p>
        </div>
        {canCreate ? (
          <Button
            disabled={!projectId}
            title={!projectId ? "Select a project first" : undefined}
            onClick={() => setCreateOpen(true)}
          >
            <Plus className="mr-2 h-4 w-4" />
            New Invoice
          </Button>
        ) : null}
      </div>

      {projectsError && (
        <QueryErrorBanner
          message="Failed to load projects"
          error={projectsErr}
          onRetry={() => void refetchProjects()}
        />
      )}

      <div className="flex flex-wrap items-center gap-2">
        <Select value={projectId || undefined} onValueChange={setProject}>
          <SelectTrigger className="w-80">
            <SelectValue placeholder="Select project" />
          </SelectTrigger>
          <SelectContent>
            {projects.map((p) => (
              <SelectItem key={p.id} value={p.id}>
                {p.code} — {p.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All status</SelectItem>
            {statuses.map((s) => (
              <SelectItem key={s} value={s}>
                {STATUS_BADGE[s]?.label ?? s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            void queryClient.invalidateQueries({ queryKey: ["invoices"] });
            void refetch();
          }}
        >
          Refresh
        </Button>
      </div>

      {!projectId ? (
        <div className="rounded-md border border-dashed p-8 text-center">
          <p className="text-sm text-muted-foreground">
            Select a project to load invoices
            {canCreate ? ", then create a draft with line items." : "."} From a
            project page, use the <strong>Invoices</strong> quick link.
          </p>
        </div>
      ) : isError ? (
        <QueryErrorBanner
          message="Failed to load invoices"
          error={error}
          onRetry={() => void refetch()}
        />
      ) : (
        <div className="rounded-md border">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-3 py-2 text-left">Number</th>
                <th className="px-3 py-2 text-left">Status</th>
                <th className="px-3 py-2 text-right">Total</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td colSpan={4} className="px-3 py-6 text-center text-muted-foreground">
                    Loading…
                  </td>
                </tr>
              )}
              {rows.map((inv: Invoice) => {
                const badge = STATUS_BADGE[inv.status] ?? {
                  label: inv.status,
                  variant: "outline" as const,
                };
                const total =
                  (inv as { total?: number }).total ??
                  Number(inv.subtotal) + Number(inv.tax_amount);
                return (
                  <tr key={inv.id} className="border-b last:border-0">
                    <td className="px-3 py-2 font-mono text-xs">
                      {inv.invoice_number ?? inv.id.slice(0, 8)}
                    </td>
                    <td className="px-3 py-2">
                      <Badge variant={badge.variant}>{badge.label}</Badge>
                    </td>
                    <td className="px-3 py-2 text-right font-medium">
                      ₹{Number(total).toLocaleString("en-IN")}
                    </td>
                    <td className="px-3 py-2 text-right">
                      <Button variant="outline" size="sm" onClick={() => setSelectedId(inv.id)}>
                        View
                      </Button>
                    </td>
                  </tr>
                );
              })}
              {!isLoading && rows.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-3 py-8 text-center text-sm text-muted-foreground">
                    No invoices for this project yet.
                    {canCreate ? (
                      <>
                        {" "}
                        <button
                          type="button"
                          className="underline font-medium text-foreground"
                          onClick={() => setCreateOpen(true)}
                        >
                          Create the first invoice
                        </button>
                        .
                      </>
                    ) : null}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <Dialog
        open={!!selectedId}
        onOpenChange={(o) => {
          if (!o) setSelectedId(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Invoice detail</DialogTitle>
          </DialogHeader>
          {detail ? (
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-muted-foreground">Number</p>
                  <p className="font-mono font-medium">{detail.invoice_number}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Status</p>
                  <p className="capitalize">{detail.status}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Total</p>
                  <p className="font-medium">
                    ₹{Number(detail.total).toLocaleString("en-IN")}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Due</p>
                  <p>{detail.due_date ?? "—"}</p>
                </div>
              </div>
              {detail.items?.length ? (
                <div className="rounded border">
                  <table className="min-w-full text-xs">
                    <thead>
                      <tr className="border-b bg-muted/40">
                        <th className="px-2 py-1 text-left">Description</th>
                        <th className="px-2 py-1 text-right">Qty</th>
                        <th className="px-2 py-1 text-right">Rate</th>
                        <th className="px-2 py-1 text-right">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.items.map((item) => (
                        <tr key={item.id} className="border-b last:border-0">
                          <td className="px-2 py-1">{item.description}</td>
                          <td className="px-2 py-1 text-right">{Number(item.quantity)}</td>
                          <td className="px-2 py-1 text-right">
                            ₹{Number(item.rate).toLocaleString("en-IN")}
                          </td>
                          <td className="px-2 py-1 text-right">
                            ₹{Number(item.amount).toLocaleString("en-IN")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}
              {detail.notes ? (
                <p className="text-muted-foreground">Notes: {detail.notes}</p>
              ) : null}
              {detail.project_id ? (
                <Link
                  className="text-xs underline text-muted-foreground"
                  to={`/projects/${detail.project_id}`}
                >
                  Open project
                </Link>
              ) : null}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Loading…</p>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedId(null)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>New invoice</DialogTitle>
          </DialogHeader>
          {projectId ? (
            <InvoiceCreateForm
              projectId={projectId}
              onSuccess={() => {
                setCreateOpen(false);
                void refetch();
              }}
              onCancel={() => setCreateOpen(false)}
            />
          ) : (
            <p className="text-sm text-muted-foreground">Select a project first.</p>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
