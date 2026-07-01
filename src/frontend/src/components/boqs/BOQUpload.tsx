import { useState } from "react";
import { useUploadBoq } from "@/hooks/useBoqs";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload } from "lucide-react";

interface BOQUploadProps {
  projectId: string;
  onSuccess?: () => void;
}

export function BOQUpload({ projectId, onSuccess }: BOQUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [notes, setNotes] = useState("");
  const uploadMutation = useUploadBoq();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    await uploadMutation.mutateAsync({ projectId, file, notes: notes || undefined });
    setFile(null);
    setNotes("");
    onSuccess?.();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload BOQ</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="boq-file">BOQ File (.xlsx or .json)</Label>
            <input
              id="boq-file"
              type="file"
              accept=".xlsx,.json"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="block w-full text-sm file:mr-4 file:rounded-md file:border-0 file:bg-primary file:px-4 file:py-2 file:text-primary-foreground hover:file:bg-primary/90"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="boq-notes">Notes (optional)</Label>
            <Textarea
              id="boq-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any notes about this BOQ version..."
              rows={3}
            />
          </div>
          <Button type="submit" disabled={!file || uploadMutation.isPending}>
            <Upload className="mr-2 h-4 w-4" />
            {uploadMutation.isPending ? "Uploading..." : "Upload BOQ"}
          </Button>
          {uploadMutation.isError && (
            <p className="text-sm text-destructive">Upload failed. Please try again.</p>
          )}
        </form>
      </CardContent>
    </Card>
  );
}
