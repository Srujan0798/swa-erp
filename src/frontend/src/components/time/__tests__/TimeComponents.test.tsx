import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TimeEntryForm } from "../TimeEntryForm";
import { TimesheetView } from "../TimesheetView";
import { TimesheetSummary } from "../TimesheetSummary";

const createMutationMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));
const updateMutationMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));
const submitTimesheetMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));
const approveTimesheetMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));
const rejectTimesheetMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));

vi.mock("@/hooks/useTimeEntries", () => ({
  useCreateTimeEntry: () => ({ mutateAsync: createMutationMock, isPending: false }),
  useUpdateTimeEntry: () => ({ mutateAsync: updateMutationMock, isPending: false }),
}));

vi.mock("@/hooks/useTimesheets", () => ({
  useSubmitTimesheet: () => ({ mutateAsync: submitTimesheetMock, isPending: false }),
  useApproveTimesheet: () => ({ mutateAsync: approveTimesheetMock, isPending: false }),
  useRejectTimesheet: () => ({ mutateAsync: rejectTimesheetMock, isPending: false }),
}));

const projects = [{ id: "p1", name: "Acme Office" }];

const timesheet = {
  id: "ts1",
  week_start: "2026-01-05T00:00:00.000Z",
  week_end: "2026-01-11T00:00:00.000Z",
  total_hours: 8,
  billable_hours: 6,
  status: "draft",
  user_name: "Alice",
};

const entries = [
  { id: "e1", date: "2026-01-05", hours: 4, is_billable: true, project_id: "p1", description: "x" },
  { id: "e2", date: "2026-01-05", hours: 2, is_billable: false, project_id: "p1", description: "y" },
];

describe("TimeEntryForm", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates a new entry and calls onSuccess", async () => {
    const onSuccess = vi.fn();
    const user = userEvent.setup();
    render(<TimeEntryForm projects={projects} onSuccess={onSuccess} onCancel={vi.fn()} />);

    const desc = screen.getByLabelText(/description/i);
    await user.type(desc, "Worked on design");
    await user.click(screen.getByRole("button", { name: "Add Entry" }));

    expect(createMutationMock).toHaveBeenCalledWith(
      expect.objectContaining({ project_id: "p1", description: "Worked on design" })
    );
    expect(onSuccess).toHaveBeenCalled();
  });

  it("requires a project", async () => {
    const user = userEvent.setup();
    render(<TimeEntryForm projects={[]} onSuccess={vi.fn()} onCancel={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Add Entry" }));
    expect(screen.getByText("Project is required")).toBeInTheDocument();
    expect(createMutationMock).not.toHaveBeenCalled();
  });

  it("rejects hours outside 0.25-24", async () => {
    const user = userEvent.setup();
    render(<TimeEntryForm projects={projects} onSuccess={vi.fn()} onCancel={vi.fn()} />);

    const hours = screen.getByLabelText(/hours/i);
    await user.clear(hours);
    await user.type(hours, "0.1");
    await user.click(screen.getByRole("button", { name: "Add Entry" }));
    expect(screen.getByText("Hours must be between 0.25 and 24")).toBeInTheDocument();
  });

  it("requires a description", async () => {
    const user = userEvent.setup();
    render(<TimeEntryForm projects={projects} onSuccess={vi.fn()} onCancel={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Add Entry" }));
    expect(screen.getByText("Description is required")).toBeInTheDocument();
  });

  it("updates an existing entry and surfaces mutation errors", async () => {
    const onSuccess = vi.fn();
    const user = userEvent.setup();
    updateMutationMock.mockRejectedValueOnce(new Error("Network down"));
    render(
      <TimeEntryForm
        projects={projects}
        editEntry={{ id: "e1", project_id: "p1", date: "2026-01-05", hours: 4, is_billable: true, description: "x" }}
        onSuccess={onSuccess}
        onCancel={vi.fn()}
      />
    );

    expect(screen.getByRole("button", { name: "Update" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Update" }));
    expect(updateMutationMock).toHaveBeenCalledWith(
      expect.objectContaining({ id: "e1", data: expect.objectContaining({ project_id: "p1" }) })
    );
    expect(onSuccess).not.toHaveBeenCalled();
    expect(screen.getByText("Network down")).toBeInTheDocument();
  });

  it("calls onCancel", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(<TimeEntryForm projects={projects} onSuccess={vi.fn()} onCancel={onCancel} />);
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalled();
  });
});

describe("TimesheetView", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders entries, totals, and status badge", () => {
    render(<TimesheetView timesheet={timesheet} entries={entries} />);
    expect(screen.getByText(/week of/i)).toBeInTheDocument();
    expect(screen.getByText("draft")).toBeInTheDocument();
    expect(screen.getByText("4h")).toBeInTheDocument();
    expect(screen.getByText("2h")).toBeInTheDocument();
    expect(screen.getByText("Total:")).toBeInTheDocument();
    expect(screen.getAllByText("8.0h").length).toBeGreaterThanOrEqual(2);
  });

  it("shows the submit button only for drafts and submits", async () => {
    const user = userEvent.setup();
    render(<TimesheetView timesheet={timesheet} entries={entries} />);
    await user.click(screen.getByRole("button", { name: /submit timesheet/i }));
    expect(submitTimesheetMock).toHaveBeenCalledWith("ts1");
  });

  it("hides the submit button for non-draft timesheets", () => {
    render(<TimesheetView timesheet={{ ...timesheet, status: "submitted" }} entries={entries} />);
    expect(screen.queryByRole("button", { name: /submit timesheet/i })).not.toBeInTheDocument();
  });
});

describe("TimesheetSummary", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders loading and empty states", () => {
    const { rerender } = render(
      <TimesheetSummary timesheets={[]} isLoading weekOffset={0} onWeekChange={vi.fn()} />
    );
    expect(screen.getByText("Loading...")).toBeInTheDocument();

    rerender(<TimesheetSummary timesheets={[]} isLoading={false} weekOffset={0} onWeekChange={vi.fn()} />);
    expect(screen.getByText("No timesheets found")).toBeInTheDocument();
  });

  it("renders timesheets and changes the week", async () => {
    const onWeekChange = vi.fn();
    const user = userEvent.setup();
    render(
      <TimesheetSummary
        timesheets={[{ ...timesheet, status: "submitted" }]}
        isLoading={false}
        weekOffset={0}
        onWeekChange={onWeekChange}
        isManager
      />
    );

    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("This Week")).toBeInTheDocument();
    expect(
      screen.getByText((_, el) =>
        el?.classList.contains("text-muted-foreground") &&
        el?.textContent?.includes("8.0h total") &&
        el?.textContent?.includes("6.0h billable") &&
        el?.textContent?.length < 100
          ? true
          : false
      )
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Previous week" }));
    expect(onWeekChange).toHaveBeenCalledWith(-1);

    await user.click(screen.getByRole("button", { name: "Next week" }));
    expect(onWeekChange).toHaveBeenCalledWith(1);
  });

  it("approves and rejects submitted timesheets as manager", async () => {
    const user = userEvent.setup();
    render(
      <TimesheetSummary
        timesheets={[{ ...timesheet, status: "submitted" }]}
        isLoading={false}
        weekOffset={-1}
        onWeekChange={vi.fn()}
        isManager
      />
    );

    expect(screen.getByText("Last Week")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Approve" }));
    expect(approveTimesheetMock).toHaveBeenCalledWith("ts1");

    await user.click(screen.getByRole("button", { name: "Reject" }));
    expect(rejectTimesheetMock).toHaveBeenCalledWith("ts1");
  });

  it("hides approve/reject for non-managers and non-submitted", () => {
    render(
      <TimesheetSummary
        timesheets={[timesheet]}
        isLoading={false}
        weekOffset={0}
        onWeekChange={vi.fn()}
        isManager={false}
      />
    );
    expect(screen.queryByRole("button", { name: "Approve" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Reject" })).not.toBeInTheDocument();
  });
});