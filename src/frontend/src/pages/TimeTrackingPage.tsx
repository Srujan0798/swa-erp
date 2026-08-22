"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, type ReactElement } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { api } from "@/lib/api";
import { useCurrentUser } from "@/hooks/useAuth";
import { canWrite } from "@/lib/permissions";
import type { TimeEntry, TimeEntryListResponse } from "@/types/time";
import { useToast } from "@/hooks/useToast";

const timeKey = (...segments: (string | number | boolean | undefined)[]) =>
  ["time", ...segments] as const;

export default function TimeTrackingPage(): ReactElement {
  const qc = useQueryClient();
  const { toast } = useToast();
  const { data: user } = useCurrentUser();
  const write = canWrite(user);
  const [searchParams, setSearchParams] = useSearchParams();
  const today = new Date().toISOString().split("T")[0];
  const [projectId, setProjectId] = useState(searchParams.get("project") ?? "");
  const [form, setForm] = useState({
    date: today,
    hours: "",
    description: "",
    is_billable: true,
    work_type: "",
    activity_type: "",
    software_used: "",
    work_mode: "",
    employee_name: "",
    employee_role: "",
    sheet_reference_id: "",
    billable_hours: "",
  });

  useEffect(() => {
    if (user?.name) {
      setForm((prev) => (prev.employee_name ? prev : { ...prev, employee_name: user.name }));
    }
  }, [user?.name]);

  useEffect(() => {
    const fromUrl = searchParams.get("project") ?? "";
    if (fromUrl && fromUrl !== projectId) setProjectId(fromUrl);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const selectProject = (id: string): void => {
    setProjectId(id);
    if (id) setSearchParams({ project: id }, { replace: true });
    else setSearchParams({}, { replace: true });
  };

  const { data: projectsData } = useQuery({
    queryKey: ["projects-for-time"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

  const { data: list, isLoading, isError, error, refetch } = useQuery<TimeEntryListResponse>({
    queryKey: timeKey("entries"),
    queryFn: async () => api.listTimeEntries({ page_size: 100 }),
  });

  const entries: TimeEntry[] = list?.items ?? [];

  const submit = async () => {
    const hours = parseFloat(form.hours);
    if (!projectId) {
      toast({ title: "Select a project", variant: "destructive" });
      return;
    }
    if (Number.isNaN(hours) || hours <= 0 || hours > 24) {
      toast({ title: "Hours must be between 0.25 and 24", variant: "destructive" });
      return;
    }
    if (!form.description.trim() && !form.activity_type.trim()) {
      toast({ title: "Remarks or activity type required", variant: "destructive" });
      return;
    }
    const billableParsed =
      form.billable_hours.trim() === "" ? undefined : parseFloat(form.billable_hours);
    try {
      await api.createTimeEntry({
        project_id: projectId,
        date: form.date,
        hours,
        description: form.description.trim() || form.activity_type.trim(),
        is_billable: form.is_billable,
        work_type: form.work_type.trim() || undefined,
        activity_type: form.activity_type.trim() || undefined,
        software_used: form.software_used.trim() || undefined,
        work_mode: form.work_mode.trim() || undefined,
        employee_name: form.employee_name.trim() || undefined,
        employee_role: form.employee_role.trim() || undefined,
        sheet_reference_id: form.sheet_reference_id.trim() || undefined,
        billable_hours:
          billableParsed !== undefined && !Number.isNaN(billableParsed)
            ? billableParsed
            : undefined,
      });
      toast({ title: "Time entry saved" });
      qc.invalidateQueries({ queryKey: timeKey("entries") });
      setForm({
        date: today,
        hours: "",
        description: "",
        is_billable: true,
        work_type: "",
        activity_type: "",
        software_used: "",
        work_mode: "",
        employee_name: user?.name ?? "",
        employee_role: "",
        sheet_reference_id: "",
        billable_hours: "",
      });
    } catch (e) {
      toast({
        title: (e as Error).message || "Failed to save",
        variant: "destructive",
      });
    }
  };

  const weeklyHours = entries.reduce((sum, e) => sum + Number(e.hours || 0), 0);
  const billableHours = entries.reduce((s, e) => {
    if (e.billable_hours != null) return s + Number(e.billable_hours);
    return e.is_billable ? s + Number(e.hours || 0) : s;
  }, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Time logging</h1>
        <p className="text-sm text-muted-foreground">
          Same columns as the Excel <span className="font-medium">Time Logging Sheet</span> — work
          type, activity, software, mode, hours, billable hours. Increments: 0.25h (Excel often
          0.5h).
        </p>
      </div>

      {projects.length === 0 && (
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/5 px-4 py-3 text-sm">
          <p className="font-medium">No projects to log against yet</p>
          <p className="mt-1 text-muted-foreground">
            Sample Project Tracking sheet is often empty. Run{" "}
            <code className="rounded bg-muted px-1">make swa-live-local</code> (creates projects from
            converted inquiries) or{" "}
            <Link className="underline font-medium text-foreground" to="/inquiries">
              convert an inquiry
            </Link>
            .
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total hours</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold tabular-nums">{weeklyHours.toFixed(2)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Billable</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold tabular-nums">{billableHours.toFixed(2)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Entries</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold tabular-nums">{entries.length}</p>
          </CardContent>
        </Card>
      </div>

      {write ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Add time entry</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Project *</Label>
              <Select value={projectId || undefined} onValueChange={selectProject}>
                <SelectTrigger>
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
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div className="space-y-2">
                <Label>Date</Label>
                <Input
                  type="date"
                  value={form.date}
                  onChange={(e) => setForm({ ...form, date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Hours logged</Label>
                <Input
                  type="number"
                  step="0.25"
                  min="0.25"
                  max="24"
                  value={form.hours}
                  onChange={(e) => setForm({ ...form, hours: e.target.value })}
                  placeholder="e.g. 1.5"
                />
              </div>
              <div className="space-y-2">
                <Label>Billable hours</Label>
                <Input
                  type="number"
                  step="0.25"
                  min="0"
                  max="24"
                  value={form.billable_hours}
                  onChange={(e) => setForm({ ...form, billable_hours: e.target.value })}
                  placeholder="Optional"
                />
              </div>
              <div className="space-y-2">
                <Label>Work type</Label>
                <Input
                  value={form.work_type}
                  onChange={(e) => setForm({ ...form, work_type: e.target.value })}
                  placeholder="PROJECT / PRE-PROJECT / INTERNAL"
                />
              </div>
              <div className="space-y-2">
                <Label>Activity type</Label>
                <Input
                  value={form.activity_type}
                  onChange={(e) => setForm({ ...form, activity_type: e.target.value })}
                  placeholder="CON, DBR, CAL…"
                />
              </div>
              <div className="space-y-2">
                <Label>Employee name</Label>
                <Input
                  value={form.employee_name}
                  onChange={(e) => setForm({ ...form, employee_name: e.target.value })}
                  placeholder="Defaults to signed-in user"
                />
              </div>
              <div className="space-y-2">
                <Label>Employee role</Label>
                <Input
                  value={form.employee_role}
                  onChange={(e) => setForm({ ...form, employee_role: e.target.value })}
                  placeholder="AE / RE / SE"
                />
              </div>
              <div className="space-y-2">
                <Label>Software used</Label>
                <Input
                  value={form.software_used}
                  onChange={(e) => setForm({ ...form, software_used: e.target.value })}
                  placeholder="CAD, EASE, RPS…"
                />
              </div>
              <div className="space-y-2">
                <Label>Work mode</Label>
                <Input
                  value={form.work_mode}
                  onChange={(e) => setForm({ ...form, work_mode: e.target.value })}
                  placeholder="Manual / Automated"
                />
              </div>
              <div className="space-y-2">
                <Label>Reference ID</Label>
                <Input
                  value={form.sheet_reference_id}
                  onChange={(e) => setForm({ ...form, sheet_reference_id: e.target.value })}
                  placeholder="SWA-… link"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Remarks</Label>
              <Input
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Excel Remarks (optional if activity set)"
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_billable}
                onChange={(e) => setForm({ ...form, is_billable: e.target.checked })}
              />
              Billable
            </label>
            <Button onClick={submit}>Add entry</Button>
          </CardContent>
        </Card>
      ) : (
        <p className="text-sm text-muted-foreground rounded-md border border-dashed p-4">
          View-only: time entry logging is disabled for viewer accounts.
        </p>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Recent entries</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
          {isError && (
            <QueryErrorBanner
              message="Failed to load time entries"
              error={error}
              onRetry={() => void refetch()}
            />
          )}
          {!isLoading && !isError && entries.length === 0 && (
            <p className="text-sm text-muted-foreground">
              No entries yet. Pick a project, fill the Excel-style fields, and click Add entry.
            </p>
          )}
          {entries.length > 0 && (
            <div className="overflow-x-auto rounded-md border">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/40">
                    <th className="px-3 py-2 text-left">Date</th>
                    <th className="px-3 py-2 text-left">Work</th>
                    <th className="px-3 py-2 text-left">Activity</th>
                    <th className="px-3 py-2 text-left">Hours</th>
                    <th className="px-3 py-2 text-left">Billable</th>
                    <th className="px-3 py-2 text-left">Software</th>
                    <th className="px-3 py-2 text-left">Remarks</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.slice(0, 50).map((e) => (
                    <tr key={e.id} className="border-b last:border-0">
                      <td className="px-3 py-2">{e.date}</td>
                      <td className="px-3 py-2 text-xs">{e.work_type ?? "—"}</td>
                      <td className="px-3 py-2 text-xs">{e.activity_type ?? "—"}</td>
                      <td className="px-3 py-2 tabular-nums">{e.hours}</td>
                      <td className="px-3 py-2 tabular-nums text-xs">
                        {e.billable_hours != null
                          ? e.billable_hours
                          : e.is_billable
                            ? "Yes"
                            : "No"}
                      </td>
                      <td className="px-3 py-2 text-xs">{e.software_used ?? "—"}</td>
                      <td className="max-w-md truncate px-3 py-2">{e.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
