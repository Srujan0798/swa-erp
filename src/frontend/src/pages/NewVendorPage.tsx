"use client";

import { Navigate } from "react-router-dom";
import { useCreateVendor } from "@/hooks/useVendors";
import { VendorForm } from "@/components/vendors/VendorForm";
import { useCurrentUser } from "@/hooks/useAuth";
import { canWrite } from "@/lib/permissions";

export function NewVendorPage() {
  const createVendorMutation = useCreateVendor();
  const { data: user, isLoading } = useCurrentUser();

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (!canWrite(user)) {
    return <Navigate to="/vendors" replace />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">New Vendor</h1>
        <p className="text-sm text-muted-foreground">Create a new vendor record.</p>
      </div>

      <VendorForm
        onSubmit={async (data) => {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          await createVendorMutation.mutateAsync(data as any);
        }}
        onCancel={() => history.back()}
        isLoading={createVendorMutation.isPending}
      />
    </div>
  );
}
