import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { PnlDashboard } from "../PnlDashboard";

const mockPnL = {
  total_revenue: 5000000,
  total_costs: 3500000,
  net_profit: 1500000,
  margin_pct: 30.0,
  cost_breakdown: [
    { category: "material", count: 10, amount: 2000000, percentage: 57.1 },
    { category: "vendor", count: 5, amount: 1000000, percentage: 28.6 },
    { category: "overhead", count: 3, amount: 500000, percentage: 14.3 },
  ],
};

describe("PnlDashboard", () => {
  it("shows loading state", () => {
    render(<PnlDashboard isLoading />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("shows no data message when pnl is null", () => {
    render(<PnlDashboard pnl={null} />);
    expect(screen.getByText("No P&L data available")).toBeInTheDocument();
  });

  it("renders revenue, costs, net profit, and margin cards", () => {
    render(<PnlDashboard pnl={mockPnL} />);

    expect(screen.getByText("Revenue")).toBeInTheDocument();
    expect(screen.getByText("₹5,000,000")).toBeInTheDocument();

    expect(screen.getByText("Costs")).toBeInTheDocument();
    expect(screen.getByText("₹3,500,000")).toBeInTheDocument();

    expect(screen.getByText("Net Profit")).toBeInTheDocument();
    expect(screen.getByText("₹1,500,000")).toBeInTheDocument();
    expect(screen.getByText("₹1,500,000")).toHaveClass("text-green-600");

    expect(screen.getByText("Margin")).toBeInTheDocument();
    expect(screen.getByText("30.0%")).toBeInTheDocument();
    expect(screen.getByText("30.0%")).toHaveClass("text-green-600");
  });

  it("shows negative profit and margin in red", () => {
    const negativePnL = {
      ...mockPnL,
      net_profit: -500000,
      margin_pct: -10.0,
    };
    render(<PnlDashboard pnl={negativePnL} />);

    expect(screen.getByText("₹-500,000")).toHaveClass("text-red-600");
    expect(screen.getByText("-10.0%")).toHaveClass("text-red-600");
  });

  it("renders cost breakdown with categories and progress bars", () => {
    render(<PnlDashboard pnl={mockPnL} />);

    expect(screen.getByText("Cost Breakdown")).toBeInTheDocument();
    expect(screen.getByText("material")).toBeInTheDocument();
    expect(screen.getByText("vendor")).toBeInTheDocument();
    expect(screen.getByText("overhead")).toBeInTheDocument();

    expect(screen.getByText("(10 items)")).toBeInTheDocument();
    expect(screen.getByText("(5 items)")).toBeInTheDocument();
    expect(screen.getByText("(3 items)")).toBeInTheDocument();

    expect(screen.getByText("₹2,000,000 (57.1%)")).toBeInTheDocument();
    expect(screen.getByText("₹1,000,000 (28.6%)")).toBeInTheDocument();
    expect(screen.getByText("₹500,000 (14.3%)")).toBeInTheDocument();
  });

  it("shows no costs message when cost_breakdown is empty", () => {
    const emptyPnL = { ...mockPnL, cost_breakdown: [] };
    render(<PnlDashboard pnl={emptyPnL} />);
    expect(screen.getByText("No costs recorded")).toBeInTheDocument();
  });

  it("caps progress bar width at 100%", () => {
    const cappedPnL = {
      ...mockPnL,
      cost_breakdown: [{ category: "material", count: 1, amount: 5000000, percentage: 150 }],
    };
    render(<PnlDashboard pnl={cappedPnL} />);
    const percentageText = screen.getByText((content) => content.includes("150"));
    const parent = percentageText.closest("div.space-y-1");
    const bar = parent?.querySelector("div[style*='width: 100%']");
    expect(bar).toBeInTheDocument();
  });
});