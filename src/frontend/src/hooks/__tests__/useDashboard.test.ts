import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { useDashboard, useProjects, useClients } from "../useDashboard";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    getProjectStats: vi.fn(),
    listProjects: vi.fn(),
    listClients: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockStats = {
  total_active: 5,
  by_status: { Lead: 1, Quote: 1, Awarded: 1, Design: 1, Closed: 1, Execution: 0, Vendor: 0, Validation: 0 },
  total_estimated_value: 5000000,
};

const mockProject = {
  id: "proj-1",
  client_id: "client-1",
  name: "Project Alpha",
  code: "PROJ-001",
  description: null,
  status: "Design" as const,
  pm_id: null,
  designer_id: null,
  auditor_id: null,
  location: "Mumbai",
  estimated_value: 1000000,
  actual_value: null,
  start_date: null,
  target_end_date: null,
  actual_end_date: null,
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  client_name: "Acme Corp",
  pm_name: null,
  designer_name: null,
  auditor_name: null,
};

const mockClient = {
  id: "client-1",
  name: "Acme Corp",
  code: "CL-001",
  address: null,
  city: null,
  state: null,
  pincode: null,
  country: "India",
  gst_number: null,
  primary_email: "test@acme.com",
  primary_phone: null,
  notes: null,
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  contacts: [],
};

describe("useDashboard", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches project stats", async () => {
    vi.mocked(api.getProjectStats).mockResolvedValue(mockStats);

    const { result } = renderHook(() => useDashboard(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockStats);
    expect(api.getProjectStats).toHaveBeenCalled();
  });
});

describe("useProjects", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated projects with default params", async () => {
    const response = { items: [mockProject], total: 1, page: 1, page_size: 5 };
    vi.mocked(api.listProjects).mockResolvedValue(response);

    const { result } = renderHook(() => useProjects(1, 5), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listProjects).toHaveBeenCalledWith({ page: 1, page_size: 5 });
  });
});

describe("useClients", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated clients with default params", async () => {
    const response = { items: [mockClient], total: 1, page: 1, page_size: 5 };
    vi.mocked(api.listClients).mockResolvedValue(response);

    const { result } = renderHook(() => useClients(1, 5), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listClients).toHaveBeenCalledWith({ page: 1, page_size: 5 });
  });
});
