import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginPage } from "../LoginPage";

const useAuthMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => useAuthMock(),
}));

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthMock.mockReturnValue({ login: vi.fn(), isLoggingIn: false, isAuthenticated: false });
  });

  it("renders the login form", () => {
    render(<LoginPage />);
    expect(screen.getByRole("heading", { name: /swa consultancy erp/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toHaveValue("admin@swa.co.in");
    expect(screen.getByLabelText(/password/i)).toHaveValue("admin123!");
  });

  it("shows validation errors for an invalid email and empty password", async () => {
    const user = userEvent.setup();
    render(<LoginPage />);

    await user.clear(screen.getByLabelText(/email/i));
    await user.clear(screen.getByLabelText(/password/i));
    await user.type(screen.getByLabelText(/email/i), "not-an-email");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByText("Invalid email address")).toBeInTheDocument();
    expect(screen.getByText("Password is required")).toBeInTheDocument();
  });

  it("submits credentials and shows a generic error on failure", async () => {
    const user = userEvent.setup();
    const login = vi.fn().mockRejectedValue(new Error("401"));
    useAuthMock.mockReturnValue({ login, isLoggingIn: false, isAuthenticated: false });
    render(<LoginPage />);

    await user.click(screen.getByRole("button", { name: /sign in/i }));
    expect(login).toHaveBeenCalledWith({ email: "admin@swa.co.in", password: "admin123!" });
    expect(await screen.findByText("Invalid credentials")).toBeInTheDocument();
  });

  it("shows the signing-in state while logging in", () => {
    useAuthMock.mockReturnValue({ login: vi.fn(), isLoggingIn: true, isAuthenticated: false });
    render(<LoginPage />);
    expect(screen.getByRole("button", { name: /signing in/i })).toBeDisabled();
  });

  it("redirects to dashboard when already authenticated", () => {
    const originalLocation = window.location;
    Object.defineProperty(window, "location", { value: { href: "http://localhost/login" }, writable: true });
    useAuthMock.mockReturnValue({ login: vi.fn(), isLoggingIn: false, isAuthenticated: true });
    render(<LoginPage />);
    expect(window.location.href).toBe("/dashboard");
    expect(screen.queryByRole("heading", { name: /swa consultancy erp/i })).not.toBeInTheDocument();
    Object.defineProperty(window, "location", { value: originalLocation, writable: true });
  });
});