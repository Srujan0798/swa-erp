import { useState, useEffect, type ReactElement } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
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
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { ArrowLeft, ArrowRight, Search } from "lucide-react";

/**
 * Global Document Reference inventory — maps to SWA "Document Reference Sheet".
 * (Sidebar "Files / drawings" is file storage; this page is DRN / DBR / KDR / …)
 */
export function DocumentReferencesPage(): ReactElement {
  const [searchParams] = useSearchParams();
  const projectFilter = searchParams.get("project") ?? undefined;
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debounced, setDebounced] = useState("");
  const pageSize = 20;

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["document-references-global", page, debounced, projectFilter],
    queryFn: () =>
      api.listDocumentReferences({
        page,
        page_size: pageSize,
        q: debounced || undefined,
        project_id: projectFilter,
      }),
  });

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize) || 1);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Document References</h1>
        <p className="text-sm text-muted-foreground">
          Same idea as the Excel <span className="font-medium">Document Reference Sheet</span> —
          DRN / DBR / KDR / CON / GED / PRN. DBR and KDR share one number sequence.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              className="pl-10"
              placeholder="Search by reference ID, type, or description…"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          {isError && (
            <QueryErrorBanner
              message="Failed to load document references"
              error={error}
              onRetry={() => void refetch()}
            />
          )}
          {projectFilter ? (
            <p className="mb-3 text-xs text-muted-foreground">
              Filtered to project.{" "}
              <Link className="underline" to="/document-references">
                Show all
              </Link>
            </p>
          ) : null}

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Reference</TableHead>
                  <TableHead>Doc type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Project</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-muted-foreground">
                      Loading…
                    </TableCell>
                  </TableRow>
                ) : items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-muted-foreground">
                      No document references yet. Load SWA sheets with{" "}
                      <code className="rounded bg-muted px-1">make bootstrap-real</code>, or create
                      one from a Project.
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((d) => (
                    <TableRow key={d.id}>
                      <TableCell className="font-mono text-sm font-semibold">
                        {d.reference_id}
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">{d.document_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{d.status}</Badge>
                      </TableCell>
                      <TableCell className="text-sm">{d.doc_date}</TableCell>
                      <TableCell className="max-w-[240px] truncate text-sm">
                        {d.description || "—"}
                      </TableCell>
                      <TableCell>
                        {d.project_id ? (
                          <Link
                            className="text-sm text-primary underline-offset-2 hover:underline"
                            to={`/projects/${d.project_id}`}
                          >
                            Open project
                          </Link>
                        ) : (
                          "—"
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <p className="text-xs text-muted-foreground">
              {total} reference{total === 1 ? "" : "s"}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ArrowLeft className="mr-1 h-4 w-4" />
                Prev
              </Button>
              <span className="flex items-center text-xs text-muted-foreground">
                {page} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
