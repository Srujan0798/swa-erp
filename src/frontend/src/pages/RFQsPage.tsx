"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import type { RFQListResponse, RFQ, RFQCreatePayload } from "@/types/rfq";

const STATUSES = ["draft", "sent", "responded", "compared", "awarded", "closed", "cancelled"];

function statusLabel(status: string) {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}

type Vendor = { id: string; name: string };

const VENDORS: Vendor[] = [
  { id: "v1", name: "Vendor Alpha" },
  { id: "v2", name: "Vendor Beta" },
];

const DEFAULT_PAYLOAD = (vendor_id: string, notes?: string): RFQCreatePayload => ({
  vendor_id,
  notes,
  items: [],
});

export function RFQsPage() {
  const queryClient = useQueryClient();
  const [projectId, setProjectId] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [viewId, setViewId] = useState<string | null>(null);

  const { data, isLoading } = useQuery<RFQListResponse>({
    queryKey: ["rfqs", projectId, statusFilter],
    enabled: !!projectId,
    queryFn: async () => api.listProjectRfqs(projectId, { page: 1, page_size: 50, status: statusFilter || undefined }),
  });

  const { data: detail } = useQuery<RFQ>({
    queryKey: ["rfq", viewId],
    enabled: !!viewId,
    queryFn: async () => api.getRfq(viewId as string),
  });

  const sendMutation = useMutation({
    mutationFn: (id: string) => api.sendRfq(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["rfqs"] }); },
  });

  const rows = data?.items ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">RFQs</h1>
          <p className="text-sm text-muted-foreground">Run vendor RFQs through send, respond, compare, award, and close.</p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)} disabled={!projectId}>New RFQ</Button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Select value={projectId} onValueChange={setProjectId}>
          <SelectTrigger className="w-48"><SelectValue placeholder="Select project" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="p1">Project Alpha</SelectItem>
            <SelectItem value="p2">Project Beta</SelectItem>
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-36"><SelectValue placeholder="All status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="">All</SelectItem>
            {STATUSES.map((s) => <SelectItem key={s} value={s}>{statusLabel(s)}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {!projectId ? (
        <p className="text-sm text-muted-foreground">Select a project to view RFQs.</p>
      ) : isLoading ? (
        <p className="text-sm text-muted-foreground">Loading...</p>
      ) : (
        <div className="rounded-md border">
          <table className="min-w-full text-sm">
            <thead><tr className="border-b"><th className="text-left py-2 px-3">#</th><th className="text-left py-2 px-3">Status</th><th className="text-left py-2 px-3">Created</th><th className="text-right py-2 px-3">Actions</th></tr></thead>
            <tbody>
              {rows.map((r: RFQ) => (
                <tr key={r.id} className="border-b last:border-0">
                  <td className="py-2 px-3 font-medium">{r.id.slice(0, 8)}</td>
                  <td className="py-2 px-3"><Badge variant="outline">{statusLabel(r.status)}</Badge></td>
                  <td className="py-2 px-3 text-sm text-muted-foreground">{r.created_at ?? "—"}</td>
                  <td className="py-2 px-3 text-right">
                    <div className="flex justify-end gap-2">
                      {r.status === "draft" && <Button variant="ghost" size="sm" onClick={() => sendMutation.mutate(r.id)}>Send</Button>}
                      <Button variant="ghost" size="sm" onClick={() => setViewId(r.id)}>View</Button>
                    </div>
                  </td>
                </tr>
              ))}
              {rows.length === 0 && <tr><td colSpan={4} className="text-center text-sm text-muted-foreground py-6">No RFQs found.</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={!!viewId} onOpenChange={(o) => !o && setViewId(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>RFQ Detail</DialogTitle></DialogHeader>
          {detail ? (
            <div className="space-y-2 text-sm">
              <div><div className="text-xs text-muted-foreground">Status</div><div>{statusLabel(detail.status)}</div></div>
              <div><div className="text-xs text-muted-foreground">Created</div><div>{detail.created_at ?? "—"}</div></div>
              <div><div className="text-xs text-muted-foreground">Notes</div><div>{detail.notes ?? "—"}</div></div>
            </div>
          ) : <p className="text-sm text-muted-foreground">Loading...</p>}
          <DialogFooter><Button variant="outline" onClick={() => setViewId(null)}>Close</Button></DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>New RFQ</DialogTitle></DialogHeader>
          <CreateForm projectId={projectId} onCancel={() => setIsCreateOpen(false)} onDone={() => { setIsCreateOpen(false); queryClient.invalidateQueries({ queryKey: ["rfqs"] }); }} />
        </DialogContent>
      </Dialog>
    </div>
  );
}

function CreateForm({ projectId, onCancel, onDone }: { projectId: string; onCancel: () => void; onDone: () => void }) {
  const [vendorId, setVendorId] = useState(VENDORS[0]?.id ?? "v1");
  const [notes, setNotes] = useState("");

  const create = useMutation({
    mutationFn: () => api.createRfq(projectId, DEFAULT_PAYLOAD(vendorId, notes || undefined)),
    onSuccess: onDone,
  });

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>Vendor</Label>
        <Select value={vendorId} onValueChange={setVendorId}>
          <SelectTrigger><SelectValue placeholder="Select vendor" /></SelectTrigger>
          <SelectContent>
            {VENDORS.map((v) => <SelectItem key={v.id} value={v.id}>{v.name}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Notes</Label>
        <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>Cancel</Button>
        <Button onClick={() => create.mutate()} disabled={create.isPending}>Create RFQ</Button>
      </DialogFooter>
    </div>
  );
}
