import { useCurrentUser } from "@/hooks/useAuth";
import { useSubmitQuote, useApproveQuote, useSendQuote, useRespondQuote } from "@/hooks/useQuotes";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { QuoteStatus } from "@/types/api";

interface QuoteActionsProps {
  quoteId: string;
  status: QuoteStatus;
  onAction?: () => void;
}

const STATUS_CONFIG: Record<QuoteStatus, { label: string; className: string }> = {
  draft: { label: "Draft", className: "bg-gray-100 text-gray-800" },
  pending_approval: { label: "Pending Approval", className: "bg-yellow-100 text-yellow-800" },
  approved: { label: "Approved", className: "bg-blue-100 text-blue-800" },
  sent: { label: "Sent", className: "bg-purple-100 text-purple-800" },
  accepted: { label: "Accepted", className: "bg-green-100 text-green-800" },
  rejected: { label: "Rejected", className: "bg-red-100 text-red-800" },
};

export function QuoteActions({ quoteId, status, onAction }: QuoteActionsProps) {
  const { data: user } = useCurrentUser();
  const submitMutation = useSubmitQuote();
  const approveMutation = useApproveQuote();
  const sendMutation = useSendQuote();
  const respondMutation = useRespondQuote();

  const isAdminOrPm = user?.role === "admin" || user?.role === "pm";

  const handleAction = async (action: () => Promise<unknown>) => {
    await action();
    onAction?.();
  };

  const buttons: React.ReactNode[] = [];

  if (status === "draft" && isAdminOrPm) {
    buttons.push(
      <Button
        key="submit"
        onClick={() => handleAction(() => submitMutation.mutateAsync(quoteId))}
        disabled={submitMutation.isPending}
      >
        Submit for Approval
      </Button>
    );
  }

  if (status === "pending_approval" && user?.role === "admin") {
    buttons.push(
      <Button
        key="approve"
        onClick={() => handleAction(() => approveMutation.mutateAsync(quoteId))}
        disabled={approveMutation.isPending}
      >
        Approve
      </Button>
    );
    buttons.push(
      <Button
        key="reject-draft"
        variant="outline"
        onClick={() => handleAction(() =>
          respondMutation.mutateAsync({
            id: quoteId,
            data: { response: "rejected", notes: "Rejected — sent back to draft" },
          })
        )}
        disabled={respondMutation.isPending}
      >
        Reject to Draft
      </Button>
    );
  }

  if (status === "approved" && isAdminOrPm) {
    buttons.push(
      <Button
        key="send"
        onClick={() => handleAction(() => sendMutation.mutateAsync(quoteId))}
        disabled={sendMutation.isPending}
      >
        Send to Client
      </Button>
    );
  }

  if (status === "sent" && isAdminOrPm) {
    buttons.push(
      <Button
        key="accept"
        onClick={() => handleAction(() =>
          respondMutation.mutateAsync({ id: quoteId, data: { response: "accepted" } })
        )}
        disabled={respondMutation.isPending}
        className="bg-green-600 hover:bg-green-700"
      >
        Record: Accepted
      </Button>
    );
    buttons.push(
      <Button
        key="reject"
        variant="destructive"
        onClick={() => handleAction(() =>
          respondMutation.mutateAsync({ id: quoteId, data: { response: "rejected" } })
        )}
        disabled={respondMutation.isPending}
      >
        Record: Rejected
      </Button>
    );
  }

  const statusCfg = STATUS_CONFIG[status];

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <Badge className={statusCfg.className}>{statusCfg.label}</Badge>
      {buttons}
    </div>
  );
}
