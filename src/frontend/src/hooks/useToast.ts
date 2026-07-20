"use client";

let toastContainer: HTMLDivElement | null = null;

function getContainer() {
  if (!toastContainer || !document.body.contains(toastContainer)) {
    const container = document.createElement("div");
    container.style.position = "fixed";
    container.style.top = "16px";
    container.style.right = "16px";
    container.style.zIndex = "9999";
    container.style.display = "flex";
    container.style.flexDirection = "column";
    container.style.gap = "8px";
    document.body.appendChild(container);
    toastContainer = container;
  }
  return toastContainer;
}

let toastCounter = 0;

export function useToast() {
  const toast = ({ title, variant }: { title: string; variant?: string }) => {
    const container = getContainer();
    const el = document.createElement("div");
    el.textContent = title ?? "";
    el.style.padding = "8px 12px";
    el.style.borderRadius = "6px";
    el.style.fontSize = "14px";
    el.style.color = "#fff";
    el.style.background = variant === "destructive" ? "#b91c1c" : "#0f172a";
    container.appendChild(el);
    toastCounter += 1;
    el.setAttribute("data-toast-id", String(toastCounter));
    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transition = "opacity 0.2s";
      setTimeout(() => el.remove(), 200);
    }, 2400);
  };

  return { toast } as const;
}
