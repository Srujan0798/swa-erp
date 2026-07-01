import { useState } from "react";
import { useBoqs, useBoqItems } from "@/hooks/useBoqs";
import { useCreateQuote } from "@/hooks/useQuotes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface QuoteBuilderProps {
  projectId: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function QuoteBuilder({ projectId, onSuccess, onCancel }: QuoteBuilderProps) {
  const [selectedBoqId, setSelectedBoqId] = useState("");
  const [markupPercent, setMarkupPercent] = useState(15);
  const [taxPercent, setTaxPercent] = useState(18);
  const [terms, setTerms] = useState("");
  const [validityDays, setValidityDays] = useState(30);
  const [editableRates, setEditableRates] = useState<Record<string, number>>({});

  const { data: boqsData, isLoading: boqsLoading } = useBoqs(projectId, 1, 100);
  const { data: boqItemsData, isLoading: itemsLoading } = useBoqItems(selectedBoqId);
  const createMutation = useCreateQuote();

  const boqs = boqsData?.items ?? [];
  const rawItems = boqItemsData?.items ?? [];

  const items = rawItems.map((item) => ({
    ...item,
    rate: editableRates[item.id] ?? item.rate,
    amount: (editableRates[item.id] ?? item.rate) * item.quantity,
  }));

  const subtotal = items.reduce((sum, item) => sum + item.amount, 0);
  const markupAmount = subtotal * (markupPercent / 100);
  const afterMarkup = subtotal + markupAmount;
  const taxAmount = afterMarkup * (taxPercent / 100);
  const totalAmount = afterMarkup + taxAmount;

  const handleRateChange = (itemId: string, value: string) => {
    const num = parseFloat(value);
    if (!isNaN(num) && num >= 0) {
      setEditableRates((prev) => ({ ...prev, [itemId]: num }));
    }
  };

  const handleCreate = async () => {
    if (!selectedBoqId) return;
    await createMutation.mutateAsync({
      projectId,
      data: {
        boq_id: selectedBoqId,
        markup_percent: markupPercent,
        tax_percent: taxPercent,
        terms: terms || undefined,
        validity_days: validityDays,
      },
    });
    onSuccess?.();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create Quote</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>BOQ Version</Label>
            <Select value={selectedBoqId} onValueChange={setSelectedBoqId}>
              <SelectTrigger>
                <SelectValue placeholder={boqsLoading ? "Loading..." : "Select BOQ version"} />
              </SelectTrigger>
              <SelectContent>
                {boqs.map((boq) => (
                  <SelectItem key={boq.id} value={boq.id}>
                    v{boq.version_number} — {boq.file_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Validity (days)</Label>
            <Input
              type="number"
              value={validityDays}
              onChange={(e) => setValidityDays(parseInt(e.target.value) || 30)}
              min={1}
            />
          </div>
          <div className="space-y-2">
            <Label>Markup %</Label>
            <Input
              type="number"
              value={markupPercent}
              onChange={(e) => setMarkupPercent(parseFloat(e.target.value) || 0)}
              min={0}
              step={0.5}
            />
          </div>
          <div className="space-y-2">
            <Label>Tax %</Label>
            <Input
              type="number"
              value={taxPercent}
              onChange={(e) => setTaxPercent(parseFloat(e.target.value) || 0)}
              min={0}
              step={0.5}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label>Terms & Conditions</Label>
          <Textarea
            value={terms}
            onChange={(e) => setTerms(e.target.value)}
            placeholder="Payment terms, warranty, delivery conditions..."
            rows={3}
          />
        </div>

        {selectedBoqId && (
          <>
            {itemsLoading ? (
              <div className="p-4 text-muted-foreground">Loading BOQ items...</div>
            ) : (
              <div className="space-y-2">
                <Label>Line Items (edit rates as needed)</Label>
                <div className="max-h-[400px] overflow-auto border rounded-md">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Line</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Unit</TableHead>
                        <TableHead className="text-right">Qty</TableHead>
                        <TableHead className="text-right w-32">Rate</TableHead>
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
                          <TableCell className="text-right">
                            <Input
                              type="number"
                              value={item.rate}
                              onChange={(e) => handleRateChange(item.id, e.target.value)}
                              className="h-8 w-32 text-right"
                              min={0}
                            />
                          </TableCell>
                          <TableCell className="text-right">₹{item.amount.toLocaleString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}

            <Card className="bg-muted/50">
              <CardContent className="p-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Subtotal</span>
                  <span>₹{subtotal.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Markup ({markupPercent}%)</span>
                  <span>₹{markupAmount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Tax ({taxPercent}%)</span>
                  <span>₹{taxAmount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between font-semibold border-t pt-2">
                  <span>Total</span>
                  <span>₹{totalAmount.toLocaleString()}</span>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        <div className="flex gap-2">
          <Button onClick={handleCreate} disabled={!selectedBoqId || createMutation.isPending}>
            {createMutation.isPending ? "Creating..." : "Create Quote"}
          </Button>
          {onCancel && (
            <Button variant="outline" onClick={onCancel}>
              Cancel
            </Button>
          )}
        </div>
        {createMutation.isError && (
          <p className="text-sm text-destructive">Failed to create quote.</p>
        )}
      </CardContent>
    </Card>
  );
}
