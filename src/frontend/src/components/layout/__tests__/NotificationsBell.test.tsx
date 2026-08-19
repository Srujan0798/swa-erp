import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { NotificationsBell } from "../NotificationsBell";
import { api } from "@/lib/api";

const toastMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useToast", () => ({
  useToast: () => ({ toast: toastMock }),
}));

vi.mock("@/lib/api", () => ({
  api: {
    listNotifications: vi.fn(),
    markNotificationRead: vi.fn(),
  },
}));

function createWrapper() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

const notifications = [
  { id: "n1", title: "Task assigned", message: "Design review", is_read: false, created_at: "2026-01-05T00:00:00Z" },
  { id: "n2", title: "Quote approved", message: "Quote #1 approved", is_read: true, created_at: "2026-01-04T00:00:00Z" },
];

describe("NotificationsBell", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.listNotifications).mockResolvedValue(notifications);
    vi.mocked(api.markNotificationRead).mockResolvedValue(undefined);
  });

  it("shows unread count badge and opens the dropdown", async () => {
    const user = userEvent.setup();
    render(<NotificationsBell />, { wrapper: createWrapper() });

    const bell = await screen.findByRole("button", { name: /notifications/i });
    expect(await screen.findByText("1")).toBeInTheDocument();

    await user.click(bell);
    expect(screen.getByText("Task assigned")).toBeInTheDocument();
    expect(screen.getByText("Quote approved")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /mark read/i })).toBeInTheDocument();
  });

  it("shows no notifications message when empty", async () => {
    vi.mocked(api.listNotifications).mockResolvedValue([]);
    const user = userEvent.setup();
    render(<NotificationsBell />, { wrapper: createWrapper() });

    const bell = await screen.findByRole("button", { name: /notifications/i });
    await user.click(bell);
    expect(await screen.findByText("No notifications")).toBeInTheDocument();
  });

  it("marks a notification as read", async () => {
    const user = userEvent.setup();
    render(<NotificationsBell />, { wrapper: createWrapper() });

    const bell = await screen.findByRole("button", { name: /notifications/i });
    await user.click(bell);
    await user.click(await screen.findByRole("button", { name: /mark read/i }));
    expect(api.markNotificationRead).toHaveBeenCalledWith("n1");
  });

  it("closes the dropdown when clicking outside", async () => {
    const user = userEvent.setup();
    render(
      <div>
        <NotificationsBell />
        <button type="button">outside</button>
      </div>,
      { wrapper: createWrapper() }
    );

    const bell = await screen.findByRole("button", { name: /notifications/i });
    await user.click(bell);
    expect(screen.getByText("Task assigned")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /outside/i }));
    expect(screen.queryByText("Task assigned")).not.toBeInTheDocument();
  });
});