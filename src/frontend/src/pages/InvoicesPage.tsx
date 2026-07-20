"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { Invoice } from "@/types/financial";

const STATUS_BADGE: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  draft: { label: "Draft", variant: "outline" },
  sent: { label: "Sent", variant: "default" },
  paid: { label: "Paid", variant: "secondary" },
  cancelled: { label: "Cancelled", variant: "destructive" },
};

export function InvoicesPage() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({ projectId: "", q: "", status: "" });
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["invoices", filters.projectId, filters.q, filters.status],
    queryFn: async () => api.listProjectInvoices(filters.projectId, { page: 1, page_size: 100, status: filters.status || undefined }),
  });

  const { data: detail } = useQuery({
    queryKey: ["invoice", selectedId],
    enabled: !!selectedId,
    queryFn: async () => api.getInvoice(selectedId as string),
  });

  const setFilter = (patch: Partial<{ projectId: string; q: string; status: string }>) => setFilters((f) => ({ ...f, ...patch }));
  const rows = (data as { items?: Invoice[] } | undefined)?.items ?? [];
  const statuses = Object.keys(STATUS_BADGE);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Invoices</h1>
          <p className="text-sm text-muted-foreground">Track billing, payments, and outstanding invoices.</p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)} disabled={!filters.projectId}>New Invoice</Button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input placeholder="Project ID" className="w-40" value={filters.projectId} onChange={(e) => setFilter({ projectId: e.target.value })} />
        <Input placeholder="Search..." className="max-w-xs" value={filters.q} onChange={(e) => setFilter({ q: e.target.value })} />
        <Select value={filters.status} onValueChange={(v) => setFilter({ status: v })}>
          <SelectTrigger className="w-36"><SelectValue placeholder="All status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="">All</SelectItem>
            {statuses.map((s) => <SelectItem key={s} value={s}>{STATUS_BADGE[s]?.label ?? s}</SelectItem>)}
          </SelectContent>
        </Select>
        <Button variant="outline" size="sm" onClick={() => queryClient.invalidateQueries({ queryKey: ["invoices"] })}>Refresh</Button>
      </div>

      {error ? (
        <p className="text-sm text-destructive">Failed to load invoices.</p>
      ) : (
        <div className="rounded-md border">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-3">#</th>
                <th className="text-left py-2 px-3">Project</th>
                <th className="text-left py-2 px-3">Status</th>
                <th className="text-right py-2 px-3">Total</th>
                <th className="text-right py-2 px-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((inv: Invoice) => {
                const badge = STATUS_BADGE[inv.status] ?? { label: inv.status, variant: "outline" };
                const total = (inv as { total?: number }).total ?? inv.subtotal + inv.tax_amount;
                return (
                  <tr key={inv.id} className="border-b last:border-0">
                    <td className="font-medium">{inv.id.slice(0, 8)}</td>
                    <td>{inv.project_id}</td>
                    <td><Badge variant={badge.variant}>{badge.label}</Badge></td>
                    <td className="text-right font-medium">₹{total.toLocaleString()}</td>
                    <td className="text-right"><Button variant="ghost" size="sm" onClick={() => setSelectedId(inv.id)}>View</Button></td>
                  </tr>
                );
              })}
              {!isLoading && rows.length === 0 && <tr><td colSpan={5} className="text-center text-sm text-muted-foreground py-6">No invoices found.</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={!!selectedId} onOpenChange={(o) => { if (!o) setSelectedId(null); }}>
        <DialogContent>
          <DialogHeader><DialogTitle>Invoice Detail</DialogTitle></DialogHeader>
          {detail ? (
            <div className="space-y-2 text-sm">
              <div><div className="text-xs text-muted-foreground">Status</div><div>{detail.status}</div></div>
              <div className="flex justify-between"><span className="text-xs text-muted-foreground">Subtotal</span><span>₹{detail.subtotal.toLocaleString()}</span></div>
              <div className="flex justify-between"><span className="text-xs text-muted-foreground">GST (tax)</span><span>₹{detail.tax_amount.toLocaleString()}</span></div>
              <div className="flex justify-between font-medium border-t pt-2"><span>Total</span><span>₹{detail.total.toLocaleString()}</span></div>
            </div>
          ) : <p className="text-sm text-muted-foreground">Loading...</p>}
          <DialogFooter><Button variant="outline" onClick={() => setSelectedId(null)}>Close</Button></DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Invoice</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2"><Label>Project ID</Label><Input value={filters.projectId} onChange={(e) => setFilter({ projectId: e.target.value })} /></div>
            <div className="space-y-2"><Label>Due date</Label><Input type="date" /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
            <Button onClick={() => setIsCreateOpen(false)}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
