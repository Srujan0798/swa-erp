import { cn } from "@/lib/utils";
import type { ComplianceStatus } from "@/types/compliance";
import { useUpdateComplianceItem } from "@/hooks/useCompliance";

const STATUS_CONFIG: Record<ComplianceStatus, { label: string; className: string }> = {
  pending: { label: "Pending", className: "bg-yellow-100 text-yellow-800 hover:bg-yellow-200" },
  compliant: { label: "Compliant", className: "bg-green-100 text-green-800 hover:bg-green-200" },
  non_compliant: { label: "Non-Compliant", className: "bg-red-100 text-red-800 hover:bg-red-200" },
  na: { label: "N/A", className: "bg-blue-100 text-blue-800 hover:bg-blue-200" },
};

const STATUS_ORDER: ComplianceStatus[] = ["pending", "compliant", "non_compliant", "na"];

interface ComplianceItemStatusProps {
  itemId: string;
  status: ComplianceStatus;
}

export function ComplianceItemStatus({ itemId, status }: ComplianceItemStatusProps) {
  const updateItem = useUpdateComplianceItem();

  const cycleStatus = () => {
    const currentIndex = STATUS_ORDER.indexOf(status);
    const nextStatus = STATUS_ORDER[(currentIndex + 1) % STATUS_ORDER.length];
    updateItem.mutate({ itemId, data: { status: nextStatus } });
  };

  const config = STATUS_CONFIG[status];

  return (
    <button
      onClick={cycleStatus}
      disabled={updateItem.isPending}
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors cursor-pointer disabled:opacity-50",
        config.className
      )}
    >
      {config.label}
    </button>
  );
}
