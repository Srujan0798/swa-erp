import type { ReactElement } from "react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

export type ProjectTabKey = "overview" | "boqs" | "quotes" | "documents" | "sustainability";

interface ProjectQuickLinksProps {
  projectId: string;
  clientId?: string | null;
  activeTab?: ProjectTabKey;
  onTabChange?: (tab: ProjectTabKey) => void;
  className?: string;
}

type Chip =
  | { kind: "tab"; key: ProjectTabKey; label: string }
  | { kind: "link"; to: string; label: string; external?: boolean };

/**
 * Nav chips from project detail to related work areas (tabs + routes).
 */
export function ProjectQuickLinks({
  projectId,
  clientId,
  activeTab,
  onTabChange,
  className,
}: ProjectQuickLinksProps): ReactElement {
  const chips: Chip[] = [
    { kind: "tab", key: "boqs", label: "BOQs" },
    { kind: "tab", key: "quotes", label: "Quotations" },
    { kind: "tab", key: "documents", label: "Documents" },
    { kind: "link", to: `/tasks?project=${projectId}`, label: "Tasks" },
    { kind: "link", to: `/invoices?project=${projectId}`, label: "Invoices" },
    { kind: "link", to: `/reports?project=${projectId}`, label: "Costs / P&L" },
    { kind: "link", to: `/time-tracking?project=${projectId}`, label: "Time" },
    ...(clientId
      ? [{ kind: "link" as const, to: `/clients/${clientId}`, label: "Client" }]
      : []),
    { kind: "link", to: "/agreements", label: "Agreements" },
    { kind: "link", to: `/tokens?project=${projectId}`, label: "Tokens" },
  ];

  const chipClass =
    "inline-flex items-center rounded-full border bg-background px-3 py-1 text-xs font-medium transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

  return (
    <nav
      aria-label="Project shortcuts"
      className={cn("flex flex-wrap items-center gap-2", className)}
    >
      <span className="text-xs font-medium text-muted-foreground mr-1">Go to:</span>
      {chips.map((chip) => {
        if (chip.kind === "tab") {
          const isActive = activeTab === chip.key;
          return (
            <button
              key={chip.key}
              type="button"
              onClick={() => onTabChange?.(chip.key)}
              className={cn(
                chipClass,
                isActive && "border-primary bg-primary/10 text-primary",
              )}
            >
              {chip.label}
            </button>
          );
        }
        return (
          <Link key={chip.to + chip.label} to={chip.to} className={chipClass}>
            {chip.label}
          </Link>
        );
      })}
    </nav>
  );
}
