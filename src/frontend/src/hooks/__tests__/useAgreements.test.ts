import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useAgreements,
  useAgreement,
  useCreateAgreement,
  useUpdateAgreement,
  useDeleteAgreement,
} from "../useAgreements";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listAgreements: vi.fn(),
    getAgreement: vi.fn(),
    createAgreement: vi.fn(),
    updateAgreement: vi.fn(),
    deleteAgreement: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockAgreement = {
  id: "agr-1",
  reference_id: "SWA-2025-AGR-001",
  client_id: "client-1",
  inquiry_id: null,
  service_name: "Annual Maintenance",
  start_date: "2025-01-01",
  end_date: null,
  total_tokens: 12,
  status: "Active",
  notes: null,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
};

describe("useAgreements", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated list", async () => {
    const response = { items: [mockAgreement], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listAgreements).mockResolvedValue(response);

    const { result } = renderHook(() => useAgreements({ page: 1, page_size: 20 }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listAgreements).toHaveBeenCalledWith({ page: 1, page_size: 20 });
  });
});

describe("useAgreement", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single agreement by id", async () => {
    vi.mocked(api.getAgreement).mockResolvedValue(mockAgreement);

    const { result } = renderHook(() => useAgreement("agr-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockAgreement);
    expect(api.getAgreement).toHaveBeenCalledWith("agr-1");
  });

  it("does not fetch when id is undefined", () => {
    renderHook(() => useAgreement(undefined), { wrapper: createWrapper() });
    expect(api.getAgreement).not.toHaveBeenCalled();
  });
});

describe("useCreateAgreement", () => {
  beforeEach(() => vi.clearAllMocks());

  it("posts agreement and invalidates list", async () => {
    vi.mocked(api.createAgreement).mockResolvedValue(mockAgreement);

    const { result } = renderHook(() => useCreateAgreement(), { wrapper: createWrapper() });

    result.current.mutate({ client_id: "client-1", service_name: "Maintenance", start_date: "2025-01-01" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createAgreement).toHaveBeenCalledWith({
      client_id: "client-1",
      service_name: "Maintenance",
      start_date: "2025-01-01",
    });
  });
});

describe("useUpdateAgreement", () => {
  beforeEach(() => vi.clearAllMocks());

  it("patches agreement by id", async () => {
    vi.mocked(api.updateAgreement).mockResolvedValue({ ...mockAgreement, notes: "Updated" });

    const { result } = renderHook(() => useUpdateAgreement(), { wrapper: createWrapper() });

    result.current.mutate({ id: "agr-1", data: { notes: "Updated" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateAgreement).toHaveBeenCalledWith("agr-1", { notes: "Updated" });
  });
});

describe("useDeleteAgreement", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes agreement by id", async () => {
    vi.mocked(api.deleteAgreement).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteAgreement(), { wrapper: createWrapper() });

    result.current.mutate("agr-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteAgreement).toHaveBeenCalledWith("agr-1");
  });
});
