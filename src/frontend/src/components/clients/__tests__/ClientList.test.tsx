import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { ClientList } from "../ClientList";
import { api } from "@/lib/api";
import type { Client } from "@/types/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/lib/api", () => ({
  api: {
    listClients: vi.fn(),
  },
}));

const client: Client = {
  id: "client-1",
  name: "Acme Corp",
  code: "AC-001",
  address: null,
  city: "Mumbai",
  state: null,
  pincode: null,
  country: "IN",
  gst_number: null,
  primary_email: "ops@acme.com",
  primary_phone: null,
  notes: null,
  is_active: true,
  industry: "Construction",
  client_status: "Active",
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  contacts: [],
};

function createWrapper() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

function renderList(role: string | undefined) {
  useCurrentUserMock.mockReturnValue({ data: role ? { role } : undefined });
  return render(
    <MemoryRouter>
      <ClientList />
    </MemoryRouter>,
    { wrapper: createWrapper() }
  );
}

const response = (items: Client[]) => ({ items, total: items.length, page: 1, page_size: 20 });

describe("ClientList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows New Client button for pm and hides it for viewers", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    vi.mocked(api.listClients).mockResolvedValue(response([]));
    const { unmount } = renderList("pm");
    await waitFor(() => expect(screen.getByRole("link", { name: /new client/i })).toBeInTheDocument());
    unmount();

    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    vi.mocked(api.listClients).mockResolvedValue(response([]));
    renderList("viewer");
    await waitFor(() =>
      expect(screen.queryByRole("link", { name: /new client/i })).not.toBeInTheDocument()
    );
  });

  it("renders clients in a table with open links", async () => {
    vi.mocked(api.listClients).mockResolvedValue(response([client]));
    renderList("pm");

    expect(await screen.findByText("Acme Corp")).toBeInTheDocument();
    expect(screen.getByText("AC-001")).toBeInTheDocument();
    expect(screen.getByText("Construction")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open" })).toHaveAttribute("href", "/clients/client-1");
  });

  it("renders empty state with CTA for pm", async () => {
    vi.mocked(api.listClients).mockResolvedValue(response([]));
    renderList("pm");

    expect(await screen.findByText(/no clients yet/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /add the first client/i })).toBeInTheDocument();
  });

  it("renders empty state asking for admin/PM for viewer", async () => {
    vi.mocked(api.listClients).mockResolvedValue(response([]));
    renderList("viewer");

    expect(await screen.findByText(/ask an admin or pm to add one/i)).toBeInTheDocument();
  });

  it("shows error banner and retries", async () => {
    const user = userEvent.setup();
    vi.mocked(api.listClients).mockRejectedValueOnce(new Error("network down"));
    vi.mocked(api.listClients).mockResolvedValue(response([client]));
    renderList("pm");

    expect(await screen.findByText("Failed to load clients")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findByText("Acme Corp")).toBeInTheDocument();
  });

  it("paginates and shows total count", async () => {
    const user = userEvent.setup();
    vi.mocked(api.listClients).mockResolvedValue({ items: [client], total: 45, page: 1, page_size: 20 });
    renderList("pm");

    await waitFor(() => expect(screen.getByText("45 clients")).toBeInTheDocument());
    expect(screen.getByText("Page 1 of 3")).toBeInTheDocument();
    expect(screen.getAllByRole("button")[0]).toBeDisabled();

    const nextButton = screen.getAllByRole("button")[1];
    await user.click(nextButton);
    await waitFor(() => expect(api.listClients).toHaveBeenLastCalledWith({ page: 2, page_size: 20, q: undefined }));
  });
});