import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Sidebar } from "../Sidebar";

const useAuthMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => useAuthMock(),
}));

function renderSidebar(role: string | undefined) {
  useAuthMock.mockReturnValue({ user: { role } });
  return render(
    <MemoryRouter>
      <Sidebar />
    </MemoryRouter>
  );
}

describe("Sidebar admin-only nav gating", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows the Users link for an admin", () => {
    renderSidebar("admin");
    expect(screen.getByRole("link", { name: "Users" })).toBeInTheDocument();
  });

  it("hides the Users link for non-admin roles", () => {
    renderSidebar("viewer");
    expect(screen.queryByRole("link", { name: "Users" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Dashboard" })).toBeInTheDocument();
  });

  it("hides the Users link when role is unknown", () => {
    renderSidebar(undefined);
    expect(screen.queryByRole("link", { name: "Users" })).not.toBeInTheDocument();
  });

  it("renders Excel workflow links for every role", () => {
    renderSidebar("viewer");
    expect(screen.getByRole("link", { name: "1. Inquiries" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "5. Document refs" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "6. Projects" })).toBeInTheDocument();
  });
});