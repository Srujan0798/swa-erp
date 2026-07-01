import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ComplianceItemStatus } from "./ComplianceItemStatus";
import {
  useComplianceItems,
  useUpdateComplianceItem,
  useReviewComplianceItem,
} from "@/hooks/useCompliance";
import { useCurrentUser } from "@/hooks/useAuth";
import type { ComplianceStatus, ProjectComplianceItem } from "@/types/compliance";

const STATUS_FILTERS: { value: string; label: string }[] = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "compliant", label: "Compliant" },
  { value: "non_compliant", label: "Non-Compliant" },
  { value: "na", label: "N/A" },
];

interface ComplianceChecklistProps {
  projectId: string;
  standardId: string;
  standardName: string;
  onBack: () => void;
}

export function ComplianceChecklist({
  projectId,
  standardId,
  standardName,
  onBack,
}: ComplianceChecklistProps) {
  const { data: user } = useCurrentUser();
  const { data: items = [], isLoading } = useComplianceItems(projectId, standardId);
  const updateItem = useUpdateComplianceItem();
  const reviewItem = useReviewComplianceItem();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [editingNotes, setEditingNotes] = useState<string | null>(null);
  const [notesValue, setNotesValue] = useState("");

  const filteredItems =
    statusFilter === "all"
      ? items
      : items.filter((item) => item.status === statusFilter);

  const startEditNotes = (item: ProjectComplianceItem) => {
    setEditingNotes(item.id);
    setNotesValue(item.notes ?? "");
  };

  const saveNotes = (itemId: string) => {
    updateItem.mutate({ itemId, data: { notes: notesValue } });
    setEditingNotes(null);
  };

  const isAuditor = user?.role === "auditor";

  if (isLoading) {
    return <div className="text-muted-foreground p-4">Loading checklist...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBack}>
          &larr; Back to Dashboard
        </Button>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Filter:</span>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[160px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {STATUS_FILTERS.map((f) => (
                <SelectItem key={f.value} value={f.value}>
                  {f.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <h3 className="text-lg font-semibold">{standardName} Checklist</h3>

      {filteredItems.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          No items found. {statusFilter === "all" ? "Run initialization." : "Try a different filter."}
        </div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Requirement</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Mandatory</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Evidence</TableHead>
              <TableHead>Notes</TableHead>
              {isAuditor && <TableHead>Review</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.map((item) => (
              <TableRow key={item.id}>
                <TableCell className="max-w-[300px]">
                  {item.requirement}
                </TableCell>
                <TableCell>{item.category}</TableCell>
                <TableCell>
                  <Badge variant={item.is_mandatory ? "destructive" : "secondary"}>
                    {item.is_mandatory ? "Required" : "Optional"}
                  </Badge>
                </TableCell>
                <TableCell>
                  <ComplianceItemStatus itemId={item.id} status={item.status} />
                </TableCell>
                <TableCell>
                  {item.evidence_document_id ? (
                    <Badge variant="outline">Linked</Badge>
                  ) : (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        updateItem.mutate({
                          itemId: item.id,
                          data: { evidence_document_id: null },
                        })
                      }
                    >
                      Link Doc
                    </Button>
                  )}
                </TableCell>
                <TableCell>
                  {editingNotes === item.id ? (
                    <div className="flex gap-1">
                      <Textarea
                        value={notesValue}
                        onChange={(e) => setNotesValue(e.target.value)}
                        className="min-h-[60px] text-xs"
                      />
                      <div className="flex flex-col gap-1">
                        <Button size="sm" onClick={() => saveNotes(item.id)}>
                          Save
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setEditingNotes(null)}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => startEditNotes(item)}
                      className="text-sm text-left hover:underline text-muted-foreground"
                    >
                      {item.notes || "Add notes..."}
                    </button>
                  )}
                </TableCell>
                {isAuditor && (
                  <TableCell>
                    {item.reviewed_by ? (
                      <span className="text-xs text-muted-foreground">
                        Reviewed
                      </span>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => reviewItem.mutate({ itemId: item.id })}
                        disabled={reviewItem.isPending}
                      >
                        Review
                      </Button>
                    )}
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
