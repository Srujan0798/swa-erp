import { useParams } from "react-router-dom";
import { FileBrowser } from "@/components/documents/FileBrowser";

export function DocumentsPage() {
  const { projectId } = useParams<{ projectId: string }>();

  if (!projectId) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Documents</h1>
      <FileBrowser projectId={projectId} />
    </div>
  );
}
