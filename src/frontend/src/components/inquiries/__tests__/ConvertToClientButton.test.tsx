import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ConvertToClientButton } from "../ConvertToClientButton";
import { ApiError } from "@/lib/api";

const navigateMock = vi.hoisted(() => vi.fn());
const convertMutationMock = vi.hoisted(() => ({
  mutateAsync: vi.fn(),
  isPending: false,
  isError: false,
  error: null as Error | null,
}));

vi.mock("react-router-dom", () => ({
  useNavigate: () => navigateMock,
}));

vi.mock("@/hooks/useInquiries", () => ({
  useConvertInquiry: () => convertMutationMock,
}));

const candidates = [
  { id: "client-1", name: "Acme Corp", code: "AC-001" },
  { id: "client-2", name: "Acme Corp", code: "AC-002" },
];

function renderButton() {
  return render(
    <ConvertToClientButton
      inquiryId="inq-1"
      inquiryClientName="Acme Corp"
      inquiryEstimatedValue={1500000}
    />
  );
}

describe("ConvertToClientButton", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    convertMutationMock.mutateAsync.mockResolvedValue({
      inquiry: {},
      client_id: "client-new",
      project_id: "project-99",
    });
    convertMutationMock.isPending = false;
    convertMutationMock.isError = false;
    convertMutationMock.error = null;
  });

  it("converts with a new client on the happy path and navigates to the project", async () => {
    const user = userEvent.setup();
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    expect(screen.getByText("Convert Inquiry to Project")).toBeInTheDocument();

    await user.clear(screen.getByLabelText(/project name/i));
    await user.type(screen.getByLabelText(/project name/i), "Acme Corp - Project");
    await user.type(screen.getByLabelText(/project code/i), "AC-2026-01");
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    await waitFor(() =>
      expect(convertMutationMock.mutateAsync).toHaveBeenCalledWith({
        id: "inq-1",
        payload: {
          project_name: "Acme Corp - Project",
          project_code: "AC-2026-01",
          estimated_value: 1500000,
        },
      })
    );
    expect(navigateMock).toHaveBeenCalledWith("/projects/project-99");
  });

  it("shows the ambiguous-match picker when the API returns 300 with candidates", async () => {
    const user = userEvent.setup();
    convertMutationMock.mutateAsync.mockRejectedValue(
      new ApiError(300, { candidates })
    );
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    expect(screen.getByText(/multiple clients named/i)).toBeInTheDocument();
    expect(screen.getAllByRole("radio")).toHaveLength(3);
    expect(screen.getByText("(AC-001)")).toBeInTheDocument();
    expect(screen.getByText("(AC-002)")).toBeInTheDocument();

    // Convert is disabled until a choice is made
    expect(screen.getByRole("button", { name: /^convert$/i })).toBeDisabled();
  });

  it("reuses an existing client when one is selected", async () => {
    const user = userEvent.setup();
    convertMutationMock.mutateAsync.mockRejectedValue(
      new ApiError(300, { candidates })
    );
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    await user.click(screen.getAllByRole("radio")[0]);
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    await waitFor(() =>
      expect(convertMutationMock.mutateAsync).toHaveBeenCalledWith({
        id: "inq-1",
        payload: expect.objectContaining({ client_id: "client-1" }),
      })
    );
  });

  it("creates a new client when the new-client option is selected", async () => {
    const user = userEvent.setup();
    convertMutationMock.mutateAsync.mockRejectedValue(
      new ApiError(300, { candidates })
    );
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    await user.click(screen.getByLabelText(/create a new client/i));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    await waitFor(() =>
      expect(convertMutationMock.mutateAsync).toHaveBeenCalledWith({
        id: "inq-1",
        payload: expect.not.objectContaining({ client_id: expect.any(String) }),
      })
    );
  });

  it("disables convert while the mutation is pending", () => {
    convertMutationMock.isPending = true;
    renderButton();

    const btn = screen.getByRole("button", { name: /convert to project/i });
    expect(btn).toBeDisabled();
  });

  it("renders non-300 errors inline", async () => {
    const user = userEvent.setup();
    convertMutationMock.mutateAsync.mockRejectedValue(new Error("boom"));
    convertMutationMock.isError = true;
    convertMutationMock.error = new Error("boom");
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    expect(screen.getByText(/conversion failed: boom/i)).toBeInTheDocument();
  });
});