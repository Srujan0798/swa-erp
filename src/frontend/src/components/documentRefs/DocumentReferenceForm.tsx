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

const docRefSchema = z.object({
  project_id: z.string().min(1, "Project is required"),
  doc_date: z.string().min(1, "Document date is required"),
  document_type: z.string().min(1, "Document type is required"),
  type: z.string().optional(),
  author_name: z.string().optional(),
  user_ref: z.string().optional(),
  description: z.string().optional(),
  revision: z.string().default("R0"),
  status: z.string().default("Draft"),
  remarks: z.string().optional(),
  token_id: z.string().optional(),
});

type DocRefFormData = z.infer<typeof docRefSchema>;

interface DocumentReferenceFormProps {
  /** When set, project is locked (project-scoped create). */
  projectId?: string;
  initialData?: Partial<DocRefFormData>;
  onSubmit: (data: DocRefFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export function DocumentReferenceForm({
  projectId,
  initialData,
  onSubmit,
  onCancel,
  isLoading,
}: DocumentReferenceFormProps) {
  const today = new Date().toISOString().slice(0, 10);
  const form = useForm<DocRefFormData>({
    resolver: zodResolver(docRefSchema),
    defaultValues: {
      project_id: projectId || "",
      doc_date: today,
      revision: "R0",
      status: "Draft",
      ...initialData,
    },
  });

  const selectedProjectId = form.watch("project_id") || projectId || "";

  const { data: projectsData } = useQuery({
    queryKey: ["projects-select-docref"],
    queryFn: () => api.listProjects({ page_size: 100 }),
    enabled: !projectId,
  });

  const { data: tokensData } = useQuery({
    queryKey: ["tokens-for-project", selectedProjectId],
    queryFn: () => api.listTokens({ project_id: selectedProjectId, page_size: 100 }),
    enabled: !!selectedProjectId,
  });
  const tokens = tokensData?.items ?? [];
  const tokenId = form.watch("token_id");

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Document reference</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {!projectId ? (
            <div className="space-y-2">
              <Label>Associated project *</Label>
              <Select
                value={selectedProjectId || undefined}
                onValueChange={(v) => {
                  form.setValue("project_id", v, { shouldValidate: true });
                  form.setValue("token_id", undefined);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select project (Excel: Associated Project ID)" />
                </SelectTrigger>
                <SelectContent>
                  {(projectsData?.items ?? []).map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.code} — {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {form.formState.errors.project_id && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.project_id.message as string}
                </p>
              )}
            </div>
          ) : null}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="doc_date">Document date *</Label>
              <Input id="doc_date" type="date" {...form.register("doc_date")} />
              {form.formState.errors.doc_date && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.doc_date.message as string}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="document_type">Document type *</Label>
              <Input
                id="document_type"
                placeholder="DBR, KDR, Concept Note…"
                {...form.register("document_type")}
              />
              {form.formState.errors.document_type && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.document_type.message as string}
                </p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="type">Type (Submittal / Internal…)</Label>
              <Input
                id="type"
                placeholder="Submittal, Internal…"
                {...form.register("type")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="author_name">Author</Label>
              <Input
                id="author_name"
                placeholder="Excel: Author name"
                {...form.register("author_name")}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="user_ref">User / reviewer</Label>
            <Input
              id="user_ref"
              placeholder="Client / Reviewer / Authority"
              {...form.register("user_ref")}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="revision">Revision</Label>
              <Input id="revision" {...form.register("revision")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Input id="status" {...form.register("status")} />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Linked token (optional)</Label>
            <Select
              value={tokenId || "none"}
              onValueChange={(v) => form.setValue("token_id", v === "none" ? undefined : v)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select token" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">No token link</SelectItem>
                {tokens.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.reference_id}
                    {t.token_type ? ` — ${t.token_type}` : ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea id="description" {...form.register("description")} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="remarks">Remarks</Label>
            <Textarea id="remarks" {...form.register("remarks")} />
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
          {isLoading ? "Saving…" : "Save document reference"}
        </Button>
      </div>
    </form>
  );
}
