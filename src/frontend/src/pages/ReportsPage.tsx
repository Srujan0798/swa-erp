"use client";

import { useEffect, useState, type ReactElement } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { PnlDashboard } from "@/components/financials/PnlDashboard";
import { CostEntryForm } from "@/components/financials/CostEntryForm";
import { useProjectPnL, useProjectCosts } from "@/hooks/useProjectPnL";
import { useCurrentUser } from "@/hooks/useAuth";
import { canManageCommercial } from "@/lib/permissions";
import { api } from "@/lib/api";
import { Plus } from "lucide-react";

export function ReportsPage(): ReactElement {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const { data: user } = useCurrentUser();
  const canAddCost = canManageCommercial(user);
  const [projectId, setProjectId] = useState(searchParams.get("project") ?? "");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [appliedCategory, setAppliedCategory] = useState("");
  const [showCostForm, setShowCostForm] = useState(false);

  // Async export state
  const [exportJobId, setExportJobId] = useState<string | null>(null);
  const [exportStatus, setExportStatus] = useState<string>("");
  const [exportError, setExportError] = useState<string>("");
  const [exportResultUrl, setExportResultUrl] = useState<string>("");

  // Poll job status once started
  useEffect(() => {
    if (!exportJobId) return;
    let cancelled = false;
    const interval = setInterval(() => {
      void api.getExportJob(exportJobId).then(
        (data) => {
          if (cancelled) return;
          setExportStatus(data.status);
          if (data.status === "SUCCESS") {
            setExportResultUrl(data.result_url ?? "");
            setExportJobId(null);
          } else if (data.status === "FAILURE") {
            setExportError(data.error ?? "Export failed");
            setExportJobId(null);
          }
        },
        () => {
          if (!cancelled) setExportError("Poll failed");
        },
      );
    }, 2000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [exportJobId]);

  useEffect(() => {
    const fromUrl = searchParams.get("project") ?? "";
    if (fromUrl !== projectId) setProjectId(fromUrl);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const selectProject = (id: string): void => {
    setProjectId(id);
    setShowCostForm(false);
    setCategoryFilter("");
    setAppliedCategory("");
    if (id) setSearchParams({ project: id }, { replace: true });
    else setSearchParams({}, { replace: true });
  };

  const {
    data: projectsData,
    isError: projectsError,
    error: projectsErr,
    refetch: refetchProjects,
  } = useQuery({
    queryKey: ["projects-for-reports"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

  const {
    data: pnl,
    isLoading: pnlLoading,
    isError: pnlError,
    error: pnlErr,
    refetch: refetchPnl,
  } = useProjectPnL(projectId);

  const {
    data: costsData,
    isLoading: costsLoading,
    isError: costsError,
    error: costsErr,
    refetch: refetchCosts,
  } = useProjectCosts(projectId, appliedCategory || undefined);
  const costItems = costsData?.items ?? [];

  const refreshFinancials = (): void => {
    void queryClient.invalidateQueries({ queryKey: ["projectPnL", projectId] });
    void queryClient.invalidateQueries({ queryKey: ["projectCosts", projectId] });
    setShowCostForm(false);
  };

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold">Reports</h1>
        <p className="text-sm text-muted-foreground">
          Project profitability, cost breakdown, and financial summaries.
        </p>
      </div>

      {projectsError && (
        <QueryErrorBanner
          message="Failed to load projects"
          error={projectsErr}
          onRetry={() => void refetchProjects()}
        />
      )}

      <div className="flex items-center gap-2">
        <Select value={projectId || undefined} onValueChange={selectProject}>
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
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            if (!projectId) return;
            void api
              .startExport(`/api/exports/projects/${projectId}/summary.pdf?async=true`)
              .then((data) => {
                setExportJobId(data.job_id);
                setExportStatus("PENDING");
                setExportError("");
                setExportResultUrl("");
              })
              .catch((e) => setExportError(e.message));
          }}
        >
          Export summary PDF
        </Button>
      </div>

      {(exportJobId || exportStatus || exportError || exportResultUrl) && (
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-base">Export job</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>
              Job: <code className="text-xs bg-muted px-1 rounded">{exportJobId ?? "—"}</code>
            </p>
            <p>Status: <strong>{exportStatus}</strong></p>
            {exportError && <p className="text-destructive">{exportError}</p>}
            {exportResultUrl && (
              <p>
                <a className="underline" href={exportResultUrl} target="_blank" rel="noreferrer">
                  Download result
                </a>
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {!projectId ? (
        <p className="text-sm text-muted-foreground">
          Select a project to view P&amp;L and costs, or use Costs / P&amp;L from a project page.
        </p>
      ) : (
        <Tabs defaultValue="pnl" className="space-y-4">
          <TabsList>
            <TabsTrigger value="pnl">P&L</TabsTrigger>
            <TabsTrigger value="costs">Costs</TabsTrigger>
          </TabsList>

          <TabsContent value="pnl" className="space-y-4">
            {pnlError ? (
              <QueryErrorBanner
                message="Failed to load project report"
                error={pnlErr}
                onRetry={() => void refetchPnl()}
              />
            ) : (
              <PnlDashboard pnl={pnl} isLoading={pnlLoading} />
            )}
          </TabsContent>

          <TabsContent value="costs" className="space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <Input
                placeholder="Filter category"
                className="max-w-xs"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") setAppliedCategory(categoryFilter.trim());
                }}
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => setAppliedCategory(categoryFilter.trim())}
              >
                Apply
              </Button>
              {canAddCost && !showCostForm && (
                <Button size="sm" className="ml-auto" onClick={() => setShowCostForm(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add cost
                </Button>
              )}
            </div>

            {canAddCost && showCostForm && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Add project cost</CardTitle>
                </CardHeader>
                <CardContent>
                  <CostEntryForm
                    projectId={projectId}
                    onSuccess={refreshFinancials}
                    onCancel={() => setShowCostForm(false)}
                  />
                </CardContent>
              </Card>
            )}

            {costsError ? (
              <QueryErrorBanner
                message="Failed to load project costs"
                error={costsErr}
                onRetry={() => void refetchCosts()}
              />
            ) : costsLoading ? (
              <p className="text-sm text-muted-foreground">Loading costs...</p>
            ) : (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {costItems.map((cost) => (
                      <TableRow key={cost.id}>
                        <TableCell>{cost.date}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{cost.category}</Badge>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {cost.description}
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          ₹{cost.amount.toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                    {costItems.length === 0 && (
                      <TableRow>
                        <TableCell
                          colSpan={4}
                          className="py-6 text-center text-sm text-muted-foreground"
                        >
                          No costs found.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
