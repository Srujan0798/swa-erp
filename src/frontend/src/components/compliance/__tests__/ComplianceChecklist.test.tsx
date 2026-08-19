import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ComplianceChecklist } from "../ComplianceChecklist";

const useComplianceItemsMock = vi.hoisted(() => vi.fn());
const updateComplianceItemMock = vi.hoisted(() => vi.fn());
const reviewComplianceItemMock = vi.hoisted(() => vi.fn());
const useCurrentUserMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useCompliance", () => ({
  useComplianceItems: (projectId: string, standardId: string) =>
    useComplianceItemsMock(projectId, standardId),
  useUpdateComplianceItem: () => ({ mutate: updateComplianceItemMock }),
  useReviewComplianceItem: () => ({ mutate: reviewComplianceItemMock, isPending: false }),
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

const item = {
  id: "ci1",
  requirement: "Follow NBC 2023 ventilation norms",
  category: "Ventilation",
  is_mandatory: true,
  status: "pending",
  notes: "Awaiting drawings",
  evidence_document_id: null,
  reviewed_by: null,
};

describe("ComplianceChecklist", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
  });

  it("shows loading state", () => {
    useComplianceItemsMock.mockReturnValue({ data: undefined, isLoading: true });
    render(
      <ComplianceChecklist projectId="p1" standardId="s1" standardName="NBC 2023" onBack={vi.fn()} />
    );
    expect(screen.getByText("Loading checklist...")).toBeInTheDocument();
  });

  it("renders items and goes back", async () => {
    useComplianceItemsMock.mockReturnValue({ data: [item], isLoading: false });
    const onBack = vi.fn();
    const user = userEvent.setup();
    render(
      <ComplianceChecklist projectId="p1" standardId="s1" standardName="NBC 2023" onBack={onBack} />
    );

    expect(screen.getByText("NBC 2023 Checklist")).toBeInTheDocument();
    expect(screen.getByText("Follow NBC 2023 ventilation norms")).toBeInTheDocument();
    expect(screen.getByText("Required")).toBeInTheDocument();
    expect(screen.getByText("Awaiting drawings")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /back to dashboard/i }));
    expect(onBack).toHaveBeenCalled();
  });

  it("shows empty state and links a document", async () => {
    useComplianceItemsMock.mockReturnValue({ data: [], isLoading: false });
    const user = userEvent.setup();
    render(
      <ComplianceChecklist projectId="p1" standardId="s1" standardName="NBC 2023" onBack={vi.fn()} />
    );
    expect(screen.getByText(/No items found/)).toBeInTheDocument();

    useComplianceItemsMock.mockReturnValue({ data: [item], isLoading: false });
    const { rerender } = render(
      <ComplianceChecklist projectId="p1" standardId="s1" standardName="NBC 2023" onBack={vi.fn()} />
    );
    rerender(
      <ComplianceChecklist projectId="p1" standardId="s1" standardName="NBC 2023" onBack={vi.fn()} />
    );
    await user.click(screen.getByRole("button", { name: "Link Doc" }));
    expect(updateComplianceItemMock).toHaveBeenCalledWith({
      itemId: "ci1",
      data: { evidence_document_id: null },
    });
  });

  it("edits and saves notes", async () => {
    useComplianceItemsMock.mockReturnValue({ data: [item], isLoading: false });
    const user = userEvent.setup();
    render(
      <ComplianceChecklist projectId="p1" standardId="s1" standardName="NBC 2023" onBack={vi.fn()} />
    );

    await user.click(screen.getByText("Awaiting drawings"));
    const textarea = screen.getByRole("textbox");
    await user.clear(textarea);
    await user.type(textarea, "Updated notes");
    await user.click(screen.getByRole("button", { name: "Save" }));
    expect(updateComplianceItemMock).toHaveBeenCalledWith({
      itemId: "ci1",
      data: { notes: "Updated notes" },
    });
  });

  it("shows review actions only for auditors", async () => {
    useComplianceItemsMock.mockReturnValue({ data: [item], isLoading: false });
    const user = userEvent.setup();
    const { rerender } = render(
      <ComplianceChecklist projectId="p1" standardId="s1" standardName="NBC 2023" onBack={vi.fn()} />
    );
    expect(screen.queryByRole("button", { name: "Review" })).not.toBeInTheDocument();

    useCurrentUserMock.mockReturnValue({ data: { role: "auditor" } });
    rerender(
      <ComplianceChecklist projectId="p1" standardId="s1" standardName="NBC 2023" onBack={vi.fn()} />
    );
    await user.click(screen.getByRole("button", { name: "Review" }));
    expect(reviewComplianceItemMock).toHaveBeenCalledWith({ itemId: "ci1" });
  });
});