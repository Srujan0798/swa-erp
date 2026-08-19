import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { Topbar } from "../Topbar";

const useAuthMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => useAuthMock(),
}));

vi.mock("../NotificationsBell", () => ({
  NotificationsBell: () => <div data-testid="notifications-bell" />,
}));

function renderTopbar(pathname: string) {
  return render(
    <MemoryRouter initialEntries={[pathname]}>
      <Routes>
        <Route path="*" element={<Topbar />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("Topbar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthMock.mockReturnValue({
      user: { name: "Priya", role: "admin" },
      logout: vi.fn(),
      isLoggingOut: false,
    });
  });

  it("shows the title for a known path", () => {
    renderTopbar("/inquiries");
    expect(screen.getByRole("heading", { name: "Inquiries" })).toBeInTheDocument();
  });

  it("falls back to section title for nested paths", () => {
    renderTopbar("/inquiries/abc-123");
    expect(screen.getByRole("heading", { name: "Inquiries" })).toBeInTheDocument();
  });

  it("shows generic title for unknown paths", () => {
    renderTopbar("/whatever");
    expect(screen.getByRole("heading", { name: "SWA ERP" })).toBeInTheDocument();
  });

  it("renders the current user name and role", () => {
    renderTopbar("/dashboard");
    expect(screen.getByText("Priya")).toBeInTheDocument();
    expect(screen.getByText("admin")).toBeInTheDocument();
  });

  it("logs out when the Logout button is clicked", async () => {
    const user = userEvent.setup();
    const logout = vi.fn();
    useAuthMock.mockReturnValue({
      user: { name: "Priya", role: "admin" },
      logout,
      isLoggingOut: false,
    });

    renderTopbar("/dashboard");
    await user.click(screen.getByRole("button", { name: /logout/i }));
    expect(logout).toHaveBeenCalled();
  });

  it("disables the logout button while logging out", () => {
    useAuthMock.mockReturnValue({
      user: { name: "Priya", role: "admin" },
      logout: vi.fn(),
      isLoggingOut: true,
    });
    renderTopbar("/dashboard");
    expect(screen.getByRole("button", { name: /logout/i })).toBeDisabled();
  });
});