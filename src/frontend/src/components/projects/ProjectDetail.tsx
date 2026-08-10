import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ProjectStatus } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";



const STATUS_TRANSITIONS: Record<ProjectStatus, ProjectStatus[]> = {
  Lead: ["Quote"],
  Quote: ["Awarded"],
  Awarded: ["Design"],
  Design: ["Vendor"],
  Vendor: ["Execution"],
  Execution: ["Validation"],
  Validation: ["Closed"],
  Closed: [],
};

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

interface ProjectDetailProps {
  projectId: string;
}

export function ProjectDetail({ projectId }: ProjectDetailProps): JSX.Element {
  const queryClient = useQueryClient();
  const [nextStatus, setNextStatus] = useState<string>("");

  const {
    data: project,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => api.getProject(projectId),
  });

  const transitionMutation = useMutation({
    mutationFn: (status: ProjectStatus) => api.transitionProject(projectId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      setNextStatus("");
    },
  });

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (isError) {
    return (
      <QueryErrorBanner
        message="Failed to load project"
        error={error}
        onRetry={() => void refetch()}
      />
    );
  }
  if (!project) return <div className="p-6">Project not found</div>;

  const allowedTransitions = STATUS_TRANSITIONS[project.status] ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold flex-1">{project.name}</h1>
        <span className={`px-3 py-1 rounded text-sm font-semibold ${STATUS_COLORS[project.status]}`}>
          {project.status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Project Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-muted-foreground">Code</Label>
                <p className="font-mono">{project.code}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Status</Label>
                <p>{project.status}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Location</Label>
                <p>{project.location ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Estimated Value</Label>
                <p>{project.estimated_value ? `₹${project.estimated_value.toLocaleString()}` : "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Start Date</Label>
                <p>{project.start_date ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Target End Date</Label>
                <p>{project.target_end_date ?? "—"}</p>
              </div>
            </div>
            {project.description && (
              <div>
                <Label className="text-muted-foreground">Description</Label>
                <p className="text-sm">{project.description}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          {project.client_name && (
            <Card>
              <CardHeader>
                <CardTitle>Client</CardTitle>
              </CardHeader>
              <CardContent>
                <Link to={`/clients/${project.client_id}`} className="text-primary hover:underline">
                  {project.client_name}
                </Link>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Assigned Team</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label className="text-muted-foreground">Project Manager</Label>
                <p>{project.pm_name ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Designer</Label>
                <p>{project.designer_name ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Auditor</Label>
                <p>{project.auditor_name ?? "—"}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {allowedTransitions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Transition Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-4">
              <div className="space-y-2 flex-1">
                <Label htmlFor="next-status">Next Status</Label>
                <Select value={nextStatus} onValueChange={setNextStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select next status" />
                  </SelectTrigger>
                  <SelectContent>
                    {allowedTransitions.map((s) => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => transitionMutation.mutate(nextStatus as ProjectStatus)}
                disabled={!nextStatus || transitionMutation.isPending}
              >
                {transitionMutation.isPending ? "Transitioning..." : "Transition"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}