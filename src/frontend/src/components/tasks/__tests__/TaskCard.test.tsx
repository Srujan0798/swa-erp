import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const useSortableMock = vi.hoisted(() => vi.fn());

vi.mock("@dnd-kit/sortable", () => ({
  useSortable: () => useSortableMock(),
}));

vi.mock("@dnd-kit/utilities", () => ({
  CSS: { Transform: { toString: () => "none" } },
}));

import { TaskCard } from "../TaskCard";

const baseTask = {
  id: "t1",
  project_id: "p1",
  title: "Design review",
  description: null,
  priority: "high" as const,
  comment_count: 3,
  assignee_id: "u1",
  assignee_name: "Alice Smith",
  sort_order: 1,
  created_by: "u2",
  created_by_name: "Bob",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  due_date: "2026-12-31",
  status: "todo" as const,
};

describe("TaskCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useSortableMock.mockReturnValue({
      attributes: {},
      listeners: {},
      setNodeRef: () => undefined,
      transform: null,
      transition: undefined,
      isDragging: false,
    });
  });

  it("renders task details and calls onClick", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(<TaskCard task={baseTask} onClick={onClick} />);

    expect(screen.getByText("Design review")).toBeInTheDocument();
    expect(screen.getByText("High")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("AS")).toBeInTheDocument();
    expect(screen.getByText("Alice Smith")).toBeInTheDocument();
    expect(screen.getByText(/Due in/)).toBeInTheDocument();

    await user.click(screen.getByText("Design review"));
    expect(onClick).toHaveBeenCalledWith(baseTask);
  });

  it("renders overdue, due today, and tomorrow labels", () => {
    const today = new Date();
    // Local Y-M-D — matches TaskCard parsing of `dueDate + "T00:00:00"` as local time.
    // toISOString() is UTC and flips the calendar day under IST near midnight.
    const fmt = (d: Date): string => {
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      return `${y}-${m}-${day}`;
    };

    const past = new Date(today);
    past.setDate(past.getDate() - 3);
    const { rerender } = render(<TaskCard task={{ ...baseTask, due_date: fmt(past) }} onClick={vi.fn()} />);
    expect(screen.getByText("3d overdue")).toBeInTheDocument();

    rerender(<TaskCard task={{ ...baseTask, due_date: fmt(today) }} onClick={vi.fn()} />);
    expect(screen.getByText("Due today")).toBeInTheDocument();

    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    rerender(<TaskCard task={{ ...baseTask, due_date: fmt(tomorrow) }} onClick={vi.fn()} />);
    expect(screen.getByText("Due tomorrow")).toBeInTheDocument();
  });

  it("handles unassigned tasks without due dates", () => {
    render(<TaskCard task={{ ...baseTask, assignee_name: null, due_date: null, comment_count: 0 }} onClick={vi.fn()} />);
    expect(screen.getByText("Unassigned")).toBeInTheDocument();
    expect(screen.queryByText(/Due/)).not.toBeInTheDocument();
    expect(screen.queryByText("3")).not.toBeInTheDocument();
  });

  it("shows project name when requested", () => {
    render(<TaskCard task={baseTask} onClick={vi.fn()} showProject projectName="Acme" />);
    expect(screen.getByText("Acme")).toBeInTheDocument();
  });
});