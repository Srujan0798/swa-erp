import { useNavigate } from "react-router-dom";
import { useCreateVendor } from "@/hooks/useVendors";
import { VendorForm } from "@/components/vendors/VendorForm";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Vendor } from "@/types/api";

export function NewVendorPage() {
  const navigate = useNavigate();
  const createVendorMutation = useCreateVendor();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" asChild>
          <a href="/vendors">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Vendors
          </a>
        </Button>
        <h1 className="text-2xl font-bold">New Vendor</h1>
      </div>

      <VendorForm
        onSubmit={async (data) => {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          await createVendorMutation.mutateAsync(data as any);
          navigate("/vendors");
        }}
        onCancel={() => navigate("/vendors")}
        isLoading={createVendorMutation.isPending}
      />
    </div>
  );
}
