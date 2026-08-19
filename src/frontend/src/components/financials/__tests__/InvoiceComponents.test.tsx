import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { InvoiceList } from "../InvoiceList";
import { InvoiceDetail } from "../InvoiceDetail";

const deleteInvoiceMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));
const updateStatusMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));

vi.mock("@/hooks/useInvoices", () => ({
  useDeleteInvoice: () => ({ mutateAsync: deleteInvoiceMock, isPending: false }),
  useUpdateInvoiceStatus: () => ({ mutateAsync: updateStatusMock, isPending: false }),
}));

const invoice = {
  id: "inv1",
  invoice_number: "INV-001",
  project_name: "Acme Office",
  status: "draft",
  total: 118000,
  subtotal: 100000,
  tax_rate: 0.18,
  tax_amount: 18000,
  due_date: "2026-02-01",
  created_at: "2026-01-01T00:00:00Z",
  notes: "Net 30",
  items: [{ id: "li1", description: "Design fees", quantity: 1, rate: 100000, amount: 100000 }],
};

describe("InvoiceList", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading and empty states", () => {
    render(<InvoiceList invoices={[]} isLoading onView={vi.fn()} />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders invoices and views one", async () => {
    const onView = vi.fn();
    const user = userEvent.setup();
    render(<InvoiceList invoices={[invoice]} isLoading={false} onView={onView} />);

    expect(screen.getByText("INV-001")).toBeInTheDocument();
    expect(screen.getByText("Acme Office")).toBeInTheDocument();
    expect(screen.getByText("draft")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /view invoice/i }));
    expect(onView).toHaveBeenCalledWith("inv1");
  });

  it("deletes an invoice after confirmation", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const user = userEvent.setup();
    render(<InvoiceList invoices={[invoice]} isLoading={false} onView={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: /delete invoice/i }));
    expect(deleteInvoiceMock).toHaveBeenCalledWith("inv1");
  });

  it("renders empty text when no invoices", () => {
    render(<InvoiceList invoices={[]} isLoading={false} onView={vi.fn()} />);
    expect(screen.getByText("No invoices found")).toBeInTheDocument();
  });
});

describe("InvoiceDetail", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders invoice line items and totals", () => {
    render(<InvoiceDetail invoice={invoice} onBack={vi.fn()} />);
    expect(screen.getByText("INV-001")).toBeInTheDocument();
    expect(screen.getByText("Design fees")).toBeInTheDocument();
    expect(screen.getByText("Tax (18.0%)")).toBeInTheDocument();
    expect(screen.getAllByText("₹1,00,000").length).toBeGreaterThanOrEqual(2);
  });

  it("sends a draft invoice and marks a sent invoice paid", async () => {
    const user = userEvent.setup();
    render(<InvoiceDetail invoice={invoice} onBack={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: /send invoice/i }));
    expect(updateStatusMock).toHaveBeenCalledWith({ id: "inv1", status: "sent" });
  });

  it("marks a sent invoice as paid", async () => {
    const user = userEvent.setup();
    render(<InvoiceDetail invoice={{ ...invoice, status: "sent" }} onBack={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: /mark as paid/i }));
    expect(updateStatusMock).toHaveBeenCalledWith({ id: "inv1", status: "paid" });
  });

  it("hides action buttons for paid invoices and goes back", async () => {
    const onBack = vi.fn();
    const user = userEvent.setup();
    render(<InvoiceDetail invoice={{ ...invoice, status: "paid", notes: null }} onBack={onBack} />);
    expect(screen.queryByRole("button", { name: /send invoice/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /mark as paid/i })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /back to invoices/i }));
    expect(onBack).toHaveBeenCalled();
  });
});