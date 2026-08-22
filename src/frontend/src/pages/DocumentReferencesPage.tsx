import { useState, useEffect, type ReactElement } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
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
import { DocumentReferenceForm } from "@/components/documentRefs/DocumentReferenceForm";
import { useCreateDocumentReference } from "@/hooks/useDocumentReferences";
import { useCurrentUser } from "@/hooks/useAuth";
import { useToast } from "@/hooks/useToast";
import { canWrite } from "@/lib/permissions";
import { ArrowLeft, ArrowRight, Plus, Search } from "lucide-react";

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
  const [showForm, setShowForm] = useState(false);
  const pageSize = 20;
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { data: user } = useCurrentUser();
  const write = canWrite(user);
  const createMutation = useCreateDocumentReference();

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

  const { data: counters } = useQuery({
    queryKey: ["document-reference-counters"],
    queryFn: () => api.getDocumentReferenceCounters(),
  });

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize) || 1);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Document References</h1>
          <p className="text-sm text-muted-foreground">
            Excel <span className="font-medium">Document Reference Sheet</span> — columns: Date, DRN /
            Doc Ref No, Associated Project, Author, Document Type, Type, User, Description, Revision,
            Status, Remarks.
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            Not the same as sidebar <strong>Files / drawings</strong> (uploads).
          </p>
        </div>
        {write && !showForm ? (
          <Button onClick={() => setShowForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Document Reference
          </Button>
        ) : null}
      </div>

      {counters ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col gap-1 py-4 text-sm sm:flex-row sm:items-center sm:justify-between">
            <div>
              <span className="font-medium">DBR / KDR shared counter</span>
              <span className="text-muted-foreground">
                {" "}
                (Meeting 1) — year {counters.year}, last issued seq{" "}
                <span className="font-mono">{counters.dbr_kdr_last_seq}</span>
              </span>
            </div>
            <div className="text-xs sm:text-sm">
              Next DBR/KDR preview:{" "}
              <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-foreground">
                {counters.dbr_kdr_next_preview}
              </code>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {showForm && write ? (
        <DocumentReferenceForm
          onSubmit={async (formData) => {
            try {
              await createMutation.mutateAsync({
                project_id: formData.project_id,
                token_id: formData.token_id || undefined,
                doc_date: formData.doc_date,
                document_type: formData.document_type,
                type: formData.type,
                author_name: formData.author_name || undefined,
                user_ref: formData.user_ref,
                description: formData.description,
                revision: formData.revision,
                status: formData.status,
                remarks: formData.remarks,
              });
              toast({ title: "Document reference created" });
              setShowForm(false);
              void queryClient.invalidateQueries({ queryKey: ["document-references-global"] });
              void queryClient.invalidateQueries({ queryKey: ["document-reference-counters"] });
            } catch (err) {
              toast({ title: (err as Error).message, variant: "destructive" });
            }
          }}
          onCancel={() => setShowForm(false)}
          isLoading={createMutation.isPending}
        />
      ) : null}

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
                  <TableHead>Author</TableHead>
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
                    <TableCell colSpan={10} className="text-muted-foreground">
                      Loading…
                    </TableCell>
                  </TableRow>
                ) : items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={10} className="py-8 text-center text-muted-foreground">
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
                          <code className="rounded bg-muted px-1">make swa-live-local</code>
                          {write ? (
                            <>
                              , or{" "}
                              <button
                                type="button"
                                className="underline font-medium text-foreground"
                                onClick={() => setShowForm(true)}
                              >
                                create one here
                              </button>{" "}
                              (pick a project).
                            </>
                          ) : (
                            <>
                              , or open a{" "}
                              <Link className="underline font-medium text-foreground" to="/projects">
                                Project
                              </Link>
                              .
                            </>
                          )}
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
                      <TableCell className="text-xs">{d.author_name || "—"}</TableCell>
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
                            className="text-sm text-primary underline-offset-2 hover:underline font-mono"
                            to={`/projects/${d.project_id}`}
                          >
                            {d.project_code || "Open"}
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
