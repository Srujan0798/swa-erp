import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const inquirySchema = z.object({
  inquiry_date: z.string().min(1, "Inquiry date is required"),
  inquiry_type: z.string().optional(),
  inquiry_source: z.string().optional(),
  client_name: z.string().min(1, "Client name is required"),
  requirement_summary: z.string().optional(),
  estimated_value: z.preprocess(
    (v) => (typeof v === "number" && Number.isNaN(v) ? undefined : v),
    z.number().optional()
  ),
  priority: z.string().optional(),
  status: z.string().default("New"),
  notes: z.string().optional(),
});

type InquiryFormData = z.infer<typeof inquirySchema>;

interface InquiryFormProps {
  initialData?: Partial<InquiryFormData>;
  onSubmit: (data: InquiryFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export function InquiryForm({ initialData, onSubmit, onCancel, isLoading }: InquiryFormProps) {
  const today = new Date().toISOString().slice(0, 10);
  const form = useForm<InquiryFormData>({
    resolver: zodResolver(inquirySchema),
    defaultValues: {
      inquiry_date: today,
      status: "New",
      ...initialData,
    },
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Inquiry Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="inquiry_date">Inquiry Date *</Label>
              <Input id="inquiry_date" type="date" {...form.register("inquiry_date")} />
              {form.formState.errors.inquiry_date && (
                <p className="text-sm text-red-500">{form.formState.errors.inquiry_date.message as string}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="client_name">Client Name *</Label>
              <Input id="client_name" {...form.register("client_name")} />
              {form.formState.errors.client_name && (
                <p className="text-sm text-red-500">{form.formState.errors.client_name.message as string}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="inquiry_type">Type</Label>
              <Input id="inquiry_type" placeholder="e.g. New Build, Retrofit" {...form.register("inquiry_type")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="inquiry_source">Source</Label>
              <Input id="inquiry_source" placeholder="e.g. Website, Referral" {...form.register("inquiry_source")} />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="requirement_summary">Requirement Summary</Label>
            <Textarea id="requirement_summary" {...form.register("requirement_summary")} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="estimated_value">Estimated Value (INR)</Label>
              <Input
                id="estimated_value"
                type="number"
                {...form.register("estimated_value", { valueAsNumber: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <Input id="priority" placeholder="e.g. High, Medium, Low" {...form.register("priority")} />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea id="notes" {...form.register("notes")} />
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
          {isLoading ? "Saving..." : "Save Inquiry"}
        </Button>
      </div>
    </form>
  );
}
