import { useState } from "react";
import { useBoqItems } from "@/hooks/useBoqs";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChevronLeft, ChevronRight, ArrowLeft } from "lucide-react";

interface BOQItemTableProps {
  boqId: string;
  onBack: () => void;
}

export function BOQItemTable({ boqId, onBack }: BOQItemTableProps) {
  const [page, setPage] = useState(1);
  const pageSize = 50;
  const { data, isLoading } = useBoqItems(boqId, page, pageSize);

  if (isLoading) return <div className="p-4 text-muted-foreground">Loading items...</div>;

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" aria-label="Back to BOQ versions" onClick={onBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <CardTitle>BOQ Items ({total})</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-muted-foreground text-sm">No items found.</p>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Line</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Specification</TableHead>
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
                    <TableCell>{item.category ?? "—"}</TableCell>
                    <TableCell>{item.description}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{item.specification ?? "—"}</TableCell>
                    <TableCell>{item.unit}</TableCell>
                    <TableCell className="text-right">{item.quantity}</TableCell>
                    <TableCell className="text-right">₹{item.rate.toLocaleString()}</TableCell>
                    <TableCell className="text-right">₹{item.amount.toLocaleString()}</TableCell>
                  </TableRow>
                ))}
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
