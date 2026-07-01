import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useSubmitTimesheet } from "@/hooks/useTimesheets";
import type { Timesheet } from "@/types/time";
import type { TimeEntry } from "@/types/time";

interface TimesheetViewProps {
  timesheet: Timesheet;
  entries: TimeEntry[];
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800",
  submitted: "bg-blue-100 text-blue-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
};

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function getWeekDates(weekStart: string): string[] {
  const start = new Date(weekStart);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    return d.toISOString().split("T")[0];
  });
}

export function TimesheetView({ timesheet, entries }: TimesheetViewProps) {
  const submitMutation = useSubmitTimesheet();
  const weekDates = getWeekDates(timesheet.week_start);

  const entriesByDate = entries.reduce<Record<string, TimeEntry[]>>((acc, entry) => {
    if (!acc[entry.date]) acc[entry.date] = [];
    acc[entry.date].push(entry);
    return acc;
  }, {});

  const handleSubmit = async () => {
    await submitMutation.mutateAsync(timesheet.id);
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <h3 className="font-semibold">
              Week of {new Date(timesheet.week_start).toLocaleDateString()}
            </h3>
            <Badge className={STATUS_COLORS[timesheet.status]}>
              {timesheet.status}
            </Badge>
          </div>
          {timesheet.status === "draft" && (
            <Button onClick={handleSubmit} disabled={submitMutation.isPending}>
              Submit Timesheet
            </Button>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                {DAYS.map((day, i) => (
                  <th key={day} className="border p-2 text-left text-sm font-medium bg-muted/50">
                    {day} ({new Date(weekDates[i]).toLocaleDateString("en-US", { month: "short", day: "numeric" })})
                  </th>
                ))}
                <th className="border p-2 text-left text-sm font-medium bg-muted/50">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                {weekDates.map((date) => (
                  <td key={date} className="border p-2 align-top">
                    {entriesByDate[date]?.map((entry) => (
                      <div key={entry.id} className={`text-xs p-1 mb-1 rounded ${entry.is_billable ? "bg-blue-50" : "bg-gray-50"}`}>
                        {entry.hours}h
                      </div>
                    ))}
                  </td>
                ))}
                <td className="border p-2 font-mono font-medium">
                  {timesheet.total_hours.toFixed(1)}h
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex gap-4 text-sm">
          <span>Total: <strong>{timesheet.total_hours.toFixed(1)}h</strong></span>
          <span>Billable: <strong>{timesheet.billable_hours.toFixed(1)}h</strong></span>
          <span>Non-billable: <strong>{(timesheet.total_hours - timesheet.billable_hours).toFixed(1)}h</strong></span>
        </div>
      </CardContent>
    </Card>
  );
}
