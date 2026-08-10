import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useConvertInquiry } from "@/hooks/useInquiries";
import { ApiError } from "@/lib/api";
import type { InquiryCandidateClient, InquiryConvertPayload } from "@/types/api";

interface ConvertToClientButtonProps {
  inquiryId: string;
  inquiryClientName: string;
  inquiryEstimatedValue?: number | null;
  disabled?: boolean;
}

export function ConvertToClientButton({
  inquiryId,
  inquiryClientName,
  inquiryEstimatedValue,
  disabled,
}: ConvertToClientButtonProps) {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [projectName, setProjectName] = useState(`${inquiryClientName} - Project`);
  const [projectCode, setProjectCode] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [startDate, setStartDate] = useState<string>("");
  const [targetEndDate, setTargetEndDate] = useState<string>("");
  const [location, setLocation] = useState("");

  const [candidates, setCandidates] = useState<InquiryCandidateClient[] | null>(null);
  const [selectedClientId, setSelectedClientId] = useState<string | null>(null);

  const mutation = useConvertInquiry();

  const resetState = () => {
    setProjectName(`${inquiryClientName} - Project`);
    setProjectCode("");
    setProjectDescription("");
    setStartDate("");
    setTargetEndDate("");
    setLocation("");
    setCandidates(null);
    setSelectedClientId(null);
  };

  const closeDialog = () => {
    if (mutation.isPending) return;
    setOpen(false);
    setTimeout(resetState, 200);
  };

  const buildPayload = (clientId?: string): InquiryConvertPayload => {
    const payload: InquiryConvertPayload = {
      project_name: projectName,
    };
    if (clientId) payload.client_id = clientId;
    if (projectCode) payload.project_code = projectCode;
    if (projectDescription) payload.project_description = projectDescription;
    if (location) payload.location = location;
    if (startDate) payload.start_date = startDate;
    if (targetEndDate) payload.target_end_date = targetEndDate;
    if (inquiryEstimatedValue != null) payload.estimated_value = inquiryEstimatedValue;
    return payload;
  };

  const performConvert = async (clientId?: string) => {
    try {
      const result = await mutation.mutateAsync({
        id: inquiryId,
        payload: buildPayload(clientId),
      });
      setOpen(false);
      navigate(`/projects/${result.project_id}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 300) {
        const body = err.body as { candidates?: InquiryCandidateClient[] } | null;
        if (body?.candidates) {
          setCandidates(body.candidates);
        }
        return;
      }
      throw err;
    }
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!projectName.trim()) return;
    // selectedClientId === "new" | null → create new client; uuid → reuse
    if (candidates && selectedClientId === null) {
      // require explicit choice when matches exist
      return;
    }
    const clientId =
      candidates && selectedClientId && selectedClientId !== "new"
        ? selectedClientId
        : undefined;
    await performConvert(clientId);
  };

  return (
    <>
      <Button
        size="sm"
        onClick={() => setOpen(true)}
        disabled={disabled || mutation.isPending}
      >
        Convert to Project
      </Button>
      <Dialog open={open} onOpenChange={(o) => (o ? setOpen(true) : closeDialog())}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Convert Inquiry to Project</DialogTitle>
            <DialogDescription>
              {candidates
                ? `Multiple clients named "${inquiryClientName}" exist. Choose one or create a new client.`
                : `Create a Project for "${inquiryClientName}". A matching Client will be created if needed.`}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            {candidates && (
              <div className="space-y-2 rounded-md border border-amber-200 bg-amber-50 p-3">
                <Label className="text-sm font-semibold">
                  Multiple clients match this name — choose one
                </Label>
                <div className="mt-2 space-y-2">
                  {candidates.map((c) => (
                    <label
                      key={c.id}
                      className="flex cursor-pointer items-center gap-2 text-sm"
                    >
                      <input
                        type="radio"
                        name="client_match"
                        value={c.id}
                        checked={selectedClientId === c.id}
                        onChange={() => setSelectedClientId(c.id)}
                      />
                      <span className="font-medium">{c.name}</span>
                      <span className="font-mono text-xs text-muted-foreground">
                        ({c.code})
                      </span>
                    </label>
                  ))}
                  <label className="flex cursor-pointer items-center gap-2 text-sm">
                    <input
                      type="radio"
                      name="client_match"
                      value="new"
                      checked={selectedClientId === "new"}
                      onChange={() => setSelectedClientId("new")}
                    />
                    <span className="font-medium">Create a new client</span>
                    <span className="text-xs text-muted-foreground">
                      (do not reuse matches above)
                    </span>
                  </label>
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="project_name">Project Name *</Label>
              <Input
                id="project_name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="project_code">Project Code (optional)</Label>
                <Input
                  id="project_code"
                  value={projectCode}
                  onChange={(e) => setProjectCode(e.target.value)}
                  placeholder="auto-generated if blank"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="project_description">Description</Label>
              <Textarea
                id="project_description"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="target_end_date">Target End Date</Label>
                <Input
                  id="target_end_date"
                  type="date"
                  value={targetEndDate}
                  onChange={(e) => setTargetEndDate(e.target.value)}
                />
              </div>
            </div>

            {mutation.isError && !(mutation.error instanceof ApiError && (mutation.error as ApiError).status === 300) && (
              <p className="text-sm text-red-500">
                Conversion failed: {(mutation.error as Error).message}
              </p>
            )}

            <DialogFooter>
              <Button type="button" variant="outline" onClick={closeDialog}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={
                  mutation.isPending ||
                  !projectName.trim() ||
                  (!!candidates && selectedClientId === null)
                }
              >
                {mutation.isPending ? "Converting…" : "Convert"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
