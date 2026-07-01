import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { ComplianceDashboard } from "@/components/compliance/ComplianceDashboard";
import { ComplianceChecklist } from "@/components/compliance/ComplianceChecklist";
import { useStandards } from "@/hooks/useCompliance";

export function CompliancePage() {
  const { id } = useParams<{ id: string }>();
  const [selectedStandard, setSelectedStandard] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const { data: standards = [] } = useStandards();

  if (!id) return null;

  const handleSelectStandard = (standardName: string) => {
    const std = standards.find((s) => s.name === standardName);
    if (std) {
      setSelectedStandard({ id: std.id, name: std.name });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to={`/projects/${id}`}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Project
          </Link>
        </Button>
        <nav className="text-sm text-muted-foreground">
          <Link to="/projects" className="hover:underline">
            Projects
          </Link>
          <span className="mx-2">/</span>
          <Link to={`/projects/${id}`} className="hover:underline">
            Project
          </Link>
          <span className="mx-2">/</span>
          <span>Compliance</span>
        </nav>
      </div>

      {selectedStandard ? (
        <ComplianceChecklist
          projectId={id}
          standardId={selectedStandard.id}
          standardName={selectedStandard.name}
          onBack={() => setSelectedStandard(null)}
        />
      ) : (
        <ComplianceDashboard
          projectId={id}
          onSelectStandard={handleSelectStandard}
        />
      )}
    </div>
  );
}
