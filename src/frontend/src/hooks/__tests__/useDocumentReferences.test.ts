import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useDocumentReferences,
  useDocumentReference,
  useCreateDocumentReference,
  useUpdateDocumentReference,
  useDeleteDocumentReference,
} from "../useDocumentReferences";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listDocumentReferences: vi.fn(),
    getDocumentReference: vi.fn(),
    createDocumentReference: vi.fn(),
    updateDocumentReference: vi.fn(),
    deleteDocumentReference: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockDocRef = {
  id: "docref-1",
  reference_id: "SWA-DOC-001",
  project_id: "proj-1",
  token_id: null,
  doc_date: "2025-01-15",
  document_type: "Drawing",
  type: "Architectural",
  author_id: null,
  user_ref: null,
  description: "Floor plan",
  revision: "A1",
  status: "Issued",
  remarks: null,
  created_at: "2025-01-15T00:00:00Z",
  updated_at: "2025-01-15T00:00:00Z",
};

describe("useDocumentReferences", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated document references", async () => {
    const response = { items: [mockDocRef], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listDocumentReferences).mockResolvedValue(response);

    const { result } = renderHook(() => useDocumentReferences({ page: 1, page_size: 20 }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listDocumentReferences).toHaveBeenCalledWith({ page: 1, page_size: 20 });
  });
});

describe("useDocumentReference", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single document reference by id", async () => {
    vi.mocked(api.getDocumentReference).mockResolvedValue(mockDocRef);

    const { result } = renderHook(() => useDocumentReference("docref-1"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockDocRef);
    expect(api.getDocumentReference).toHaveBeenCalledWith("docref-1");
  });

  it("does not fetch when id is undefined", () => {
    renderHook(() => useDocumentReference(undefined), { wrapper: createWrapper() });
    expect(api.getDocumentReference).not.toHaveBeenCalled();
  });
});

describe("useCreateDocumentReference", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates document reference and invalidates lists", async () => {
    vi.mocked(api.createDocumentReference).mockResolvedValue(mockDocRef);

    const { result } = renderHook(() => useCreateDocumentReference(), { wrapper: createWrapper() });

    result.current.mutate({
      project_id: "proj-1",
      doc_date: "2025-01-15",
      document_type: "Drawing",
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createDocumentReference).toHaveBeenCalledWith({
      project_id: "proj-1",
      doc_date: "2025-01-15",
      document_type: "Drawing",
    });
  });
});

describe("useUpdateDocumentReference", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates document reference by id", async () => {
    vi.mocked(api.updateDocumentReference).mockResolvedValue({ ...mockDocRef, status: "Approved" });

    const { result } = renderHook(() => useUpdateDocumentReference(), { wrapper: createWrapper() });

    result.current.mutate({ id: "docref-1", data: { status: "Approved" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateDocumentReference).toHaveBeenCalledWith("docref-1", { status: "Approved" });
  });
});

describe("useDeleteDocumentReference", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes document reference by id", async () => {
    vi.mocked(api.deleteDocumentReference).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteDocumentReference(), { wrapper: createWrapper() });

    result.current.mutate("docref-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteDocumentReference).toHaveBeenCalledWith("docref-1");
  });
});
