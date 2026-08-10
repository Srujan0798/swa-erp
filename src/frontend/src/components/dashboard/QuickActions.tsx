import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { FolderPlus, UserPlus, Inbox } from "lucide-react";

export function QuickActions() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-wrap gap-2">
      <Button onClick={() => navigate("/inquiries")}>
        <Inbox className="mr-2 h-4 w-4" />
        Inquiries
      </Button>
      <Button variant="outline" onClick={() => navigate("/clients/new")}>
        <UserPlus className="mr-2 h-4 w-4" />
        New client
      </Button>
      <Button variant="outline" onClick={() => navigate("/projects/new")}>
        <FolderPlus className="mr-2 h-4 w-4" />
        New project
      </Button>
    </div>
  );
}
