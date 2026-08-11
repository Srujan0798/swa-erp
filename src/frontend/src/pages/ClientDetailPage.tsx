import { useState, type ReactElement } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/useToast";
import { useCurrentUser } from "@/hooks/useAuth";
import { canManageCommercial, canWrite } from "@/lib/permissions";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ContactForm } from "@/components/clients/ContactForm";
import { ClientForm } from "@/components/clients/ClientForm";
import { AgreementsTab } from "@/components/agreements/AgreementsTab";
import { QueryErrorBanner } from "@/components/ui/QueryErrorBanner";
import { Plus, Trash2, ArrowLeft, Pencil } from "lucide-react";
// ClientProjectsList defined below

export function ClientDetailPage(): ReactElement {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { data: user } = useCurrentUser();
  const canEdit = canManageCommercial(user);
  const canMutate = canWrite(user);
  const [showAddContact, setShowAddContact] = useState(false);
  const [showEdit, setShowEdit] = useState(false);

  const { data: client, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["client", id],
    queryFn: () => api.getClient(id!),
    enabled: !!id,
  });

  const updateClientMutation = useMutation({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    mutationFn: (payload: any) => api.updateClient(id!, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["client", id] });
      void queryClient.invalidateQueries({ queryKey: ["clients"] });
      setShowEdit(false);
      toast({ title: "Client updated" });
    },
    onError: (err) => {
      toast({ title: (err as Error).message, variant: "destructive" });
    },
  });

  const deleteContactMutation = useMutation({
    mutationFn: (contactId: string) => api.deleteContact(id!, contactId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["client", id] }),
  });

  const addContactMutation = useMutation({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    mutationFn: (payload: any) => api.addContact(id!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client", id] });
      setShowAddContact(false);
    },
  });

  const deleteClientMutation = useMutation({
    mutationFn: () => api.deleteClient(id!),
    onSuccess: () => {
      toast({ title: "Client deleted" });
      navigate("/clients");
    },
    onError: (err) => {
      toast({ title: (err as Error).message, variant: "destructive" });
    },
  });

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (isError) {
    return (
      <QueryErrorBanner
        message="Failed to load client"
        error={error}
        onRetry={() => void refetch()}
      />
    );
  }
  if (!client) return <div className="p-6">Client not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to="/clients">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Clients
          </Link>
        </Button>
        <h1 className="text-2xl font-bold flex-1">{client.name}</h1>
        {canEdit && (
          <Button variant="outline" onClick={() => setShowEdit(true)}>
            <Pencil className="mr-2 h-4 w-4" />
            Edit
          </Button>
        )}
        {canEdit && (
          <Button
            variant="destructive"
            disabled={deleteClientMutation.isPending}
            onClick={() => {
              if (confirm(`Delete client "${client.name}"? This cannot be undone.`)) {
                deleteClientMutation.mutate();
              }
            }}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete Client
          </Button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Client Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-muted-foreground">Code</Label>
                <p className="font-mono text-sm">{client.code}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Industry</Label>
                <p>{client.industry ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Client status</Label>
                <p>{client.client_status ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Primary Email</Label>
                <p className="break-all text-sm">{client.primary_email}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Primary Phone</Label>
                <p>{client.primary_phone ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">City</Label>
                <p>{client.city ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">State</Label>
                <p>{client.state ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Pincode</Label>
                <p>{client.pincode ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Country</Label>
                <p>{client.country}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">GST Number</Label>
                <p>{client.gst_number ?? "—"}</p>
              </div>
            </div>
            {client.address && (
              <div>
                <Label className="text-muted-foreground">Address</Label>
                <p>{client.address}</p>
              </div>
            )}
            {client.notes && (
              <div>
                <Label className="text-muted-foreground">Notes</Label>
                <p className="text-sm">{client.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>Contacts</CardTitle>
            {canMutate && (
              <Button size="sm" onClick={() => setShowAddContact(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Contact
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {showAddContact && (
              <div className="mb-4">
                <ContactForm
                  onSubmit={async (data) => {
                    await addContactMutation.mutateAsync(data);
                  }}
                  onCancel={() => setShowAddContact(false)}
                  isLoading={addContactMutation.isPending}
                />
              </div>
            )}
            {client.contacts.length === 0 ? (
              <p className="text-muted-foreground text-sm">No contacts yet</p>
            ) : (
              <div className="space-y-2">
                {client.contacts.map((contact) => (
                  <div key={contact.id} className="flex items-center justify-between border-b py-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{contact.name}</span>
                        {contact.is_primary && (
                          <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded">
                            Primary
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {contact.email} {contact.phone ? `· ${contact.phone}` : ""}
                        {contact.designation ? ` · ${contact.designation}` : ""}
                      </div>
                    </div>
                    {canMutate && (
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => deleteContactMutation.mutate(contact.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <div>
            <CardTitle>Projects</CardTitle>
            <p className="mt-1 text-xs font-normal text-muted-foreground">
              Work under this client
            </p>
          </div>
          {canMutate && (
            <Button size="sm" asChild>
              <Link to={`/projects/new?client_id=${client.id}`}>
                <Plus className="mr-2 h-4 w-4" />
                New project
              </Link>
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <ClientProjectsList clientId={client.id} />
        </CardContent>
      </Card>

      <AgreementsTab clientId={client.id} />

      <Dialog open={showEdit} onOpenChange={setShowEdit}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit client</DialogTitle>
          </DialogHeader>
          <ClientForm
            key={`edit-client-${client.id}`}
            initialData={{
              name: client.name,
              code: client.code,
              primary_email: client.primary_email,
              primary_phone: client.primary_phone ?? undefined,
              address: client.address ?? undefined,
              city: client.city ?? undefined,
              state: client.state ?? undefined,
              pincode: client.pincode ?? undefined,
              country: client.country ?? "India",
              gst_number: client.gst_number ?? undefined,
              notes: client.notes ?? undefined,
            }}
            onSubmit={async (data) => {
              // Contacts are managed on the detail page, not via client update.
              const { contacts: _contacts, ...payload } = data;
              await updateClientMutation.mutateAsync(payload);
            }}
            onCancel={() => setShowEdit(false)}
            isLoading={updateClientMutation.isPending}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}

function ClientProjectsList({ clientId }: { clientId: string }) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["projects", "by-client", clientId],
    queryFn: () => api.listProjects({ page: 1, page_size: 50, client_id: clientId }),
  });
  const projects = data?.items ?? [];

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading projects…</p>;
  }
  if (isError) {
    return <p className="text-sm text-destructive">Failed to load projects.</p>;
  }
  if (projects.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No projects yet for this client.
      </p>
    );
  }
  return (
    <div className="space-y-2">
      {projects.map((p) => (
        <div
          key={p.id}
          className="flex items-center justify-between rounded-md border px-3 py-2 text-sm"
        >
          <div className="min-w-0">
            <span className="font-mono text-xs font-semibold">{p.code}</span>
            <span className="mx-2 text-muted-foreground">·</span>
            <span className="font-medium">{p.name}</span>
            <span className="ml-2 text-xs text-muted-foreground">{p.status}</span>
          </div>
          <Button variant="outline" size="sm" asChild>
            <Link to={`/projects/${p.id}`}>Open</Link>
          </Button>
        </div>
      ))}
    </div>
  );
}