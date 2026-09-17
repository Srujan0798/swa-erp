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
  { id: "11111111-1111-4111-8111-111111111111", name: "Acme Corp", code: "AC-001" },
  { id: "22222222-2222-4222-8222-222222222222", name: "Acme Corp", code: "AC-002" },
];
const ambiguousBody = {
  detail: {
    detail: "Ambiguous client match",
    inquiry_client_name: "Acme Corp",
    candidates,
  },
};

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
    vi.resetAllMocks();
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
    const error = new ApiError(300, ambiguousBody);
    convertMutationMock.mutateAsync.mockRejectedValue(error);
    convertMutationMock.isError = true;
    convertMutationMock.error = error;
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    expect(screen.getByText(/multiple clients named/i)).toBeInTheDocument();
    expect(screen.getAllByRole("radio")).toHaveLength(2);
    expect(screen.queryByLabelText(/create a new client/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/choose one or create/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/conversion failed/i)).not.toBeInTheDocument();
    expect(navigateMock).not.toHaveBeenCalled();
    expect(screen.getByText("(AC-001)")).toBeInTheDocument();
    expect(screen.getByText("(AC-002)")).toBeInTheDocument();

    expect(screen.getByRole("button", { name: /^convert$/i })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: /^convert$/i }));
    expect(convertMutationMock.mutateAsync).toHaveBeenCalledTimes(1);
  });

  it("retries with the explicitly selected client and preserves project fields", async () => {
    const user = userEvent.setup();
    convertMutationMock.mutateAsync
      .mockRejectedValueOnce(new ApiError(300, ambiguousBody))
      .mockResolvedValueOnce({
        inquiry: {},
        client_id: candidates[1].id,
        project_id: "project-42",
      });
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    await user.type(screen.getByLabelText(/project code/i), "AC-2026-01");
    await user.type(screen.getByLabelText(/^location$/i), "Mumbai");
    await user.type(screen.getByLabelText(/^description$/i), "Design work");
    await user.type(screen.getByLabelText(/start date/i), "2026-09-17");
    await user.type(screen.getByLabelText(/target end date/i), "2026-10-17");
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    const payload = {
      project_name: "Acme Corp - Project",
      project_code: "AC-2026-01",
      project_description: "Design work",
      location: "Mumbai",
      start_date: "2026-09-17",
      target_end_date: "2026-10-17",
      estimated_value: 1500000,
    };
    expect(convertMutationMock.mutateAsync).toHaveBeenNthCalledWith(1, {
      id: "inq-1",
      payload,
    });
    expect(screen.getByRole("button", { name: /^convert$/i })).toBeDisabled();
    await user.click(screen.getByRole("radio", { name: /AC-002/ }));
    expect(screen.getByRole("button", { name: /^convert$/i })).toBeEnabled();
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    await waitFor(() =>
      expect(convertMutationMock.mutateAsync).toHaveBeenNthCalledWith(2, {
        id: "inq-1",
        payload: { ...payload, client_id: candidates[1].id },
      })
    );
    expect(convertMutationMock.mutateAsync).toHaveBeenCalledTimes(2);
    expect(navigateMock).toHaveBeenCalledWith("/projects/project-42");
  });

  it.each([
    null,
    {},
    { candidates },
    { detail: null },
    { detail: "Invalid conversion response" },
    { detail: {} },
    { detail: { candidates: [] } },
    { detail: { candidates: "invalid" } },
    { detail: { candidates: [null] } },
    { detail: { candidates: [{ id: "", name: "Acme Corp", code: "AC-001" }] } },
    { detail: { candidates: [{ id: 42, name: "Acme Corp", code: "AC-001" }] } },
    { detail: { candidates: [{ id: candidates[0].id, name: {}, code: "AC-001" }] } },
    { detail: { candidates: [candidates[0], { id: candidates[1].id }] } },
  ])("surfaces malformed HTTP 300 responses: %j", async (body) => {
    const user = userEvent.setup();
    const error = new ApiError(300, body);
    convertMutationMock.mutateAsync.mockRejectedValue(error);
    convertMutationMock.isError = true;
    convertMutationMock.error = error;
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    expect(screen.getByText(`Conversion failed: ${error.message}`)).toBeInTheDocument();
    expect(screen.queryByRole("radio")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^convert$/i })).toBeEnabled();
    expect(navigateMock).not.toHaveBeenCalled();
  });

  it("requires a fresh selection if the API returns candidates again", async () => {
    const user = userEvent.setup();
    convertMutationMock.mutateAsync.mockRejectedValue(new ApiError(300, ambiguousBody));
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));
    await user.click(screen.getByRole("radio", { name: /AC-001/ }));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    expect(screen.getByRole("radio", { name: /AC-001/ })).not.toBeChecked();
    expect(screen.getByRole("button", { name: /^convert$/i })).toBeDisabled();
    expect(convertMutationMock.mutateAsync).toHaveBeenCalledTimes(2);
    expect(navigateMock).not.toHaveBeenCalled();
  });

  it("disables convert while the mutation is pending", () => {
    convertMutationMock.isPending = true;
    renderButton();

    const btn = screen.getByRole("button", { name: /convert to project/i });
    expect(btn).toBeDisabled();
  });

  it.each([
    new Error("boom"),
    new ApiError(409, { detail: "Inquiry already converted" }),
    new ApiError(500, ambiguousBody),
  ])("preserves non-300 errors inline: %s", async (error) => {
    const user = userEvent.setup();
    convertMutationMock.mutateAsync.mockRejectedValue(error);
    convertMutationMock.isError = true;
    convertMutationMock.error = error;
    renderButton();

    await user.click(screen.getByRole("button", { name: /convert to project/i }));
    await user.click(screen.getByRole("button", { name: /^convert$/i }));

    expect(screen.getByText(`Conversion failed: ${error.message}`)).toBeInTheDocument();
    expect(screen.queryByRole("radio")).not.toBeInTheDocument();
    expect(navigateMock).not.toHaveBeenCalled();
  });
});