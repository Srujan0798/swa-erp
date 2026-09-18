import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { StatsCards } from "../StatsCards";
import { RecentProjects } from "../RecentProjects";
import { RecentClients } from "../RecentClients";
import { QuickActions } from "../QuickActions";
import { DashboardPage } from "@/pages/DashboardPage";

const useQueryMock = vi.hoisted(() => vi.fn());

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: { queryKey: string[] }) => useQueryMock(options),
}));

const useDashboardMock = vi.hoisted(() => vi.fn());
const useCurrentUserMock = vi.hoisted(() => vi.fn());
const navigateMock = vi.hoisted(() => vi.fn());

function emptyList() {
  return { data: { items: [], total: 0 }, isLoading: false, isError: false };
}

function listWithTotal(total: number) {
  return { data: { items: [], total }, isLoading: false, isError: false };
}

function mockAllCountsZero() {
  useQueryMock.mockImplementation((options: { queryKey: string[] }) => {
    const key = options.queryKey[0];
    if (typeof key === "string" && key.startsWith("dash-")) return emptyList();
    return { data: undefined, isLoading: false };
  });
}

vi.mock("@/hooks/useDashboard", () => ({
  useDashboard: () => useDashboardMock(),
  useProjects: (page: number, pageSize: number) => useDashboardMock(page, pageSize),
  useClients: (page: number, pageSize: number) => useDashboardMock(page, pageSize),
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

const project = {
  id: "p1",
  code: "PRJ-001",
  name: "Acme Office",
  client_name: "Acme Corp",
  status: "Execution",
};

const client = {
  id: "c1",
  code: "AC-001",
  name: "Acme Corp",
  industry: "Construction",
  client_status: "Active",
};

describe("StatsCards", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders loading skeletons while loading", () => {
    useDashboardMock.mockReturnValue({ data: undefined, isLoading: true });
    render(<StatsCards />);
    expect(document.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
  });

  it("renders formatted values from dashboard stats", () => {
    useDashboardMock.mockReturnValue({
      data: { total_active: 3, total_estimated_value: 15000000, by_status: { Quote: 1, Execution: 2 } },
      isLoading: false,
    });
    render(<StatsCards />);
    expect(screen.getByText("Total Active Projects")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("₹1,50,00,000")).toBeInTheDocument();
  });
});

describe("RecentProjects", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders projects with status badges", () => {
    useDashboardMock.mockReturnValue({ data: { items: [project] }, isLoading: false, isError: false });
    render(
      <MemoryRouter>
        <RecentProjects />
      </MemoryRouter>
    );
    expect(screen.getByText("PRJ-001")).toBeInTheDocument();
    expect(screen.getByText("Acme Office")).toBeInTheDocument();
    expect(screen.getByText("Execution")).toBeInTheDocument();
  });

  it("renders the empty state", () => {
    useDashboardMock.mockReturnValue({ data: { items: [] }, isLoading: false, isError: false });
    render(
      <MemoryRouter>
        <RecentProjects />
      </MemoryRouter>
    );
    expect(screen.getByText(/no projects/i)).toBeInTheDocument();
  });

  it("renders error state", () => {
    useDashboardMock.mockReturnValue({ data: undefined, isLoading: false, isError: true });
    render(
      <MemoryRouter>
        <RecentProjects />
      </MemoryRouter>
    );
    expect(screen.getByText("Failed to load projects")).toBeInTheDocument();
  });
});

describe("RecentClients", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders clients with industry and status", () => {
    useDashboardMock.mockReturnValue({ data: { items: [client] }, isLoading: false, isError: false });
    render(
      <MemoryRouter>
        <RecentClients />
      </MemoryRouter>
    );
    expect(screen.getByText("AC-001")).toBeInTheDocument();
    expect(screen.getByText("Construction")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("renders the empty state", () => {
    useDashboardMock.mockReturnValue({ data: { items: [] }, isLoading: false, isError: false });
    render(
      <MemoryRouter>
        <RecentClients />
      </MemoryRouter>
    );
    expect(screen.getByText(/no clients/i)).toBeInTheDocument();
  });

  it("renders error state", () => {
    useDashboardMock.mockReturnValue({ data: undefined, isLoading: false, isError: true });
    render(
      <MemoryRouter>
        <RecentClients />
      </MemoryRouter>
    );
    expect(screen.getByText("Failed to load clients")).toBeInTheDocument();
  });
});

describe("QuickActions", () => {
  beforeEach(() => vi.clearAllMocks());

  it("always shows the inquiries shortcut", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    render(
      <MemoryRouter>
        <QuickActions />
      </MemoryRouter>
    );
    expect(screen.getByRole("button", { name: /inquiries/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /new client/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /new project/i })).not.toBeInTheDocument();
  });

  it("shows commercial and write actions for admins", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
    render(
      <MemoryRouter>
        <QuickActions />
      </MemoryRouter>
    );
    expect(screen.getByRole("button", { name: /new client/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /new project/i })).toBeInTheDocument();
  });

  it("navigates on action click", async () => {
    const user = (await import("@testing-library/user-event")).default;
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
    render(
      <MemoryRouter>
        <QuickActions />
      </MemoryRouter>
    );
    await user.click(screen.getByRole("button", { name: /new client/i }));
    expect(navigateMock).toHaveBeenCalledWith("/clients/new");
  });
});

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAllCountsZero();
    useDashboardMock.mockReturnValue({ data: undefined, isLoading: false });
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
  });

  it("renders flow steps in order: Inquiry, Client, Project, SA, Token, Document Ref, Time", () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );
    const titles = ["Inquiry", "Client", "Project", "Service Agreement", "Token", "Document Ref", "Time log"];
    const positions = titles.map((title) => {
      const links = screen.getAllByRole("link");
      const el = links.find((link) => link.textContent?.includes(title));
      expect(el).toBeDefined();
      return el as HTMLElement;
    });
    positions.forEach((el, i) => {
      if (i > 0) {
        const prev = positions[i - 1];
        expect(prev.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
      }
    });
  });

  it("gates looksEmpty until all counts finished loading and covers all counts", () => {
    useQueryMock.mockImplementation((options: { queryKey: string[] }) => {
      const key = options.queryKey[0];
      if (key === "dash-time") return { data: undefined, isLoading: true, isError: false };
      if (typeof key === "string" && key.startsWith("dash-")) return emptyList();
      return { data: undefined, isLoading: false };
    });
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );
    expect(screen.queryByText(/No workflow records yet/i)).not.toBeInTheDocument();
    expect(screen.getByText("SWA operations")).toBeInTheDocument();
  });

  it("shows empty dashboard guidance with all counts zero and no admin password or import commands", () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );
    expect(screen.getByText(/No workflow records yet/i)).toBeInTheDocument();
    expect(screen.queryByText(/admin123!/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/admin@swa.co.in/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/make swa-live-local/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/make bootstrap-real/i)).not.toBeInTheDocument();
  });

  it("links Invoice/GST and Compliance using existing routes with no fake counts", () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );
    const invoiceLink = screen.getByRole("link", { name: /invoice\/gst/i });
    const complianceLink = screen.getByRole("link", { name: /^compliance$/i });
    expect(invoiceLink).toHaveAttribute("href", "/invoices");
    expect(complianceLink).toHaveAttribute("href", "/compliance");
    expect(screen.queryByText(/total revenue/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/invoices?\s+\d+/i)).not.toBeInTheDocument();
  });

  it("marks files/drawings as a stub and does not claim uploads are implemented", () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );
    expect(screen.getByText(/Files \/ drawings/i)).toBeInTheDocument();
    expect(screen.getByText(/placeholder/i)).toBeInTheDocument();
    expect(screen.queryByText(/uploaded PDFs and CAD files/i)).not.toBeInTheDocument();
  });

  it("gates projectsSparse until counts ready and requires at least one other non-zero count", () => {
    useQueryMock.mockImplementation((options: { queryKey: string[] }) => {
      const key = options.queryKey[0];
      if (key === "dash-prj") return listWithTotal(0);
      if (key === "dash-tkn") return listWithTotal(2);
      if (typeof key === "string" && key.startsWith("dash-")) return emptyList();
      return { data: undefined, isLoading: false };
    });
    const first = render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );
    expect(screen.getByText(/Projects list looks empty/i)).toBeInTheDocument();
    first.unmount();

    useQueryMock.mockImplementation((options: { queryKey: string[] }) => {
      const key = options.queryKey[0];
      if (key === "dash-tkn") return { data: undefined, isLoading: true, isError: false };
      if (key === "dash-prj") return listWithTotal(0);
      if (typeof key === "string" && key.startsWith("dash-")) return emptyList();
      return { data: undefined, isLoading: false };
    });
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );
    expect(screen.queryByText(/Projects list looks empty/i)).not.toBeInTheDocument();
  });
});