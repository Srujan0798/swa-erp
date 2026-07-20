import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type {
  SustainabilityMetric,
  SustainabilityMetricCreate,
} from "@/types/api";

interface SustainabilityFormProps {
  projectId: string;
  initial?: SustainabilityMetric | null;
  onSubmit: (data: SustainabilityMetricCreate) => void;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

function toNumber(value: string): number | null {
  if (value.trim() === "") return null;
  const n = Number(value);
  return Number.isNaN(n) ? null : n;
}

export function SustainabilityForm({
  projectId,
  initial,
  onSubmit,
  onCancel,
  isSubmitting,
}: SustainabilityFormProps) {
  const [referenceId, setReferenceId] = useState(initial?.reference_id ?? "");
  const [recordedDate, setRecordedDate] = useState(
    initial?.recorded_date ? initial.recorded_date.slice(0, 10) : ""
  );
  const [compliant, setCompliant] = useState<string>(
    initial?.compliant_with_green_standards === null ||
      initial?.compliant_with_green_standards === undefined
      ? "na"
      : initial.compliant_with_green_standards
        ? "yes"
        : "no"
  );
  const [energySaved, setEnergySaved] = useState(
    initial?.energy_saved_kwh != null ? String(initial.energy_saved_kwh) : ""
  );
  const [co2Avoided, setCo2Avoided] = useState(
    initial?.co2_avoided_tco2e != null ? String(initial.co2_avoided_tco2e) : ""
  );
  const [lifecycleSavings, setLifecycleSavings] = useState(
    initial?.lifecycle_cost_savings_inr != null
      ? String(initial.lifecycle_cost_savings_inr)
      : ""
  );
  const [insulationRatio, setInsulationRatio] = useState(
    initial?.insulation_efficiency_ratio != null
      ? String(initial.insulation_efficiency_ratio)
      : ""
  );
  const [paybackMonths, setPaybackMonths] = useState(
    initial?.payback_period_months != null ? String(initial.payback_period_months) : ""
  );
  const [notes, setNotes] = useState(initial?.notes ?? "");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data: SustainabilityMetricCreate = {
      project_id: projectId,
      reference_id: referenceId.trim() || null,
      recorded_date: recordedDate || null,
      compliant_with_green_standards:
        compliant === "na" ? null : compliant === "yes",
      energy_saved_kwh: toNumber(energySaved),
      co2_avoided_tco2e: toNumber(co2Avoided),
      lifecycle_cost_savings_inr: toNumber(lifecycleSavings),
      insulation_efficiency_ratio: toNumber(insulationRatio),
      payback_period_months: toNumber(paybackMonths),
      notes: notes.trim() || null,
    };
    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="reference_id">Reference ID</Label>
          <Input
            id="reference_id"
            value={referenceId}
            onChange={(e) => setReferenceId(e.target.value)}
            placeholder="SWA-2025-PRJ-065"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="recorded_date">Recorded Date</Label>
          <Input
            id="recorded_date"
            type="date"
            value={recordedDate}
            onChange={(e) => setRecordedDate(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label>Compliant with Green Standards</Label>
        <Select value={compliant} onValueChange={setCompliant}>
          <SelectTrigger>
            <SelectValue placeholder="Select" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="na">Not specified</SelectItem>
            <SelectItem value="yes">Yes</SelectItem>
            <SelectItem value="no">No</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="energy_saved">Total Energy Saved (kWh)</Label>
          <Input
            id="energy_saved"
            type="number"
            step="0.01"
            value={energySaved}
            onChange={(e) => setEnergySaved(e.target.value)}
            placeholder="0.00"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="co2_avoided">CO2 Avoided (tCO2e)</Label>
          <Input
            id="co2_avoided"
            type="number"
            step="0.01"
            value={co2Avoided}
            onChange={(e) => setCo2Avoided(e.target.value)}
            placeholder="0.00"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="lifecycle_savings">Lifecycle Cost Savings (INR)</Label>
          <Input
            id="lifecycle_savings"
            type="number"
            step="0.01"
            value={lifecycleSavings}
            onChange={(e) => setLifecycleSavings(e.target.value)}
            placeholder="0.00"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="insulation_ratio">Insulation Efficiency (Actual/Expected)</Label>
          <Input
            id="insulation_ratio"
            type="number"
            step="0.01"
            value={insulationRatio}
            onChange={(e) => setInsulationRatio(e.target.value)}
            placeholder="e.g. 0.89"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="payback_months">Payback Period (Months)</Label>
          <Input
            id="payback_months"
            type="number"
            step="0.01"
            value={paybackMonths}
            onChange={(e) => setPaybackMonths(e.target.value)}
            placeholder="0.00"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
        />
      </div>

      <div className="flex gap-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : initial ? "Update Metric" : "Add Metric"}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
