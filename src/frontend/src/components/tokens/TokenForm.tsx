import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
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
import { api } from "@/lib/api";

const tokenSchema = z.object({
  token_date: z.string().min(1, "Token date is required"),
  token_type: z.string().optional(),
  description: z.string().optional(),
  token_status: z.string().default("In Progress"),
  tokens_used: z.preprocess(
    (val) => {
      if (val === null || val === undefined || Number.isNaN(val)) return 1;
      return Number(val);
    },
    z.number().int().positive()
  ),
  client_employee_name: z.string().optional(),
  project_id: z.string().optional(),
});

type TokenFormData = z.infer<typeof tokenSchema>;

interface TokenFormProps {
  initialData?: Partial<TokenFormData>;
  onSubmit: (data: TokenFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export function TokenForm({ initialData, onSubmit, onCancel, isLoading }: TokenFormProps) {
  const today = new Date().toISOString().slice(0, 10);
  const form = useForm<TokenFormData>({
    resolver: zodResolver(tokenSchema),
    defaultValues: {
      token_date: today,
      token_status: "In Progress",
      tokens_used: 1,
      ...initialData,
    },
  });

  const { data: projectsData } = useQuery({
    queryKey: ["projects-token-form"],
    queryFn: () => api.listProjects({ page: 1, page_size: 100 }),
  });
  const projects = projectsData?.items ?? [];
  const projectId = form.watch("project_id");

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <Card>
        <CardHeader>
          <CardTitle>Token details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="token_date">Token date *</Label>
              <Input id="token_date" type="date" {...form.register("token_date")} />
              {form.formState.errors.token_date && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.token_date.message as string}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="token_type">Type</Label>
              <Input
                id="token_type"
                placeholder="Query, Design, Site visit…"
                {...form.register("token_type")}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tokens_used">Tokens used *</Label>
              <Input
                id="tokens_used"
                type="number"
                min={1}
                {...form.register("tokens_used", { valueAsNumber: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="token_status">Status</Label>
              <Input id="token_status" {...form.register("token_status")} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="client_employee_name">Client employee</Label>
              <Input id="client_employee_name" {...form.register("client_employee_name")} />
            </div>
            <div className="space-y-2">
              <Label>Linked project (optional)</Label>
              <Select
                value={projectId || "none"}
                onValueChange={(v) =>
                  form.setValue("project_id", v === "none" ? undefined : v)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select project" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No project link</SelectItem>
                  {projects.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.code} — {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea id="description" {...form.register("description")} />
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Saving…" : "Save token"}
        </Button>
      </div>
    </form>
  );
}
