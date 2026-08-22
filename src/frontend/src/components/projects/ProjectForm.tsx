import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useCurrentUser } from "@/hooks/useAuth";
import { canManageProjects } from "@/lib/permissions";

const projectSchema = z.object({
  name: z.string().min(1, "Name is required"),
  code: z.string().min(1, "Code is required"),
  client_id: z.string().min(1, "Client is required"),
  description: z.string().optional(),
  location: z.string().optional(),
  estimated_value: z.number().optional(),
  start_date: z.string().optional(),
  target_end_date: z.string().optional(),
  milestone: z.string().optional(),
  progress_indicators: z.string().optional(),
  team_leader_name: z.string().optional(),
  project_owner_name: z.string().optional(),
  notes: z.string().optional(),
  pm_id: z.string().optional(),
  designer_id: z.string().optional(),
  auditor_id: z.string().optional(),
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface ProjectFormProps {
  initialData?: Partial<ProjectFormData>;
  onSubmit: (data: ProjectFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export function ProjectForm({ initialData, onSubmit, onCancel, isLoading }: ProjectFormProps) {
  const { data: user } = useCurrentUser();
  const showTeamFields = canManageProjects(user);
  const form = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: initialData,
  });

  const { data: clientsData } = useQuery({
    queryKey: ["clients-select"],
    queryFn: () => api.listClients({ page_size: 100 }),
  });

  const { data: pmUsers } = useQuery({
    queryKey: ["users-pm"],
    queryFn: () => api.listAssignees({ role: "pm" }),
  });

  const { data: designerUsers } = useQuery({
    queryKey: ["users-designer"],
    queryFn: () => api.listAssignees({ role: "designer" }),
  });

  const { data: auditorUsers } = useQuery({
    queryKey: ["users-auditor"],
    queryFn: () => api.listAssignees({ role: "auditor" }),
  });

  const handleSubmit = async (data: ProjectFormData) => {
    await onSubmit(data);
  };

  return (
    <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Project Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input id="name" {...form.register("name")} />
              {form.formState.errors.name && (
                <p className="text-sm text-red-500">{form.formState.errors.name.message as string}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="code">Code *</Label>
              <Input id="code" {...form.register("code")} />
              {form.formState.errors.code && (
                <p className="text-sm text-red-500">{form.formState.errors.code.message as string}</p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="client_id">Client *</Label>
            <Select onValueChange={(v) => form.setValue("client_id", v)} defaultValue={initialData?.client_id}>
              <SelectTrigger>
                <SelectValue placeholder="Select a client" />
              </SelectTrigger>
              <SelectContent>
                {clientsData?.items.map((c) => (
                  <SelectItem key={c.id} value={c.id}>{c.name} ({c.code})</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {form.formState.errors.client_id && (
              <p className="text-sm text-red-500">{form.formState.errors.client_id.message as string}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea id="description" {...form.register("description")} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input id="location" {...form.register("location")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="estimated_value">Estimated Value (INR)</Label>
              <Input id="estimated_value" type="number" {...form.register("estimated_value", { valueAsNumber: true })} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start_date">Start date</Label>
              <Input id="start_date" type="date" {...form.register("start_date")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="target_end_date">End date</Label>
              <Input id="target_end_date" type="date" {...form.register("target_end_date")} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="milestone">Milestone</Label>
              <Input id="milestone" placeholder="Excel: Milestone" {...form.register("milestone")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="progress_indicators">Progress Indicators</Label>
              <Input
                id="progress_indicators"
                placeholder="Excel: Progress Indicators"
                {...form.register("progress_indicators")}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="team_leader_name">Team Leader</Label>
              <Input
                id="team_leader_name"
                placeholder="Excel: Team Leader"
                {...form.register("team_leader_name")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="project_owner_name">Project owner</Label>
              <Input
                id="project_owner_name"
                placeholder="Excel: Project owner"
                {...form.register("project_owner_name")}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea id="notes" {...form.register("notes")} />
          </div>

          {showTeamFields ? (
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="pm_id">Project Manager</Label>
                <Select onValueChange={(v) => form.setValue("pm_id", v)} defaultValue={initialData?.pm_id}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select PM" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {pmUsers?.items.filter(u => u.role === "admin" || u.role === "pm").map((u) => (
                      <SelectItem key={u.id} value={u.id}>{u.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="designer_id">Designer</Label>
                <Select onValueChange={(v) => form.setValue("designer_id", v)} defaultValue={initialData?.designer_id}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Designer" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {designerUsers?.items.filter(u => u.role === "admin" || u.role === "designer").map((u) => (
                      <SelectItem key={u.id} value={u.id}>{u.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="auditor_id">Auditor</Label>
                <Select onValueChange={(v) => form.setValue("auditor_id", v)} defaultValue={initialData?.auditor_id}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Auditor" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {auditorUsers?.items.filter(u => u.role === "admin" || u.role === "auditor").map((u) => (
                      <SelectItem key={u.id} value={u.id}>{u.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          ) : null}

          <div className="p-3 bg-muted rounded-md">
            <span className="font-medium">Status:</span> <span className="text-muted-foreground">Lead (default)</span>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-3 justify-end">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Saving..." : "Save"}
        </Button>
      </div>
    </form>
  );
}