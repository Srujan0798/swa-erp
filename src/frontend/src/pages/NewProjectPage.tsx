import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ProjectForm } from "@/components/projects/ProjectForm";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Project } from "@/types/api";

export function NewProjectPage() {
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: (data: Partial<Project>) => api.createProject(data),
    onSuccess: (project) => {
      navigate(`/projects/${project.id}`);
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" asChild>
          <a href="/projects">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </a>
        </Button>
        <h1 className="text-2xl font-bold">New Project</h1>
      </div>

      <ProjectForm
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