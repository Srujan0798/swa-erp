import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useStandards,
  useChecklistItems,
  useComplianceSummary,
  useComplianceItems,
  useUpdateComplianceItem,
  useReviewComplianceItem,
  useBulkCreateItems,
} from "../useCompliance";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listStandards: vi.fn(),
    getChecklistItems: vi.fn(),
    getComplianceSummary: vi.fn(),
    listComplianceItems: vi.fn(),
    updateComplianceItem: vi.fn(),
    reviewComplianceItem: vi.fn(),
    bulkCreateComplianceItems: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockStandard = { id: "std-1", name: "NBC 2016", code: "NBC" };

const mockChecklistItem = {
  id: "item-1",
  standard_id: "std-1",
  clause: "Fire safety",
  description: "Provide fire extinguishers",
  category: "Fire",
  is_mandatory: true,
}

const mockComplianceSummary = {
  total_items: 10,
  compliant: 7,
  non_compliant: 2,
  pending: 1,
};

const mockComplianceItem = {
  id: "ci-1",
  project_id: "proj-1",
  standard_id: "std-1",
  clause: "Fire safety",
  description: "Provide fire extinguishers",
  category: "Fire",
  status: "Pending",
  notes: null,
  evidence_document_id: null,
};

const mockComplianceItemUpdate = { id: "ci-1", ...mockComplianceItem, status: "Compliant" };

describe("useStandards", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches compliance standards", async () => {
    vi.mocked(api.listStandards).mockResolvedValue([mockStandard]);

    const { result } = renderHook(() => useStandards(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([mockStandard]);
    expect(api.listStandards).toHaveBeenCalled();
  });
});

describe("useChecklistItems", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches checklist items for a standard", async () => {
    vi.mocked(api.getChecklistItems).mockResolvedValue([mockChecklistItem]);

    const { result } = renderHook(() => useChecklistItems("std-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([mockChecklistItem]);
    expect(api.getChecklistItems).toHaveBeenCalledWith("std-1");
  });

  it("does not fetch when standardId is empty", () => {
    renderHook(() => useChecklistItems(""), { wrapper: createWrapper() });
    expect(api.getChecklistItems).not.toHaveBeenCalled();
  });
});

describe("useComplianceSummary", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches compliance summary for project", async () => {
    vi.mocked(api.getComplianceSummary).mockResolvedValue(mockComplianceSummary);

    const { result } = renderHook(() => useComplianceSummary("proj-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockComplianceSummary);
    expect(api.getComplianceSummary).toHaveBeenCalledWith("proj-1");
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useComplianceSummary(""), { wrapper: createWrapper() });
    expect(api.getComplianceSummary).not.toHaveBeenCalled();
  });
});

describe("useComplianceItems", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches compliance items for project", async () => {
    vi.mocked(api.listComplianceItems).mockResolvedValue([mockComplianceItem]);

    const { result } = renderHook(() => useComplianceItems("proj-1", "std-1"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([mockComplianceItem]);
    expect(api.listComplianceItems).toHaveBeenCalledWith("proj-1", "std-1");
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useComplianceItems("", undefined), { wrapper: createWrapper() });
    expect(api.listComplianceItems).not.toHaveBeenCalled();
  });
});

describe("useUpdateComplianceItem", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates compliance item status", async () => {
    vi.mocked(api.updateComplianceItem).mockResolvedValue(mockComplianceItemUpdate);

    const { result } = renderHook(() => useUpdateComplianceItem(), { wrapper: createWrapper() });

    result.current.mutate({ itemId: "ci-1", data: { status: "Compliant" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateComplianceItem).toHaveBeenCalledWith("ci-1", { status: "Compliant" });
  });

  it("passes notes and evidence_document_id", async () => {
    vi.mocked(api.updateComplianceItem).mockResolvedValue(mockComplianceItemUpdate);

    const { result } = renderHook(() => useUpdateComplianceItem(), { wrapper: createWrapper() });

    result.current.mutate({
      itemId: "ci-1",
      data: { status: "Compliant", notes: "Checked", evidence_document_id: "doc-1" },
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateComplianceItem).toHaveBeenCalledWith("ci-1", {
      status: "Compliant",
      notes: "Checked",
      evidence_document_id: "doc-1",
    });
  });
});

describe("useReviewComplianceItem", () => {
  beforeEach(() => vi.clearAllMocks());

  it("reviews item with notes", async () => {
    vi.mocked(api.reviewComplianceItem).mockResolvedValue(mockComplianceItem);

    const { result } = renderHook(() => useReviewComplianceItem(), { wrapper: createWrapper() });

    result.current.mutate({ itemId: "ci-1", notes: "Reviewed" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.reviewComplianceItem).toHaveBeenCalledWith("ci-1", { notes: "Reviewed" });
  });

  it("reviews item without notes", async () => {
    vi.mocked(api.reviewComplianceItem).mockResolvedValue(mockComplianceItem);

    const { result } = renderHook(() => useReviewComplianceItem(), { wrapper: createWrapper() });

    result.current.mutate({ itemId: "ci-1" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.reviewComplianceItem).toHaveBeenCalledWith("ci-1", undefined);
  });
});

describe("useBulkCreateItems", () => {
  beforeEach(() => vi.clearAllMocks());

  it("bulk creates compliance items", async () => {
    const response = { message: "Created 10 items" };
    vi.mocked(api.bulkCreateComplianceItems).mockResolvedValue(response);

    const { result } = renderHook(() => useBulkCreateItems("proj-1"), { wrapper: createWrapper() });

    result.current.mutate("std-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.bulkCreateComplianceItems).toHaveBeenCalledWith("proj-1", "std-1");
  });
});
