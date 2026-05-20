import { StatsCards } from "@/components/dashboard/StatsCards";
import { RecentProjects } from "@/components/dashboard/RecentProjects";
import { RecentClients } from "@/components/dashboard/RecentClients";
import { QuickActions } from "@/components/dashboard/QuickActions";

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Overview of your projects and clients</p>
      </div>
      <QuickActions />
      <StatsCards />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentProjects />
        <RecentClients />
      </div>
    </div>
  );
}