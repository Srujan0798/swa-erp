import type { ReactElement } from "react";
import { Button } from "@/components/ui/button";

interface QueryErrorBannerProps {
  message?: string;
  error?: unknown;
  onRetry?: () => void;
  className?: string;
}

export function QueryErrorBanner({
  message = "Failed to load data",
  error,
  onRetry,
  className,
}: QueryErrorBannerProps): ReactElement {
  const detail =
    error instanceof Error
      ? error.message
      : typeof error === "string"
        ? error
        : null;

  return (
    <div
      role="alert"
      className={
        className ??
        "flex flex-wrap items-center justify-between gap-3 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive"
      }
    >
      <div>
        <p className="font-medium">{message}</p>
        {detail && <p className="mt-0.5 text-xs opacity-90">{detail}</p>}
      </div>
      {onRetry && (
        <Button type="button" variant="outline" size="sm" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}
