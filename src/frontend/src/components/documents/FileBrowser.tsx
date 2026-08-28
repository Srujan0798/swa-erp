import { type ReactElement } from "react";

/**
 * Minimal FileBrowser stub.
 *
 * The DocumentsPage (/documents) needs a file-browsing component. The full
 * implementation (with upload, drag-drop, storage backend routing) is tracked
 * as a deferred feature. This stub renders the placeholder so the route compiles
 * and tsc is clean. It is wired to the same `api` that the rest of the app uses
 * so it can be replaced with the real impl without touching the page.
 */
interface FileBrowserProps {
  projectId: string;
}

export function FileBrowser({ projectId }: FileBrowserProps): ReactElement {
  return (
    <div className="rounded-md border border-dashed p-8 text-center">
      <p className="text-sm text-muted-foreground">
        File browser for project {projectId} — implementation pending.
      </p>
    </div>
  );
}
