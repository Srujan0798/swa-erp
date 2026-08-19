import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { QuoteList } from "../QuoteList";
import { QuoteActions } from "../QuoteActions";

const useQuotesMock = vi.hoisted(() => vi.fn());
const deleteQuoteMock = vi.hoisted(() => vi.fn());
const cloneQuoteMock = vi.hoisted(() => vi.fn());
const submitQuoteMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));
const approveQuoteMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));
const sendQuoteMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));
const respondQuoteMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));
const useCurrentUserMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useQuotes", () => ({
  useQuotes: (projectId: string, page: number, pageSize: number) =>
    useQuotesMock(projectId, page, pageSize),
  useDeleteQuote: () => ({ mutate: deleteQuoteMock, isPending: false }),
  useCloneQuote: () => ({ mutate: cloneQuoteMock }),
  useSubmitQuote: () => ({ mutateAsync: submitQuoteMock, isPending: false }),
  useApproveQuote: () => ({ mutateAsync: approveQuoteMock, isPending: false }),
  useSendQuote: () => ({ mutateAsync: sendQuoteMock, isPending: false }),
  useRespondQuote: () => ({ mutateAsync: respondQuoteMock, isPending: false }),
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

function createWrapper() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

const quote = {
  id: "q1",
  version_number: 2,
  status: "draft",
  subtotal: 100000,
  total_amount: 118000,
  valid_until: null,
  created_by_name: "Alice",
};

describe("QuoteList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
  });

  it("shows loading state", () => {
    useQuotesMock.mockReturnValue({ data: undefined, isLoading: true });
    render(<QuoteList projectId="p1" onViewQuote={vi.fn()} />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading quotes...")).toBeInTheDocument();
  });

  it("shows empty state", () => {
    useQuotesMock.mockReturnValue({ data: { items: [], total: 0 }, isLoading: false });
    render(<QuoteList projectId="p1" onViewQuote={vi.fn()} />, { wrapper: createWrapper() });
    expect(screen.getByText(/No quotes yet/)).toBeInTheDocument();
  });

  it("renders quotes and views one", async () => {
    useQuotesMock.mockReturnValue({ data: { items: [quote], total: 1 }, isLoading: false });
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
    const onViewQuote = vi.fn();
    const user = userEvent.setup();
    render(<QuoteList projectId="p1" onViewQuote={onViewQuote} />, { wrapper: createWrapper() });

    expect(screen.getByText("Quotes (1)")).toBeInTheDocument();
    expect(screen.getByText("v2")).toBeInTheDocument();
    expect(screen.getByText("Draft")).toBeInTheDocument();
    expect(screen.getByText("₹1,00,000")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "View quote" }));
    expect(onViewQuote).toHaveBeenCalledWith("q1");
  });

  it("deletes a draft quote after confirmation", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    useQuotesMock.mockReturnValue({ data: { items: [quote], total: 1 }, isLoading: false });
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    const user = userEvent.setup();
    render(<QuoteList projectId="p1" onViewQuote={vi.fn()} />, { wrapper: createWrapper() });

    await user.click(screen.getByRole("button", { name: /delete/i }));
    expect(deleteQuoteMock).toHaveBeenCalledWith({ id: "q1", projectId: "p1" });
  });

  it("hides clone/delete actions for viewers", () => {
    useQuotesMock.mockReturnValue({ data: { items: [quote], total: 1 }, isLoading: false });
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    render(<QuoteList projectId="p1" onViewQuote={vi.fn()} />, { wrapper: createWrapper() });
    expect(screen.queryByRole("button", { name: /delete/i })).not.toBeInTheDocument();
  });
});

describe("QuoteActions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
  });

  it("shows submit for draft to admins/pms and calls it", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    const onAction = vi.fn();
    const user = userEvent.setup();
    render(<QuoteActions quoteId="q1" status="draft" onAction={onAction} />);

    await user.click(screen.getByRole("button", { name: "Submit for Approval" }));
    expect(submitQuoteMock).toHaveBeenCalledWith("q1");
    expect(onAction).toHaveBeenCalled();
  });

  it("hides submit for viewers", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    render(<QuoteActions quoteId="q1" status="draft" />);
    expect(screen.queryByRole("button", { name: "Submit for Approval" })).not.toBeInTheDocument();
  });

  it("shows approve and reject-to-draft only to admins for pending_approval", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
    const user = userEvent.setup();
    render(<QuoteActions quoteId="q1" status="pending_approval" />);

    await user.click(screen.getByRole("button", { name: "Approve" }));
    expect(approveQuoteMock).toHaveBeenCalledWith("q1");

    await user.click(screen.getByRole("button", { name: "Reject to Draft" }));
    expect(respondQuoteMock).toHaveBeenCalledWith({ id: "q1", data: { response: "rejected", notes: "Rejected — sent back to draft" } });
  });

  it("shows send for approved", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    const user = userEvent.setup();
    render(<QuoteActions quoteId="q1" status="approved" />);
    await user.click(screen.getByRole("button", { name: "Send to Client" }));
    expect(sendQuoteMock).toHaveBeenCalledWith("q1");
  });

  it("records accepted/rejected for sent", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
    const user = userEvent.setup();
    render(<QuoteActions quoteId="q1" status="sent" />);

    await user.click(screen.getByRole("button", { name: "Record: Accepted" }));
    expect(respondQuoteMock).toHaveBeenCalledWith({ id: "q1", data: { response: "accepted" } });

    await user.click(screen.getByRole("button", { name: "Record: Rejected" }));
    expect(respondQuoteMock).toHaveBeenCalledWith({ id: "q1", data: { response: "rejected" } });
  });

  it("renders status badge with no buttons for accepted", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
    render(<QuoteActions quoteId="q1" status="accepted" />);
    expect(screen.getByText("Accepted")).toBeInTheDocument();
    expect(screen.queryAllByRole("button")).toHaveLength(0);
  });
});