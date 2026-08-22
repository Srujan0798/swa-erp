import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TokensList } from "../TokensList";
import type { Token } from "@/types/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());
const useTokensMock = vi.hoisted(() => vi.fn());
const createMutationMock = vi.hoisted(() => ({ mutateAsync: vi.fn(), isPending: false }));
const deleteMutationMock = vi.hoisted(() => ({ mutate: vi.fn(), isPending: false }));
const toastMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/hooks/useTokens", () => ({
  useTokens: () => useTokensMock(),
  useCreateToken: () => createMutationMock,
  useDeleteToken: () => deleteMutationMock,
}));

vi.mock("@/hooks/useToast", () => ({
  useToast: () => ({ toast: toastMock }),
}));

vi.mock("@/components/tokens/TokenForm", () => ({
  TokenForm: ({
    onSubmit,
    onCancel,
  }: {
    onSubmit: (data: { token_type: string; token_date: string }) => Promise<void>;
    onCancel: () => void;
  }) => (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ token_type: "Design", token_date: "2026-01-01" });
      }}
    >
      <button type="submit">Submit Token</button>
      <button type="button" onClick={onCancel}>
        Cancel Form
      </button>
    </form>
  ),
}));

const token: Token = {
  id: "tok-1",
  reference_id: "SWA-TOK-001",
  agreement_id: "ag-1",
  token_date: "2026-01-10",
  token_type: "Design",
  description: "Preliminary sketches",
  token_status: "In Progress",
  tokens_used: 2,
  swa_employee_id: null,
  project_owner_id: null,
  swa_employee_name: "Mihir",
  project_owner_name: null,
  client_employee_name: "Ravi",
  project_id: null,
  created_at: "2026-01-10T00:00:00Z",
  updated_at: "2026-01-10T00:00:00Z",
};

function renderList(role: string | undefined) {
  useCurrentUserMock.mockReturnValue({ data: role ? { role } : undefined });
  useTokensMock.mockReturnValue({
    data: { items: [token], total: 1, page: 1, page_size: 100 },
    isLoading: false,
  });
  return render(<TokensList agreementId="ag-1" />);
}

describe("TokensList role gating (canManageCommercial)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    createMutationMock.mutateAsync.mockResolvedValue(undefined);
  });

  it("shows New Token button for admin", () => {
    renderList("admin");
    expect(screen.getByRole("button", { name: /new token/i })).toBeInTheDocument();
  });

  it("hides New Token and delete controls for designer", () => {
    renderList("designer");
    expect(screen.queryByRole("button", { name: /new token/i })).not.toBeInTheDocument();
    expect(document.querySelectorAll("button")).toHaveLength(0);
  });

  it("renders token details", () => {
    renderList("pm");
    expect(screen.getByText("SWA-TOK-001")).toBeInTheDocument();
    expect(screen.getByText("×2")).toBeInTheDocument();
    expect(
      screen.getByText("Design · 2026-01-10 · SWA: Mihir · Client: Ravi")
    ).toBeInTheDocument();
    expect(screen.getByText("Preliminary sketches")).toBeInTheDocument();
  });

  it("creates a token through the form and shows a toast", async () => {
    const user = userEvent.setup();
    renderList("pm");

    await user.click(screen.getByRole("button", { name: /new token/i }));
    await user.click(screen.getByRole("button", { name: "Submit Token" }));

    expect(createMutationMock.mutateAsync).toHaveBeenCalledWith({
      agreement_id: "ag-1",
      token_date: "2026-01-01",
      token_type: "Design",
      description: undefined,
      token_status: undefined,
      tokens_used: undefined,
      swa_employee_name: undefined,
      project_owner_name: undefined,
      client_employee_name: undefined,
      project_id: undefined,
    });
    expect(toastMock).toHaveBeenCalledWith({ title: "Token created" });
  });

  it("deletes a token after confirmation", async () => {
    const user = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(true);
    renderList("admin");

    await user.click(screen.getByRole("button", { name: /delete token/i }));
    expect(deleteMutationMock.mutate).toHaveBeenCalledWith("tok-1");
  });

  it("renders loading and empty states", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    useTokensMock.mockReturnValue({ data: undefined, isLoading: true });
    const { unmount } = render(<TokensList agreementId="ag-1" />);
    expect(screen.getByText("Loading tokens...")).toBeInTheDocument();
    unmount();

    useTokensMock.mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 100 },
      isLoading: false,
    });
    render(<TokensList agreementId="ag-1" />);
    expect(screen.getByText("No tokens yet for this agreement.")).toBeInTheDocument();
  });
});