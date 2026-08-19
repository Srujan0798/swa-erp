import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDeleteTimeEntry } from "@/hooks/useTimeEntries";
import { useCurrentUser } from "@/hooks/useAuth";
import { canWrite } from "@/lib/permissions";
import type { TimeEntry } from "@/types/time";
import { Pencil, Trash2 } from "lucide-react";

interface TimeEntryListProps {
  entries: TimeEntry[];
  isLoading: boolean;
  onEdit: (entry: TimeEntry) => void;
}

export function TimeEntryList({ entries, isLoading, onEdit }: TimeEntryListProps) {
  const { data: user } = useCurrentUser();
  const write = canWrite(user);
  const deleteMutation = useDeleteTimeEntry();

  const handleDelete = async (id: string) => {
    if (window.confirm("Delete this time entry?")) {
      await deleteMutation.mutateAsync(id);
    }
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Project</TableHead>
                <TableHead>Hours</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Billable</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center">Loading...</TableCell>
                </TableRow>
              ) : entries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center">No time entries found</TableCell>
                </TableRow>
              ) : (
                entries.map((entry) => (
                  <TableRow key={entry.id} className={entry.is_billable ? "" : "bg-muted/50"}>
                    <TableCell>{new Date(entry.date).toLocaleDateString()}</TableCell>
                    <TableCell>{entry.project_name ?? "—"}</TableCell>
                    <TableCell className="font-mono">{entry.hours.toFixed(2)}</TableCell>
                    <TableCell className="max-w-xs truncate">{entry.description}</TableCell>
                    <TableCell>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${entry.is_billable ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}>
                        {entry.is_billable ? "Yes" : "No"}
                      </span>
                    </TableCell>
                    <TableCell>
                      {write ? (
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm" onClick={() => onEdit(entry)} aria-label="Edit entry">
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDelete(entry.id)} aria-label="Delete entry">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
