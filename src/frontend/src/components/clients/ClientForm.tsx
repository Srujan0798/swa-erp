import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const clientSchema = z.object({
  name: z.string().min(1, "Name is required"),
  code: z.string().min(1, "Code is required"),
  primary_email: z.string().email("Valid email required"),
  primary_phone: z.string().optional(),
  primary_contact: z.string().optional(),
  date_onboarded: z.string().optional(),
  industry: z.string().optional(),
  client_status: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  pincode: z.string().optional(),
  country: z.string().default("India"),
  gst_number: z.string().optional(),
  notes: z.string().optional(),
  contacts: z.array(z.object({
    name: z.string().min(1, "Contact name required"),
    email: z.string().email("Valid email required"),
    phone: z.string().optional(),
    designation: z.string().optional(),
    is_primary: z.boolean().default(false),
  })).optional(),
});

type ClientFormData = z.infer<typeof clientSchema>;

interface ClientFormProps {
  initialData?: Partial<ClientFormData>;
  onSubmit: (data: ClientFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export function ClientForm({ initialData, onSubmit, onCancel, isLoading }: ClientFormProps) {
  const form = useForm<ClientFormData>({
    resolver: zodResolver(clientSchema),
    defaultValues: {
      country: "India",
      contacts: [],
      ...initialData,
    },
  });

  const handleSubmit = async (data: ClientFormData) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    await onSubmit(data as any);
  };

  return (
    <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6" noValidate>
      <Card>
        <CardHeader>
          <CardTitle>Client Details</CardTitle>
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

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="primary_email">Email *</Label>
              <Input id="primary_email" type="email" {...form.register("primary_email")} />
              {form.formState.errors.primary_email && (
                <p className="text-sm text-red-500">{form.formState.errors.primary_email.message as string}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="primary_phone">Phone</Label>
              <Input id="primary_phone" {...form.register("primary_phone")} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="primary_contact">Primary Contact</Label>
              <Input
                id="primary_contact"
                placeholder="Excel: Primary Contact"
                {...form.register("primary_contact")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="date_onboarded">Date Onboarded</Label>
              <Input id="date_onboarded" type="date" {...form.register("date_onboarded")} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="industry">Industry</Label>
              <Input id="industry" placeholder="HVAC, Process…" {...form.register("industry")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="client_status">Client Status</Label>
              <Input
                id="client_status"
                placeholder="Active / Dormant…"
                {...form.register("client_status")}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="address">Billing Address</Label>
            <Textarea id="address" {...form.register("address")} />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="city">City</Label>
              <Input id="city" {...form.register("city")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="state">State</Label>
              <Input id="state" {...form.register("state")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pincode">Pincode</Label>
              <Input id="pincode" {...form.register("pincode")} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="country">Country</Label>
              <Input id="country" {...form.register("country")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gst_number">GST Number</Label>
              <Input id="gst_number" {...form.register("gst_number")} />
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
          {isLoading ? "Saving..." : "Save"}
        </Button>
      </div>
    </form>
  );
}