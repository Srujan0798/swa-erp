import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { ComplianceDashboard } from "../ComplianceDashboard";
import { MemoryRouter } from "react-router-dom";

const useComplianceSummaryMock = vi.hoisted(() => vi.fn());
const useStandardsMock = vi.hoisted(() => vi.fn());
const useBulkCreateItemsMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useCompliance", () => ({
  useComplianceSummary: useComplianceSummaryMock,
  useStandards: useStandardsMock,
  useBulkCreateItems: useBulkCreateItemsMock,
}));

describe("ComplianceDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useComplianceSummaryMock.mockReturnValue({ data: null, isLoading: false });
    useStandardsMock.mockReturnValue({ data: [] });
    useBulkCreateItemsMock.mockReturnValue({ mutate: vi.fn(), isPending: false });
  });

  const renderComponent = (overrides: Partial<{ projectId: string; onSelectStandard: (id: string, name: string) => void }> = {}) => {
    return render(
      <MemoryRouter>
        <ComplianceDashboard projectId="p1" onSelectStandard={vi.fn()} {...overrides} />
      </MemoryRouter>
    );
  };

  it("shows loading state", () => {
    useComplianceSummaryMock.mockReturnValue({ data: null, isLoading: true });
    renderComponent();
    expect(screen.getByText("Loading compliance data...")).toBeInTheDocument();
  });

  it("shows empty state with initialize buttons", () => {
    useStandardsMock.mockReturnValue({ data: [{ id: "s1", name: "NBC" }, { id: "s2", name: "ECBC" }] });
    renderComponent();
    expect(screen.getByText("Compliance Tracking")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /initialize nbc/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /initialize ecbc/i })).toBeInTheDocument();
  });

  it("shows empty state with no standards", () => {
    useStandardsMock.mockReturnValue({ data: [] });
    renderComponent();
    expect(screen.getByRole("button", { name: /no standards available/i })).toBeInTheDocument();
  });

  it("renders compliance overview and standard cards", () => {
    useComplianceSummaryMock.mockReturnValue({
      data: {
        overall_percentage: 75,
        standards: [
          { standard_name: "NBC", compliance_percentage: 80, compliant_count: 4, non_compliant_count: 1, pending_count: 0, na_count: 0, total_items: 5 },
          { standard_name: "ECBC", compliance_percentage: 70, compliant_count: 3, non_compliant_count: 1, pending_count: 1, na_count: 0, total_items: 5 },
        ],
      },
      isLoading: false,
    });
    renderComponent();
    expect(screen.getByText("Compliance Overview")).toBeInTheDocument();
    expect(screen.getByText("Overall compliance: 75%")).toBeInTheDocument();
    expect(screen.getByText("NBC")).toBeInTheDocument();
    expect(screen.getByText("ECBC")).toBeInTheDocument();
    expect(screen.getByText("80%")).toBeInTheDocument();
    expect(screen.getByText("70%")).toBeInTheDocument();
  });
});