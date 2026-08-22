import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useCreateTimeEntry, useUpdateTimeEntry } from "@/hooks/useTimeEntries";
import type { TimeEntry, TimeEntryCreate } from "@/types/time";

interface TimeEntryFormProps {
  projects: { id: string; name: string }[];
  editEntry?: TimeEntry;
  onSuccess: () => void;
  onCancel: () => void;
}

export function TimeEntryForm({ projects, editEntry, onSuccess, onCancel }: TimeEntryFormProps) {
  const [formData, setFormData] = useState<TimeEntryCreate>({
    project_id: editEntry?.project_id ?? projects[0]?.id ?? "",
    date: editEntry?.date ?? new Date().toISOString().split("T")[0],
    hours: editEntry?.hours ?? 1,
    description: editEntry?.description ?? "",
    is_billable: editEntry?.is_billable ?? true,
    employee_name: editEntry?.employee_name ?? "",
    employee_role: editEntry?.employee_role ?? "",
    work_type: editEntry?.work_type ?? "",
    sheet_reference_id: editEntry?.sheet_reference_id ?? "",
    activity_type: editEntry?.activity_type ?? "",
    software_used: editEntry?.software_used ?? "",
    work_mode: editEntry?.work_mode ?? "",
    revision: editEntry?.revision ?? "",
    billable_hours: editEntry?.billable_hours ?? undefined,
  });
  const [error, setError] = useState("");

  const createMutation = useCreateTimeEntry();
  const updateMutation = useUpdateTimeEntry();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.project_id) {
      setError("Project is required");
      return;
    }
    if (formData.hours < 0.25 || formData.hours > 24) {
      setError("Hours must be between 0.25 and 24");
      return;
    }
    if (!formData.description.trim()) {
      setError("Description / remarks is required");
      return;
    }

    const payload: TimeEntryCreate = {
      ...formData,
      employee_name: formData.employee_name?.trim() || undefined,
      employee_role: formData.employee_role?.trim() || undefined,
      work_type: formData.work_type?.trim() || undefined,
      sheet_reference_id: formData.sheet_reference_id?.trim() || undefined,
      activity_type: formData.activity_type?.trim() || undefined,
      software_used: formData.software_used?.trim() || undefined,
      work_mode: formData.work_mode?.trim() || undefined,
      revision: formData.revision?.trim() || undefined,
    };

    try {
      if (editEntry) {
        await updateMutation.mutateAsync({ id: editEntry.id, data: payload });
      } else {
        await createMutation.mutateAsync(payload);
      }
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const set =
    (key: keyof TimeEntryCreate) =>
    (value: string | number | boolean | undefined): void => {
      setFormData((prev) => ({ ...prev, [key]: value }));
    };

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="project">Project *</Label>
          <select
            id="project"
            value={formData.project_id}
            onChange={(e) => set("project_id")(e.target.value)}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="date">Date *</Label>
          <Input
            id="date"
            type="date"
            value={formData.date}
            onChange={(e) => set("date")(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="hours">Hours logged *</Label>
          <Input
            id="hours"
            type="number"
            step="0.25"
            min="0.25"
            max="24"
            value={formData.hours}
            onChange={(e) => set("hours")(parseFloat(e.target.value) || 0)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="billable_hours">Billable hours</Label>
          <Input
            id="billable_hours"
            type="number"
            step="0.25"
            min="0"
            max="24"
            value={formData.billable_hours ?? ""}
            onChange={(e) => {
              const v = e.target.value;
              set("billable_hours")(v === "" ? undefined : parseFloat(v) || 0);
            }}
            placeholder="From Excel sheet"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="work_type">Work type</Label>
          <Input
            id="work_type"
            placeholder="PROJECT / PRE-PROJECT / INTERNAL"
            value={formData.work_type ?? ""}
            onChange={(e) => set("work_type")(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="activity_type">Activity type</Label>
          <Input
            id="activity_type"
            placeholder="CON, DBR, CAL…"
            value={formData.activity_type ?? ""}
            onChange={(e) => set("activity_type")(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="employee_name">Employee name</Label>
          <Input
            id="employee_name"
            value={formData.employee_name ?? ""}
            onChange={(e) => set("employee_name")(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="employee_role">Employee role</Label>
          <Input
            id="employee_role"
            placeholder="AE / RE / SE"
            value={formData.employee_role ?? ""}
            onChange={(e) => set("employee_role")(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="software_used">Software used</Label>
          <Input
            id="software_used"
            placeholder="CAD, EASE, RPS…"
            value={formData.software_used ?? ""}
            onChange={(e) => set("software_used")(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="work_mode">Work mode</Label>
          <Input
            id="work_mode"
            placeholder="Manual / Automated"
            value={formData.work_mode ?? ""}
            onChange={(e) => set("work_mode")(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="sheet_reference_id">Reference ID (sheet)</Label>
          <Input
            id="sheet_reference_id"
            placeholder="SWA-… project / token / doc"
            value={formData.sheet_reference_id ?? ""}
            onChange={(e) => set("sheet_reference_id")(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="revision">Revision write?</Label>
          <Input
            id="revision"
            placeholder="Yes / No (Excel column)"
            value={formData.revision ?? ""}
            onChange={(e) => set("revision")(e.target.value)}
          />
        </div>

        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="billable" className="flex items-center gap-2">
            <input
              id="billable"
              type="checkbox"
              checked={formData.is_billable}
              onChange={(e) => set("is_billable")(e.target.checked)}
              className="rounded"
            />
            Billable
          </Label>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Remarks / description *</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => set("description")(e.target.value)}
          placeholder="What did you work on? (Excel Remarks)"
          rows={3}
        />
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
          {createMutation.isPending || updateMutation.isPending
            ? "Saving..."
            : editEntry
              ? "Update"
              : "Add Entry"}
        </Button>
      </div>
    </form>
  );
}
