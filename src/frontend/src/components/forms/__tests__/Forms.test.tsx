/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { ClientForm } from "@/components/clients/ClientForm";
import { ContactForm } from "@/components/clients/ContactForm";
import { AgreementForm } from "@/components/agreements/AgreementForm";
import { TokenForm } from "@/components/tokens/TokenForm";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: { listProjects: vi.fn() },
}));

function createWrapper() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

describe("ClientForm", () => {
  beforeEach(() => vi.clearAllMocks());

  it("submits valid client data", async () => {
    const onSubmit = vi.fn(() => Promise.resolve());
    const user = userEvent.setup();
    render(<ClientForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/^name \*/i), "Acme Corp");
    await user.type(screen.getByLabelText(/^code \*/i), "AC-001");
    await user.type(screen.getByLabelText(/^email \*/i), "billing@acme.com");
    await user.type(screen.getByLabelText(/city/i), "Mumbai");
    await user.click(screen.getByRole("button", { name: "Save" }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ name: "Acme Corp", code: "AC-001", primary_email: "billing@acme.com", city: "Mumbai", country: "India" })
    );
  });

  it("shows validation errors for empty required fields", async () => {
    const onSubmit = vi.fn(() => Promise.resolve());
    const user = userEvent.setup();
    render(<ClientForm onSubmit={onSubmit} />);

    await user.click(screen.getByRole("button", { name: "Save" }));
    expect(screen.getByText("Name is required")).toBeInTheDocument();
    expect(screen.getByText("Code is required")).toBeInTheDocument();
    expect(screen.getByText("Valid email required")).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("pre-fills initial data and calls onCancel", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(
      <ClientForm initialData={{ name: "Acme Corp" }} onSubmit={vi.fn()} onCancel={onCancel} />
    );
    expect(screen.getByLabelText(/^name \*/i)).toHaveValue("Acme Corp");
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalled();
  });
});

describe("ContactForm", () => {
  beforeEach(() => vi.clearAllMocks());

  it("submits a valid contact", async () => {
    const onSubmit = vi.fn(() => Promise.resolve());
    const user = userEvent.setup();
    render(<ContactForm onSubmit={onSubmit} onCancel={vi.fn()} />);

    await user.type(screen.getByLabelText(/^name \*/i), "Riya");
    await user.type(screen.getByLabelText(/^email \*/i), "riya@acme.com");
    await user.click(screen.getByRole("button", { name: "Add Contact" }));

    expect((onSubmit as any).mock.calls[0][0]).toMatchObject({ name: "Riya", email: "riya@acme.com", is_primary: false });
  });

  it("shows validation errors and calls onCancel", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(<ContactForm onSubmit={vi.fn()} onCancel={onCancel} />);

    await user.click(screen.getByRole("button", { name: "Add Contact" }));
    expect(screen.getByText("Name is required")).toBeInTheDocument();
    expect(screen.getByText("Valid email required")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalled();
  });
});

describe("AgreementForm", () => {
  beforeEach(() => vi.clearAllMocks());

  it("submits a valid agreement", async () => {
    const onSubmit = vi.fn(() => Promise.resolve());
    const user = userEvent.setup();
    render(<AgreementForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/service name \*/i), "Energy Audit");
    await user.type(screen.getByLabelText(/start date \*/i), "2026-01-15");
    await user.click(screen.getByRole("button", { name: "Save Agreement" }));

    expect((onSubmit as any).mock.calls[0][0]).toMatchObject({
      service_name: "Energy Audit",
      start_date: "2026-01-15",
      status: "Active",
    });
  });

  it("shows required-field errors", async () => {
    const onSubmit = vi.fn(() => Promise.resolve());
    const user = userEvent.setup();
    render(<AgreementForm onSubmit={onSubmit} />);

    await user.click(screen.getByRole("button", { name: "Save Agreement" }));
    expect(screen.getByText("Service name is required")).toBeInTheDocument();
    expect(screen.getByText("Start date is required")).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });
});

describe("TokenForm", () => {
  beforeEach(() => vi.clearAllMocks());
  vi.mocked(api.listProjects).mockResolvedValue({ items: [], total: 0 } as never);

  it("submits a valid token", async () => {
    const onSubmit = vi.fn(() => Promise.resolve());
    const user = userEvent.setup();
    render(<TokenForm onSubmit={onSubmit} />, { wrapper: createWrapper() });

    fireEvent.change(screen.getByLabelText(/token date \*/i), { target: { value: "2026-01-20" } });
    await user.type(screen.getByLabelText(/type/i), "Site visit");
    await user.click(screen.getByRole("button", { name: "Save token" }));

    expect((onSubmit as any).mock.calls[0][0]).toMatchObject({
      token_date: "2026-01-20",
      token_type: "Site visit",
      tokens_used: 1,
      token_status: "In Progress",
    });
  });

  it("shows token date error and cancel", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(<TokenForm onSubmit={vi.fn()} onCancel={onCancel} />, { wrapper: createWrapper() });

    const date = screen.getByLabelText(/token date \*/i);
    await user.clear(date);
    await user.click(screen.getByRole("button", { name: "Save token" }));
    expect(screen.getByText("Token date is required")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalled();
  });
});