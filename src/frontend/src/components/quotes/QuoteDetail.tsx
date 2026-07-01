import { useQuote } from "@/hooks/useQuotes";
import { useBoqItems } from "@/hooks/useBoqs";
import { QuoteActions } from "./QuoteActions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download } from "lucide-react";
import { getAccessToken } from "@/lib/auth";

interface QuoteDetailProps {
  quoteId: string;
  onBack: () => void;
}

const TIMELINE_STEPS = ["draft", "pending_approval", "approved", "sent", "accepted"] as const;

function StatusTimeline({ status }: { status: string }) {
  const statusIndex = TIMELINE_STEPS.indexOf(status as typeof TIMELINE_STEPS[number]);
  const isRejected = status === "rejected";
  const currentIndex = isRejected ? -1 : statusIndex;

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {TIMELINE_STEPS.map((step, idx) => {
        const isActive = idx === currentIndex;
        const isCompleted = idx < currentIndex;
        return (
          <div key={step} className="flex items-center gap-2">
            <div
              className={`flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
                isActive
                  ? "bg-primary text-primary-foreground"
                  : isCompleted
                    ? "bg-primary/20 text-primary"
                    : "bg-muted text-muted-foreground"
              }`}
            >
              {idx + 1}
            </div>
            <span className={`text-xs ${isActive ? "font-semibold" : "text-muted-foreground"}`}>
              {step.replace(/_/g, " ")}
            </span>
            {idx < TIMELINE_STEPS.length - 1 && (
              <div className={`w-6 h-px ${isCompleted ? "bg-primary" : "bg-muted"}`} />
            )}
          </div>
        );
      })}
      {isRejected && (
        <Badge className="bg-red-100 text-red-800 ml-2">Rejected</Badge>
      )}
    </div>
  );
}

export function QuoteDetail({ quoteId, onBack }: QuoteDetailProps) {
  const { data: quote, isLoading } = useQuote(quoteId);
  const { data: itemsData } = useBoqItems(quote?.boq_id ?? "");

  if (isLoading) return <div className="p-4 text-muted-foreground">Loading quote...</div>;
  if (!quote) return <div className="p-4 text-destructive">Quote not found</div>;

  const items = itemsData?.items ?? [];

  const handleDownloadPdf = async () => {
    try {
      const response = await fetch(`/api/quotes/${quoteId}/pdf`, {
        headers: { Authorization: `Bearer ${getAccessToken()}` },
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `quote-${quoteId}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch {
      console.error("PDF download failed");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h2 className="text-xl font-bold">Quote v{quote.version_number}</h2>
        </div>
        <Button variant="outline" onClick={handleDownloadPdf}>
          <Download className="mr-2 h-4 w-4" />
          PDF
        </Button>
      </div>

      <QuoteActions quoteId={quoteId} status={quote.status} />

      <Card>
        <CardHeader>
          <CardTitle>Status Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <StatusTimeline status={quote.status} />
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-muted-foreground">Status</Label>
                <p>{quote.status.replace(/_/g, " ")}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Created By</Label>
                <p>{quote.created_by_name ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Valid Until</Label>
                <p>{quote.valid_until ? new Date(quote.valid_until).toLocaleDateString() : "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Validity Days</Label>
                <p>{quote.validity_days}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Approved By</Label>
                <p>{quote.approved_by_name ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Sent At</Label>
                <p>{quote.sent_at ? new Date(quote.sent_at).toLocaleString() : "—"}</p>
              </div>
            </div>
            {quote.terms && (
              <div>
                <Label className="text-muted-foreground">Terms & Conditions</Label>
                <p className="text-sm whitespace-pre-wrap">{quote.terms}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Totals</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Subtotal</span>
              <span>₹{quote.subtotal.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Markup ({quote.markup_percent}%)</span>
              <span>₹{quote.markup_amount.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Tax ({quote.tax_percent}%)</span>
              <span>₹{quote.tax_amount.toLocaleString()}</span>
            </div>
            <div className="flex justify-between font-semibold border-t pt-2">
              <span>Total</span>
              <span>₹{quote.total_amount.toLocaleString()}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Line Items</CardTitle>
        </CardHeader>
        <CardContent>
          {items.length === 0 ? (
            <p className="text-muted-foreground text-sm">No items loaded.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Line</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Unit</TableHead>
                  <TableHead className="text-right">Qty</TableHead>
                  <TableHead className="text-right">Rate</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-mono">{item.line_number}</TableCell>
                    <TableCell>{item.description}</TableCell>
                    <TableCell>{item.unit}</TableCell>
                    <TableCell className="text-right">{item.quantity}</TableCell>
                    <TableCell className="text-right">₹{item.rate.toLocaleString()}</TableCell>
                    <TableCell className="text-right">₹{item.amount.toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
