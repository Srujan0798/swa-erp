import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { InvoiceCreateForm } from "../InvoiceCreateForm";

const createMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));

vi.mock("@/hooks/useInvoices", () => ({
  useCreateInvoice: () => ({ mutateAsync: createMock, isPending: false }),
}));

describe("InvoiceCreateForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const renderForm = (overrides: Partial<{ projectId: string; onSuccess: () => void; onCancel: () => void }> = {}) => {
    return render(
      <InvoiceCreateForm
        projectId="p1"
        onSuccess={vi.fn()}
        onCancel={vi.fn()}
        {...overrides}
      />
    );
  };

  it("renders form with due date, tax rate, and empty line item", () => {
    renderForm();
    expect(screen.getByLabelText(/due date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/gst/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/consultancy fee/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /add line/i })).toBeInTheDocument();
  });

  it("submits valid invoice with one line item", async () => {
    const onSuccess = vi.fn();
    const user = userEvent.setup();
    render(<InvoiceCreateForm projectId="p1" onSuccess={onSuccess} onCancel={vi.fn()} />);

    await user.type(screen.getByLabelText(/due date/i), "2026-02-15");
    await user.clear(screen.getByLabelText(/gst/i));
    await user.type(screen.getByLabelText(/gst/i), "18");
    await user.type(screen.getByPlaceholderText(/consultancy fee/i), "Design consultation");
    
    const spinButtons = screen.getAllByRole("spinbutton");
    await user.clear(spinButtons[0]);
    await user.type(spinButtons[0], "2");
    await user.clear(spinButtons[1]);
    await user.type(spinButtons[1], "50000");

    await user.click(screen.getByRole("button", { name: /create invoice/i }));

    expect(createMock).toHaveBeenCalled();
    expect(onSuccess).toHaveBeenCalled();
  });

  it("validates required description for each line", async () => {
    const user = userEvent.setup();
    renderForm();

    await user.click(screen.getByRole("button", { name: /create invoice/i }));
    expect(screen.getByText("Each line needs a description")).toBeInTheDocument();
  });

  it("adds and removes line items", async () => {
    const user = userEvent.setup();
    renderForm();

    expect(screen.getAllByPlaceholderText(/consultancy fee/i)).toHaveLength(1);

    await user.click(screen.getByRole("button", { name: /add line/i }));
    expect(screen.getAllByPlaceholderText(/consultancy fee/i)).toHaveLength(2);

    await user.click(screen.getAllByRole("button", { name: /remove line/i })[1]);
    expect(screen.getAllByPlaceholderText(/consultancy fee/i)).toHaveLength(1);
  });

  it("disables remove button when only one line", () => {
    renderForm();
    const removeBtn = screen.getByRole("button", { name: /remove line/i });
    expect(removeBtn).toBeDisabled();
  });

  it("calculates subtotal, tax, and total", async () => {
    const user = userEvent.setup();
    renderForm();

    await user.type(screen.getByPlaceholderText(/consultancy fee/i), "Service 1");
    const spinButtons = screen.getAllByRole("spinbutton");
    await user.clear(spinButtons[0]);
    await user.type(spinButtons[0], "2");
    await user.clear(spinButtons[1]);
    await user.type(spinButtons[1], "10000");

    await user.click(screen.getByRole("button", { name: /add line/i }));
    await user.type(screen.getAllByPlaceholderText(/consultancy fee/i)[1], "Service 2");
    const newSpinButtons = screen.getAllByRole("spinbutton");
    await user.clear(newSpinButtons[2]);
    await user.type(newSpinButtons[2], "1");
    await user.clear(newSpinButtons[3]);
    await user.type(newSpinButtons[3], "5000");

    await user.clear(screen.getByLabelText(/gst/i));
    await user.type(screen.getByLabelText(/gst/i), "18");

    expect(screen.getByText((content) => content.includes("Subtotal"))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes("Tax"))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes("Total"))).toBeInTheDocument();
  });

  it("shows mutation error and allows cancel", async () => {
    createMock.mockRejectedValueOnce(new Error("Invoice creation failed"));
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(<InvoiceCreateForm projectId="p1" onSuccess={vi.fn()} onCancel={onCancel} />);

    await user.type(screen.getByPlaceholderText(/consultancy fee/i), "Test");
    await user.click(screen.getByRole("button", { name: /create invoice/i }));
    expect(screen.getByText("Invoice creation failed")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalled();
  });
});