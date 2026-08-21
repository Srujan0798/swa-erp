import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

const useUsersMock = vi.hoisted(() => vi.fn());
const useCreateUserMock = vi.hoisted(() => vi.fn());
const useDeleteUserMock = vi.hoisted(() => vi.fn());
const useToastMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useUsers: (page: number) => useUsersMock(page),
  useCreateUser: () => useCreateUserMock(),
  useDeleteUser: () => useDeleteUserMock(),
}));

vi.mock("@/hooks/useToast", () => ({
  useToast: () => useToastMock(),
}));

const user1 = {
  id: "u1",
  name: "Alice Smith",
  email: "alice@swa.com",
  role: "pm",
  is_active: true,
};

async function renderPage() {
  const { UsersPage } = await import("@/pages/UsersPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <UsersPage />
    </QueryClientProvider>
  );
}

describe("UsersPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useToastMock.mockReturnValue({ toast: vi.fn() });
    useUsersMock.mockReturnValue({
      data: { items: [user1], total: 1 },
      isLoading: false,
    });
    useCreateUserMock.mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue(undefined),
      isPending: false,
    });
    useDeleteUserMock.mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue(undefined),
      isPending: false,
    });
  });

  it("renders header", async () => {
    await renderPage();
    expect(screen.getByText("Users")).toBeInTheDocument();
    expect(screen.getByText("Manage system users")).toBeInTheDocument();
  });

  it("displays users in table", async () => {
    await renderPage();
    expect(screen.getByText("Alice Smith")).toBeInTheDocument();
    expect(screen.getByText("alice@swa.com")).toBeInTheDocument();
    expect(screen.getByText("pm")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("shows New User button", async () => {
    await renderPage();
    expect(screen.getByText("New User")).toBeInTheDocument();
  });

  it("shows loading state", async () => {
    useUsersMock.mockReturnValue({ data: undefined, isLoading: true });
    await renderPage();
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("shows total users count", async () => {
    await renderPage();
    expect(screen.getByText("Total: 1 users")).toBeInTheDocument();
  });

  it("opens create user dialog", async () => {
    await renderPage();
    await userEvent.click(screen.getByText("New User"));
    expect(screen.getByText("Create New User")).toBeInTheDocument();
    expect(screen.getByText("Name *")).toBeInTheDocument();
    expect(screen.getByText("Email *")).toBeInTheDocument();
    expect(screen.getByText("Password *")).toBeInTheDocument();
  });

  it("validates required fields on create", async () => {
    await renderPage();
    await userEvent.click(screen.getByText("New User"));
    const createBtn = screen.getByText("Create User");
    await userEvent.click(createBtn);
    expect(useToastMock().toast).toHaveBeenCalledWith(
      expect.objectContaining({ title: "Name, email, and password are required" })
    );
  });

  it("shows pagination buttons", async () => {
    await renderPage();
    expect(screen.getByText("Previous")).toBeInTheDocument();
    expect(screen.getByText("Next")).toBeInTheDocument();
    expect(screen.getByText("Page 1 of 1")).toBeInTheDocument();
  });

  it("disables Previous on first page", async () => {
    await renderPage();
    expect(screen.getByText("Previous")).toBeDisabled();
  });

  it("displays inactive user status", async () => {
    useUsersMock.mockReturnValue({
      data: { items: [{ ...user1, is_active: false }], total: 1 },
      isLoading: false,
    });
    await renderPage();
    expect(screen.getByText("Inactive")).toBeInTheDocument();
  });
});
