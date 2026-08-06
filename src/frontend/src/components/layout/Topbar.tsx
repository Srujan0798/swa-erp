import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";
import { NotificationsBell } from "./NotificationsBell";

export function Topbar() {
  const { user, logout, isLoggingOut } = useAuth();

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-6">
      <div className="text-sm text-muted-foreground">
        {user?.name} ({user?.role})
      </div>
      <div className="flex items-center gap-2">
        <NotificationsBell />
        <Button
          variant="ghost"
          size="sm"
          onClick={() => logout()}
          disabled={isLoggingOut}
        >
          <LogOut className="mr-2 h-4 w-4" />
          Logout
        </Button>
      </div>
    </header>
  );
}