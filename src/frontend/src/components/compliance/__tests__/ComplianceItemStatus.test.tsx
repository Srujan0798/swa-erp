import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ComplianceItemStatus } from "../ComplianceItemStatus";
import type { ComplianceStatus } from "@/types/compliance";

const updateItemMock = vi.hoisted(() => ({ mutate: vi.fn(), isPending: false }));

vi.mock("@/hooks/useCompliance", () => ({
  useUpdateComplianceItem: () => updateItemMock,
}));

describe("ComplianceItemStatus", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    updateItemMock.mutate.mockClear();
    updateItemMock.isPending = false;
  });

  it.each<[ComplianceStatus, string]>([
    ["pending", "Pending"],
    ["compliant", "Compliant"],
    ["non_compliant", "Non-Compliant"],
    ["na", "N/A"],
  ])("renders the %s label", (status, label) => {
    render(<ComplianceItemStatus itemId="item-1" status={status} />);
    expect(screen.getByRole("button", { name: label })).toBeInTheDocument();
  });

  it("cycles to the next status on click", async () => {
    const user = userEvent.setup();
    render(<ComplianceItemStatus itemId="item-1" status="pending" />);

    await user.click(screen.getByRole("button", { name: "Pending" }));
    expect(updateItemMock.mutate).toHaveBeenCalledWith({
      itemId: "item-1",
      data: { status: "compliant" },
    });
  });

  it("wraps around from the last status to the first", async () => {
    const user = userEvent.setup();
    render(<ComplianceItemStatus itemId="item-1" status="na" />);

    await user.click(screen.getByRole("button", { name: "N/A" }));
    expect(updateItemMock.mutate).toHaveBeenCalledWith({
      itemId: "item-1",
      data: { status: "pending" },
    });
  });

  it("disables the button while the mutation is pending", () => {
    updateItemMock.isPending = true;
    render(<ComplianceItemStatus itemId="item-1" status="pending" />);
    expect(screen.getByRole("button", { name: "Pending" })).toBeDisabled();
  });
});