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
  CheckSquare2,
  Leaf,
  Receipt,
  Package,
  Send,
  BarChart3,
  Clock,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const navItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/clients", icon: Building2, label: "Clients" },
  { to: "/projects", icon: FolderKanban, label: "Projects" },
  { to: "/tasks", icon: CheckSquare2, label: "Tasks" },
  { to: "/vendors", icon: Truck, label: "Vendors" },
  { to: "/documents", icon: FileText, label: "Documents" },
  { to: "/compliance", icon: ShieldCheck, label: "Compliance" },
  { to: "/sustainability", icon: Leaf, label: "Sustainability" },
  { to: "/invoices", icon: Receipt, label: "Invoices" },
  { to: "/materials", icon: Package, label: "Materials" },
  { to: "/rfqs", icon: Send, label: "RFQs" },
  { to: "/reports", icon: BarChart3, label: "Reports" },
  { to: "/time-tracking", icon: Clock, label: "Time Tracking" },
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