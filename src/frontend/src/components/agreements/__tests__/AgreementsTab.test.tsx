import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AgreementsTab } from "../AgreementsTab";
import type { ServiceAgreement } from "@/types/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());
const useAgreementsMock = vi.hoisted(() => vi.fn());
const createMutationMock = vi.hoisted(() => ({ mutateAsync: vi.fn(), isPending: false }));
const deleteMutationMock = vi.hoisted(() => ({ mutate: vi.fn(), isPending: false }));
const toastMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/hooks/useAgreements", () => ({
  useAgreements: () => useAgreementsMock(),
  useCreateAgreement: () => createMutationMock,
  useDeleteAgreement: () => deleteMutationMock,
}));

vi.mock("@/hooks/useToast", () => ({
  useToast: () => ({ toast: toastMock }),
}));

vi.mock("@/components/agreements/AgreementForm", () => ({
  AgreementForm: ({
    onSubmit,
    onCancel,
  }: {
    onSubmit: (data: { service_name: string; start_date: string }) => Promise<void>;
    onCancel: () => void;
  }) => (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ service_name: "INSUDESIGN", start_date: "2026-01-01" });
      }}
    >
      <button type="submit">Submit Agreement</button>
      <button type="button" onClick={onCancel}>
        Cancel Form
      </button>
    </form>
  ),
}));

vi.mock("@/components/tokens/TokensList", () => ({
  TokensList: () => <div>TokensList mock</div>,
}));

const agreement: ServiceAgreement = {
  id: "ag-1",
  reference_id: "SWA-SA-001",
  client_id: "client-1",
  inquiry_id: null,
  service_name: "Insulation Design",
  start_date: "2026-01-01",
  end_date: null,
  total_tokens: 10,
  status: "Active",
  notes: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderTab(role: string | undefined) {
  useCurrentUserMock.mockReturnValue({ data: role ? { role } : undefined });
  useAgreementsMock.mockReturnValue({
    data: { items: [agreement], total: 1, page: 1, page_size: 100 },
    isLoading: false,
  });
  return render(<AgreementsTab clientId="client-1" />);
}

describe("AgreementsTab role gating (canManageCommercial)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    createMutationMock.mutateAsync.mockResolvedValue(undefined);
  });

  it("shows New Agreement button for pm", () => {
    renderTab("pm");
    expect(screen.getByRole("button", { name: /new agreement/i })).toBeInTheDocument();
  });

  it("hides New Agreement and delete for viewer", () => {
    renderTab("viewer");
    expect(screen.queryByRole("button", { name: /new agreement/i })).not.toBeInTheDocument();
    expect(document.querySelectorAll("button")).toHaveLength(1);
  });

  it("hides New Agreement and delete when no user is loaded", () => {
    renderTab(undefined);
    expect(screen.queryByRole("button", { name: /new agreement/i })).not.toBeInTheDocument();
  });

  it("expands an agreement to show tokens", async () => {
    const user = userEvent.setup();
    renderTab("pm");
    expect(screen.queryByText("TokensList mock")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Show tokens" }));
    expect(screen.getByText("TokensList mock")).toBeInTheDocument();
  });

  it("creates an agreement through the form and shows a toast", async () => {
    const user = userEvent.setup();
    renderTab("pm");

    await user.click(screen.getByRole("button", { name: /new agreement/i }));
    await user.click(screen.getByRole("button", { name: "Submit Agreement" }));

    expect(createMutationMock.mutateAsync).toHaveBeenCalledWith({
      client_id: "client-1",
      service_name: "INSUDESIGN",
      start_date: "2026-01-01",
      end_date: undefined,
      total_tokens: undefined,
      status: undefined,
      notes: undefined,
    });
    expect(toastMock).toHaveBeenCalledWith({ title: "Agreement created" });
  });

  it("deletes an agreement after confirmation for commercial roles", async () => {
    const user = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(true);
    renderTab("admin");

    const deleteBtn = screen.getByRole("button", { name: /delete agreement/i });
    await user.click(deleteBtn);
    expect(deleteMutationMock.mutate).toHaveBeenCalledWith("ag-1");
  });

  it("does not delete when confirm is cancelled", async () => {
    const user = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(false);
    renderTab("admin");

    const deleteBtn = screen.getByRole("button", { name: /delete agreement/i });
    await user.click(deleteBtn);
    expect(deleteMutationMock.mutate).not.toHaveBeenCalled();
  });

  it("renders loading state", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
    useAgreementsMock.mockReturnValue({ data: undefined, isLoading: true });
    render(<AgreementsTab clientId="client-1" />);
    expect(screen.getByText("Loading agreements...")).toBeInTheDocument();
  });

  it("renders empty state", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "admin" } });
    useAgreementsMock.mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 100 },
      isLoading: false,
    });
    render(<AgreementsTab clientId="client-1" />);
    expect(screen.getByText("No agreements yet for this client.")).toBeInTheDocument();
  });
});