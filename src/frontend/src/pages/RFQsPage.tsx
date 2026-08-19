"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { useCurrentUser } from "@/hooks/useAuth";
import { canManageCommercial } from "@/lib/permissions";
import { api } from "@/lib/api";
import type {
  RFQListResponse,
  RFQ,
  RFQCreatePayload,
  RFQItem,
} from "@/types/rfq";
import type { Material } from "@/types/api";

const STATUSES = [
  "draft",
  "sent",
  "responded",
  "compared",
  "awarded",
  "closed",
  "cancelled",
];

function statusLabel(status: string): string {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}

function mutationErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

export function RFQsPage(): JSX.Element {
  const queryClient = useQueryClient();
  const { data: user } = useCurrentUser();
  const commercial = canManageCommercial(user);
  const [projectId, setProjectId] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [viewId, setViewId] = useState<string | null>(null);
  const [respondId, setRespondId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const { data: projectsData } = useQuery({
    queryKey: ["projects-for-rfqs"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

  const { data: vendorsData } = useQuery({
    queryKey: ["vendors-for-rfqs"],
    queryFn: () => api.listVendors({ page: 1, page_size: 100 }),
  });
  const vendors = vendorsData?.items ?? [];

  const { data, isLoading, isError, error, refetch } = useQuery<RFQListResponse>({
    queryKey: ["rfqs", projectId, statusFilter],
    enabled: !!projectId,
    queryFn: async () =>
      api.listProjectRfqs(projectId, {
        page: 1,
        page_size: 50,
        status: statusFilter || undefined,
      }),
  });

  const { data: detail } = useQuery<RFQ>({
    queryKey: ["rfq", viewId],
    enabled: !!viewId,
    queryFn: async () => api.getRfq(viewId as string),
  });

  const invalidateRfqs = (): void => {
    void queryClient.invalidateQueries({ queryKey: ["rfqs"] });
    void queryClient.invalidateQueries({ queryKey: ["rfq"] });
  };

  const sendMutation = useMutation({
    mutationFn: (id: string) => api.sendRfq(id),
    onSuccess: () => {
      setActionError(null);
      invalidateRfqs();
    },
    onError: (err) => setActionError(mutationErrorMessage(err, "Failed to send RFQ")),
  });

  const awardMutation = useMutation({
    mutationFn: (id: string) => api.awardRfq(id),
    onSuccess: () => {
      setActionError(null);
      invalidateRfqs();
    },
    onError: (err) => setActionError(mutationErrorMessage(err, "Failed to award RFQ")),
  });

  const rows = data?.items ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">RFQs</h1>
          <p className="text-sm text-muted-foreground">
            Run vendor RFQs through send, respond, compare, award, and close.
          </p>
        </div>
        {commercial ? (
          <Button onClick={() => setIsCreateOpen(true)} disabled={!projectId}>
            New RFQ
          </Button>
        ) : null}
      </div>

      <div className="flex flex-wrap items-center gap-3">
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
        <Select
          value={statusFilter || "all"}
          onValueChange={(v) => setStatusFilter(v === "all" ? "" : v)}
        >
          <SelectTrigger className="w-36">
            <SelectValue placeholder="All status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            {STATUSES.map((s) => (
              <SelectItem key={s} value={s}>
                {statusLabel(s)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {projectId && isError && (
        <QueryErrorBanner
          message="Failed to load RFQs"
          error={error}
          onRetry={() => void refetch()}
        />
      )}

      {actionError && (
        <div
          role="alert"
          className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive"
        >
          <p className="font-medium">{actionError}</p>
          <Button type="button" variant="outline" size="sm" onClick={() => setActionError(null)}>
            Dismiss
          </Button>
        </div>
      )}

      {!projectId ? (
        <p className="text-sm text-muted-foreground">Select a project to view RFQs.</p>
      ) : isLoading ? (
        <p className="text-sm text-muted-foreground">Loading...</p>
      ) : isError ? null : (
        <div className="rounded-md border">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-3">#</th>
                <th className="text-left py-2 px-3">Vendor</th>
                <th className="text-left py-2 px-3">Status</th>
                <th className="text-left py-2 px-3">Created</th>
                <th className="text-right py-2 px-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-b last:border-0">
                  <td className="py-2 px-3 font-medium font-mono text-xs">
                    {r.rfq_number || r.id.slice(0, 8)}
                  </td>
                  <td className="py-2 px-3">{r.vendor_name ?? "—"}</td>
                  <td className="py-2 px-3">
                    <Badge variant="outline">{statusLabel(r.status)}</Badge>
                  </td>
                  <td className="py-2 px-3 text-sm text-muted-foreground">
                    {r.created_at
                      ? new Date(r.created_at).toLocaleDateString()
                      : "—"}
                  </td>
                  <td className="py-2 px-3 text-right">
                    <div className="flex justify-end gap-1 flex-wrap">
                      {commercial && r.status === "draft" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          disabled={sendMutation.isPending}
                          onClick={() => sendMutation.mutate(r.id)}
                        >
                          Send
                        </Button>
                      )}
                      {commercial && r.status === "sent" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setRespondId(r.id)}
                        >
                          Respond
                        </Button>
                      )}
                      {commercial &&
                        (r.status === "responded" || r.status === "compared") && (
                        <Button
                          variant="ghost"
                          size="sm"
                          disabled={awardMutation.isPending}
                          onClick={() => awardMutation.mutate(r.id)}
                        >
                          Award
                        </Button>
                      )}
                      <Button variant="ghost" size="sm" onClick={() => setViewId(r.id)}>
                        View
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    className="text-center text-sm text-muted-foreground py-6"
                  >
                    {statusFilter ? (
                      <>No RFQs match this status filter.</>
                    ) : (
                      <>
                        No RFQs for this project yet.{" "}
                        <button
                          type="button"
                          className="underline font-medium text-foreground"
                          onClick={() => setIsCreateOpen(true)}
                        >
                          Create the first RFQ
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={!!viewId} onOpenChange={(o) => !o && setViewId(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>RFQ Detail</DialogTitle>
          </DialogHeader>
          {detail ? (
            <div className="space-y-3 text-sm">
              <div>
                <div className="text-xs text-muted-foreground">Number</div>
                <div className="font-mono">{detail.rfq_number}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Vendor</div>
                <div>{detail.vendor_name ?? "—"}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Status</div>
                <div>{statusLabel(detail.status)}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Created</div>
                <div>{detail.created_at ?? "—"}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Notes</div>
                <div>{detail.notes ?? "—"}</div>
              </div>
              {detail.items?.length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Line items</div>
                  <ul className="space-y-1 rounded border p-2">
                    {detail.items.map((item: RFQItem) => (
                      <li key={item.id} className="flex justify-between gap-2">
                        <span>
                          {item.material_name ?? item.material_id}
                          {item.material_unit ? ` (${item.material_unit})` : ""} ×{" "}
                          {item.quantity}
                        </span>
                        <span className="text-muted-foreground">
                          {item.vendor_rate != null ? `₹${item.vendor_rate}` : "—"}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Loading...</p>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewId(null)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={!!respondId} onOpenChange={(o) => !o && setRespondId(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Record vendor response</DialogTitle>
          </DialogHeader>
          {respondId && (
            <RespondForm
              rfqId={respondId}
              onCancel={() => setRespondId(null)}
              onDone={() => {
                setRespondId(null);
                setActionError(null);
                invalidateRfqs();
              }}
              onError={(msg) => setActionError(msg)}
            />
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>New RFQ</DialogTitle>
          </DialogHeader>
          <CreateForm
            projectId={projectId}
            vendors={vendors}
            onCancel={() => setIsCreateOpen(false)}
            onDone={() => {
              setIsCreateOpen(false);
              invalidateRfqs();
            }}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}

function CreateForm({
  projectId,
  vendors,
  onCancel,
  onDone,
}: {
  projectId: string;
  vendors: { id: string; name: string }[];
  onCancel: () => void;
  onDone: () => void;
}): JSX.Element {
  const [vendorId, setVendorId] = useState(vendors[0]?.id ?? "");
  const [notes, setNotes] = useState("");
  const [materialId, setMaterialId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [itemNotes, setItemNotes] = useState("");

  const { data: materialsData, isLoading: materialsLoading } = useQuery({
    queryKey: ["materials-for-rfqs"],
    queryFn: () => api.listMaterials({ page: 1, page_size: 100 }),
  });
  const materials: Material[] = useMemo(() => materialsData?.items ?? [], [materialsData]);

  useEffect(() => {
    if (!materialId && materials[0]?.id) setMaterialId(materials[0].id);
  }, [materials, materialId]);

  const selectedMaterial = materials.find((m) => m.id === materialId);

  const create = useMutation({
    mutationFn: () => {
      if (!vendorId) throw new Error("Select a vendor");
      if (!materialId) throw new Error("Select a material line item");
      const qty = Number(quantity);
      if (!Number.isFinite(qty) || qty <= 0) throw new Error("Quantity must be greater than 0");
      const payload: RFQCreatePayload = {
        project_id: projectId,
        vendor_id: vendorId,
        notes: notes || undefined,
        items: [
          {
            material_id: materialId,
            quantity: qty,
            notes: itemNotes || undefined,
          },
        ],
      };
      return api.createRfq(projectId, payload);
    },
    onSuccess: onDone,
  });

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>Vendor</Label>
        <Select value={vendorId || undefined} onValueChange={setVendorId}>
          <SelectTrigger>
            <SelectValue placeholder="Select vendor" />
          </SelectTrigger>
          <SelectContent>
            {vendors.length === 0 ? (
              <SelectItem value="none" disabled>
                No vendors in DB — create under Vendors
              </SelectItem>
            ) : (
              vendors.map((v) => (
                <SelectItem key={v.id} value={v.id}>
                  {v.name}
                </SelectItem>
              ))
            )}
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border p-3 space-y-3">
        <p className="text-sm font-medium">Line item (required)</p>
        <div className="space-y-2">
          <Label>Material</Label>
          <Select
            value={materialId || undefined}
            onValueChange={setMaterialId}
            disabled={materialsLoading}
          >
            <SelectTrigger>
              <SelectValue
                placeholder={materialsLoading ? "Loading materials…" : "Select material"}
              />
            </SelectTrigger>
            <SelectContent>
              {materials.length === 0 ? (
                <SelectItem value="none" disabled>
                  No materials — create under Materials
                </SelectItem>
              ) : (
                materials.map((m) => (
                  <SelectItem key={m.id} value={m.id}>
                    {m.name}
                    {m.unit ? ` (${m.unit})` : ""}
                  </SelectItem>
                ))
              )}
            </SelectContent>
          </Select>
          {selectedMaterial && (
            <p className="text-xs text-muted-foreground">
              Unit: {selectedMaterial.unit || "—"}
              {selectedMaterial.description
                ? ` · ${selectedMaterial.description}`
                : ""}
            </p>
          )}
        </div>
        <div className="space-y-2">
          <Label>Quantity</Label>
          <Input
            type="number"
            min={0.01}
            step="any"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label>Item notes (optional)</Label>
          <Input
            value={itemNotes}
            onChange={(e) => setItemNotes(e.target.value)}
            placeholder="Specs / description override"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label>Notes</Label>
        <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
      </div>

      {create.isError && (
        <p className="text-sm text-destructive" role="alert">
          {mutationErrorMessage(create.error, "Failed to create RFQ")}
        </p>
      )}

      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button
          onClick={() => create.mutate()}
          disabled={
            create.isPending || !vendorId || !materialId || materials.length === 0
          }
        >
          {create.isPending ? "Creating…" : "Create RFQ"}
        </Button>
      </DialogFooter>
    </div>
  );
}

function RespondForm({
  rfqId,
  onCancel,
  onDone,
  onError,
}: {
  rfqId: string;
  onCancel: () => void;
  onDone: () => void;
  onError: (message: string) => void;
}): JSX.Element {
  const { data: rfq, isLoading, isError, error, refetch } = useQuery<RFQ>({
    queryKey: ["rfq", rfqId, "respond"],
    queryFn: () => api.getRfq(rfqId),
  });

  const [rates, setRates] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!rfq?.items) return;
    const next: Record<string, string> = {};
    for (const item of rfq.items) {
      next[item.id] =
        item.vendor_rate != null ? String(item.vendor_rate) : "";
    }
    setRates(next);
  }, [rfq]);

  const respond = useMutation({
    mutationFn: () => {
      if (!rfq?.items?.length) throw new Error("RFQ has no line items");
      const items = rfq.items.map((item) => {
        const raw = rates[item.id];
        const rate = Number(raw);
        if (!Number.isFinite(rate) || rate < 0) {
          throw new Error(`Enter a valid rate for ${item.material_name ?? item.id}`);
        }
        return { item_id: item.id, vendor_rate: rate };
      });
      return api.respondRfq(rfqId, { items });
    },
    onSuccess: onDone,
    onError: (err) => onError(mutationErrorMessage(err, "Failed to record response")),
  });

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading RFQ items…</p>;
  }

  if (isError || !rfq) {
    return (
      <div className="space-y-3">
        <QueryErrorBanner
          message="Failed to load RFQ"
          error={error}
          onRetry={() => void refetch()}
        />
        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        </DialogFooter>
      </div>
    );
  }

  if (!rfq.items?.length) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-muted-foreground">This RFQ has no line items.</p>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        </DialogFooter>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Enter vendor rates for each line item on {rfq.rfq_number}.
      </p>
      <div className="space-y-3 max-h-72 overflow-y-auto">
        {rfq.items.map((item) => (
          <div key={item.id} className="grid grid-cols-[1fr_auto] gap-3 items-end">
            <div>
              <div className="text-sm font-medium">
                {item.material_name ?? "Material"}
              </div>
              <div className="text-xs text-muted-foreground">
                Qty {item.quantity}
                {item.material_unit ? ` ${item.material_unit}` : ""}
              </div>
            </div>
            <div className="w-32 space-y-1">
              <Label className="text-xs">Rate (₹)</Label>
              <Input
                type="number"
                min={0}
                step="any"
                value={rates[item.id] ?? ""}
                onChange={(e) =>
                  setRates((prev) => ({ ...prev, [item.id]: e.target.value }))
                }
              />
            </div>
          </div>
        ))}
      </div>

      {respond.isError && (
        <p className="text-sm text-destructive" role="alert">
          {mutationErrorMessage(respond.error, "Failed to record response")}
        </p>
      )}

      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button onClick={() => respond.mutate()} disabled={respond.isPending}>
          {respond.isPending ? "Saving…" : "Submit response"}
        </Button>
      </DialogFooter>
    </div>
  );
}
