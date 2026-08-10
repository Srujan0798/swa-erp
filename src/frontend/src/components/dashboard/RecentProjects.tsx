import { Link } from "react-router-dom";
import { useProjects } from "@/hooks/useDashboard";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import type { ProjectStatus } from "@/types/api";

const statusColors: Record<ProjectStatus, string> = {
  Lead: "bg-gray-100 text-gray-800",
  Quote: "bg-blue-100 text-blue-800",
  Awarded: "bg-green-100 text-green-800",
  Design: "bg-purple-100 text-purple-800",
  Vendor: "bg-orange-100 text-orange-800",
  Execution: "bg-yellow-100 text-yellow-800",
  Validation: "bg-indigo-100 text-indigo-800",
  Closed: "bg-slate-100 text-slate-800",
};

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function RecentProjects() {
  const { data, isLoading, isError } = useProjects(1, 5);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-base">Projects</CardTitle>
        <Button variant="link" className="h-auto p-0 text-sm" asChild>
          <Link to="/projects">View all</Link>
        </Button>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Code</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Client</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 4 }).map((_, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-destructive">
                  Failed to load projects
                </TableCell>
              </TableRow>
            ) : data?.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground">
                  No projects — run make bootstrap-real
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((project) => (
                <TableRow key={project.id}>
                  <TableCell className="font-mono text-xs">
                    <Link className="hover:underline" to={`/projects/${project.id}`}>
                      {project.code}
                    </Link>
                  </TableCell>
                  <TableCell className="max-w-[140px] truncate font-medium">
                    {project.name}
                  </TableCell>
                  <TableCell className="max-w-[100px] truncate">
                    {project.client_name ?? "—"}
                  </TableCell>
                  <TableCell>
                    <Badge className={statusColors[project.status] ?? ""} variant="secondary">
                      {project.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}