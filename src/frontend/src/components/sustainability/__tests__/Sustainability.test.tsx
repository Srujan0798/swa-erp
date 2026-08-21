import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SustainabilityForm } from "../SustainabilityForm";
import { SustainabilityList } from "../SustainabilityList";

const metric = {
  id: "sm1",
  project_id: "p1",
  reference_id: "SWA-2025-PRJ-065",
  recorded_date: "2026-01-10",
  compliant_with_green_standards: true,
  energy_saved_kwh: 12000,
  co2_avoided_tco2e: 8.5,
  lifecycle_cost_savings_inr: 500000,
  insulation_efficiency_ratio: 0.89,
  payback_period_months: 24,
  notes: "certified",
  created_at: "2026-01-10T00:00:00Z",
  updated_at: "2026-01-10T00:00:00Z",
};

describe("SustainabilityForm", () => {
  beforeEach(() => vi.clearAllMocks());

  it("submits a new metric with converted numbers", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<SustainabilityForm projectId="p1" onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/reference id/i), "SWA-001");
    await user.type(screen.getByLabelText(/energy saved/i), "100");
    await user.click(screen.getByRole("button", { name: "Add Metric" }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        project_id: "p1",
        reference_id: "SWA-001",
        energy_saved_kwh: 100,
        compliant_with_green_standards: null,
      })
    );
  });

  it("pre-fills values when editing and updates", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<SustainabilityForm projectId="p1" initial={metric} onSubmit={onSubmit} />);

    expect(screen.getByLabelText(/reference id/i)).toHaveValue("SWA-2025-PRJ-065");
    expect(screen.getByLabelText(/energy saved/i)).toHaveValue(12000);
    await user.click(screen.getByRole("button", { name: "Update Metric" }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        project_id: "p1",
        energy_saved_kwh: 12000,
        compliant_with_green_standards: true,
        co2_avoided_tco2e: 8.5,
      })
    );
  });

  it("shows the saving label when submitting", () => {
    render(<SustainabilityForm projectId="p1" onSubmit={vi.fn()} isSubmitting />);
    expect(screen.getByRole("button", { name: "Saving..." })).toBeDisabled();
  });

  it("calls onCancel when provided", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(<SustainabilityForm projectId="p1" onSubmit={vi.fn()} onCancel={onCancel} />);
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalled();
  });
});

describe("SustainabilityList", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading state", () => {
    render(<SustainabilityList metrics={[]} isLoading onEdit={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByText("Loading metrics...")).toBeInTheDocument();
  });

  it("renders metrics with formatted values", () => {
    render(<SustainabilityList metrics={[metric]} onEdit={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByText("Sustainability Metrics (1)")).toBeInTheDocument();
    expect(screen.getByText("SWA-2025-PRJ-065")).toBeInTheDocument();
    expect(screen.getByText("Yes")).toBeInTheDocument();
    expect(screen.getByText("12,000")).toBeInTheDocument();
  });

  it("renders empty state with add link", async () => {
    const onAdd = vi.fn();
    const user = userEvent.setup();
    render(<SustainabilityList metrics={[]} onEdit={vi.fn()} onDelete={vi.fn()} onAdd={onAdd} />);
    await user.click(screen.getByRole("button", { name: /add the first metric/i }));
    expect(onAdd).toHaveBeenCalled();
  });

  it("calls onEdit and onDelete for a metric", async () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    const user = userEvent.setup();
    render(<SustainabilityList metrics={[metric]} onEdit={onEdit} onDelete={onDelete} />);

    await user.click(screen.getByRole("button", { name: /edit/i }));
    expect(onEdit).toHaveBeenCalledWith(metric);

    await user.click(screen.getByRole("button", { name: /delete/i }));
    expect(onDelete).toHaveBeenCalledWith(metric);
  });
});