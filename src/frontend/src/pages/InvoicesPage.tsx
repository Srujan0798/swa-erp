"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
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
import { api } from "@/lib/api";
import type { Invoice } from "@/types/financial";

const STATUS_BADGE: Record<
  string,
  { label: string; variant: "default" | "secondary" | "destructive" | "outline" }
> = {
  draft: { label: "Draft", variant: "outline" },
  sent: { label: "Sent", variant: "default" },
  paid: { label: "Paid", variant: "secondary" },
  cancelled: { label: "Cancelled", variant: "destructive" },
};

export function InvoicesPage() {
  const queryClient = useQueryClient();
  const [projectId, setProjectId] = useState("");
  const [status, setStatus] = useState("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: projectsData } = useQuery({
    queryKey: ["projects-for-invoices"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

  const { data, isLoading, isError, error } = useQuery({
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
        <Button disabled={!projectId} title={!projectId ? "Select a project first" : undefined}>
          New Invoice
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Select value={projectId || undefined} onValueChange={setProjectId}>
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
          onClick={() => queryClient.invalidateQueries({ queryKey: ["invoices"] })}
        >
          Refresh
        </Button>
      </div>

      {!projectId ? (
        <p className="text-sm text-muted-foreground">
          Select a project to load invoices.
        </p>
      ) : isError ? (
        <p className="text-sm text-destructive">
          Failed to load invoices: {(error as Error)?.message ?? "API error"}
        </p>
      ) : (
        <div className="rounded-md border">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40">
                <th className="px-3 py-2 text-left">ID</th>
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
                    <td className="px-3 py-2 font-mono text-xs">{inv.id.slice(0, 8)}…</td>
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
                  <td colSpan={4} className="px-3 py-6 text-center text-sm text-muted-foreground">
                    No invoices for this project yet.
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
            <pre className="max-h-80 overflow-auto rounded bg-muted p-3 text-xs">
              {JSON.stringify(detail, null, 2)}
            </pre>
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
    </div>
  );
}
