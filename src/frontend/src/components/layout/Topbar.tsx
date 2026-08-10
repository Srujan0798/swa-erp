import { useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LogOut } from "lucide-react";
import { NotificationsBell } from "./NotificationsBell";

const TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/inquiries": "Inquiries",
  "/clients": "Clients",
  "/projects": "Projects",
  "/tasks": "Tasks",
  "/vendors": "Vendors",
  "/documents": "Documents",
  "/compliance": "Compliance",
  "/sustainability": "Sustainability",
  "/invoices": "Invoices",
  "/materials": "Materials",
  "/rfqs": "RFQs",
  "/reports": "Reports",
  "/time-tracking": "Time tracking",
  "/users": "Users",
};

function titleForPath(pathname: string): string {
  if (TITLES[pathname]) return TITLES[pathname];
  const base = "/" + pathname.split("/").filter(Boolean)[0];
  return TITLES[base] ?? "SWA ERP";
}

export function Topbar() {
  const { user, logout, isLoggingOut } = useAuth();
  const { pathname } = useLocation();

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card/80 px-6 backdrop-blur">
      <div className="flex min-w-0 items-center gap-3">
        <h1 className="truncate text-base font-semibold tracking-tight">
          {titleForPath(pathname)}
        </h1>
        <Badge variant="secondary" className="hidden font-normal sm:inline-flex">
          Live data
        </Badge>
      </div>
      <div className="flex items-center gap-3">
        <div className="hidden text-right text-xs leading-tight sm:block">
          <div className="font-medium text-foreground">{user?.name}</div>
          <div className="capitalize text-muted-foreground">{user?.role}</div>
        </div>
        <NotificationsBell />
        <Button
          variant="outline"
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
