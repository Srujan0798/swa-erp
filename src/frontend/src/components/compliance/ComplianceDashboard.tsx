import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  useComplianceSummary,
  useStandards,
  useBulkCreateItems,
} from "@/hooks/useCompliance";
import type { ComplianceDashboardStandard } from "@/types/compliance";

interface ComplianceDashboardProps {
  projectId: string;
  onSelectStandard: (standardId: string, standardName: string) => void;
}

function StandardCard({
  data,
  onClick,
}: {
  data: ComplianceDashboardStandard;
  onClick: () => void;
}) {
  return (
    <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={onClick}>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{data.standard_name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Progress</span>
          <span className="font-medium">{data.compliance_percentage.toFixed(0)}%</span>
        </div>
        <Progress value={data.compliance_percentage} />
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{data.compliant_count} compliant</span>
          <span className="text-red-600">{data.non_compliant_count} non-compliant</span>
          <span className="text-yellow-600">{data.pending_count} pending</span>
          <span className="text-blue-600">{data.na_count} N/A</span>
        </div>
        <div className="text-xs text-muted-foreground">
          {data.total_items} total items
        </div>
      </CardContent>
    </Card>
  );
}

export function ComplianceDashboard({
  projectId,
  onSelectStandard,
}: ComplianceDashboardProps) {
  const { data: summary, isLoading: summaryLoading } = useComplianceSummary(projectId);
  const { data: standards = [] } = useStandards();
  const bulkCreate = useBulkCreateItems(projectId);

  if (summaryLoading) {
    return <div className="text-muted-foreground p-4">Loading compliance data...</div>;
  }

  if (!summary || summary.standards.length === 0) {
    return (
      <div className="text-center py-12 space-y-4">
        <h3 className="text-lg font-semibold">Compliance Tracking</h3>
        <p className="text-muted-foreground">
          No compliance data initialized for this project.
        </p>
        <div className="flex gap-2 justify-center flex-wrap">
          {standards.map((std) => (
            <Button
              key={std.id}
              variant="outline"
              onClick={() => bulkCreate.mutate(std.id)}
              disabled={bulkCreate.isPending}
            >
              Initialize {std.name}
            </Button>
          ))}
          {standards.length === 0 && (
            <Button
              variant="outline"
              disabled
            >
              No standards available
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Compliance Overview</h3>
          <p className="text-sm text-muted-foreground">
            Overall compliance: {summary.overall_percentage.toFixed(0)}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {summary.standards.map((std) => (
          <StandardCard
            key={std.standard_name}
            data={std}
            onClick={() => onSelectStandard(std.standard_name, std.standard_name)}
          />
        ))}
      </div>
    </div>
  );
}
