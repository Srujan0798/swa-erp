import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { RecentClients } from "../RecentClients";
import { MemoryRouter } from "react-router-dom";

const useClientsMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useDashboard", () => ({
  useClients: useClientsMock,
}));

describe("RecentClients", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useClientsMock.mockReturnValue({ data: { items: [], total: 0 }, isLoading: false, isError: false });
  });

  const renderComponent = () => {
    return render(
      <MemoryRouter>
        <RecentClients />
      </MemoryRouter>
    );
  };

  it("shows loading skeleton", () => {
    useClientsMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    renderComponent();
    expect(screen.getAllByRole("row").length).toBeGreaterThan(0);
  });

  it("shows error state", () => {
    useClientsMock.mockReturnValue({ data: { items: [] }, isLoading: false, isError: true });
    renderComponent();
    expect(screen.getByText("Failed to load clients")).toBeInTheDocument();
  });

  it("shows empty state", () => {
    useClientsMock.mockReturnValue({ data: { items: [], total: 0 }, isLoading: false, isError: false });
    renderComponent();
    expect(screen.getByText("No clients — run make bootstrap-real")).toBeInTheDocument();
  });

  it("renders clients table", () => {
    useClientsMock.mockReturnValue({
      data: {
        items: [
          { id: "c1", code: "ACME", name: "Acme Corp", industry: "Construction", client_status: "Active" },
        ],
        total: 1,
      },
      isLoading: false,
      isError: false,
    });
    renderComponent();
    expect(screen.getByText("ACME")).toBeInTheDocument();
    expect(screen.getByText("Acme Corp")).toBeInTheDocument();
    expect(screen.getByText("Construction")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /view all/i })).toBeInTheDocument();
  });
});