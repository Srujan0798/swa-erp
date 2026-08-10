import { useState, type FormEvent, type ReactElement } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useCreateInvoice } from "@/hooks/useInvoices";
import type { InvoiceCreate, InvoiceItemCreate } from "@/types/financial";
import { Plus, Trash2 } from "lucide-react";

interface InvoiceCreateFormProps {
  projectId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

interface LineDraft {
  description: string;
  quantity: string;
  rate: string;
  category: string;
}

const emptyLine = (): LineDraft => ({
  description: "",
  quantity: "1",
  rate: "",
  category: "",
});

/**
 * Minimal create-invoice form matching Tokens/Agreements patterns.
 */
export function InvoiceCreateForm({
  projectId,
  onSuccess,
  onCancel,
}: InvoiceCreateFormProps): ReactElement {
  const createMutation = useCreateInvoice();
  const [dueDate, setDueDate] = useState("");
  const [taxRate, setTaxRate] = useState("18");
  const [notes, setNotes] = useState("");
  const [lines, setLines] = useState<LineDraft[]>([emptyLine()]);
  const [error, setError] = useState("");

  const updateLine = (index: number, patch: Partial<LineDraft>): void => {
    setLines((prev) => prev.map((line, i) => (i === index ? { ...line, ...patch } : line)));
  };

  const removeLine = (index: number): void => {
    setLines((prev) => (prev.length <= 1 ? prev : prev.filter((_, i) => i !== index)));
  };

  const handleSubmit = async (e: FormEvent): Promise<void> => {
    e.preventDefault();
    setError("");

    const items: InvoiceItemCreate[] = [];
    for (const line of lines) {
      const description = line.description.trim();
      const quantity = Number(line.quantity);
      const rate = Number(line.rate);
      if (!description) {
        setError("Each line needs a description");
        return;
      }
      if (!Number.isFinite(quantity) || quantity <= 0) {
        setError("Quantity must be greater than 0");
        return;
      }
      if (!Number.isFinite(rate) || rate < 0) {
        setError("Rate must be a non-negative number");
        return;
      }
      items.push({
        description,
        quantity,
        rate,
        category: line.category.trim() || undefined,
      });
    }

    const tax = Number(taxRate);
    if (!Number.isFinite(tax) || tax < 0) {
      setError("Tax rate must be a non-negative number");
      return;
    }

    const payload: InvoiceCreate = {
      project_id: projectId,
      tax_rate: tax,
      due_date: dueDate || undefined,
      notes: notes.trim() || undefined,
      items,
    };

    try {
      await createMutation.mutateAsync({ projectId, data: payload });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create invoice");
    }
  };

  const subtotal = lines.reduce((sum, line) => {
    const q = Number(line.quantity) || 0;
    const r = Number(line.rate) || 0;
    return sum + q * r;
  }, 0);
  const taxAmount = subtotal * ((Number(taxRate) || 0) / 100);

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="inv-due">Due date</Label>
          <Input
            id="inv-due"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="inv-tax">GST / tax rate (%)</Label>
          <Input
            id="inv-tax"
            type="number"
            min={0}
            step="0.01"
            value={taxRate}
            onChange={(e) => setTaxRate(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>Line items *</Label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setLines((prev) => [...prev, emptyLine()])}
          >
            <Plus className="mr-1 h-3 w-3" />
            Add line
          </Button>
        </div>
        <div className="space-y-3">
          {lines.map((line, index) => (
            <div
              key={index}
              className="grid grid-cols-12 gap-2 rounded-md border p-2 items-end"
            >
              <div className="col-span-5 space-y-1">
                <Label className="text-xs text-muted-foreground">Description</Label>
                <Input
                  value={line.description}
                  placeholder="Consultancy fee, design hours…"
                  onChange={(e) => updateLine(index, { description: e.target.value })}
                />
              </div>
              <div className="col-span-2 space-y-1">
                <Label className="text-xs text-muted-foreground">Qty</Label>
                <Input
                  type="number"
                  min={0}
                  step="0.01"
                  value={line.quantity}
                  onChange={(e) => updateLine(index, { quantity: e.target.value })}
                />
              </div>
              <div className="col-span-2 space-y-1">
                <Label className="text-xs text-muted-foreground">Rate (₹)</Label>
                <Input
                  type="number"
                  min={0}
                  step="0.01"
                  value={line.rate}
                  onChange={(e) => updateLine(index, { rate: e.target.value })}
                />
              </div>
              <div className="col-span-2 space-y-1">
                <Label className="text-xs text-muted-foreground">Category</Label>
                <Input
                  value={line.category}
                  placeholder="Optional"
                  onChange={(e) => updateLine(index, { category: e.target.value })}
                />
              </div>
              <div className="col-span-1 flex justify-end pb-0.5">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  disabled={lines.length <= 1}
                  onClick={() => removeLine(index)}
                  aria-label="Remove line"
                >
                  <Trash2 className="h-4 w-4 text-muted-foreground" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="inv-notes">Notes</Label>
        <Textarea
          id="inv-notes"
          rows={2}
          value={notes}
          placeholder="Payment terms, PO reference…"
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>

      <div className="rounded-md bg-muted/50 px-3 py-2 text-sm flex justify-between">
        <span className="text-muted-foreground">
          Subtotal ₹{subtotal.toLocaleString("en-IN", { maximumFractionDigits: 2 })} · Tax ₹
          {taxAmount.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
        </span>
        <span className="font-semibold">
          Total ₹{(subtotal + taxAmount).toLocaleString("en-IN", { maximumFractionDigits: 2 })}
        </span>
      </div>

      {error ? <p className="text-sm text-destructive">{error}</p> : null}

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel} disabled={createMutation.isPending}>
          Cancel
        </Button>
        <Button type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? "Creating…" : "Create invoice"}
        </Button>
      </div>
    </form>
  );
}
