import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDeleteInvoice } from "@/hooks/useInvoices";
import type { Invoice } from "@/types/financial";
import { Eye, Trash2 } from "lucide-react";

interface InvoiceListProps {
  invoices: Invoice[];
  isLoading: boolean;
  onView: (id: string) => void;
  statusFilter?: string;
  onStatusFilterChange?: (status: string) => void;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800",
  sent: "bg-blue-100 text-blue-800",
  paid: "bg-green-100 text-green-800",
};

export function InvoiceList({ invoices, isLoading, onView, statusFilter, onStatusFilterChange }: InvoiceListProps) {
  const deleteMutation = useDeleteInvoice();

  const handleDelete = async (id: string) => {
    if (window.confirm("Delete this invoice?")) {
      await deleteMutation.mutateAsync(id);
    }
  };

  return (
    <Card>
      <CardContent className="pt-6">
        {onStatusFilterChange && (
          <div className="mb-4">
            <Select value={statusFilter ?? ""} onValueChange={onStatusFilterChange}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Statuses</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="sent">Sent</SelectItem>
                <SelectItem value="paid">Paid</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Invoice #</TableHead>
                <TableHead>Project</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center">Loading...</TableCell>
                </TableRow>
              ) : invoices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center">No invoices found</TableCell>
                </TableRow>
              ) : (
                invoices.map((invoice) => (
                  <TableRow key={invoice.id}>
                    <TableCell className="font-mono">{invoice.invoice_number}</TableCell>
                    <TableCell>{invoice.project_name ?? "—"}</TableCell>
                    <TableCell>
                      <Badge className={STATUS_COLORS[invoice.status]}>
                        {invoice.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono">₹{invoice.total.toLocaleString("en-IN")}</TableCell>
                    <TableCell>
                      {invoice.due_date ? new Date(invoice.due_date).toLocaleDateString() : "—"}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm" aria-label="View invoice" onClick={() => onView(invoice.id)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" aria-label="Delete invoice" onClick={() => handleDelete(invoice.id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
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
