import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ProjectPnL, CostBreakdownItem } from "@/types/financial";

interface PnlDashboardProps {
  pnl: ProjectPnL;
  isLoading: boolean;
}

export function PnlDashboard({ pnl, isLoading }: PnlDashboardProps) {
  if (isLoading) {
    return <p className="text-muted-foreground text-sm">Loading...</p>;
  }

  if (!pnl) {
    return <p className="text-muted-foreground text-sm">No P&L data available</p>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Revenue</p>
            <p className="text-2xl font-bold">₹{pnl.total_revenue.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Costs</p>
            <p className="text-2xl font-bold">₹{pnl.total_costs.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Net Profit</p>
            <p className={`text-2xl font-bold ${pnl.net_profit >= 0 ? "text-green-600" : "text-red-600"}`}>
              ₹{pnl.net_profit.toLocaleString()}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Margin</p>
            <p className={`text-2xl font-bold ${pnl.margin_pct >= 0 ? "text-green-600" : "text-red-600"}`}>
              {pnl.margin_pct.toFixed(1)}%
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <h3 className="font-semibold mb-4">Cost Breakdown</h3>
          {pnl.cost_breakdown.length === 0 ? (
            <p className="text-muted-foreground text-sm">No costs recorded</p>
          ) : (
            <div className="space-y-3">
              {pnl.cost_breakdown.map((item) => (
                <CostBreakdownRow key={item.category} item={item} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function CostBreakdownRow({ item }: { item: CostBreakdownItem }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="outline">{item.category}</Badge>
          <span className="text-sm text-muted-foreground">({item.count} items)</span>
        </div>
        <span className="font-mono">₹{item.amount.toLocaleString()} ({item.percentage.toFixed(1)}%)</span>
      </div>
      <div className="w-full bg-muted rounded-full h-2">
        <div
          className="bg-primary h-2 rounded-full"
          style={{ width: `${Math.min(item.percentage, 100)}%` }}
        />
      </div>
    </div>
  );
}
