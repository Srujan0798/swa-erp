import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";

const useCurrentUserMock = vi.hoisted(() => vi.fn());
const useInquiriesMock = vi.hoisted(() => vi.fn());
const useCreateInquiryMock = vi.hoisted(() => vi.fn());
const useDeleteInquiryMock = vi.hoisted(() => vi.fn());
const useToastMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/hooks/useInquiries", () => ({
  useInquiries: (params: any) => useInquiriesMock(params),
  useCreateInquiry: () => useCreateInquiryMock(),
  useDeleteInquiry: () => useDeleteInquiryMock(),
}));

vi.mock("@/hooks/useToast", () => ({
  useToast: () => useToastMock(),
}));

vi.mock("@/components/inquiries/InquiryForm", () => ({
  InquiryForm: ({ onSubmit, onCancel, isLoading }: any) => (
    <div data-testid="inquiry-form">
      <button onClick={() => onSubmit({ client_name: "Test" })} disabled={isLoading}>
        Submit
      </button>
      <button onClick={onCancel}>Cancel Form</button>
    </div>
  ),
}));

const inquiry = {
  id: "inq1",
  reference_id: "INQ-001",
  client_name: "Acme Corp",
  inquiry_date: "2026-01-15",
  status: "New",
  priority: "High",
  estimated_value: 500000,
};

async function renderPage() {
  const { InquiriesPage } = await import("@/pages/InquiriesPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <InquiriesPage />
      </QueryClientProvider>
    </MemoryRouter>
  );
}

describe("InquiriesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    useToastMock.mockReturnValue({ toast: vi.fn() });
    useInquiriesMock.mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    useCreateInquiryMock.mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    });
    useDeleteInquiryMock.mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    });
  });

  it("renders header and description", async () => {
    await renderPage();
    expect(screen.getByText("Inquiries")).toBeInTheDocument();
    expect(screen.getByText(/Step 1 of the SWA chain/)).toBeInTheDocument();
  });

  it("shows New Inquiry button for write users", async () => {
    await renderPage();
    expect(screen.getByText("New Inquiry")).toBeInTheDocument();
  });

  it("hides New Inquiry for viewer users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage();
    expect(screen.queryByText("New Inquiry")).not.toBeInTheDocument();
  });

  it("displays inquiries in table", async () => {
    useInquiriesMock.mockReturnValue({
      data: { items: [inquiry], total: 1 },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    await renderPage();
    expect(screen.getByText("INQ-001")).toBeInTheDocument();
    expect(screen.getByText("Acme Corp")).toBeInTheDocument();
    expect(screen.getByText("High")).toBeInTheDocument();
    expect(screen.getByText(/500,000/)).toBeInTheDocument();
  });

  it("shows loading state", async () => {
    useInquiriesMock.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    await renderPage();
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("shows error banner", async () => {
    useInquiriesMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("Failed to load"),
      refetch: vi.fn(),
    });
    await renderPage();
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("shows empty state for writer", async () => {
    await renderPage();
    expect(screen.getByText(/No inquiries yet/)).toBeInTheDocument();
    expect(screen.getByText("Create the first inquiry")).toBeInTheDocument();
  });

  it("shows empty state for viewer without create link", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage();
    expect(screen.getByText(/No inquiries yet/)).toBeInTheDocument();
    expect(screen.queryByText("Create the first inquiry")).not.toBeInTheDocument();
  });

  it("opens create dialog", async () => {
    await renderPage();
    const newBtn = screen.getByRole("button", { name: /New Inquiry/i });
    await userEvent.click(newBtn);
    expect(screen.getByTestId("inquiry-form")).toBeInTheDocument();
  });

  it("shows pagination", async () => {
    await renderPage();
    expect(screen.getByText(/0 inquiry/)).toBeInTheDocument();
    expect(screen.getByText(/Page 1 of 1/)).toBeInTheDocument();
  });

  it("shows search input", async () => {
    await renderPage();
    expect(screen.getByPlaceholderText("Search inquiries...")).toBeInTheDocument();
  });

  it("shows status filter", async () => {
    await renderPage();
    const select = screen.getByDisplayValue("All Statuses");
    expect(select).toBeInTheDocument();
  });

  it("displays inquiry with no priority", async () => {
    useInquiriesMock.mockReturnValue({
      data: { items: [{ ...inquiry, priority: null }], total: 1 },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    await renderPage();
    expect(screen.getByText("\u2014")).toBeInTheDocument();
  });

  it("displays inquiry with no estimated value", async () => {
    useInquiriesMock.mockReturnValue({
      data: { items: [{ ...inquiry, estimated_value: null }], total: 1 },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    await renderPage();
    expect(screen.getByText("\u2014")).toBeInTheDocument();
  });

  it("shows delete button for write users with inquiries", async () => {
    useInquiriesMock.mockReturnValue({
      data: { items: [inquiry], total: 1 },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    await renderPage();
    const trashButtons = screen.getAllByRole("button", { name: "" });
    expect(trashButtons.length).toBeGreaterThan(0);
  });

  it("hides delete button for viewer users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    useInquiriesMock.mockReturnValue({
      data: { items: [inquiry], total: 1 },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    await renderPage();
    expect(screen.getByText("View")).toBeInTheDocument();
  });
});
