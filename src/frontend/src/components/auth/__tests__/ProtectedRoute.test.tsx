import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "../ProtectedRoute";

const useAuthMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => useAuthMock(),
}));

function renderWithRoutes(ui: React.ReactElement) {
  return render(
    <MemoryRouter initialEntries={["/protected"]}>
      <Routes>
        <Route path="/protected" element={ui} />
        <Route path="/login" element={<div>Login Page</div>} />
        <Route path="/dashboard" element={<div>Dashboard Page</div>} />
      </Routes>
    </MemoryRouter>
  );
}

const viewerUser = { id: "u1", role: "viewer", name: "Viewer" };
const adminUser = { id: "u2", role: "admin", name: "Admin" };

describe("ProtectedRoute", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state while authenticating", () => {
    useAuthMock.mockReturnValue({ isAuthenticated: false, isLoading: true, user: null });
    renderWithRoutes(
      <ProtectedRoute>
        <div>Secret Content</div>
      </ProtectedRoute>
    );
    expect(screen.getByText("Loading...")).toBeInTheDocument();
    expect(screen.queryByText("Secret Content")).not.toBeInTheDocument();
  });

  it("redirects unauthenticated users to /login", () => {
    useAuthMock.mockReturnValue({ isAuthenticated: false, isLoading: false, user: null });
    renderWithRoutes(
      <ProtectedRoute>
        <div>Secret Content</div>
      </ProtectedRoute>
    );
    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  it("renders children for any authenticated user without role requirements", () => {
    useAuthMock.mockReturnValue({ isAuthenticated: true, isLoading: false, user: viewerUser });
    renderWithRoutes(
      <ProtectedRoute>
        <div>Secret Content</div>
      </ProtectedRoute>
    );
    expect(screen.getByText("Secret Content")).toBeInTheDocument();
  });

  it("redirects to /dashboard when user lacks the exact requiredRole", () => {
    useAuthMock.mockReturnValue({ isAuthenticated: true, isLoading: false, user: viewerUser });
    renderWithRoutes(
      <ProtectedRoute requiredRole="admin">
        <div>Admin Only</div>
      </ProtectedRoute>
    );
    expect(screen.getByText("Dashboard Page")).toBeInTheDocument();
  });

  it("renders children when user matches requiredRole", () => {
    useAuthMock.mockReturnValue({ isAuthenticated: true, isLoading: false, user: adminUser });
    renderWithRoutes(
      <ProtectedRoute requiredRole="admin">
        <div>Admin Only</div>
      </ProtectedRoute>
    );
    expect(screen.getByText("Admin Only")).toBeInTheDocument();
  });

  it("redirects to /dashboard when user role is not in requiredRoles", () => {
    useAuthMock.mockReturnValue({ isAuthenticated: true, isLoading: false, user: viewerUser });
    renderWithRoutes(
      <ProtectedRoute requiredRoles={["admin", "pm"]}>
        <div>Privileged</div>
      </ProtectedRoute>
    );
    expect(screen.getByText("Dashboard Page")).toBeInTheDocument();
  });

  it("renders children when user role is in requiredRoles", () => {
    useAuthMock.mockReturnValue({ isAuthenticated: true, isLoading: false, user: adminUser });
    renderWithRoutes(
      <ProtectedRoute requiredRoles={["admin", "pm"]}>
        <div>Privileged</div>
      </ProtectedRoute>
    );
    expect(screen.getByText("Privileged")).toBeInTheDocument();
  });

  it("redirects to /dashboard when requiredRoles is set but user has no role", () => {
    useAuthMock.mockReturnValue({ isAuthenticated: true, isLoading: false, user: { id: "u3", role: null, name: "?" } });
    renderWithRoutes(
      <ProtectedRoute requiredRoles={["admin"]}>
        <div>Privileged</div>
      </ProtectedRoute>
    );
    expect(screen.getByText("Dashboard Page")).toBeInTheDocument();
  });
});