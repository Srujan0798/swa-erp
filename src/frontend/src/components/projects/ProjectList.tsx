import { useState, useEffect, type ReactElement } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ProjectStatus } from "@/types/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { useCurrentUser } from "@/hooks/useAuth";
import { ArrowLeft, ArrowRight, Plus, Search } from "lucide-react";

const STATUSES: ProjectStatus[] = ["Lead", "Quote", "Awarded", "Design", "Vendor", "Execution", "Validation", "Closed"];

const STATUS_COLORS: Record<ProjectStatus, string> = {
  Lead: "bg-gray-100 text-gray-800",
  Quote: "bg-yellow-100 text-yellow-800",
  Awarded: "bg-blue-100 text-blue-800",
  Design: "bg-purple-100 text-purple-800",
  Vendor: "bg-orange-100 text-orange-800",
  Execution: "bg-red-100 text-red-800",
  Validation: "bg-teal-100 text-teal-800",
  Closed: "bg-green-100 text-green-800",
};

export function ProjectList(): ReactElement {
  const { data: user } = useCurrentUser();
  const canCreate = user?.role !== "viewer";
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const pageSize = 20;

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["projects", page, debouncedSearch, statusFilter],
    queryFn: () =>
      api.listProjects({
        page,
        page_size: pageSize,
        q: debouncedSearch || undefined,
        status: statusFilter || undefined,
      }),
  });

  const projects = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize) || 1);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Projects</h1>
          <p className="text-sm text-muted-foreground">
            Open a project for BOQ, quotes, document references, sustainability.
          </p>
        </div>
        {canCreate ? (
          <Button asChild>
            <Link to="/projects/new">
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </Link>
          </Button>
        ) : null}
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="mb-4 flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search projects..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select
              value={statusFilter || "all"}
              onValueChange={(v) => setStatusFilter(v === "all" ? "" : v)}
            >
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                {STATUSES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {isError && (
            <div className="mb-4">
              <QueryErrorBanner
                message="Failed to load projects"
                error={error}
                onRetry={() => void refetch()}
              />
            </div>
          )}

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>PM</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground">
                      Loading…
                    </TableCell>
                  </TableRow>
                ) : projects.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="py-8 text-center text-muted-foreground">
                      {debouncedSearch || statusFilter ? (
                        <>No projects match these filters. Clear search/status and try again.</>
                      ) : canCreate ? (
                        <>
                          No projects yet.{" "}
                          <Link className="underline font-medium text-foreground" to="/projects/new">
                            Create a project
                          </Link>{" "}
                          after you have a client on file.
                        </>
                      ) : (
                        <>No projects yet. Ask a PM to create one from a client engagement.</>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  projects.map((project) => (
                    <TableRow key={project.id}>
                      <TableCell className="font-mono text-sm">{project.code}</TableCell>
                      <TableCell>{project.name}</TableCell>
                      <TableCell>{project.client_name ?? "—"}</TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[project.status]}`}>
                          {project.status}
                        </span>
                      </TableCell>
                      <TableCell>{project.pm_name ?? "—"}</TableCell>
                      <TableCell>{project.location ?? "—"}</TableCell>
                      <TableCell>
                        <Button variant="ghost" asChild>
                          <Link to={`/projects/${project.id}`}>View</Link>
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
              {total} project{total !== 1 ? "s" : ""}
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
    </div>
  );
}