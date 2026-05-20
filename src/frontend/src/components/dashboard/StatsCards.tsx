import { useDashboard } from "@/hooks/useDashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { IndianRupee, FolderOpen, FileText, Hammer } from "lucide-react";

function formatINR(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

export function StatsCards() {
  const { data: stats, isLoading } = useDashboard();

  const cards = [
    {
      title: "Total Active Projects",
      value: stats?.total_active ?? 0,
      icon: FolderOpen,
      format: (v: number) => v.toString(),
    },
    {
      title: "Total Estimated Value",
      value: stats?.total_estimated_value ?? 0,
      icon: IndianRupee,
      format: formatINR,
    },
    {
      title: "In Quote Stage",
      value: stats?.by_status?.Quote ?? 0,
      icon: FileText,
      format: (v: number) => v.toString(),
    },
    {
      title: "In Execution",
      value: stats?.by_status?.Execution ?? 0,
      icon: Hammer,
      format: (v: number) => v.toString(),
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
            <card.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">{card.format(card.value)}</div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}