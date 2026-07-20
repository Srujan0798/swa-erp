import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const docRefSchema = z.object({
  doc_date: z.string().min(1, "Document date is required"),
  document_type: z.string().min(1, "Document type is required"),
  type: z.string().optional(),
  user_ref: z.string().optional(),
  description: z.string().optional(),
  revision: z.string().default("R0"),
  status: z.string().default("Draft"),
  remarks: z.string().optional(),
  token_id: z.string().optional(),
});

type DocRefFormData = z.infer<typeof docRefSchema>;

interface DocumentReferenceFormProps {
  initialData?: Partial<DocRefFormData>;
  onSubmit: (data: DocRefFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export function DocumentReferenceForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading,
}: DocumentReferenceFormProps) {
  const today = new Date().toISOString().slice(0, 10);
  const form = useForm<DocRefFormData>({
    resolver: zodResolver(docRefSchema),
    defaultValues: {
      doc_date: today,
      revision: "R0",
      status: "Draft",
      ...initialData,
    },
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Document Reference Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="doc_date">Document Date *</Label>
              <Input id="doc_date" type="date" {...form.register("doc_date")} />
              {form.formState.errors.doc_date && (
                <p className="text-sm text-red-500">{form.formState.errors.doc_date.message as string}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="document_type">Document Type *</Label>
              <Input
                id="document_type"
                placeholder="e.g. DBR, KDR, Concept Note"
                {...form.register("document_type")}
              />
              {form.formState.errors.document_type && (
                <p className="text-sm text-red-500">{form.formState.errors.document_type.message as string}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="type">Category (optional)</Label>
              <Input id="type" placeholder="e.g. Architectural, Structural" {...form.register("type")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="user_ref">User Reference</Label>
              <Input id="user_ref" {...form.register("user_ref")} />
            </div>
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
            <Label htmlFor="token_id">Linked Token ID (optional)</Label>
            <Input id="token_id" placeholder="UUID" {...form.register("token_id")} />
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

      <div className="flex gap-3 justify-end">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Saving..." : "Save Document Reference"}
        </Button>
      </div>
    </form>
  );
}
