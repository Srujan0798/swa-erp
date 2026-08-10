"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
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
import { api } from "@/lib/api";
import type { TimeEntry, TimeEntryListResponse } from "@/types/time";
import { useToast } from "@/hooks/useToast";

const timeKey = (...segments: (string | number | boolean | undefined)[]) =>
  ["time", ...segments] as const;

export default function TimeTrackingPage() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const today = new Date().toISOString().split("T")[0];
  const [projectId, setProjectId] = useState("");
  const [form, setForm] = useState({
    date: today,
    hours: "",
    description: "",
    is_billable: true,
  });

  const { data: projectsData } = useQuery({
    queryKey: ["projects-for-time"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];

  const { data: list, isLoading, isError } = useQuery<TimeEntryListResponse>({
    queryKey: timeKey("entries"),
    queryFn: async () => api.listTimeEntries(),
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
    if (!form.description.trim()) {
      toast({ title: "Description required", variant: "destructive" });
      return;
    }
    try {
      await api.createTimeEntry({
        project_id: projectId,
        date: form.date,
        hours,
        description: form.description,
        is_billable: form.is_billable,
      });
      toast({ title: "Time entry saved" });
      qc.invalidateQueries({ queryKey: timeKey("entries") });
      setForm({ date: today, hours: "", description: "", is_billable: true });
    } catch (e) {
      toast({
        title: (e as Error).message || "Failed to save",
        variant: "destructive",
      });
    }
  };

  const weeklyHours = entries.reduce((sum, e) => sum + Number(e.hours || 0), 0);
  const billableHours = entries
    .filter((e) => e.is_billable)
    .reduce((s, e) => s + Number(e.hours || 0), 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Time tracking</h1>
        <p className="text-sm text-muted-foreground">
          Log hours against a real project (15-minute style increments supported as 0.25).
        </p>
      </div>

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

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add time entry</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Project *</Label>
            <Select value={projectId || undefined} onValueChange={setProjectId}>
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
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Date</Label>
              <Input
                type="date"
                value={form.date}
                onChange={(e) => setForm({ ...form, date: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Hours</Label>
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
          </div>
          <div className="space-y-2">
            <Label>Description</Label>
            <Input
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="What did you work on?"
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

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Recent entries</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <p className="text-sm text-muted-foreground">Loading…</p>
          )}
          {isError && (
            <p className="text-sm text-destructive">Failed to load time entries.</p>
          )}
          {!isLoading && entries.length === 0 && (
            <p className="text-sm text-muted-foreground">No entries yet.</p>
          )}
          {entries.length > 0 && (
            <div className="overflow-x-auto rounded-md border">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/40">
                    <th className="px-3 py-2 text-left">Date</th>
                    <th className="px-3 py-2 text-left">Hours</th>
                    <th className="px-3 py-2 text-left">Billable</th>
                    <th className="px-3 py-2 text-left">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.slice(0, 50).map((e) => (
                    <tr key={e.id} className="border-b last:border-0">
                      <td className="px-3 py-2">{e.date}</td>
                      <td className="px-3 py-2 tabular-nums">{e.hours}</td>
                      <td className="px-3 py-2">{e.is_billable ? "Yes" : "No"}</td>
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
