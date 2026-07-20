"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { TimeEntry, TimeEntryListResponse } from "@/types/time";

type TimeEntryForm = { date: string; hours: string; task_id: string; description: string; is_billable: boolean };

const timeKey = (...segments: (string | number | boolean | undefined)[]) => ["time", ...segments] as const;

export default function TimeTrackingPage() {
  const qc = useQueryClient();
  const today = new Date().toISOString().split("T")[0];
  const [form, setForm] = useState<TimeEntryForm>({ date: today, hours: "", task_id: "", description: "", is_billable: true });
  const [selectedDate, setSelectedDate] = useState(today);

  const { data: list, isLoading } = useQuery<TimeEntryListResponse>({
    queryKey: timeKey("entries"),
    queryFn: async () => api.listTimeEntries(),
  });

  const entries: TimeEntry[] = list?.items ?? [];

  const submit = async () => {
    const hours = parseFloat(form.hours as string);
    if (Number.isNaN(hours) || hours <= 0 || hours > 24) return;
    await api.createTimeEntry({
      project_id: "",
      task_id: form.task_id || undefined,
      date: form.date,
      hours: hours as number,
      description: form.description,
      is_billable: form.is_billable,
    });
    qc.invalidateQueries({ queryKey: timeKey("entries") });
    setForm({ date: today, hours: "", task_id: "", description: "", is_billable: true });
  };

  const weeklyHours = entries.reduce((sum, e) => sum + Number(e.hours || 0), 0);
  const billableHours = entries.filter((e) => e.is_billable).reduce((s, e) => s + Number(e.hours || 0), 0);

  if (isLoading) return <div className="p-6 text-sm text-muted-foreground">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Time Tracking</h1>
          <p className="text-sm text-muted-foreground">Log time against projects and tasks.</p>
        </div>
        <div className="flex items-center gap-2">
          <input type="date" className="rounded-md border px-2 py-1 text-sm" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} />
          <Button variant="outline" size="sm">Generate weekly</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card><CardHeader><CardTitle className="text-sm">Total Hours</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{weeklyHours.toFixed(2)}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Billable Hours</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{billableHours.toFixed(2)}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Entries</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{entries.length}</p></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Add Time Entry</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><Label>Date</Label><Input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} /></div>
            <div><Label>Hours</Label><Input type="number" step="0.25" value={form.hours} onChange={(e) => setForm({ ...form, hours: e.target.value })} /></div>
          </div>
          <div><Label>Description</Label><Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          <div><Label>Task ID (optional)</Label><Input value={form.task_id} onChange={(e) => setForm({ ...form, task_id: e.target.value })} /></div>
          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_billable} onChange={(e) => setForm({ ...form, is_billable: e.target.checked })} /> Billable</label>
          <Button onClick={submit}>Add Entry</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Recent Entries</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {entries.map((e) => (
              <div key={e.id} className="flex justify-between p-2 border-b last:border-0">
                <div><p className="font-medium">{e.description || "No description"}</p><p className="text-sm text-muted-foreground">{e.date} · Task: {e.task_id || "General"}</p></div>
                <div className="text-right"><p className="font-medium">{e.hours}h</p>{e.is_billable ? <Badge>Billable</Badge> : <Badge variant="secondary">Non-billable</Badge>}</div>
              </div>
            ))}
            {entries.length === 0 && <p className="text-sm text-muted-foreground">No entries yet.</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
