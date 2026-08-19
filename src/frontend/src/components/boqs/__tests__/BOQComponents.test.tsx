import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BOQItemTable } from "../BOQItemTable";
import { BOQUpload } from "../BOQUpload";

const useBoqItemsMock = vi.hoisted(() => vi.fn());
const uploadBoqMock = vi.hoisted(() => vi.fn(() => Promise.resolve()));

vi.mock("@/hooks/useBoqs", () => ({
  useBoqItems: (boqId: string, page: number, pageSize: number) =>
    useBoqItemsMock(boqId, page, pageSize),
  useUploadBoq: () => ({ mutateAsync: uploadBoqMock, isPending: false, isError: false }),
}));

const item = {
  id: "i1",
  line_number: 10,
  category: "Electrical",
  description: "Cable tray",
  specification: "GI, 300mm",
  unit: "m",
  quantity: 50,
  rate: 350,
  amount: 17500,
};

describe("BOQItemTable", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading and empty states", () => {
    useBoqItemsMock.mockReturnValue({ data: undefined, isLoading: true });
    const { rerender } = render(<BOQItemTable boqId="b1" onBack={vi.fn()} />);
    expect(screen.getByText("Loading items...")).toBeInTheDocument();

    useBoqItemsMock.mockReturnValue({ data: { items: [], total: 0 }, isLoading: false });
    rerender(<BOQItemTable boqId="b1" onBack={vi.fn()} />);
    expect(screen.getByText("No items found.")).toBeInTheDocument();
  });

  it("renders items and goes back", async () => {
    useBoqItemsMock.mockReturnValue({ data: { items: [item], total: 1 }, isLoading: false });
    const onBack = vi.fn();
    const user = userEvent.setup();
    render(<BOQItemTable boqId="b1" onBack={onBack} />);

    expect(screen.getByText("BOQ Items (1)")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("Cable tray")).toBeInTheDocument();
    expect(screen.getByText("GI, 300mm")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /back/i }));
    expect(onBack).toHaveBeenCalled();
  });
});

describe("BOQUpload", () => {
  beforeEach(() => vi.clearAllMocks());

  it("uploads a file and clears the form", async () => {
    const onSuccess = vi.fn();
    const user = userEvent.setup();
    render(<BOQUpload projectId="p1" onSuccess={onSuccess} />);

    const file = new File(["[]"], "boq.json", { type: "application/json" });
    await user.upload(screen.getByLabelText(/boq file/i), file);
    await user.type(screen.getByLabelText(/notes/i), "first pass");
    await user.click(screen.getByRole("button", { name: /upload boq/i }));

    expect(uploadBoqMock).toHaveBeenCalledWith({
      projectId: "p1",
      file,
      notes: "first pass",
    });
    expect(onSuccess).toHaveBeenCalled();
  });

  it("disables submit until a file is chosen", () => {
    render(<BOQUpload projectId="p1" onSuccess={vi.fn()} />);
    expect(screen.getByRole("button", { name: /upload boq/i })).toBeDisabled();
  });
});