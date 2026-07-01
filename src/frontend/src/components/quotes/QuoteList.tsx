import { useState } from "react";
import { useQuotes, useDeleteQuote, useCloneQuote } from "@/hooks/useQuotes";
import { useCurrentUser } from "@/hooks/useAuth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Eye, Trash2, Copy, ChevronLeft, ChevronRight } from "lucide-react";
import type { QuoteStatus } from "@/types/api";

const STATUS_CONFIG: Record<QuoteStatus, { label: string; className: string }> = {
  draft: { label: "Draft", className: "bg-gray-100 text-gray-800" },
  pending_approval: { label: "Pending Approval", className: "bg-yellow-100 text-yellow-800" },
  approved: { label: "Approved", className: "bg-blue-100 text-blue-800" },
  sent: { label: "Sent", className: "bg-purple-100 text-purple-800" },
  accepted: { label: "Accepted", className: "bg-green-100 text-green-800" },
  rejected: { label: "Rejected", className: "bg-red-100 text-red-800" },
};

interface QuoteListProps {
  projectId: string;
  onViewQuote: (quoteId: string) => void;
}

export function QuoteList({ projectId, onViewQuote }: QuoteListProps) {
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const { data, isLoading } = useQuotes(projectId, page, pageSize);
  const deleteMutation = useDeleteQuote();
  const cloneMutation = useCloneQuote();
  const { data: user } = useCurrentUser();

  const handleDelete = (id: string) => {
    if (confirm("Delete this quote?")) {
      deleteMutation.mutate({ id, projectId });
    }
  };

  const handleClone = (id: string) => {
    cloneMutation.mutate({ id, projectId });
  };

  if (isLoading) return <div className="p-4 text-muted-foreground">Loading quotes...</div>;

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quotes ({total})</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-muted-foreground text-sm">No quotes yet. Create one from a BOQ version.</p>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Version</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Subtotal</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                  <TableHead>Valid Until</TableHead>
                  <TableHead>Created By</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((quote) => {
                  const statusCfg = STATUS_CONFIG[quote.status];
                  return (
                    <TableRow key={quote.id}>
                      <TableCell className="font-mono">v{quote.version_number}</TableCell>
                      <TableCell>
                        <Badge className={statusCfg.className}>{statusCfg.label}</Badge>
                      </TableCell>
                      <TableCell className="text-right">₹{quote.subtotal.toLocaleString()}</TableCell>
                      <TableCell className="text-right font-medium">₹{quote.total_amount.toLocaleString()}</TableCell>
                      <TableCell>{quote.valid_until ? new Date(quote.valid_until).toLocaleDateString() : "—"}</TableCell>
                      <TableCell>{quote.created_by_name ?? "—"}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex gap-1 justify-end">
                          <Button variant="ghost" size="icon" onClick={() => onViewQuote(quote.id)}>
                            <Eye className="h-4 w-4" />
                          </Button>
                          {quote.status === "rejected" && (user?.role === "admin" || user?.role === "pm") && (
                            <Button variant="ghost" size="icon" onClick={() => handleClone(quote.id)}>
                              <Copy className="h-4 w-4" />
                            </Button>
                          )}
                          {quote.status === "draft" && (user?.role === "admin" || user?.role === "pm") && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDelete(quote.id)}
                              disabled={deleteMutation.isPending}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {page} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
