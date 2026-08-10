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
 * Global Tokens inventory. New tokens are created under a Client → Agreement.
 */
export function TokensPage(): ReactElement {
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
    queryKey: ["tokens-global", page, debounced, projectFilter],
    queryFn: () =>
      api.listTokens({
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
        <h1 className="text-2xl font-bold tracking-tight">Tokens</h1>
        <p className="text-sm text-muted-foreground">
          Units of work under a service agreement. Create from Client → Agreement → Tokens.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              className="pl-10"
              placeholder="Search by token ID or description…"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          {isError && (
            <QueryErrorBanner
              message="Failed to load tokens"
              error={error}
              onRetry={() => void refetch()}
            />
          )}
          {projectFilter ? (
            <p className="mb-3 text-xs text-muted-foreground">
              Filtered to project from quick link.{" "}
              <Link className="underline" to="/tokens">
                Show all tokens
              </Link>
            </p>
          ) : null}

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Reference</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Used</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Project</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground">
                      Loading…
                    </TableCell>
                  </TableRow>
                ) : items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="py-8 text-center text-muted-foreground">
                      {debounced || projectFilter ? (
                        <>
                          No tokens match this filter.{" "}
                          <Link className="underline font-medium text-foreground" to="/tokens">
                            Clear filters
                          </Link>
                          .
                        </>
                      ) : (
                        <>
                          No tokens yet. Open a{" "}
                          <Link className="underline font-medium text-foreground" to="/clients">
                            client
                          </Link>{" "}
                          → agreement to issue the first token.
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((t) => (
                    <TableRow key={t.id} className="hover:bg-muted/40">
                      <TableCell className="font-mono text-xs font-semibold">
                        {t.reference_id}
                      </TableCell>
                      <TableCell>{t.token_type ?? "—"}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{t.token_status}</Badge>
                      </TableCell>
                      <TableCell className="text-sm">{t.token_date}</TableCell>
                      <TableCell className="tabular-nums">×{t.tokens_used}</TableCell>
                      <TableCell className="max-w-[200px] truncate text-sm">
                        {t.description ?? "—"}
                      </TableCell>
                      <TableCell>
                        {t.project_id ? (
                          <Button variant="outline" size="sm" asChild>
                            <Link to={`/projects/${t.project_id}`}>Project</Link>
                          </Button>
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
            <span className="text-sm text-muted-foreground">
              {total} token{total !== 1 ? "s" : ""}
            </span>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
