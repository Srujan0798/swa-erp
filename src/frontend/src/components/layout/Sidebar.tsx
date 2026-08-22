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
  Inbox,
  FileSignature,
  Coins,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

type NavItem = {
  to: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  adminOnly?: boolean;
};

const CORE_FLOW: NavItem[] = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/inquiries", icon: Inbox, label: "1. Inquiries" },
  { to: "/clients", icon: Building2, label: "2. Clients" },
  { to: "/agreements", icon: FileSignature, label: "3. Service Agreements" },
  { to: "/tokens", icon: Coins, label: "4. Tokens" },
  { to: "/document-references", icon: FileText, label: "5. Document refs" },
  { to: "/projects", icon: FolderKanban, label: "6. Projects" },
  { to: "/time-tracking", icon: Clock, label: "7. Time logging" },
];

const DELIVERY: NavItem[] = [
  { to: "/documents", icon: FileText, label: "Files / drawings" },
  { to: "/tasks", icon: CheckSquare2, label: "Tasks" },
  { to: "/sustainability", icon: Leaf, label: "Sustainability" },
  { to: "/compliance", icon: ShieldCheck, label: "Compliance" },
];

/** Demoted — not the Excel core chain; keep available but not equal weight */
const MORE: NavItem[] = [
  { to: "/vendors", icon: Truck, label: "Vendors" },
  { to: "/materials", icon: Package, label: "Materials" },
  { to: "/rfqs", icon: Send, label: "RFQs" },
  { to: "/invoices", icon: Receipt, label: "Invoices" },
  { to: "/reports", icon: BarChart3, label: "Reports" },
];

const ADMIN: NavItem[] = [
  { to: "/users", icon: Users, label: "Users", adminOnly: true },
];

function NavSection({
  title,
  items,
  role,
}: {
  title: string;
  items: NavItem[];
  role?: string;
}) {
  const visible = items.filter((i) => !i.adminOnly || role === "admin");
  if (visible.length === 0) return null;
  return (
    <div className="mb-4">
      <p className="mb-1.5 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/80">
        {title}
      </p>
      <div className="space-y-0.5">
        {visible.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )
            }
          >
            <item.icon className="h-4 w-4 shrink-0" />
            <span className="truncate">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </div>
  );
}

export function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r bg-card">
      <div className="flex h-14 items-center gap-2 border-b px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
          <FileSignature className="h-4 w-4" />
        </div>
        <div className="min-w-0 leading-tight">
          <div className="truncate text-sm font-bold tracking-tight">SWA ERP</div>
          <div className="truncate text-[10px] text-muted-foreground">
            Consultancy · insulation
          </div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-3">
        <NavSection title="Excel workflow" items={CORE_FLOW} role={user?.role} />
        <NavSection title="Delivery" items={DELIVERY} role={user?.role} />
        <NavSection title="More" items={MORE} role={user?.role} />
        <NavSection title="Admin" items={ADMIN} role={user?.role} />
      </nav>

      <div className="border-t p-3 text-[10px] leading-snug text-muted-foreground">
        <p className="font-medium text-foreground/80">SWA sheet chain</p>
        <p>Inquiry → Client → SA → Token → Doc Ref → Time</p>
        <p className="mt-1">
          Data: <span className="font-mono">make swa-live-local</span>
        </p>
      </div>
    </aside>
  );
}
