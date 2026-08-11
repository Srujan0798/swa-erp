import { useState } from "react";
import { useBoqs, useDeleteBoq } from "@/hooks/useBoqs";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCurrentUser } from "@/hooks/useAuth";
import { canWrite } from "@/lib/permissions";
import { Eye, Trash2, ChevronLeft, ChevronRight } from "lucide-react";

interface BOQVersionListProps {
  projectId: string;
  onViewItems: (boqId: string) => void;
}

export function BOQVersionList({ projectId, onViewItems }: BOQVersionListProps) {
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const { data: user } = useCurrentUser();
  const write = canWrite(user);
  const { data, isLoading } = useBoqs(projectId, page, pageSize);
  const deleteMutation = useDeleteBoq();

  const handleDelete = (id: string) => {
    if (confirm("Delete this BOQ version? This cannot be undone.")) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div className="p-4 text-muted-foreground">Loading BOQs...</div>;

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <Card>
      <CardHeader>
        <CardTitle>BOQ Versions ({total})</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-muted-foreground text-sm">No BOQ versions uploaded yet.</p>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Version</TableHead>
                  <TableHead>File Name</TableHead>
                  <TableHead>Items</TableHead>
                  <TableHead>Parsed By</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((boq) => (
                  <TableRow key={boq.id}>
                    <TableCell className="font-mono">v{boq.version_number}</TableCell>
                    <TableCell>{boq.file_name}</TableCell>
                    <TableCell>{boq.item_count ?? "—"}</TableCell>
                    <TableCell>{boq.parsed_by ?? "—"}</TableCell>
                    <TableCell>{new Date(boq.parsed_at).toLocaleDateString()}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex gap-1 justify-end">
                        <Button variant="ghost" size="icon" onClick={() => onViewItems(boq.id)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        {write ? (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(boq.id)}
                            disabled={deleteMutation.isPending}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        ) : null}
                      </div>
                    </TableCell>
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
