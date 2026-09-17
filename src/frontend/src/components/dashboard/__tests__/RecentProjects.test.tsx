import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { RecentProjects } from "../RecentProjects";
import { MemoryRouter } from "react-router-dom";

const useProjectsMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useDashboard", () => ({
  useProjects: useProjectsMock,
}));

describe("RecentProjects", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useProjectsMock.mockReturnValue({ data: { items: [], total: 0 }, isLoading: false, isError: false });
  });

  const renderComponent = () => {
    return render(
      <MemoryRouter>
        <RecentProjects />
      </MemoryRouter>
    );
  };

  it("shows loading skeleton", () => {
    useProjectsMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    renderComponent();
    expect(screen.getAllByRole("row").length).toBeGreaterThan(0);
  });

  it("shows error state", () => {
    useProjectsMock.mockReturnValue({ data: { items: [] }, isLoading: false, isError: true });
    renderComponent();
    expect(screen.getByText("Failed to load projects")).toBeInTheDocument();
  });

  it("shows empty state", () => {
    useProjectsMock.mockReturnValue({ data: { items: [], total: 0 }, isLoading: false, isError: false });
    renderComponent();
    expect(screen.getByText("No projects — run make bootstrap-real")).toBeInTheDocument();
  });

  it("renders projects table", () => {
    useProjectsMock.mockReturnValue({
      data: {
        items: [
          { id: "p1", code: "PRJ-001", name: "Office Building", client_name: "Acme Corp", status: "Design" },
        ],
        total: 1,
      },
      isLoading: false,
      isError: false,
    });
    renderComponent();
    expect(screen.getByText("PRJ-001")).toBeInTheDocument();
    expect(screen.getByText("Office Building")).toBeInTheDocument();
    expect(screen.getByText("Acme Corp")).toBeInTheDocument();
    expect(screen.getByText("Design")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /view all/i })).toBeInTheDocument();
  });
});