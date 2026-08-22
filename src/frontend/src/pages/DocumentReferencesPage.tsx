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
  const [typeFilter, setTypeFilter] = useState("");
  const pageSize = 20;

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["document-references-global", page, debounced, projectFilter, typeFilter],
    queryFn: () =>
      api.listDocumentReferences({
        page,
        page_size: pageSize,
        q: debounced || undefined,
        project_id: projectFilter,
        document_type: typeFilter || undefined,
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
          Excel <span className="font-medium">Document Reference Sheet</span> — columns: Date, DRN /
          Doc Ref No, Associated Project, Author, Document Type, Type, User, Description, Revision,
          Status, Remarks. DBR and KDR share one number sequence.
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          Not the same as sidebar <strong>Files / drawings</strong> (uploads). Create new rows from a{" "}
          <Link className="underline" to="/projects">
            Project
          </Link>
          .
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
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
            <select
              className="rounded-md border bg-background px-3 text-sm"
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value);
                setPage(1);
              }}
              aria-label="Filter by document type"
            >
              <option value="">All doc types</option>
              <option value="Concept Note">Concept Note</option>
              <option value="Design Basis Report">Design Basis Report</option>
              <option value="Calculation Sheet">Calculation Sheet</option>
              <option value="GA Drawing">GA Drawing</option>
              <option value="DBR">DBR</option>
              <option value="KDR">KDR</option>
              <option value="CON">CON</option>
            </select>
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

          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>DRN / Ref</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Doc type</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Rev</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Project</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-muted-foreground">
                      Loading…
                    </TableCell>
                  </TableRow>
                ) : items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="py-8 text-center text-muted-foreground">
                      {debounced || typeFilter || projectFilter ? (
                        <>
                          No document references match this filter.{" "}
                          <button
                            type="button"
                            className="underline font-medium text-foreground"
                            onClick={() => {
                              setSearch("");
                              setTypeFilter("");
                              setPage(1);
                            }}
                          >
                            Clear filters
                          </button>
                          .
                        </>
                      ) : (
                        <>
                          No document references yet. Load SWA sheets with{" "}
                          <code className="rounded bg-muted px-1">make swa-live-local</code>, or open
                          a{" "}
                          <Link className="underline font-medium text-foreground" to="/projects">
                            Project
                          </Link>{" "}
                          → Document References to create one.
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((d) => (
                    <TableRow key={d.id}>
                      <TableCell className="font-mono text-sm font-semibold">
                        {d.reference_id}
                      </TableCell>
                      <TableCell className="text-sm whitespace-nowrap">{d.doc_date}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{d.document_type}</Badge>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {d.type || "—"}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{d.revision}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{d.status}</Badge>
                      </TableCell>
                      <TableCell className="text-xs">{d.user_ref || "—"}</TableCell>
                      <TableCell className="max-w-[200px] truncate text-sm">
                        {d.description || "—"}
                      </TableCell>
                      <TableCell>
                        {d.project_id ? (
                          <Link
                            className="text-sm text-primary underline-offset-2 hover:underline"
                            to={`/projects/${d.project_id}`}
                          >
                            Open
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
