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
      setError("Description is required");
      return;
    }

    try {
      if (editEntry) {
        await updateMutation.mutateAsync({ id: editEntry.id, data: formData });
      } else {
        await createMutation.mutateAsync(formData);
      }
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="project">Project</Label>
          <select
            id="project"
            value={formData.project_id}
            onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
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
          <Label htmlFor="date">Date</Label>
          <Input
            id="date"
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="hours">Hours</Label>
          <Input
            id="hours"
            type="number"
            step="0.25"
            min="0.25"
            max="24"
            value={formData.hours}
            onChange={(e) => setFormData({ ...formData, hours: parseFloat(e.target.value) || 0 })}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="billable" className="flex items-center gap-2">
            <input
              id="billable"
              type="checkbox"
              checked={formData.is_billable}
              onChange={(e) => setFormData({ ...formData, is_billable: e.target.checked })}
              className="rounded"
            />
            Billable
          </Label>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="What did you work on?"
          rows={3}
        />
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
          {createMutation.isPending || updateMutation.isPending ? "Saving..." : editEntry ? "Update" : "Add Entry"}
        </Button>
      </div>
    </form>
  );
}
