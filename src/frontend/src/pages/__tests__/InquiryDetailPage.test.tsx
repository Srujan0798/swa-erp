import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import React from "react";
import { InquiryDetailPage } from "@/pages/InquiryDetailPage";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    getInquiry: vi.fn(),
    updateInquiry: vi.fn(),
    deleteInquiry: vi.fn(),
    convertInquiry: vi.fn(),
  },
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
    <MemoryRouter initialEntries={["/inquiries/i1"]}>
      <Routes>
        <Route path="/inquiries/:id" element={<InquiryDetailPage />} />
      </Routes>
    </MemoryRouter>,
    {
      wrapper: ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children),
    }
  );
}

const inquiry = {
  id: "i1",
  reference_id: "SWA-2025-INQ-001",
  inquiry_date: "2025-01-15",
  inquiry_type: "New Build",
  inquiry_source: "Website",
  client_name: "Acme Corp",
  requirement_summary: "Need design",
  estimated_value: 1500000,
  priority: "High",
  status: "New",
  owner_id: null,
  technical_lead: null,
  notes: null,
  converted_client_id: null,
  converted_project_id: null,
  created_at: "2025-01-15T00:00:00Z",
  updated_at: "2025-01-15T00:00:00Z",
};

describe("InquiryDetailPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders inquiry once loaded", async () => {
    vi.mocked(api.getInquiry).mockResolvedValue(inquiry);
    renderPage();
    expect(await screen.findAllByText("Acme Corp")).not.toHaveLength(0);
    await waitFor(() => expect(api.getInquiry).toHaveBeenCalledWith("i1"));
  });

  it("shows not-found state when inquiry missing", async () => {
    vi.mocked(api.getInquiry).mockRejectedValue(new Error("gone"));
    renderPage();
    expect(await screen.findByText(/inquiry not found/i)).toBeInTheDocument();
  });
});
