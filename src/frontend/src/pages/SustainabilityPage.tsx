import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { api } from "@/lib/api";
import {
  useSustainabilityMetrics,
  useCreateSustainabilityMetric,
  useUpdateSustainabilityMetric,
  useDeleteSustainabilityMetric,
} from "@/hooks/useSustainability";
import { SustainabilityForm } from "@/components/sustainability/SustainabilityForm";
import { SustainabilityList } from "@/components/sustainability/SustainabilityList";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import type {
  ProjectListResponse,
  SustainabilityMetric,
  SustainabilityMetricCreate,
} from "@/types/api";

export function SustainabilityManager({ projectId }: { projectId: string }) {
  const [editing, setEditing] = useState<SustainabilityMetric | null>(null);
  const [showForm, setShowForm] = useState(false);

  const {
    data: metrics = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useSustainabilityMetrics(projectId);
  const createMutation = useCreateSustainabilityMetric(projectId);
  const updateMutation = useUpdateSustainabilityMetric(projectId);
  const deleteMutation = useDeleteSustainabilityMetric(projectId);

  const handleSubmit = (data: SustainabilityMetricCreate) => {
    if (editing) {
      updateMutation.mutate(
        { metricId: editing.id, data },
        {
          onSuccess: () => {
            setEditing(null);
            setShowForm(false);
          },
        }
      );
    } else {
      createMutation.mutate(data, {
        onSuccess: () => setShowForm(false),
      });
    }
  };

  const handleDelete = (metric: SustainabilityMetric) => {
    if (confirm("Delete this sustainability metric?")) {
      deleteMutation.mutate(metric.id);
    }
  };

  const startEdit = (metric: SustainabilityMetric) => {
    setEditing(metric);
    setShowForm(true);
  };

  return (
    <div className="space-y-4">
      {isError && (
        <QueryErrorBanner
          message="Failed to load sustainability metrics"
          error={error}
          onRetry={() => void refetch()}
        />
      )}
      {!showForm && (
        <Button onClick={() => { setEditing(null); setShowForm(true); }}>
          <Plus className="mr-2 h-4 w-4" />
          Add Metric
        </Button>
      )}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>{editing ? "Edit Metric" : "New Metric"}</CardTitle>
          </CardHeader>
          <CardContent>
            <SustainabilityForm
              projectId={projectId}
              initial={editing}
              onSubmit={handleSubmit}
              onCancel={() => { setEditing(null); setShowForm(false); }}
              isSubmitting={createMutation.isPending || updateMutation.isPending}
            />
          </CardContent>
        </Card>
      )}
      {!isError && (
        <SustainabilityList
          metrics={metrics}
          isLoading={isLoading}
          onEdit={startEdit}
          onDelete={handleDelete}
          onAdd={() => {
            setEditing(null);
            setShowForm(true);
          }}
        />
      )}
    </div>
  );
}

export function SustainabilityPage() {
  const [projectId, setProjectId] = useState<string>("");
  const { data } = useQuery<ProjectListResponse>({
    queryKey: ["projects-all"],
    queryFn: () => api.listProjects({ page_size: 200 }),
  });
  const projects = data?.items ?? [];

  if (projects.length === 0) {
    return <div className="p-6 text-muted-foreground">Loading projects...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Sustainability Metrics</h1>
        <p className="text-sm text-muted-foreground">
          Per-project green-building metrics, entered when the client provides data.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Project</CardTitle>
        </CardHeader>
        <CardContent>
          <Select value={projectId} onValueChange={setProjectId}>
            <SelectTrigger>
              <SelectValue placeholder="Select a project" />
            </SelectTrigger>
            <SelectContent>
              {projects.map((p) => (
                <SelectItem key={p.id} value={p.id}>
                  {p.name} ({p.code})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {projectId ? (
        <SustainabilityManager projectId={projectId} />
      ) : (
        <p className="text-muted-foreground text-sm">Select a project to view its metrics.</p>
      )}
    </div>
  );
}
