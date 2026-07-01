import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const vendorContactSchema = z.object({
  name: z.string().min(1, "Name is required"),
  designation: z.string().optional(),
  email: z.string().email("Valid email required").optional().or(z.literal("")),
  phone: z.string().optional(),
  is_primary: z.boolean().default(false),
});

type VendorContactFormData = z.infer<typeof vendorContactSchema>;

interface VendorContactFormProps {
  onSubmit: (data: VendorContactFormData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function VendorContactForm({ onSubmit, onCancel, isLoading }: VendorContactFormProps) {
  const form = useForm<VendorContactFormData>({
    resolver: zodResolver(vendorContactSchema),
    defaultValues: { is_primary: false },
  });

  return (
    <div className="border rounded-lg p-4 space-y-4 bg-muted/30">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="contact_name">Name *</Label>
          <Input id="contact_name" {...form.register("name")} />
          {form.formState.errors.name && (
            <p className="text-sm text-red-500">{form.formState.errors.name.message as string}</p>
          )}
        </div>
        <div className="space-y-2">
          <Label htmlFor="contact_designation">Designation</Label>
          <Input id="contact_designation" {...form.register("designation")} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="contact_email">Email</Label>
          <Input id="contact_email" type="email" {...form.register("email")} />
          {form.formState.errors.email && (
            <p className="text-sm text-red-500">{form.formState.errors.email.message as string}</p>
          )}
        </div>
        <div className="space-y-2">
          <Label htmlFor="contact_phone">Phone</Label>
          <Input id="contact_phone" {...form.register("phone")} />
        </div>
      </div>
      <div className="flex items-center gap-3">
        <input type="checkbox" {...form.register("is_primary")} id="contact_primary" />
        <Label htmlFor="contact_primary">Primary Contact</Label>
      </div>
      <div className="flex gap-2">
        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
        <Button size="sm" type="button" onClick={form.handleSubmit(onSubmit as any)} disabled={isLoading}>
          {isLoading ? "Adding..." : "Add Contact"}
        </Button>
        <Button size="sm" variant="outline" type="button" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </div>
  );
}
