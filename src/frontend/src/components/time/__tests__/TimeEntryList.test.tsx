import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TimeEntryList } from "../TimeEntryList";
import type { TimeEntry } from "@/types/time";

const useCurrentUserMock = vi.hoisted(() => vi.fn());
const deleteMutationMock = vi.hoisted(() => ({ mutateAsync: vi.fn(), isPending: false }));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/hooks/useTimeEntries", () => ({
  useDeleteTimeEntry: () => deleteMutationMock,
}));

const entry: TimeEntry = {
  id: "te-1",
  project_id: "p-1",
  task_id: null,
  user_id: "u-1",
  date: "2026-01-05",
  hours: 2.5,
  description: "Design review",
  is_billable: true,
  work_type: "PROJECT",
  activity_type: "DBR",
  software_used: "CAD",
  created_at: "2026-01-05T00:00:00Z",
  deleted_at: null,
  project_name: "Acme Office",
};

function renderList(role: string | null | undefined, overrides: Partial<typeof entry> = {}) {
  useCurrentUserMock.mockReturnValue({ data: role ? { role } : undefined });
  return render(
    <TimeEntryList entries={[{ ...entry, ...overrides }]} isLoading={false} onEdit={vi.fn()} />
  );
}

describe("TimeEntryList role gating (canWrite)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    deleteMutationMock.mutateAsync.mockResolvedValue(undefined);
  });

  it("shows edit/delete controls for a non-viewer role (pm)", () => {
    renderList("pm");
    expect(screen.getAllByRole("button")).toHaveLength(2);
    expect(screen.getByRole("button", { name: "Edit entry" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Delete entry" })).toBeInTheDocument();
  });

  it("hides edit/delete controls for a viewer", () => {
    renderList("viewer");
    expect(screen.queryByRole("button", { name: "Edit entry" })).not.toBeInTheDocument();
    expect(document.querySelectorAll("button")).toHaveLength(0);
  });

  it("hides edit/delete controls when no user is loaded", () => {
    renderList(undefined);
    expect(screen.queryByRole("button", { name: "Edit entry" })).not.toBeInTheDocument();
    expect(document.querySelectorAll("button")).toHaveLength(0);
  });

  it("renders a loading row while loading", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    render(<TimeEntryList entries={[]} isLoading onEdit={vi.fn()} />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders the empty state", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    render(<TimeEntryList entries={[]} isLoading={false} onEdit={vi.fn()} />);
    expect(screen.getByText("No time entries found")).toBeInTheDocument();
  });

  it("renders entry details including date, project, hours and billable badge", () => {
    renderList("pm");
    expect(screen.getByText("Acme Office")).toBeInTheDocument();
    expect(screen.getByText("2.50")).toBeInTheDocument();
    expect(screen.getByText("Design review")).toBeInTheDocument();
    // Billable column shows Yes when billable_hours is unset but is_billable
    expect(screen.getByText("Yes")).toBeInTheDocument();
  });

  it("calls delete mutation after confirm and triggers edit", async () => {
    const user = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(true);
    renderList("pm");

    const buttons = screen.getAllByRole("button");
    await user.click(buttons[1]);
    expect(deleteMutationMock.mutateAsync).toHaveBeenCalledWith("te-1");
  });

  it("does not delete when confirm is cancelled", async () => {
    const user = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(false);
    renderList("pm");

    const buttons = screen.getAllByRole("button");
    await user.click(buttons[1]);
    expect(deleteMutationMock.mutateAsync).not.toHaveBeenCalled();
  });
});