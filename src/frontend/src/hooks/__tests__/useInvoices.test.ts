import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useProjectInvoices,
  useInvoice,
  useCreateInvoice,
  useGenerateInvoiceFromTime,
  useUpdateInvoiceStatus,
  useDeleteInvoice,
} from "../useInvoices";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listProjectInvoices: vi.fn(),
    getInvoice: vi.fn(),
    createInvoice: vi.fn(),
    generateInvoiceFromTime: vi.fn(),
    updateInvoiceStatus: vi.fn(),
    deleteInvoice: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockInvoice = {
  id: "inv-1",
  project_id: "proj-1",
  invoice_number: "SWA-INV-001",
  status: "draft" as const,
  subtotal: 100000,
  tax_amount: 18000,
  total_amount: 118000,
  currency: "INR",
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  lines: [],
};

describe("useProjectInvoices", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches invoices for project", async () => {
    const response = { items: [mockInvoice], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listProjectInvoices).mockResolvedValue(response);

    const { result } = renderHook(() => useProjectInvoices("proj-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listProjectInvoices).toHaveBeenCalledWith("proj-1", { status: undefined });
  });

  it("passes status filter", async () => {
    const response = { items: [mockInvoice], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listProjectInvoices).mockResolvedValue(response);

    const { result } = renderHook(() => useProjectInvoices("proj-1", "paid"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.listProjectInvoices).toHaveBeenCalledWith("proj-1", { status: "paid" });
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useProjectInvoices(""), { wrapper: createWrapper() });
    expect(api.listProjectInvoices).not.toHaveBeenCalled();
  });
});

describe("useInvoice", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single invoice by id", async () => {
    vi.mocked(api.getInvoice).mockResolvedValue(mockInvoice);

    const { result } = renderHook(() => useInvoice("inv-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockInvoice);
    expect(api.getInvoice).toHaveBeenCalledWith("inv-1");
  });

  it("does not fetch when id is empty", () => {
    renderHook(() => useInvoice(""), { wrapper: createWrapper() });
    expect(api.getInvoice).not.toHaveBeenCalled();
  });
});

describe("useCreateInvoice", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates invoice and invalidates list", async () => {
    vi.mocked(api.createInvoice).mockResolvedValue(mockInvoice);

    const { result } = renderHook(() => useCreateInvoice(), { wrapper: createWrapper() });

    result.current.mutate({ projectId: "proj-1", data: { lines: [], currency: "INR" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createInvoice).toHaveBeenCalledWith("proj-1", { lines: [], currency: "INR" });
  });
});

describe("useGenerateInvoiceFromTime", () => {
  beforeEach(() => vi.clearAllMocks());

  it("generates invoice from time entries", async () => {
    vi.mocked(api.generateInvoiceFromTime).mockResolvedValue(mockInvoice);

    const { result } = renderHook(() => useGenerateInvoiceFromTime(), { wrapper: createWrapper() });

    result.current.mutate({ projectId: "proj-1", startDate: "2025-01-01", endDate: "2025-01-31" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.generateInvoiceFromTime).toHaveBeenCalledWith("proj-1", "2025-01-01", "2025-01-31");
  });
});

describe("useUpdateInvoiceStatus", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates invoice status", async () => {
    vi.mocked(api.updateInvoiceStatus).mockResolvedValue({ ...mockInvoice, status: "sent" });

    const { result } = renderHook(() => useUpdateInvoiceStatus(), { wrapper: createWrapper() });

    result.current.mutate({ id: "inv-1", status: "sent" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateInvoiceStatus).toHaveBeenCalledWith("inv-1", "sent");
  });
});

describe("useDeleteInvoice", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes invoice by id", async () => {
    vi.mocked(api.deleteInvoice).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteInvoice(), { wrapper: createWrapper() });

    result.current.mutate("inv-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteInvoice).toHaveBeenCalledWith("inv-1");
  });
});
