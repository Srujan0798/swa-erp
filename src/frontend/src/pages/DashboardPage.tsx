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
  Clock,
  Coins,
  FileSignature,
  FileText,
  FolderKanban,
  Inbox,
  AlertCircle,
} from "lucide-react";

const FLOW = [
  {
    step: "1",
    title: "Inquiry",
    desc: "Lead / ML comes in",
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
    title: "Service Agreement",
    desc: "Year retainer (SA)",
    to: "/agreements",
    icon: FileSignature,
    key: "sa" as const,
  },
  {
    step: "4",
    title: "Token",
    desc: "Unit of work",
    to: "/tokens",
    icon: Coins,
    key: "tkn" as const,
  },
  {
    step: "5",
    title: "Document Ref",
    desc: "DRN / DBR / KDR sheet",
    to: "/document-references",
    icon: FileText,
    key: "drn" as const,
  },
  {
    step: "6",
    title: "Project",
    desc: "Work package",
    to: "/projects",
    icon: FolderKanban,
    key: "prj" as const,
  },
  {
    step: "7",
    title: "Time log",
    desc: "Hours (Excel time sheet)",
    to: "/time-tracking",
    icon: Clock,
    key: "time" as const,
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
  const tkn = useQuery({
    queryKey: ["dash-tkn"],
    queryFn: () => api.listTokens({ page: 1, page_size: 1 }),
  });
  const drn = useQuery({
    queryKey: ["dash-drn"],
    queryFn: () => api.listDocumentReferences({ page: 1, page_size: 1 }),
  });

  const totals = {
    inq: inq.data?.total ?? 0,
    cli: cli.data?.total ?? 0,
    sa: sa.data?.total ?? 0,
    tkn: tkn.data?.total ?? 0,
    drn: drn.data?.total ?? 0,
    prj: prj.data?.total ?? 0,
    time: 0,
  };

  const anyError =
    inq.isError || cli.isError || prj.isError || sa.isError || tkn.isError || drn.isError;
  const looksEmpty =
    !anyError && totals.inq === 0 && totals.cli === 0 && totals.sa === 0 && totals.tkn === 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">SWA operations</h1>
          <p className="text-sm text-muted-foreground">
            Your Excel workflow as a website — Inquiry → Client → SA → Token → Document Reference →
            Time.
          </p>
        </div>
        <Button asChild>
          <Link to="/inquiries">
            New inquiry
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </div>

      {looksEmpty && (
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/5 px-4 py-3 text-sm">
          <p className="font-medium text-foreground">No SWA sheet data loaded yet</p>
          <p className="mt-1 text-muted-foreground">
            Do <strong>not</strong> use synthetic demo seed for client review. Load the real Excel
            extract:
          </p>
          <pre className="mt-2 overflow-x-auto rounded bg-muted px-3 py-2 font-mono text-xs">
            make bootstrap-real
          </pre>
          <p className="mt-2 text-muted-foreground">
            Then login <code className="rounded bg-muted px-1">admin@swa.co.in</code> /{" "}
            <code className="rounded bg-muted px-1">admin123!</code> — you should see{" "}
            <code className="rounded bg-muted px-1">SWA-2025-…</code> IDs.
          </p>
        </div>
      )}

      {anyError && (
        <div className="flex items-start gap-2 rounded-lg border border-destructive/40 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            <p className="font-medium">Could not load some counts from the API</p>
            <p className="text-destructive/80">
              UI on port 3100 · API on 8100. Login again if needed.
            </p>
          </div>
        </div>
      )}

      <div>
        <h2 className="mb-2 text-sm font-semibold text-muted-foreground">
          Core business chain (Excel sheets)
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
                  <div className="text-2xl font-bold tabular-nums">
                    {f.key === "time" ? "→" : totals[f.key]}
                  </div>
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
          <CardTitle className="text-base">Where things live (match the sheets)</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
          <p>
            <span className="font-medium text-foreground">Document Reference Sheet</span> — left
            nav <strong>5. Document refs</strong> (not “Files / drawings”).
          </p>
          <p>
            <span className="font-medium text-foreground">Files / drawings</span> — uploaded PDFs
            and CAD files (storage), separate from DRN numbering.
          </p>
          <p>
            <span className="font-medium text-foreground">Load real Excel</span> —{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">make bootstrap-real</code>
          </p>
          <p>
            <span className="font-medium text-foreground">App URL</span> —{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">http://127.0.0.1:3100</code>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
