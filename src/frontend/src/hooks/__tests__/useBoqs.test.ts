import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { useBoqs, useBoq, useBoqItems, useUploadBoq, useDeleteBoq } from "../useBoqs";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listBoqs: vi.fn(),
    getBoq: vi.fn(),
    getBoqItems: vi.fn(),
    uploadBoq: vi.fn(),
    deleteBoq: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockBoq = {
  id: "boq-1",
  project_id: "proj-1",
  version_number: 1,
  file_name: "boq.xlsx",
  parsed_at: "2025-01-01T00:00:00Z",
  parsed_by: null,
  notes: null,
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
};

const mockBoqItem = {
  id: "item-1",
  boq_id: "boq-1",
  line_number: 1,
  category: "Civil",
  description: "Excavation",
  specification: null,
  unit: "cum",
  quantity: 10,
  rate: 500,
  amount: 5000,
};

describe("useBoqs", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated list for project", async () => {
    const response = { items: [mockBoq], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listBoqs).mockResolvedValue(response);

    const { result } = renderHook(() => useBoqs("proj-1", 1, 20), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listBoqs).toHaveBeenCalledWith("proj-1", { page: 1, page_size: 20 });
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useBoqs("", 1, 20), { wrapper: createWrapper() });
    expect(api.listBoqs).not.toHaveBeenCalled();
  });
});

describe("useBoq", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single boq by id", async () => {
    vi.mocked(api.getBoq).mockResolvedValue(mockBoq);

    const { result } = renderHook(() => useBoq("boq-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockBoq);
    expect(api.getBoq).toHaveBeenCalledWith("boq-1");
  });

  it("does not fetch when boqId is empty", () => {
    renderHook(() => useBoq(""), { wrapper: createWrapper() });
    expect(api.getBoq).not.toHaveBeenCalled();
  });
});

describe("useBoqItems", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated items for boq", async () => {
    const response = { items: [mockBoqItem], total: 1, page: 1, page_size: 50 };
    vi.mocked(api.getBoqItems).mockResolvedValue(response);

    const { result } = renderHook(() => useBoqItems("boq-1", 1, 50), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.getBoqItems).toHaveBeenCalledWith("boq-1", { page: 1, page_size: 50 });
  });

  it("does not fetch when boqId is empty", () => {
    renderHook(() => useBoqItems("", 1, 50), { wrapper: createWrapper() });
    expect(api.getBoqItems).not.toHaveBeenCalled();
  });
});

describe("useUploadBoq", () => {
  beforeEach(() => vi.clearAllMocks());

  it("uploads file and invalidates boqs list", async () => {
    const file = new File(["fake"], "boq.xlsx", { type: "application/octet-stream" });
    vi.mocked(api.uploadBoq).mockResolvedValue(mockBoq);

    const { result } = renderHook(() => useUploadBoq(), { wrapper: createWrapper() });

    result.current.mutate({ projectId: "proj-1", file });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.uploadBoq).toHaveBeenCalledWith("proj-1", file, undefined);
  });
});

describe("useDeleteBoq", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes boq by id", async () => {
    vi.mocked(api.deleteBoq).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteBoq(), { wrapper: createWrapper() });

    result.current.mutate("boq-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteBoq).toHaveBeenCalledWith("boq-1", expect.anything());
  });
});
