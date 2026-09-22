import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import React from "react";
import { DocumentReferencesPage } from "@/pages/DocumentReferencesPage";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: { listDocumentReferences: vi.fn(), getDocumentReferenceCounters: vi.fn() },
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => ({ data: { id: "u1", role: "admin", name: "Admin" } }),
}));

vi.mock("@/hooks/useToast", () => ({
  useToast: () => ({ toast: vi.fn() }),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter>
      <DocumentReferencesPage />
    </MemoryRouter>,
    {
      wrapper: ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children),
    }
  );
}

const refs = {
  items: [
    {
      id: "d1",
      reference_id: "SWA-2025-DBR-001",
      project_id: "p1",
      token_id: null,
      doc_date: "2025-01-15",
      document_type: "Drawing",
      type: "Architectural",
      author_id: null,
      author_name: null,
      user_ref: null,
      description: "Floor plan",
      revision: "A1",
      status: "Issued",
      remarks: null,
      created_at: "2025-01-15T00:00:00Z",
      updated_at: "2025-01-15T00:00:00Z",
    },
  ],
  total: 1,
  page: 1,
  page_size: 20,
};

describe("DocumentReferencesPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and reference rows", async () => {
    vi.mocked(api.listDocumentReferences).mockResolvedValue(refs);
    vi.mocked(api.getDocumentReferenceCounters).mockResolvedValue({
      year: 2025,
      dbr_kdr_last_seq: 1,
      dbr_kdr_next_preview: "SWA-2025-DBR-002",
      note: "",
    });
    renderPage();
    expect(
      screen.getByRole("heading", { name: /document references/i })
    ).toBeInTheDocument();
    expect(await screen.findByText("SWA-2025-DBR-001")).toBeInTheDocument();
    await waitFor(() => expect(api.listDocumentReferences).toHaveBeenCalled());
  });

  it("shows error banner when list fails", async () => {
    vi.mocked(api.listDocumentReferences).mockRejectedValue(new Error("down"));
    vi.mocked(api.getDocumentReferenceCounters).mockResolvedValue({
      year: 2025,
      dbr_kdr_last_seq: 0,
      dbr_kdr_next_preview: "SWA-2025-DBR-001",
      note: "",
    });
    renderPage();
    await waitFor(() => expect(api.listDocumentReferences).toHaveBeenCalled());
  });
});
