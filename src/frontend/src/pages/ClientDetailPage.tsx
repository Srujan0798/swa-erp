import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { ContactForm } from "@/components/clients/ContactForm";
import { AgreementsTab } from "@/components/agreements/AgreementsTab";
import { Plus, Trash2, ArrowLeft } from "lucide-react";

export function ClientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [showAddContact, setShowAddContact] = useState(false);

  const { data: client, isLoading } = useQuery({
    queryKey: ["client", id],
    queryFn: () => api.getClient(id!),
    enabled: !!id,
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

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (!client) return <div className="p-6">Client not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to="/clients">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Clients
          </Link>
        </Button>
        <h1 className="text-2xl font-bold flex-1">{client.name}</h1>
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
                <p className="font-mono">{client.code}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Primary Email</Label>
                <p>{client.primary_email}</p>
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
            <Button size="sm" onClick={() => setShowAddContact(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Contact
            </Button>
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
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => deleteContactMutation.mutate(contact.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <AgreementsTab clientId={client.id} />
    </div>
  );
}