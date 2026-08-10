import { useState, useEffect, type ReactElement } from "react";
import { Link } from "react-router-dom";
import { useAgreements } from "@/hooks/useAgreements";
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
 * Global Service Agreements inventory (consultancy core).
 * Create new SAs from Client detail; this page is for browse/search.
 */
export function AgreementsPage(): ReactElement {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debounced, setDebounced] = useState("");
  const pageSize = 20;

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { data, isLoading, isError, error, refetch } = useAgreements({
    page,
    page_size: pageSize,
    q: debounced || undefined,
  });

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize) || 1);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Service agreements</h1>
        <p className="text-sm text-muted-foreground">
          Annual retainers (e.g. INSUDESIGN). Open a client to add a new agreement or tokens.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              className="pl-10"
              placeholder="Search by reference ID or service name…"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>

          {isError && (
            <QueryErrorBanner
              message="Failed to load agreements"
              error={error}
              onRetry={() => void refetch()}
            />
          )}

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Reference</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Start</TableHead>
                  <TableHead>Tokens budget</TableHead>
                  <TableHead>Client</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      Loading…
                    </TableCell>
                  </TableRow>
                ) : items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="py-8 text-center text-muted-foreground">
                      {debounced ? (
                        <>No agreements match “{debounced}”. Try another reference or service name.</>
                      ) : (
                        <>
                          No service agreements yet. Open a{" "}
                          <Link className="underline font-medium text-foreground" to="/clients">
                            client
                          </Link>{" "}
                          → Service agreements to add a retainer (e.g. INSUDESIGN).
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((a) => (
                    <TableRow key={a.id} className="hover:bg-muted/40">
                      <TableCell className="font-mono text-xs font-semibold">
                        {a.reference_id}
                      </TableCell>
                      <TableCell className="font-medium">{a.service_name}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{a.status}</Badge>
                      </TableCell>
                      <TableCell className="text-sm">{a.start_date}</TableCell>
                      <TableCell className="tabular-nums">
                        {a.total_tokens ?? "—"}
                      </TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm" asChild>
                          <Link to={`/clients/${a.client_id}`}>Open client</Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              {total} agreement{total !== 1 ? "s" : ""}
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
