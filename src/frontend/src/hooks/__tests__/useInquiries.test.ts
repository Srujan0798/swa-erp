import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useInquiries,
  useInquiry,
  useCreateInquiry,
  useUpdateInquiry,
  useDeleteInquiry,
  useConvertInquiry,
} from "../useInquiries";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listInquiries: vi.fn(),
    getInquiry: vi.fn(),
    createInquiry: vi.fn(),
    updateInquiry: vi.fn(),
    deleteInquiry: vi.fn(),
    convertInquiry: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockInquiry = {
  id: "inq-1",
  reference_id: "SWA-2025-INQ-001",
  inquiry_date: "2025-01-15",
  inquiry_type: "New Build",
  inquiry_source: "Website",
  client_name: "Acme Corp",
  requirement_summary: "Need green building design",
  estimated_value: 1500000,
  priority: "High",
  status: "New",
  owner_id: null,
  notes: null,
  converted_client_id: null,
  converted_project_id: null,
  created_at: "2025-01-15T00:00:00Z",
  updated_at: "2025-01-15T00:00:00Z",
};

describe("useInquiries", () => {
  beforeEach(() => vi.clearAllMocks());

  it("returns paginated list", async () => {
    const response = { items: [mockInquiry], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listInquiries).mockResolvedValue(response);

    const { result } = renderHook(() => useInquiries({ page: 1, page_size: 20 }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listInquiries).toHaveBeenCalledWith({ page: 1, page_size: 20 });
  });
});

describe("useInquiry", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single inquiry by id", async () => {
    vi.mocked(api.getInquiry).mockResolvedValue(mockInquiry);

    const { result } = renderHook(() => useInquiry("inq-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockInquiry);
    expect(api.getInquiry).toHaveBeenCalledWith("inq-1");
  });

  it("does not fetch when id is undefined", () => {
    renderHook(() => useInquiry(undefined), { wrapper: createWrapper() });
    expect(api.getInquiry).not.toHaveBeenCalled();
  });
});

describe("useCreateInquiry", () => {
  beforeEach(() => vi.clearAllMocks());

  it("calls create with payload", async () => {
    vi.mocked(api.createInquiry).mockResolvedValue(mockInquiry);

    const { result } = renderHook(() => useCreateInquiry(), { wrapper: createWrapper() });

    result.current.mutate({ inquiry_date: "2025-01-15", client_name: "Acme Corp" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createInquiry).toHaveBeenCalledWith({
      inquiry_date: "2025-01-15",
      client_name: "Acme Corp",
    });
  });
});

describe("useUpdateInquiry", () => {
  beforeEach(() => vi.clearAllMocks());

  it("calls PATCH with id and data", async () => {
    vi.mocked(api.updateInquiry).mockResolvedValue({ ...mockInquiry, status: "Contacted" });

    const { result } = renderHook(() => useUpdateInquiry(), { wrapper: createWrapper() });

    result.current.mutate({ id: "inq-1", data: { status: "Contacted" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateInquiry).toHaveBeenCalledWith("inq-1", { status: "Contacted" });
  });
});

describe("useDeleteInquiry", () => {
  beforeEach(() => vi.clearAllMocks());

  it("calls DELETE with id", async () => {
    vi.mocked(api.deleteInquiry).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteInquiry(), { wrapper: createWrapper() });

    result.current.mutate("inq-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteInquiry).toHaveBeenCalledWith("inq-1");
  });
});

describe("useConvertInquiry", () => {
  beforeEach(() => vi.clearAllMocks());

  it("calls POST /convert with payload", async () => {
    const response = {
      inquiry: { ...mockInquiry, status: "Converted" },
      client_id: "client-1",
      project_id: "project-1",
    };
    vi.mocked(api.convertInquiry).mockResolvedValue(response);

    const { result } = renderHook(() => useConvertInquiry(), { wrapper: createWrapper() });

    result.current.mutate({
      id: "inq-1",
      payload: { project_name: "Acme Project" },
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.convertInquiry).toHaveBeenCalledWith("inq-1", { project_name: "Acme Project" });
  });
});
