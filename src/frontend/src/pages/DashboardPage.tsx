import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { RecentProjects } from "@/components/dashboard/RecentProjects";
import { RecentClients } from "@/components/dashboard/RecentClients";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import {
  ArrowRight,
  Building2,
  FileSignature,
  FolderKanban,
  Inbox,
  AlertCircle,
} from "lucide-react";

const FLOW = [
  {
    step: "1",
    title: "Inquiry",
    desc: "Lead comes in",
    to: "/inquiries",
    icon: Inbox,
    key: "inq" as const,
  },
  {
    step: "2",
    title: "Client",
    desc: "Create or reuse",
    to: "/clients",
    icon: Building2,
    key: "cli" as const,
  },
  {
    step: "3",
    title: "Project",
    desc: "Work package",
    to: "/projects",
    icon: FolderKanban,
    key: "prj" as const,
  },
  {
    step: "4",
    title: "SA → Token → Doc",
    desc: "Agreement & refs",
    to: "/clients",
    icon: FileSignature,
    key: "sa" as const,
  },
];

export function DashboardPage() {
  const inq = useQuery({
    queryKey: ["dash-inq"],
    queryFn: () => api.listInquiries({ page: 1, page_size: 1 }),
  });
  const cli = useQuery({
    queryKey: ["dash-cli"],
    queryFn: () => api.listClients({ page: 1, page_size: 1 }),
  });
  const prj = useQuery({
    queryKey: ["dash-prj"],
    queryFn: () => api.listProjects({ page: 1, page_size: 1 }),
  });
  const sa = useQuery({
    queryKey: ["dash-sa"],
    queryFn: () => api.listAgreements({ page: 1, page_size: 1 }),
  });

  const totals = {
    inq: inq.data?.total ?? 0,
    cli: cli.data?.total ?? 0,
    prj: prj.data?.total ?? 0,
    sa: sa.data?.total ?? 0,
  };

  const anyError = inq.isError || cli.isError || prj.isError || sa.isError;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Operations dashboard</h1>
          <p className="text-sm text-muted-foreground">
            SWA Consultancy ERP — data from your Excel sheets (import), not random demo seed.
          </p>
        </div>
        <Button asChild>
          <Link to="/inquiries">
            New inquiry
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </div>

      {anyError && (
        <div className="flex items-start gap-2 rounded-lg border border-destructive/40 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            <p className="font-medium">Could not load some counts from the API</p>
            <p className="text-destructive/80">
              Check you are on port 3100 and the API is running on 8100. Login again if needed.
            </p>
          </div>
        </div>
      )}

      <div>
        <h2 className="mb-2 text-sm font-semibold text-muted-foreground">
          Core business chain
        </h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {FLOW.map((f) => (
            <Link key={f.step} to={f.to}>
              <Card className="h-full transition-shadow hover:shadow-md">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="flex items-center gap-2">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                      {f.step}
                    </span>
                    <CardTitle className="text-sm font-semibold">{f.title}</CardTitle>
                  </div>
                  <f.icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold tabular-nums">{totals[f.key]}</div>
                  <p className="text-xs text-muted-foreground">{f.desc}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      <StatsCards />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RecentProjects />
        <RecentClients />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Where things live in the UI</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
          <p>
            <span className="font-medium text-foreground">Service Agreements & Tokens</span> —
            open a Client → Agreements tab → expand SA for tokens.
          </p>
          <p>
            <span className="font-medium text-foreground">Document references (DRN)</span> —
            open a Project → Documents tab.
          </p>
          <p>
            <span className="font-medium text-foreground">Reload Excel data</span> —{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">make bootstrap-real</code>
          </p>
          <p>
            <span className="font-medium text-foreground">Correct URL</span> —{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">http://127.0.0.1:3100</code>{" "}
            (not 3000).
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
