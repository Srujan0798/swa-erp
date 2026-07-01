import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useApproveTimesheet, useRejectTimesheet } from "@/hooks/useTimesheets";
import type { Timesheet } from "@/types/time";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface TimesheetSummaryProps {
  timesheets: Timesheet[];
  isLoading: boolean;
  weekOffset: number;
  onWeekChange: (offset: number) => void;
  isManager?: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800",
  submitted: "bg-blue-100 text-blue-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
};

export function TimesheetSummary({ timesheets, isLoading, weekOffset, onWeekChange, isManager }: TimesheetSummaryProps) {
  const approveMutation = useApproveTimesheet();
  const rejectMutation = useRejectTimesheet();

  const weekLabel = weekOffset === 0 ? "This Week" : weekOffset === -1 ? "Last Week" : `${Math.abs(weekOffset)} weeks ${weekOffset > 0 ? "ahead" : "ago"}`;

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => onWeekChange(-1)}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="font-medium">{weekLabel}</span>
            <Button variant="outline" size="sm" onClick={() => onWeekChange(1)}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : timesheets.length === 0 ? (
          <p className="text-muted-foreground text-sm">No timesheets found</p>
        ) : (
          <div className="space-y-3">
            {timesheets.map((ts) => (
              <div key={ts.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{ts.user_name ?? "User"}</span>
                    <Badge className={STATUS_COLORS[ts.status]}>{ts.status}</Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {new Date(ts.week_start).toLocaleDateString()} - {new Date(ts.week_end).toLocaleDateString()}
                    {" · "}
                    {ts.total_hours.toFixed(1)}h total, {ts.billable_hours.toFixed(1)}h billable
                  </div>
                </div>
                {isManager && ts.status === "submitted" && (
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => approveMutation.mutateAsync(ts.id)}
                      disabled={approveMutation.isPending}
                    >
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => rejectMutation.mutateAsync(ts.id)}
                      disabled={rejectMutation.isPending}
                    >
                      Reject
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
