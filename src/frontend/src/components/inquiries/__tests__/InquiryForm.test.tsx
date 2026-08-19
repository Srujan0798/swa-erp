import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { InquiryForm } from "../InquiryForm";

describe("InquiryForm", () => {
  it("renders required fields with labels", () => {
    render(<InquiryForm onSubmit={vi.fn()} />);
    expect(screen.getByLabelText(/inquiry date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/client name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/source/i)).toBeInTheDocument();
  });

  it("shows validation errors when required fields are empty", async () => {
    const user = userEvent.setup();
    render(<InquiryForm onSubmit={vi.fn()} />);

    await user.clear(screen.getByLabelText(/inquiry date/i));
    await user.click(screen.getByRole("button", { name: /save inquiry/i }));

    expect(screen.getByText("Inquiry date is required")).toBeInTheDocument();
    expect(screen.getByText("Client name is required")).toBeInTheDocument();
  });

  it("submits valid data", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<InquiryForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/client name/i), "Acme Corp");
    await user.type(screen.getByLabelText(/requirement summary/i), "Retrofit design");
    await user.click(screen.getByRole("button", { name: /save inquiry/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit.mock.calls[0][0]).toMatchObject({
      client_name: "Acme Corp",
      requirement_summary: "Retrofit design",
    });
  });

  it("calls onCancel when the cancel button is clicked", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    render(<InquiryForm onSubmit={vi.fn()} onCancel={onCancel} />);

    await user.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalled();
  });

  it("disables submit and shows saving text while loading", () => {
    render(<InquiryForm onSubmit={vi.fn()} isLoading />);
    expect(screen.getByRole("button", { name: /saving/i })).toBeDisabled();
  });

  it("pre-fills initialData", () => {
    render(<InquiryForm onSubmit={vi.fn()} initialData={{ client_name: "Acme Corp" }} />);
    expect(screen.getByLabelText(/client name/i)).toHaveValue("Acme Corp");
  });
});