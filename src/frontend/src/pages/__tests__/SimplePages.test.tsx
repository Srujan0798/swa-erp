import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import React from "react";
import { ProjectsPage } from "@/pages/ProjectsPage";
import { ClientsPage } from "@/pages/ClientsPage";
import { VendorsPage } from "@/pages/VendorsPage";
import { api } from "@/lib/api";

const useProjectsMock = vi.hoisted(() => vi.fn());
const useClientsMock = vi.hoisted(() => vi.fn());
const useVendorsMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useProjects", () => ({
  useProjects: () => useProjectsMock(),
}));

vi.mock("@/hooks/useClients", () => ({
  useClients: () => useClientsMock(),
}));

vi.mock("@/hooks/useVendors", () => ({
  useVendors: () => useVendorsMock(),
}));

vi.mock("@/lib/api", () => ({
  api: {
    listProjects: vi.fn(),
    listClients: vi.fn(),
    listVendors: vi.fn(),
  },
}));

function createWrapper() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>, { wrapper: createWrapper() });
}

const project = {
  id: "p1",
  code: "PRJ-001",
  name: "Acme Office",
  client_name: "Acme Corp",
  status: "Execution",
  pm_name: "Bob",
  location: "Mumbai",
};

const client = {
  id: "c1",
  name: "Acme Corp",
  code: "AC-001",
  primary_email: "billing@acme.com",
  city: "Mumbai",
  country: "India",
  status: "active",
};

const vendor = {
  id: "v1",
  name: "Acme Vendor",
  code: "AV-001",
  primary_email: "vendor@acme.com",
  city: "Mumbai",
  country: "India",
  status: "active",
};

describe("ProjectsPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders ProjectList component", () => {
    useProjectsMock.mockReturnValue({ data: { items: [project], total: 1 }, isLoading: false });
    vi.mocked(api.listProjects).mockResolvedValue({ items: [project], total: 1 } as never);
    renderWithRouter(<ProjectsPage />);
    expect(screen.getByText("Projects")).toBeInTheDocument();
  });
});

describe("ClientsPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders ClientList component", () => {
    useClientsMock.mockReturnValue({ data: { items: [client], total: 1 }, isLoading: false });
    vi.mocked(api.listClients).mockResolvedValue({ items: [client], total: 1 } as never);
    renderWithRouter(<ClientsPage />);
    expect(screen.getByText("Clients")).toBeInTheDocument();
  });
});

describe("VendorsPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders VendorList component", () => {
    useVendorsMock.mockReturnValue({ data: { items: [vendor], total: 1 }, isLoading: false });
    vi.mocked(api.listVendors).mockResolvedValue({ items: [vendor], total: 1 } as never);
    renderWithRouter(<VendorsPage />);
    expect(screen.getByText("Vendors")).toBeInTheDocument();
  });
});