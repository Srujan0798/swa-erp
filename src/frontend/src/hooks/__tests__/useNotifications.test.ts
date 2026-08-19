import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { useNotifications, useMarkNotificationRead } from "../useNotifications";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listNotifications: vi.fn(),
    markNotificationRead: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockNotification = {
  id: "notif-1",
  user_id: "user-1",
  notification_type: "assignment",
  title: "New task assigned",
  message: "You have a new task",
  reference_type: "task",
  reference_id: "task-1",
  is_read: false,
  created_at: "2025-01-01T00:00:00Z",
  read_at: null,
};

describe("useNotifications", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches notifications with refetchInterval", async () => {
    const response = {
      items: [mockNotification],
      total: 1,
      page: 1,
      page_size: 20,
    };
    vi.mocked(api.listNotifications).mockResolvedValue(response);

    const { result } = renderHook(() => useNotifications({ unread_only: true, page: 1, page_size: 20 }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listNotifications).toHaveBeenCalledWith({ unread_only: true, page: 1, page_size: 20 });
  });

  it("fetches notifications without params", async () => {
    const response = { items: [mockNotification], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listNotifications).mockResolvedValue(response);

    const { result } = renderHook(() => useNotifications(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.listNotifications).toHaveBeenCalledWith(undefined);
  });
});

describe("useMarkNotificationRead", () => {
  beforeEach(() => vi.clearAllMocks());

  it("marks notification as read", async () => {
    vi.mocked(api.markNotificationRead).mockResolvedValue(undefined);

    const { result } = renderHook(() => useMarkNotificationRead(), { wrapper: createWrapper() });

    result.current.mutate("notif-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.markNotificationRead).toHaveBeenCalledWith("notif-1");
  });
});
