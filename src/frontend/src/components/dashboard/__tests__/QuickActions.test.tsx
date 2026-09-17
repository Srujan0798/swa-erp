import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QuickActions } from "../QuickActions";
import { MemoryRouter } from "react-router-dom";

const useCurrentUserMock = vi.hoisted(() => vi.fn());
const canWriteMock = vi.hoisted(() => vi.fn());
const canManageCommercialMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: useCurrentUserMock,
}));

vi.mock("@/lib/permissions", () => ({
  canWrite: canWriteMock,
  canManageCommercial: canManageCommercialMock,
}));

describe("QuickActions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { id: "u1", role: "admin" } });
    canWriteMock.mockReturnValue(true);
    canManageCommercialMock.mockReturnValue(true);
  });

  const renderComponent = () => {
    return render(
      <MemoryRouter>
        <QuickActions />
      </MemoryRouter>
    );
  };

  it("renders Inquiries button for all users", () => {
    renderComponent();
    expect(screen.getByRole("button", { name: /inquiries/i })).toBeInTheDocument();
  });

  it("renders New client button for commercial users", () => {
    canManageCommercialMock.mockReturnValue(true);
    renderComponent();
    expect(screen.getByRole("button", { name: /new client/i })).toBeInTheDocument();
  });

  it("hides New client button for non-commercial users", () => {
    canManageCommercialMock.mockReturnValue(false);
    renderComponent();
    expect(screen.queryByRole("button", { name: /new client/i })).not.toBeInTheDocument();
  });

  it("renders New project button for write users", () => {
    canWriteMock.mockReturnValue(true);
    renderComponent();
    expect(screen.getByRole("button", { name: /new project/i })).toBeInTheDocument();
  });

  it("hides New project button for non-write users", () => {
    canWriteMock.mockReturnValue(false);
    renderComponent();
    expect(screen.queryByRole("button", { name: /new project/i })).not.toBeInTheDocument();
  });
});