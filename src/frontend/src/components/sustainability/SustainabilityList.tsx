import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Pencil, Trash2 } from "lucide-react";
import type { SustainabilityMetric } from "@/types/api";

interface SustainabilityListProps {
  metrics: SustainabilityMetric[];
  isLoading?: boolean;
  onEdit: (metric: SustainabilityMetric) => void;
  onDelete: (metric: SustainabilityMetric) => void;
  onAdd?: () => void;
}

function fmt(value: number | null | undefined, suffix = ""): string {
  if (value === null || value === undefined || value === 0) return "—";
  return `${Number(value).toLocaleString()}${suffix}`;
}

export function SustainabilityList({
  metrics,
  isLoading,
  onEdit,
  onDelete,
  onAdd,
}: SustainabilityListProps) {
  if (isLoading) return <div className="p-4 text-muted-foreground">Loading metrics...</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sustainability Metrics ({metrics.length})</CardTitle>
      </CardHeader>
      <CardContent>
        {metrics.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            No metrics recorded yet.{" "}
            {onAdd ? (
              <button
                type="button"
                className="underline font-medium text-foreground"
                onClick={onAdd}
              >
                Add the first metric
              </button>
            ) : (
              <>Add one when the client provides green-building data.</>
            )}
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Reference ID</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Compliant</TableHead>
                <TableHead className="text-right">Energy Saved (kWh)</TableHead>
                <TableHead className="text-right">CO2 Avoided (tCO2e)</TableHead>
                <TableHead className="text-right">Lifecycle Savings (₹)</TableHead>
                <TableHead className="text-right">Insulation Ratio</TableHead>
                <TableHead className="text-right">Payback (mo)</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {metrics.map((m) => (
                <TableRow key={m.id}>
                  <TableCell className="font-mono">{m.reference_id ?? "—"}</TableCell>
                  <TableCell>
                    {m.recorded_date ? new Date(m.recorded_date).toLocaleDateString() : "—"}
                  </TableCell>
                  <TableCell>
                    {m.compliant_with_green_standards === null ? (
                      <span className="text-muted-foreground">—</span>
                    ) : m.compliant_with_green_standards ? (
                      <Badge className="bg-green-100 text-green-800">Yes</Badge>
                    ) : (
                      <Badge className="bg-red-100 text-red-800">No</Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right">{fmt(m.energy_saved_kwh)}</TableCell>
                  <TableCell className="text-right">{fmt(m.co2_avoided_tco2e)}</TableCell>
                  <TableCell className="text-right">
                    {fmt(m.lifecycle_cost_savings_inr)}
                  </TableCell>
                  <TableCell className="text-right">{fmt(m.insulation_efficiency_ratio)}</TableCell>
                  <TableCell className="text-right">{fmt(m.payback_period_months)}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex gap-1 justify-end">
                      <Button variant="ghost" size="icon" aria-label="Edit metric" onClick={() => onEdit(m)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label="Delete metric"
                        onClick={() => onDelete(m)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
