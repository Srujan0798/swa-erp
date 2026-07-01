import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAddProjectCost } from "@/hooks/useProjectPnL";
import type { ProjectCostCreate } from "@/types/financial";

interface CostEntryFormProps {
  projectId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

const CATEGORIES = ["material", "vendor", "overhead", "other"];

export function CostEntryForm({ projectId, onSuccess, onCancel }: CostEntryFormProps) {
  const [formData, setFormData] = useState<ProjectCostCreate>({
    category: "material",
    description: "",
    amount: 0,
    date: new Date().toISOString().split("T")[0],
  });
  const [error, setError] = useState("");

  const addCostMutation = useAddProjectCost();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.description.trim()) {
      setError("Description is required");
      return;
    }
    if (formData.amount <= 0) {
      setError("Amount must be greater than 0");
      return;
    }

    try {
      await addCostMutation.mutateAsync({ projectId, data: formData });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="category">Category</Label>
          <select
            id="category"
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c.charAt(0).toUpperCase() + c.slice(1)}
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
          <Label htmlFor="amount">Amount (₹)</Label>
          <Input
            id="amount"
            type="number"
            min="0"
            step="0.01"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Cost description"
          rows={2}
        />
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={addCostMutation.isPending}>
          {addCostMutation.isPending ? "Adding..." : "Add Cost"}
        </Button>
      </div>
    </form>
  );
}
