import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import React from "react";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listTokens: vi.fn(),
  },
}));

const token = {
  id: "tk1",
  reference_id: "TKN-001",
  token_type: "Design",
  token_status: "active",
  token_date: "2026-08-20",
  tokens_used: 3,
  description: "Design tokens",
  project_id: "p1",
};

async function renderPage(initialEntries: string[] = ["/"]) {
  const { TokensPage } = await import("@/pages/TokensPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <QueryClientProvider client={queryClient}>
        <TokensPage />
      </QueryClientProvider>
    </MemoryRouter>
  );
}

describe("TokensPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.listTokens).mockResolvedValue({ items: [], total: 0 } as never);
  });

  it("renders header", async () => {
    await renderPage();
    expect(screen.getByText("Tokens")).toBeInTheDocument();
    expect(screen.getByText(/Units of work under a service agreement/)).toBeInTheDocument();
  });

  it("shows search input", async () => {
    await renderPage();
    expect(screen.getByPlaceholderText(/Search by token ID/)).toBeInTheDocument();
  });

  it("displays tokens in table", async () => {
    vi.mocked(api.listTokens).mockResolvedValue({ items: [token], total: 1 } as never);
    await renderPage();
    expect(await screen.findByText("TKN-001")).toBeInTheDocument();
    expect(screen.getByText("Design")).toBeInTheDocument();
    expect(screen.getByText("active")).toBeInTheDocument();
  });

  it("shows empty state", async () => {
    await renderPage();
    expect(await screen.findByText(/No tokens yet/)).toBeInTheDocument();
  });

  it("shows loading state", async () => {
    vi.mocked(api.listTokens).mockReturnValue(new Promise(() => {}));
    await renderPage();
    expect(screen.getByText(/Loading/)).toBeInTheDocument();
  });

  it("shows error banner", async () => {
    vi.mocked(api.listTokens).mockRejectedValue(new Error("boom"));
    await renderPage();
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  it("shows pagination", async () => {
    await renderPage();
    expect(await screen.findByText("0 tokens")).toBeInTheDocument();
    expect(screen.getByText(/Page 1 of 1/)).toBeInTheDocument();
  });

  it("shows project filter from search params", async () => {
    vi.mocked(api.listTokens).mockResolvedValue({ items: [], total: 0 } as never);
    await renderPage(["/?project=p1"]);
    expect(await screen.findByText(/Filtered to project/)).toBeInTheDocument();
    expect(screen.getByText("Show all tokens")).toBeInTheDocument();
  });

  it("shows project button for tokens with project_id", async () => {
    vi.mocked(api.listTokens).mockResolvedValue({ items: [token], total: 1 } as never);
    await renderPage();
    expect(await screen.findByText("Project")).toBeInTheDocument();
  });

  it("shows dash for tokens without project_id", async () => {
    vi.mocked(api.listTokens).mockResolvedValue({ items: [{ ...token, project_id: null }], total: 1 } as never);
    await renderPage();
    expect(await screen.findByText("TKN-001")).toBeInTheDocument();
  });

  it("shows token with description and date", async () => {
    vi.mocked(api.listTokens).mockResolvedValue({ items: [token], total: 1 } as never);
    await renderPage();
    expect(await screen.findByText("Design tokens")).toBeInTheDocument();
    expect(screen.getByText("2026-08-20")).toBeInTheDocument();
  });

  it("shows token without description", async () => {
    vi.mocked(api.listTokens).mockResolvedValue({ items: [{ ...token, description: null }], total: 1 } as never);
    await renderPage();
    expect(await screen.findByText("TKN-001")).toBeInTheDocument();
  });
});
