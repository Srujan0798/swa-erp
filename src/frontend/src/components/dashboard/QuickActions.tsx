import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { FolderPlus, UserPlus } from "lucide-react";

export function QuickActions() {
  const navigate = useNavigate();

  return (
    <div className="flex gap-4">
      <Button onClick={() => navigate("/projects/new")}>
        <FolderPlus className="mr-2 h-4 w-4" />
        New Project
      </Button>
      <Button variant="outline" onClick={() => navigate("/clients/new")}>
        <UserPlus className="mr-2 h-4 w-4" />
        New Client
      </Button>
    </div>
  );
}