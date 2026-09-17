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

function getCandidateClients(error: unknown): InquiryCandidateClient[] | null {
  if (!(error instanceof ApiError) || error.status !== 300) return null;
  const body = error.body;
  if (!body || typeof body !== "object" || !("detail" in body)) return null;
  const detail = body.detail;
  if (!detail || typeof detail !== "object" || !("candidates" in detail)) return null;
  const matches: unknown = detail.candidates;
  if (
    !Array.isArray(matches) ||
    matches.length === 0 ||
    !matches.every(
      (candidate): candidate is InquiryCandidateClient =>
        candidate !== null &&
        typeof candidate === "object" &&
        typeof candidate.id === "string" &&
        candidate.id.trim().length > 0 &&
        typeof candidate.name === "string" &&
        typeof candidate.code === "string"
    )
  ) {
    return null;
  }
  return matches;
}

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
      const matches = getCandidateClients(err);
      if (matches) {
        setCandidates(matches);
        setSelectedClientId(null);
      }
    }
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!projectName.trim()) return;
    if (candidates && selectedClientId === null) return;
    await performConvert(selectedClientId ?? undefined);
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
                ? `Multiple clients named "${inquiryClientName}" exist. Select an existing client to create the project under.`
                : `Create a project for "${inquiryClientName}". An existing client will be reused, or a client will be created if no match exists.`}
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

            {mutation.isError && !getCandidateClients(mutation.error) && (
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
