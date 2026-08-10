"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { Material, MaterialCategory, MaterialListResponse } from "@/types/api";

const materialKeys = {
  all: ["materials"] as const,
  list: (q?: string, categoryId?: string) => [...materialKeys.all, "list", q, categoryId] as const,
  categories: ["material-categories"] as const,
};

export function MaterialsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", unit: "", category_id: "" });
  const { data, isLoading } = useQuery<MaterialListResponse>({
    queryKey: materialKeys.list(search || undefined, categoryId || undefined),
    queryFn: async () => api.listMaterials({ q: search || undefined, category_id: categoryId || undefined, page: 1, page_size: 50 }),
  });

  const { data: categories = [] } = useQuery<MaterialCategory[]>({
    queryKey: materialKeys.categories,
    queryFn: () => api.listMaterialCategories(),
  });

  const rows = data?.items ?? [];

  const createMutation = useMutation({
    mutationFn: () => api.createMaterial({ name: form.name, unit: form.unit, category_id: form.category_id || undefined, description: form.description || undefined }),
    onSuccess: () => {
      setIsCreateOpen(false);
      setForm({ name: "", description: "", unit: "", category_id: "" });
      queryClient.invalidateQueries({ queryKey: materialKeys.all });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteMaterial(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: materialKeys.all }),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Materials</h1>
          <p className="text-sm text-muted-foreground">Manage material catalog and categories.</p>
        </div>
        <Button onClick={() => { setIsCreateOpen(true); setForm({ name: "", description: "", unit: "", category_id: "" }); }}>New Material</Button>
      </div>

      <div className="flex items-center gap-3">
        <Input placeholder="Search materials..." className="max-w-sm" value={search} onChange={(e) => setSearch(e.target.value)} />
        <Select
          value={categoryId || "all"}
          onValueChange={(v) => setCategoryId(v === "all" ? "" : v)}
        >
          <SelectTrigger className="w-48"><SelectValue placeholder="All categories" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {categories.map((cat) => <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading...</p>
      ) : (
        <div className="rounded-md border">
          <table className="min-w-full text-sm">
            <thead><tr className="border-b"><th className="text-left py-2 px-3">Name</th><th className="text-left py-2 px-3">Unit</th><th className="text-left py-2 px-3">Category</th><th className="text-right py-2 px-3">Actions</th></tr></thead>
            <tbody>
              {rows.map((row: Material) => (
                <tr key={row.id} className="border-b last:border-0">
                  <td className="py-2 px-3 font-medium">{row.name}</td>
                  <td className="py-2 px-3">{row.unit}</td>
                  <td className="py-2 px-3"><Badge variant="outline">{row.category_name ?? "Uncategorized"}</Badge></td>
                  <td className="py-2 px-3 text-right"><Button variant="ghost" size="sm" onClick={() => deleteMutation.mutate(row.id)}>Delete</Button></td>
                </tr>
              ))}
              {rows.length === 0 && <tr><td colSpan={4} className="text-center text-sm text-muted-foreground py-6">No materials found.</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Material</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2"><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
            <div className="space-y-2"><Label>Unit</Label><Input value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} /></div>
            <div className="space-y-2">
              <Label>Category</Label>
              <Select value={form.category_id} onValueChange={(v) => setForm({ ...form, category_id: v })}>
                <SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger>
                <SelectContent>{categories.map((cat) => <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="space-y-2"><Label>Description</Label><Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
            <Button onClick={() => createMutation.mutate()} disabled={createMutation.isPending || !form.name.trim()}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
