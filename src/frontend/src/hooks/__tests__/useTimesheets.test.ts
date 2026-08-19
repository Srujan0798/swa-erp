import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useTimesheets,
  useTimesheet,
  useGenerateTimesheet,
  useSubmitTimesheet,
  useApproveTimesheet,
  useRejectTimesheet,
} from "../useTimesheets";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listTimesheets: vi.fn(),
    getTimesheet: vi.fn(),
    generateTimesheet: vi.fn(),
    submitTimesheet: vi.fn(),
    approveTimesheet: vi.fn(),
    rejectTimesheet: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockTimesheet = {
  id: "ts-1",
  user_id: "user-1",
  project_id: null,
  week_start: "2025-01-13",
  week_end: "2025-01-19",
  total_hours: 40,
  billable_hours: 35,
  non_billable_hours: 5,
  status: "Draft" as const,
  submitted_at: null,
  approved_at: null,
  approved_by: null,
  created_at: "2025-01-13T00:00:00Z",
  updated_at: "2025-01-13T00:00:00Z",
};

const mockListResponse = { items: [mockTimesheet], total: 1, page: 1, page_size: 20 };

describe("useTimesheets", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches timesheets with status filter", async () => {
    vi.mocked(api.listTimesheets).mockResolvedValue(mockListResponse);

    const { result } = renderHook(() => useTimesheets({ status: "Draft" }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockListResponse);
    expect(api.listTimesheets).toHaveBeenCalledWith({ status: "Draft" });
  });

  it("fetches without filters", async () => {
    vi.mocked(api.listTimesheets).mockResolvedValue(mockListResponse);

    const { result } = renderHook(() => useTimesheets(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.listTimesheets).toHaveBeenCalledWith(undefined);
  });
});

describe("useTimesheet", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single timesheet by id", async () => {
    vi.mocked(api.getTimesheet).mockResolvedValue(mockTimesheet);

    const { result } = renderHook(() => useTimesheet("ts-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockTimesheet);
    expect(api.getTimesheet).toHaveBeenCalledWith("ts-1");
  });

  it("does not fetch when id is empty", () => {
    renderHook(() => useTimesheet(""), { wrapper: createWrapper() });
    expect(api.getTimesheet).not.toHaveBeenCalled();
  });
});

describe("useGenerateTimesheet", () => {
  beforeEach(() => vi.clearAllMocks());

  it("generates timesheet for week", async () => {
    vi.mocked(api.generateTimesheet).mockResolvedValue(mockTimesheet);

    const { result } = renderHook(() => useGenerateTimesheet(), { wrapper: createWrapper() });

    result.current.mutate("2025-01-13");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.generateTimesheet).toHaveBeenCalledWith("2025-01-13");
  });
});

describe("useSubmitTimesheet", () => {
  beforeEach(() => vi.clearAllMocks());

  it("submits timesheet by id", async () => {
    vi.mocked(api.submitTimesheet).mockResolvedValue({ ...mockTimesheet, status: "Submitted" });

    const { result } = renderHook(() => useSubmitTimesheet(), { wrapper: createWrapper() });

    result.current.mutate("ts-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.submitTimesheet).toHaveBeenCalledWith("ts-1");
  });
});

describe("useApproveTimesheet", () => {
  beforeEach(() => vi.clearAllMocks());

  it("approves timesheet by id", async () => {
    vi.mocked(api.approveTimesheet).mockResolvedValue({ ...mockTimesheet, status: "Approved" });

    const { result } = renderHook(() => useApproveTimesheet(), { wrapper: createWrapper() });

    result.current.mutate("ts-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.approveTimesheet).toHaveBeenCalledWith("ts-1");
  });
});

describe("useRejectTimesheet", () => {
  beforeEach(() => vi.clearAllMocks());

  it("rejects timesheet by id", async () => {
    vi.mocked(api.rejectTimesheet).mockResolvedValue({ ...mockTimesheet, status: "Rejected" });

    const { result } = renderHook(() => useRejectTimesheet(), { wrapper: createWrapper() });

    result.current.mutate("ts-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.rejectTimesheet).toHaveBeenCalledWith("ts-1");
  });
});
