import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CostEntryForm } from "../CostEntryForm";

const addCostMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));

vi.mock("@/hooks/useProjectPnL", () => ({
  useAddProjectCost: () => ({ mutateAsync: addCostMock, isPending: false }),
}));

describe("CostEntryForm", () => {
  beforeEach(() => vi.clearAllMocks());

  it("submits a valid cost entry", async () => {
    const onSuccess = vi.fn();
    const user = userEvent.setup();
    render(<CostEntryForm projectId="p1" onSuccess={onSuccess} onCancel={vi.fn()} />);

    await user.type(screen.getByLabelText(/description/i), "Site materials");
    const amount = screen.getByLabelText(/amount/i);
    await user.clear(amount);
    await user.type(amount, "5000");
    await user.click(screen.getByRole("button", { name: "Add Cost" }));

    expect(addCostMock).toHaveBeenCalledWith(
      expect.objectContaining({
        projectId: "p1",
        data: expect.objectContaining({
          description: "Site materials",
          amount: 5000,
          project_id: "p1",
        }),
      })
    );
    expect(onSuccess).toHaveBeenCalled();
  });

  it("requires description and positive amount", async () => {
    const user = userEvent.setup();
    render(<CostEntryForm projectId="p1" onSuccess={vi.fn()} onCancel={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "Add Cost" }));
    expect(screen.getByText("Description is required")).toBeInTheDocument();

    await user.type(screen.getByLabelText(/description/i), "x");
    await user.click(screen.getByRole("button", { name: "Add Cost" }));
    expect(screen.getByText("Amount must be greater than 0")).toBeInTheDocument();
  });

  it("shows mutation errors and calls onCancel", async () => {
    addCostMock.mockRejectedValueOnce(new Error("Server rejected"));
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(<CostEntryForm projectId="p1" onSuccess={vi.fn()} onCancel={onCancel} />);

    await user.type(screen.getByLabelText(/description/i), "x");
    const amount = screen.getByLabelText(/amount/i);
    await user.clear(amount);
    await user.type(amount, "100");
    await user.click(screen.getByRole("button", { name: "Add Cost" }));
    expect(screen.getByText("Server rejected")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalled();
  });
});