import { useParams, Link } from "react-router-dom";
import { useInquiry } from "@/hooks/useInquiries";
import { useUpdateInquiry, useDeleteInquiry } from "@/hooks/useInquiries";
import { ConvertToClientButton } from "@/components/inquiries/ConvertToClientButton";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft } from "lucide-react";

const STATUS_COLORS: Record<string, string> = {
  New: "bg-blue-100 text-blue-800",
  Contacted: "bg-yellow-100 text-yellow-800",
  Converted: "bg-green-100 text-green-800",
  Dropped: "bg-gray-200 text-gray-800",
};

export function InquiryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: inquiry, isLoading } = useInquiry(id);
  const updateMutation = useUpdateInquiry();
  const deleteMutation = useDeleteInquiry();

  if (isLoading) return <div className="p-6">Loading...</div>;
  if (!inquiry) return <div className="p-6">Inquiry not found</div>;

  const statusFlow = ["New", "Contacted", "Dropped"];
  const canConvert = inquiry.status !== "Converted" && inquiry.status !== "Dropped";

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to="/inquiries">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Inquiries
          </Link>
        </Button>
        <h1 className="text-2xl font-bold flex-1 font-mono">{inquiry.reference_id}</h1>
        <Badge
          variant="secondary"
          className={STATUS_COLORS[inquiry.status] ?? ""}
        >
          {inquiry.status}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Inquiry Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-muted-foreground">Client Name</Label>
                <p className="font-medium">{inquiry.client_name}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Inquiry Date</Label>
                <p>{inquiry.inquiry_date}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Type</Label>
                <p>{inquiry.inquiry_type ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Source</Label>
                <p>{inquiry.inquiry_source ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Priority</Label>
                <p>{inquiry.priority ?? "—"}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Estimated Value</Label>
                <p>
                  {inquiry.estimated_value != null
                    ? `₹${inquiry.estimated_value.toLocaleString()}`
                    : "—"}
                </p>
              </div>
            </div>
            {inquiry.requirement_summary && (
              <div>
                <Label className="text-muted-foreground">Requirement Summary</Label>
                <p className="text-sm whitespace-pre-wrap">{inquiry.requirement_summary}</p>
              </div>
            )}
            {inquiry.notes && (
              <div>
                <Label className="text-muted-foreground">Notes</Label>
                <p className="text-sm whitespace-pre-wrap">{inquiry.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {canConvert && (
                <ConvertToClientButton
                  inquiryId={inquiry.id}
                  inquiryClientName={inquiry.client_name}
                  inquiryEstimatedValue={inquiry.estimated_value}
                />
              )}
              {inquiry.status === "Converted" && inquiry.converted_project_id && (
                <Button asChild>
                  <Link to={`/projects/${inquiry.converted_project_id}`}>
                    Open Project
                  </Link>
                </Button>
              )}
              {statusFlow.includes(inquiry.status) && (
                <div className="flex flex-col gap-2 pt-2">
                  <Label className="text-muted-foreground">Change Status</Label>
                  <div className="flex flex-wrap gap-2">
                    {statusFlow
                      .filter((s) => s !== inquiry.status)
                      .map((s) => (
                        <Button
                          key={s}
                          size="sm"
                          variant="outline"
                          disabled={updateMutation.isPending}
                          onClick={() =>
                            updateMutation.mutate({ id: inquiry.id, data: { status: s } })
                          }
                        >
                          Mark {s}
                        </Button>
                      ))}
                  </div>
                </div>
              )}
              <Button
                size="sm"
                variant="destructive"
                disabled={deleteMutation.isPending}
                onClick={() => {
                  if (confirm("Delete this inquiry?")) {
                    deleteMutation.mutate(inquiry.id);
                  }
                }}
              >
                Delete Inquiry
              </Button>
            </CardContent>
          </Card>

          {inquiry.status === "Converted" && (
            <Card>
              <CardHeader>
                <CardTitle>Conversion Result</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {inquiry.converted_client_id && (
                  <div>
                    <Label className="text-muted-foreground">Client</Label>
                    <p>
                      <Link
                        to={`/clients/${inquiry.converted_client_id}`}
                        className="text-primary hover:underline"
                      >
                        Open Client
                      </Link>
                    </p>
                  </div>
                )}
                {inquiry.converted_project_id && (
                  <div>
                    <Label className="text-muted-foreground">Project</Label>
                    <p>
                      <Link
                        to={`/projects/${inquiry.converted_project_id}`}
                        className="text-primary hover:underline"
                      >
                        Open Project
                      </Link>
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
