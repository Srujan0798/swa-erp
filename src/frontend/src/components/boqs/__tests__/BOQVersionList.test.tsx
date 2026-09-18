import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { BOQVersionList } from "../BOQVersionList";

const useBoqsMock = vi.hoisted(() => vi.fn());
const useDeleteBoqMock = vi.hoisted(() => vi.fn());
const useCurrentUserMock = vi.hoisted(() => vi.fn());
const canWriteMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useBoqs", () => ({
  useBoqs: useBoqsMock,
  useDeleteBoq: useDeleteBoqMock,
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: useCurrentUserMock,
}));

vi.mock("@/lib/permissions", () => ({
  canWrite: canWriteMock,
}));

describe("BOQVersionList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useBoqsMock.mockReturnValue({ data: { items: [], total: 0 }, isLoading: false });
    useDeleteBoqMock.mockReturnValue({ mutate: vi.fn(), isPending: false });
    useCurrentUserMock.mockReturnValue({ data: { id: "u1", role: "admin" } });
    canWriteMock.mockReturnValue(true);
  });

  it("shows loading state", () => {
    useBoqsMock.mockReturnValue({ data: undefined, isLoading: true });
    render(<BOQVersionList projectId="p1" onViewItems={vi.fn()} />);
    expect(screen.getByText("Loading BOQs...")).toBeInTheDocument();
  });

  it("shows empty state when no BOQs", () => {
    render(<BOQVersionList projectId="p1" onViewItems={vi.fn()} />);
    expect(screen.getByText("No BOQ versions uploaded yet.")).toBeInTheDocument();
  });

  it("renders BOQ versions table", () => {
    useBoqsMock.mockReturnValue({
      data: {
        items: [
          { id: "b1", version_number: 1, file_name: "boq.xlsx", item_count: 50, parsed_by: "user1", parsed_at: "2026-01-01T00:00:00Z" },
        ],
        total: 1,
      },
      isLoading: false,
    });
    const onViewItems = vi.fn();
    render(<BOQVersionList projectId="p1" onViewItems={onViewItems} />);
    expect(screen.getByText("BOQ Versions (1)")).toBeInTheDocument();
    expect(screen.getByText("v1")).toBeInTheDocument();
    expect(screen.getByText("boq.xlsx")).toBeInTheDocument();
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThanOrEqual(2);
  });

  it("handles pagination", () => {
    useBoqsMock.mockReturnValue({
      data: {
        items: Array(10).fill({ id: "b1", version_number: 1, file_name: "boq.xlsx", item_count: 50, parsed_by: "user1", parsed_at: "2026-01-01T00:00:00Z" }),
        total: 15,
      },
      isLoading: false,
    });
    render(<BOQVersionList projectId="p1" onViewItems={vi.fn()} />);
    expect(screen.getByText("Page 1 of 2")).toBeInTheDocument();
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });
});
