import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useQuotes,
  useQuote,
  useCreateQuote,
  useUpdateQuote,
  useDeleteQuote,
  useSubmitQuote,
  useApproveQuote,
  useSendQuote,
  useRespondQuote,
  useCloneQuote,
} from "../useQuotes";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listQuotes: vi.fn(),
    getQuote: vi.fn(),
    createQuote: vi.fn(),
    updateQuote: vi.fn(),
    deleteQuote: vi.fn(),
    submitQuote: vi.fn(),
    approveQuote: vi.fn(),
    sendQuote: vi.fn(),
    respondQuote: vi.fn(),
    cloneQuote: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockQuote = {
  id: "quote-1",
  project_id: "proj-1",
  boq_id: "boq-1",
  version_number: 1,
  status: "draft" as const,
  subtotal: 100000,
  markup_percent: 10,
  markup_amount: 10000,
  tax_percent: 18,
  tax_amount: 19800,
  total_amount: 129800,
  terms: null,
  validity_days: 30,
  valid_until: null,
  created_by_name: null,
  approved_by_name: null,
  approved_at: null,
  sent_at: null,
  client_response: null,
  client_response_at: null,
  client_response_notes: null,
  created_at: "2025-01-01T00:00:00Z",
};

describe("useQuotes", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches quotes for project", async () => {
    const response = { items: [mockQuote], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listQuotes).mockResolvedValue(response);

    const { result } = renderHook(() => useQuotes("proj-1", 1, 20), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listQuotes).toHaveBeenCalledWith("proj-1", { page: 1, page_size: 20 });
  });
});

describe("useQuote", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single quote by id", async () => {
    vi.mocked(api.getQuote).mockResolvedValue(mockQuote);

    const { result } = renderHook(() => useQuote("quote-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockQuote);
    expect(api.getQuote).toHaveBeenCalledWith("quote-1");
  });

  it("does not fetch when quoteId is empty", () => {
    renderHook(() => useQuote(""), { wrapper: createWrapper() });
    expect(api.getQuote).not.toHaveBeenCalled();
  });
});

describe("useCreateQuote", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates quote with boq_id and markup", async () => {
    vi.mocked(api.createQuote).mockResolvedValue(mockQuote);

    const { result } = renderHook(() => useCreateQuote(), { wrapper: createWrapper() });

    result.current.mutate({
      projectId: "proj-1",
      data: { boq_id: "boq-1", markup_percent: 10, tax_percent: 18 },
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createQuote).toHaveBeenCalledWith("proj-1", {
      boq_id: "boq-1",
      markup_percent: 10,
      tax_percent: 18,
    });
  });
});

describe("useUpdateQuote", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates quote by id", async () => {
    vi.mocked(api.updateQuote).mockResolvedValue({ ...mockQuote, terms: "Updated" });

    const { result } = renderHook(() => useUpdateQuote(), { wrapper: createWrapper() });

    result.current.mutate({ id: "quote-1", data: { terms: "Updated" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateQuote).toHaveBeenCalledWith("quote-1", { terms: "Updated" });
  });
});

describe("useDeleteQuote", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes quote and returns projectId", async () => {
    vi.mocked(api.deleteQuote).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteQuote(), { wrapper: createWrapper() });

    result.current.mutate({ id: "quote-1", projectId: "proj-1" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteQuote).toHaveBeenCalledWith("quote-1");
  });
});

describe("useSubmitQuote", () => {
  beforeEach(() => vi.clearAllMocks());

  it("submits quote by id", async () => {
    vi.mocked(api.submitQuote).mockResolvedValue({ ...mockQuote, status: "pending_approval" });

    const { result } = renderHook(() => useSubmitQuote(), { wrapper: createWrapper() });

    result.current.mutate("quote-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.submitQuote).toHaveBeenCalledWith("quote-1", expect.anything());
  });
});

describe("useApproveQuote", () => {
  beforeEach(() => vi.clearAllMocks());

  it("approves quote by id", async () => {
    vi.mocked(api.approveQuote).mockResolvedValue({ ...mockQuote, status: "approved" });

    const { result } = renderHook(() => useApproveQuote(), { wrapper: createWrapper() });

    result.current.mutate("quote-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.approveQuote).toHaveBeenCalledWith("quote-1", expect.anything());
  });
});

describe("useSendQuote", () => {
  beforeEach(() => vi.clearAllMocks());

  it("sends quote by id", async () => {
    vi.mocked(api.sendQuote).mockResolvedValue({ ...mockQuote, status: "sent" });

    const { result } = renderHook(() => useSendQuote(), { wrapper: createWrapper() });

    result.current.mutate("quote-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.sendQuote).toHaveBeenCalledWith("quote-1", expect.anything());
  });
});

describe("useRespondQuote", () => {
  beforeEach(() => vi.clearAllMocks());

  it("responds to quote (accepted)", async () => {
    vi.mocked(api.respondQuote).mockResolvedValue({ ...mockQuote, status: "accepted" });

    const { result } = renderHook(() => useRespondQuote(), { wrapper: createWrapper() });

    result.current.mutate({ id: "quote-1", data: { response: "accepted", notes: "Good" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.respondQuote).toHaveBeenCalledWith("quote-1", { response: "accepted", notes: "Good" });
  });
});

describe("useCloneQuote", () => {
  beforeEach(() => vi.clearAllMocks());

  it("clones quote and returns projectId", async () => {
    vi.mocked(api.cloneQuote).mockResolvedValue({ quote: mockQuote, projectId: "proj-1" });

    const { result } = renderHook(() => useCloneQuote(), { wrapper: createWrapper() });

    result.current.mutate({ id: "quote-1", projectId: "proj-1" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.cloneQuote).toHaveBeenCalledWith("quote-1");
  });
});
