import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import React from "react";
import { AgreementsPage } from "@/pages/AgreementsPage";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: { listAgreements: vi.fn(), listClients: vi.fn() },
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => ({ data: { id: "u1", role: "admin", name: "Admin" } }),
}));

vi.mock("@/hooks/useToast", () => ({
  useToast: () => ({ toast: vi.fn() }),
}));

vi.mock("@/components/agreements/AgreementForm", () => ({
  AgreementForm: () => <div data-testid="agreement-form" />,
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter>
      <AgreementsPage />
    </MemoryRouter>,
    {
      wrapper: ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children),
    }
  );
}

const agreements = {
  items: [
    {
      id: "a1",
      reference_id: "SWA-2025-SA-001",
      client_id: "c1",
      inquiry_id: null,
      service_name: "INSUDESIGN",
      start_date: "2025-01-01",
      end_date: null,
      total_tokens: 10,
      status: "Active",
      notes: null,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    },
  ],
  total: 1,
  page: 1,
  page_size: 20,
};

describe("AgreementsPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and agreement rows", async () => {
    vi.mocked(api.listAgreements).mockResolvedValue(agreements);
    renderPage();
    expect(
      screen.getByRole("heading", { name: /service agreements/i })
    ).toBeInTheDocument();
    expect(await screen.findByText("INSUDESIGN")).toBeInTheDocument();
    await waitFor(() => expect(api.listAgreements).toHaveBeenCalled());
  });

  it("shows empty state when no agreements", async () => {
    vi.mocked(api.listAgreements).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 });
    renderPage();
    await waitFor(() => expect(api.listAgreements).toHaveBeenCalled());
    expect(screen.queryByText("INSUDESIGN")).not.toBeInTheDocument();
  });
});
