import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useSustainabilityMetrics,
  useCreateSustainabilityMetric,
  useUpdateSustainabilityMetric,
  useDeleteSustainabilityMetric,
} from "../useSustainability";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listSustainabilityMetrics: vi.fn(),
    createSustainabilityMetric: vi.fn(),
    updateSustainabilityMetric: vi.fn(),
    deleteSustainabilityMetric: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockMetric = {
  id: "metric-1",
  project_id: "proj-1",
  reference_id: "ref-1",
  recorded_date: "2025-01-15",
  compliant_with_green_standards: true,
  energy_saved_kwh: 5000,
  co2_avoided_tco2e: 1200,
  lifecycle_cost_savings_inr: 500000,
  insulation_efficiency_ratio: 0.85,
  payback_period_months: 24,
  notes: null,
  created_at: "2025-01-15T00:00:00Z",
  updated_at: "2025-01-15T00:00:00Z",
};

describe("useSustainabilityMetrics", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches metrics for project with reference", async () => {
    vi.mocked(api.listSustainabilityMetrics).mockResolvedValue([mockMetric]);

    const { result } = renderHook(() => useSustainabilityMetrics("proj-1", "ref-1"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([mockMetric]);
    expect(api.listSustainabilityMetrics).toHaveBeenCalledWith("proj-1", "ref-1");
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useSustainabilityMetrics("", undefined), { wrapper: createWrapper() });
    expect(api.listSustainabilityMetrics).not.toHaveBeenCalled();
  });
});

describe("useCreateSustainabilityMetric", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates metric and invalidates list", async () => {
    vi.mocked(api.createSustainabilityMetric).mockResolvedValue(mockMetric);

    const { result } = renderHook(() => useCreateSustainabilityMetric("proj-1"), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ recorded_date: "2025-01-15", energy_saved_kwh: 5000 });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createSustainabilityMetric).toHaveBeenCalledWith("proj-1", {
      recorded_date: "2025-01-15",
      energy_saved_kwh: 5000,
    });
  });
});

describe("useUpdateSustainabilityMetric", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates metric by id", async () => {
    vi.mocked(api.updateSustainabilityMetric).mockResolvedValue({
      ...mockMetric,
      energy_saved_kwh: 6000,
    });

    const { result } = renderHook(() => useUpdateSustainabilityMetric("proj-1"), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ metricId: "metric-1", data: { energy_saved_kwh: 6000 } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateSustainabilityMetric).toHaveBeenCalledWith("proj-1", "metric-1", {
      energy_saved_kwh: 6000,
    });
  });
});

describe("useDeleteSustainabilityMetric", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes metric by id", async () => {
    vi.mocked(api.deleteSustainabilityMetric).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteSustainabilityMetric("proj-1"), {
      wrapper: createWrapper(),
    });

    result.current.mutate("metric-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteSustainabilityMetric).toHaveBeenCalledWith("proj-1", "metric-1");
  });
});
