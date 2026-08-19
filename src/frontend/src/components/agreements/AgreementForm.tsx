import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const agreementSchema = z.object({
  service_name: z.string().min(1, "Service name is required"),
  start_date: z.string().min(1, "Start date is required"),
  end_date: z.string().optional(),
  total_tokens: z.preprocess(
    (val) => (val === null || val === undefined || Number.isNaN(val) ? undefined : val),
    z.number().int().nonnegative().optional()
  ),
  status: z.string().default("Active"),
  notes: z.string().optional(),
});

type AgreementFormData = z.infer<typeof agreementSchema>;

interface AgreementFormProps {
  initialData?: Partial<AgreementFormData>;
  onSubmit: (data: AgreementFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export function AgreementForm({ initialData, onSubmit, onCancel, isLoading }: AgreementFormProps) {
  const form = useForm<AgreementFormData>({
    resolver: zodResolver(agreementSchema),
    defaultValues: {
      status: "Active",
      ...initialData,
    },
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <Card>
        <CardHeader>
          <CardTitle>Service Agreement Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="service_name">Service Name *</Label>
            <Input
              id="service_name"
              placeholder="e.g. Green Building Consultancy, Energy Audit"
              {...form.register("service_name")}
            />
            {form.formState.errors.service_name && (
              <p className="text-sm text-red-500">{form.formState.errors.service_name.message as string}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start_date">Start Date *</Label>
              <Input id="start_date" type="date" {...form.register("start_date")} />
              {form.formState.errors.start_date && (
                <p className="text-sm text-red-500">{form.formState.errors.start_date.message as string}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="end_date">End Date</Label>
              <Input id="end_date" type="date" {...form.register("end_date")} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="total_tokens">Total Tokens (planned)</Label>
              <Input
                id="total_tokens"
                type="number"
                min={0}
                {...form.register("total_tokens", { valueAsNumber: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Input id="status" {...form.register("status")} />
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
          {isLoading ? "Saving..." : "Save Agreement"}
        </Button>
      </div>
    </form>
  );
}
