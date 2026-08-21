import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { api } from "@/lib/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/lib/api", () => ({
  api: {
    getProject: vi.fn(),
  },
}));

vi.mock("@/components/projects/ProjectDetail", () => ({
  ProjectDetail: ({ projectId }: any) => (
    <div data-testid="project-detail">ProjectDetail {projectId}</div>
  ),
}));

vi.mock("@/components/projects/ProjectQuickLinks", () => ({
  ProjectQuickLinks: ({ activeTab }: any) => (
    <div data-testid="project-quick-links">
      <span>Tab: {activeTab}</span>
    </div>
  ),
}));

vi.mock("@/components/boqs/BOQUpload", () => ({
  BOQUpload: () => <div data-testid="boq-upload">BOQUpload</div>,
}));

vi.mock("@/components/boqs/BOQVersionList", () => ({
  BOQVersionList: (_props: any) => <div data-testid="boq-version-list">BOQVersionList</div>,
}));

vi.mock("@/components/boqs/BOQItemTable", () => ({
  BOQItemTable: (_props: any) => <div data-testid="boq-item-table">BOQItemTable</div>,
}));

vi.mock("@/components/quotes/QuoteList", () => ({
  QuoteList: ({ projectId }: any) => <div data-testid="quote-list">QuoteList {projectId}</div>,
}));

vi.mock("@/components/quotes/QuoteBuilder", () => ({
  QuoteBuilder: () => <div data-testid="quote-builder">QuoteBuilder</div>,
}));

vi.mock("@/components/quotes/QuoteDetail", () => ({
  QuoteDetail: ({ quoteId }: any) => <div data-testid="quote-detail">QuoteDetail {quoteId}</div>,
}));

vi.mock("@/components/documentRefs/DocumentReferenceList", () => ({
  DocumentReferenceList: ({ projectId }: any) => (
    <div data-testid="document-reference-list">Documents {projectId}</div>
  ),
}));

vi.mock("@/pages/SustainabilityPage", () => ({
  SustainabilityManager: ({ projectId }: any) => (
    <div data-testid="sustainability-manager">Sustainability {projectId}</div>
  ),
}));

const project = { id: "p1", code: "PRJ-001", name: "Test Project", client_id: "c1" };

async function renderPage(id = "p1") {
  const { ProjectDetailPage } = await import("@/pages/ProjectDetailPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter initialEntries={[`/projects/${id}`]}>
      <QueryClientProvider client={queryClient}>
        <Routes>
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
        </Routes>
      </QueryClientProvider>
    </MemoryRouter>
  );
}

describe("ProjectDetailPage", () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    vi.mocked(api.getProject).mockResolvedValue(project as never);
  });

  it("renders overview tab by default", async () => {
    await renderPage();
    expect(await screen.findByTestId("project-detail")).toBeInTheDocument();
    expect(screen.getByText(/Back to Projects/)).toBeInTheDocument();
  });

  it("renders with project ID from params", async () => {
    await renderPage("p1");
    expect(await screen.findByTestId("project-detail")).toHaveTextContent("p1");
  });

  it("shows project quick links with overview tab active", async () => {
    await renderPage();
    const ql = await screen.findByTestId("project-quick-links");
    expect(ql).toHaveTextContent("Tab: overview");
  });

  it("navigates to BOQs tab via tabs", async () => {
    await renderPage();
    await screen.findByTestId("project-detail");
    await user.click(screen.getByRole("tab", { name: /BOQs/i }));
    expect(screen.getByTestId("boq-version-list")).toBeInTheDocument();
  });

  it("navigates to quotes tab", async () => {
    await renderPage();
    await screen.findByTestId("project-detail");
    await user.click(screen.getByRole("tab", { name: /Quotes/i }));
    expect(screen.getByTestId("quote-list")).toBeInTheDocument();
  });

  it("shows New Quote button for commercial users", async () => {
    await renderPage();
    await screen.findByTestId("project-detail");
    await user.click(screen.getByRole("tab", { name: /Quotes/i }));
    expect(screen.getByText("New Quote")).toBeInTheDocument();
  });

  it("hides New Quote for non-commercial users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage();
    await screen.findByTestId("project-detail");
    await user.click(screen.getByRole("tab", { name: /Quotes/i }));
    expect(screen.queryByText("New Quote")).not.toBeInTheDocument();
  });

  it("navigates to documents tab", async () => {
    await renderPage();
    await screen.findByTestId("project-detail");
    await user.click(screen.getByRole("tab", { name: /Documents/i }));
    expect(screen.getByTestId("document-reference-list")).toBeInTheDocument();
  });

  it("navigates to sustainability tab", async () => {
    await renderPage();
    await screen.findByTestId("project-detail");
    await user.click(screen.getByRole("tab", { name: /Sustainability/i }));
    expect(screen.getByTestId("sustainability-manager")).toBeInTheDocument();
  });

  it("shows BOQUpload for write users", async () => {
    await renderPage();
    await screen.findByTestId("project-detail");
    await user.click(screen.getByRole("tab", { name: /BOQs/i }));
    expect(screen.getByTestId("boq-upload")).toBeInTheDocument();
  });

  it("hides BOQUpload for viewer users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage();
    await screen.findByTestId("project-detail");
    await user.click(screen.getByRole("tab", { name: /BOQs/i }));
    expect(screen.queryByTestId("boq-upload")).not.toBeInTheDocument();
  });
});
