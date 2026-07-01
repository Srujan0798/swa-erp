import { Button } from "@/components/ui/button";
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
import { useUpdateInvoiceStatus } from "@/hooks/useInvoices";
import type { Invoice } from "@/types/financial";
import { ArrowLeft, Send, CheckCircle } from "lucide-react";

interface InvoiceDetailProps {
  invoice: Invoice;
  onBack: () => void;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800",
  sent: "bg-blue-100 text-blue-800",
  paid: "bg-green-100 text-green-800",
};

export function InvoiceDetail({ invoice, onBack }: InvoiceDetailProps) {
  const updateStatusMutation = useUpdateInvoiceStatus();

  const handleSend = async () => {
    await updateStatusMutation.mutateAsync({ id: invoice.id, status: "sent" });
  };

  const handleMarkPaid = async () => {
    await updateStatusMutation.mutateAsync({ id: invoice.id, status: "paid" });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Invoices
        </Button>
        <div className="flex gap-2">
          {invoice.status === "draft" && (
            <Button onClick={handleSend} disabled={updateStatusMutation.isPending}>
              <Send className="mr-2 h-4 w-4" />
              Send Invoice
            </Button>
          )}
          {invoice.status === "sent" && (
            <Button onClick={handleMarkPaid} disabled={updateStatusMutation.isPending}>
              <CheckCircle className="mr-2 h-4 w-4" />
              Mark as Paid
            </Button>
          )}
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div>
              <p className="text-sm text-muted-foreground">Invoice Number</p>
              <p className="font-mono font-medium">{invoice.invoice_number}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Status</p>
              <Badge className={STATUS_COLORS[invoice.status]}>{invoice.status}</Badge>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Created</p>
              <p>{new Date(invoice.created_at).toLocaleDateString()}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Due Date</p>
              <p>{invoice.due_date ? new Date(invoice.due_date).toLocaleDateString() : "—"}</p>
            </div>
          </div>

          {invoice.notes && (
            <div className="mb-6">
              <p className="text-sm text-muted-foreground">Notes</p>
              <p>{invoice.notes}</p>
            </div>
          )}

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Description</TableHead>
                  <TableHead className="text-right">Qty</TableHead>
                  <TableHead className="text-right">Rate</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoice.items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.description}</TableCell>
                    <TableCell className="text-right">{item.quantity}</TableCell>
                    <TableCell className="text-right font-mono">₹{item.rate.toLocaleString()}</TableCell>
                    <TableCell className="text-right font-mono">₹{item.amount.toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="mt-4 flex justify-end">
            <div className="w-64 space-y-2">
              <div className="flex justify-between text-sm">
                <span>Subtotal</span>
                <span className="font-mono">₹{invoice.subtotal.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Tax ({(invoice.tax_rate * 100).toFixed(1)}%)</span>
                <span className="font-mono">₹{invoice.tax_amount.toLocaleString()}</span>
              </div>
              <div className="flex justify-between font-semibold border-t pt-2">
                <span>Total</span>
                <span className="font-mono">₹{invoice.total.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
