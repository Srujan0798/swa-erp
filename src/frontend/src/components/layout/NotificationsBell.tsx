import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/useToast";
import { Bell } from "lucide-react";

export function NotificationsBell() {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => api.listNotifications({ page_size: 10 }),
    refetchInterval: 30000,
  });

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const markReadMutation = useMutation({
    mutationFn: (id: string) => api.markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
    onError: (err) => {
      toast({ title: (err as Error).message, variant: "destructive" });
    },
  });

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      const target = e.target as HTMLElement;
      if (open && !target.closest("[data-notifications-bell]")) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  return (
    <div className="relative" data-notifications-bell>
      <button
        type="button"
        className="relative rounded-md p-2 hover:bg-accent"
        onClick={() => setOpen((o) => !o)}
        aria-label="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-xs text-destructive-foreground">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-md border bg-card shadow-lg">
          <div className="border-b px-4 py-2 text-sm font-semibold">
            Notifications
          </div>
          <div className="max-h-80 overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-sm text-muted-foreground">Loading...</div>
            ) : notifications.length === 0 ? (
              <div className="p-4 text-sm text-muted-foreground">No notifications</div>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  className={`flex items-start gap-2 border-b px-4 py-3 text-sm ${
                    n.is_read ? "opacity-60" : "bg-accent/30"
                  }`}
                >
                  <div className="flex-1 space-y-1">
                    <div className="font-medium">{n.title}</div>
                    <div className="text-xs text-muted-foreground">{n.message}</div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(n.created_at).toLocaleString()}
                    </div>
                  </div>
                  {!n.is_read && (
                    <button
                      type="button"
                      className="text-xs text-primary hover:underline"
                      onClick={() => markReadMutation.mutate(n.id)}
                      disabled={markReadMutation.isPending}
                    >
                      Mark read
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
