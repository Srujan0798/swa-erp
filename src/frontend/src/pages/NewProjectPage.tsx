import { useNavigate, useSearchParams, Link, Navigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ProjectForm } from "@/components/projects/ProjectForm";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Project } from "@/types/api";
import { useCurrentUser } from "@/hooks/useAuth";
import { canWrite } from "@/lib/permissions";

export function NewProjectPage(): JSX.Element {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const clientId = searchParams.get("client_id") ?? undefined;
  const { data: user, isLoading } = useCurrentUser();

  const mutation = useMutation({
    mutationFn: (data: Partial<Project>) => api.createProject(data),
    onSuccess: (project) => {
      navigate(`/projects/${project.id}`);
    },
  });

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (!canWrite(user)) {
    return <Navigate to="/projects" replace />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to="/projects">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Link>
        </Button>
        <h1 className="text-2xl font-bold">New Project</h1>
      </div>

      <ProjectForm
        initialData={clientId ? { client_id: clientId } : undefined}
        onSubmit={async (data) => {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          await mutation.mutateAsync(data as any);
        }}
        onCancel={() => navigate("/projects")}
        isLoading={mutation.isPending}
      />
    </div>
  );
}
