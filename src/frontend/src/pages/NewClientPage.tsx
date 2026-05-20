import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ClientForm } from "@/components/clients/ClientForm";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Client } from "@/types/api";

export function NewClientPage() {
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: (data: Partial<Client>) => api.createClient(data),
    onSuccess: (client) => {
      navigate(`/clients/${client.id}`);
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" asChild>
          <a href="/clients">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Clients
          </a>
        </Button>
        <h1 className="text-2xl font-bold">New Client</h1>
      </div>

      <ClientForm
        onSubmit={async (data) => {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          await mutation.mutateAsync(data as any);
        }}
        onCancel={() => navigate("/clients")}
        isLoading={mutation.isPending}
      />
    </div>
  );
}