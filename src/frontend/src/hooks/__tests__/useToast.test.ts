import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useToast } from "../useToast";

describe("useToast", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    document.body.innerHTML = "";
  });

  afterEach(() => {
    vi.useRealTimers();
    document.body.innerHTML = "";
  });

  it("creates a toast element in the DOM with the title", () => {
    const { result } = renderHook();

    result.current.toast({ title: "Saved successfully" });

    const toastEl = document.querySelector("div[data-toast-id]") as HTMLDivElement;
    expect(toastEl).not.toBeNull();
    expect(toastEl.textContent).toBe("Saved successfully");
  });

  it("applies destructive styling for destructive variant", () => {
    const { result } = renderHook();

    result.current.toast({ title: "Failed", variant: "destructive" });

    const toastEl = document.querySelector("div[data-toast-id]") as HTMLDivElement;
    expect(toastEl.style.background).toBe("rgb(185, 28, 28)");
  });

  it("applies default styling for non-destructive variant", () => {
    const { result } = renderHook();

    result.current.toast({ title: "Hello" });

    const toastEl = document.querySelector("div[data-toast-id]") as HTMLDivElement;
    expect(toastEl.style.background).toBe("rgb(15, 23, 42)");
  });

  it("removes toast element after timeout", () => {
    const { result } = renderHook();

    result.current.toast({ title: "Temporary" });

    let toastEl = document.querySelector("div[data-toast-id]");
    expect(toastEl).not.toBeNull();

    vi.advanceTimersByTime(2600);

    toastEl = document.querySelector("div[data-toast-id]");
    expect(toastEl).toBeNull();
  });

  it("reuses the same container across multiple toasts", () => {
    const { result } = renderHook();

    result.current.toast({ title: "First" });
    result.current.toast({ title: "Second" });

    const container = document.querySelector("div[style*='position: fixed']");
    expect(container).not.toBeNull();
    expect(container?.children.length).toBe(2);

    const toasts = container?.querySelectorAll("div[data-toast-id]");
    expect(toasts?.[0]?.textContent).toBe("First");
    expect(toasts?.[1]?.textContent).toBe("Second");
  });
});

function renderHook() {
  // eslint-disable-next-line react-hooks/rules-of-hooks
  return { result: { current: useToast() } };
}
