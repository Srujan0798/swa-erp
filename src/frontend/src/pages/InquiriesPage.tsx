import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useInquiries, useCreateInquiry, useDeleteInquiry } from "@/hooks/useInquiries";
import { useToast } from "@/hooks/useToast";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { InquiryForm } from "@/components/inquiries/InquiryForm";
import { ArrowLeft, ArrowRight, Plus, Search, Trash2 } from "lucide-react";

const STATUS_COLORS: Record<string, string> = {
  New: "bg-blue-100 text-blue-800",
  Contacted: "bg-yellow-100 text-yellow-800",
  Converted: "bg-green-100 text-green-800",
  Dropped: "bg-gray-200 text-gray-800",
};

export function InquiriesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const { toast } = useToast();
  const pageSize = 20;

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data, isLoading } = useInquiries({
    page,
    page_size: pageSize,
    q: debouncedSearch || undefined,
    status: statusFilter || undefined,
  });

  const createMutation = useCreateInquiry();
  const deleteMutation = useDeleteInquiry();

  const inquiries = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this inquiry?")) return;
    try {
      await deleteMutation.mutateAsync(id);
      toast({ title: "Inquiry deleted" });
    } catch (err) {
      toast({ title: (err as Error).message, variant: "destructive" });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Inquiries</h1>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Inquiry
        </Button>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-3 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search inquiries..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              className="border rounded-md px-3 text-sm bg-background"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Statuses</option>
              <option value="New">New</option>
              <option value="Contacted">Contacted</option>
              <option value="Converted">Converted</option>
              <option value="Dropped">Dropped</option>
            </select>
          </div>

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Reference</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Estimated Value</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center">Loading...</TableCell>
                  </TableRow>
                ) : inquiries.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center">No inquiries found</TableCell>
                  </TableRow>
                ) : (
                  inquiries.map((inquiry) => (
                    <TableRow key={inquiry.id}>
                      <TableCell className="font-mono text-sm">{inquiry.reference_id}</TableCell>
                      <TableCell className="font-medium">{inquiry.client_name}</TableCell>
                      <TableCell>{inquiry.inquiry_date}</TableCell>
                      <TableCell>
                        <Badge
                          variant="secondary"
                          className={STATUS_COLORS[inquiry.status] ?? ""}
                        >
                          {inquiry.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{inquiry.priority ?? "—"}</TableCell>
                      <TableCell>
                        {inquiry.estimated_value != null
                          ? `₹${inquiry.estimated_value.toLocaleString()}`
                          : "—"}
                      </TableCell>
                      <TableCell className="flex gap-1">
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/inquiries/${inquiry.id}`}>View</Link>
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(inquiry.id)}
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <div className="flex items-center justify-between mt-4">
            <span className="text-sm text-muted-foreground">
              {total} inquiry{total !== 1 ? "s" : ""}
            </span>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm">Page {page} of {totalPages}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
              >
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>New Inquiry</DialogTitle>
            <DialogDescription>
              Capture initial inquiry details. You can convert it to a Project later.
            </DialogDescription>
          </DialogHeader>
          <InquiryForm
            onSubmit={async (data) => {
              try {
                await createMutation.mutateAsync(data);
                toast({ title: "Inquiry created" });
                setShowCreate(false);
              } catch (err) {
                toast({ title: (err as Error).message, variant: "destructive" });
              }
            }}
            onCancel={() => setShowCreate(false)}
            isLoading={createMutation.isPending}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
