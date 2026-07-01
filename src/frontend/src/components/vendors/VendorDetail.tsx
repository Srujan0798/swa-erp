import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useVendor, useDeleteVendor, useAddVendorContact, useDeleteVendorContact } from "@/hooks/useVendors";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { VendorContactForm } from "@/components/vendors/VendorContactForm";
import { Plus, Trash2, ArrowLeft, Pencil } from "lucide-react";

export function VendorDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showAddContact, setShowAddContact] = useState(false);

  const { data: vendor, isLoading } = useVendor(id!);
  const deleteVendorMutation = useDeleteVendor();
  const deleteContactMutation = useDeleteVendorContact();
  const addContactMutation = useAddVendorContact();

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (!vendor) return <div className="p-6">Vendor not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to="/vendors">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Vendors
          </Link>
        </Button>
        <h1 className="text-2xl font-bold flex-1">{vendor.name}</h1>
        <Badge variant={vendor.is_active ? "default" : "secondary"}>
          {vendor.is_active ? "Active" : "Inactive"}
        </Badge>
        <Button variant="outline" asChild>
          <Link to={`/vendors/${id}/edit`}>
            <Pencil className="mr-2 h-4 w-4" />
            Edit
          </Link>
        </Button>
        <Button
          variant="destructive"
          onClick={async () => {
            await deleteVendorMutation.mutateAsync(id!);
            navigate("/vendors");
          }}
        >
          Delete
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Vendor Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-muted-foreground">Code</Label>
                <p className="font-mono">{vendor.code}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Email</Label>
                <p>{vendor.email ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Phone</Label>
                <p>{vendor.phone ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">City</Label>
                <p>{vendor.city ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">State</Label>
                <p>{vendor.state ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">GST Number</Label>
                <p>{vendor.gst_number ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">PAN Number</Label>
                <p>{vendor.pan_number ?? "—"}</p>
              </div>
            </div>
            {vendor.address && (
              <div>
                <Label className="text-muted-foreground">Address</Label>
                <p>{vendor.address}</p>
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
                <VendorContactForm
                  onSubmit={async (data) => {
                    await addContactMutation.mutateAsync({ vendorId: id!, data });
                    setShowAddContact(false);
                  }}
                  onCancel={() => setShowAddContact(false)}
                  isLoading={addContactMutation.isPending}
                />
              </div>
            )}
            {vendor.contacts.length === 0 ? (
              <p className="text-muted-foreground text-sm">No contacts yet</p>
            ) : (
              <div className="space-y-2">
                {vendor.contacts.map((contact) => (
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
                      onClick={() => deleteContactMutation.mutate({ vendorId: id!, contactId: contact.id })}
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
    </div>
  );
}
