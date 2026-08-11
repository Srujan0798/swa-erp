import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useCurrentUser } from "@/hooks/useAuth";
import { canManageCommercial, canWrite } from "@/lib/permissions";
import { FolderPlus, UserPlus, Inbox } from "lucide-react";

export function QuickActions() {
  const navigate = useNavigate();
  const { data: user } = useCurrentUser();
  const write = canWrite(user);
  const commercial = canManageCommercial(user);

  return (
    <div className="flex flex-wrap gap-2">
      <Button onClick={() => navigate("/inquiries")}>
        <Inbox className="mr-2 h-4 w-4" />
        Inquiries
      </Button>
      {commercial ? (
        <Button variant="outline" onClick={() => navigate("/clients/new")}>
          <UserPlus className="mr-2 h-4 w-4" />
          New client
        </Button>
      ) : null}
      {write ? (
        <Button variant="outline" onClick={() => navigate("/projects/new")}>
          <FolderPlus className="mr-2 h-4 w-4" />
          New project
        </Button>
      ) : null}
    </div>
  );
}
