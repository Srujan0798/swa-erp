"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api";
import type { ProjectPnL, ProjectCost } from "@/types/financial";

type CostItem = { category: string; amount: number; count: number; percentage: number };

const reportKey = (...segments: (string | number | boolean | undefined)[]) => ["reports", ...segments] as const;

export function ReportsPage() {
  const [projectId, setProjectId] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");

  const { data: projectsData } = useQuery({
    queryKey: ["projects-for-reports"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

  const { data: pnl, isLoading: pnlLoading } = useQuery<ProjectPnL>({
    queryKey: reportKey("pnl", projectId),
    enabled: !!projectId,
    queryFn: async () => api.getProjectPnL(projectId),
  });

  const { data: costs } = useQuery<{ items?: ProjectCost[] }>({
    queryKey: reportKey("costs", projectId, categoryFilter),
    enabled: !!projectId,
    queryFn: async () => api.listProjectCosts(projectId, { category: categoryFilter || undefined, page: 1, page_size: 50 }),
  });

  const chartItems: CostItem[] = pnl?.cost_breakdown ?? [];
  const costItems = costs?.items ?? [];

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold">Reports</h1>
        <p className="text-sm text-muted-foreground">Project profitability, cost breakdown, and financial summaries.</p>
      </div>

      <div className="flex items-center gap-2">
        <Select value={projectId || undefined} onValueChange={setProjectId}>
          <SelectTrigger className="w-80"><SelectValue placeholder="Select project" /></SelectTrigger>
          <SelectContent>
            {projects.map((p) => (
              <SelectItem key={p.id} value={p.id}>
                {p.code} — {p.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {!projectId ? (
        <p className="text-sm text-muted-foreground">Select a project to view reports.</p>
      ) : pnlLoading ? (
        <p className="text-sm text-muted-foreground">Loading...</p>
      ) : pnl ? (
        <Tabs defaultValue="pnl" className="space-y-4">
          <TabsList>
            <TabsTrigger value="pnl">P&L</TabsTrigger>
            <TabsTrigger value="costs">Costs</TabsTrigger>
          </TabsList>

          <TabsContent value="pnl" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <Card className="p-4"><div className="text-sm font-medium text-muted-foreground">Revenue</div><div className="text-2xl font-semibold">₹{pnl.total_revenue.toLocaleString()}</div></Card>
              <Card className="p-4"><div className="text-sm font-medium text-muted-foreground">Costs</div><div className="text-2xl font-semibold">₹{pnl.total_costs.toLocaleString()}</div></Card>
              <Card className="p-4"><div className="text-sm font-medium text-muted-foreground">Net profit</div><div className="text-2xl font-semibold">₹{pnl.net_profit.toLocaleString()}</div></Card>
            </div>

            <Card className="p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div><div className="font-semibold">Margin</div><div className="text-sm text-muted-foreground">Net profit relative to revenue</div></div>
                <Badge variant="default">{pnl.margin_pct.toFixed(1)}%</Badge>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                <div className="h-full bg-primary" style={{ width: `${Math.min(pnl.margin_pct, 100)}%` }} />
              </div>
            </Card>

            <div className="rounded-md border">
              <Table>
                <TableHeader><TableRow><TableHead>Category</TableHead><TableHead>Amount</TableHead><TableHead className="text-right">%</TableHead></TableRow></TableHeader>
                <TableBody>
                  {chartItems.map((item, idx) => (
                    <TableRow key={`chart-${item.category}-${idx}`}>
                      <TableCell className="font-medium">{item.category}</TableCell>
                      <TableCell>₹{item.amount.toLocaleString()}</TableCell>
                      <TableCell className="text-right">{item.percentage.toFixed(1)}%</TableCell>
                    </TableRow>
                  ))}
                  {chartItems.length === 0 && <tr><td colSpan={3} className="text-center text-sm text-muted-foreground py-6">No cost breakdown available.</td></tr>}
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="costs" className="space-y-4">
            <div className="flex items-center gap-2">
              <Input placeholder="Filter category" className="max-w-xs" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} />
              <Button variant="outline" size="sm">Apply</Button>
            </div>
            <div className="rounded-md border">
              <Table>
                <TableHeader><TableRow><TableHead>Date</TableHead><TableHead>Category</TableHead><TableHead>Description</TableHead><TableHead className="text-right">Amount</TableHead></TableRow></TableHeader>
                <TableBody>
                  {costItems.map((cost) => (
                    <TableRow key={cost.id}>
                      <TableCell>{cost.date}</TableCell>
                      <TableCell><Badge variant="outline">{cost.category}</Badge></TableCell>
                      <TableCell className="text-sm text-muted-foreground">{cost.description}</TableCell>
                      <TableCell className="text-right font-medium">₹{cost.amount.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                  {costItems.length === 0 && <tr><td colSpan={4} className="text-center text-sm text-muted-foreground py-6">No costs found.</td></tr>}
                </TableBody>
              </Table>
            </div>
          </TabsContent>
        </Tabs>
      ) : (
        <p className="text-sm text-muted-foreground">No financial summary available yet.</p>
      )}
    </div>
  );
}
