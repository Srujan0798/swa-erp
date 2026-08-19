import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { VendorList } from "../VendorList";
import type { Vendor } from "@/types/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());
const useVendorsMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/hooks/useVendors", () => ({
  useVendors: (params: unknown) => useVendorsMock(params),
}));

const vendor: Vendor = {
  id: "v-1",
  code: "VEN-001",
  name: "Insul Tech",
  city: "Pune",
  state: "MH",
  phone: "9820xxxxxx",
  email: "sales@insul.tech",
  gst_number: null,
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  contacts: [],
};

const response = (items: Vendor[]) => ({ items, total: items.length, page: 1, page_size: 20 });

function renderList(role: string | undefined) {
  useCurrentUserMock.mockReturnValue({ data: role ? { role } : undefined });
  return render(
    <MemoryRouter>
      <VendorList />
    </MemoryRouter>
  );
}

describe("VendorList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useVendorsMock.mockReturnValue({
      data: response([vendor]),
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
  });

  it("shows New Vendor button for writers and hides it for viewers", () => {
    const { unmount } = renderList("designer");
    expect(screen.getByRole("link", { name: /new vendor/i })).toBeInTheDocument();
    unmount();

    renderList("viewer");
    expect(screen.queryByRole("link", { name: /new vendor/i })).not.toBeInTheDocument();
  });

  it("renders vendor rows with active badge and view link", () => {
    renderList("pm");
    expect(screen.getByText("Insul Tech")).toBeInTheDocument();
    expect(screen.getByText("VEN-001")).toBeInTheDocument();
    expect(screen.getByText("Pune")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "View" })).toHaveAttribute("href", "/vendors/v-1");
  });

  it("renders loading state", () => {
    useVendorsMock.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    renderList("pm");
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders error state with banner", () => {
    useVendorsMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("boom"),
      refetch: vi.fn(),
    });
    renderList("pm");
    expect(screen.getByText("Failed to load vendors")).toBeInTheDocument();
    expect(screen.getByText("Unable to load vendors.")).toBeInTheDocument();
  });

  it("renders empty state with CTA for writers and plain empty for viewers", () => {
    useVendorsMock.mockReturnValue({
      data: response([]),
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    const { unmount } = renderList("pm");
    expect(screen.getByRole("link", { name: /add the first vendor/i })).toBeInTheDocument();
    unmount();

    renderList("viewer");
    expect(screen.queryByRole("link", { name: /add the first vendor/i })).not.toBeInTheDocument();
    expect(screen.getByText(/no vendors yet/i)).toBeInTheDocument();
  });

  it("paginates with disabled prev button on page 1", async () => {
    const user = userEvent.setup();
    useVendorsMock.mockReturnValue({
      data: { items: [vendor], total: 40, page: 1, page_size: 20 },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
    renderList("pm");

    expect(screen.getByText("Page 1 of 2")).toBeInTheDocument();
    const buttons = screen.getAllByRole("button");
    expect(buttons[0]).toBeDisabled();

    await user.click(buttons[1]);
    expect(useVendorsMock).toHaveBeenLastCalledWith({ page: 2, page_size: 20, q: "" });
  });
});