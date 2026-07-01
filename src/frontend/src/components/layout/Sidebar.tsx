import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Users,
  Building2,
  FolderKanban,
  FileText,
  Truck,
  ShieldCheck,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const navItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/clients", icon: Building2, label: "Clients" },
  { to: "/projects", icon: FolderKanban, label: "Projects" },
  { to: "/vendors", icon: Truck, label: "Vendors" },
  { to: "/documents", icon: FileText, label: "Documents" },
  { to: "/compliance", icon: ShieldCheck, label: "Compliance" },
  { to: "/users", icon: Users, label: "Users", adminOnly: true },
];

export function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="w-64 border-r bg-card">
      <div className="flex h-14 items-center border-b px-4">
        <span className="font-semibold text-lg">SWA ERP</span>
      </div>
      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          if (item.adminOnly && user?.role !== "admin") {
            return null;
          }
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
                  isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground"
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}