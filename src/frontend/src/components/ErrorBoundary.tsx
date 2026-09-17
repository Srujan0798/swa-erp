import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";
import { Button } from "@/components/ui/button";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Catches unhandled render errors below it and renders a recoverable
 * fallback instead of white-screening the whole app.
 *
 * There is no frontend Sentry SDK wired (no @sentry/react dependency —
 * Sentry lives server-side in `core/errors.py`), so the caught error is
 * reported via `console.error` for log aggregation.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Unhandled render error caught by ErrorBoundary:", error, info);
  }

  private handleReload = (): void => {
    window.location.reload();
  };

  private handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div
          role="alert"
          aria-live="assertive"
          className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-8 text-center"
        >
          <h1 className="text-xl font-semibold">Something went wrong</h1>
          <p className="max-w-md text-sm text-muted-foreground">
            This section failed to render. Your work is safe — try again or reload the
            page.
          </p>
          {this.state.error ? (
            <p className="max-w-md truncate font-mono text-xs text-muted-foreground">
              {this.state.error.message}
            </p>
          ) : null}
          <div className="flex gap-2">
            <Button onClick={this.handleReset}>Try again</Button>
            <Button variant="outline" onClick={this.handleReload}>
              Reload page
            </Button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
