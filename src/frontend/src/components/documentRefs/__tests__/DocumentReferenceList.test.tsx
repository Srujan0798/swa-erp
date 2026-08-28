import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DocumentReferenceList } from "../DocumentReferenceList";
import type { DocumentReference } from "@/types/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());
const useDocumentReferencesMock = vi.hoisted(() => vi.fn());
const createMutationMock = vi.hoisted(() => ({ mutateAsync: vi.fn(), isPending: false }));
const deleteMutationMock = vi.hoisted(() => ({ mutate: vi.fn(), isPending: false }));
const toastMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/hooks/useDocumentReferences", () => ({
  useDocumentReferences: () => useDocumentReferencesMock(),
  useCreateDocumentReference: () => createMutationMock,
  useDeleteDocumentReference: () => deleteMutationMock,
}));

vi.mock("@/hooks/useToast", () => ({
  useToast: () => ({ toast: toastMock }),
}));

vi.mock("@/components/documentRefs/DocumentReferenceForm", () => ({
  DocumentReferenceForm: ({
    onSubmit,
    onCancel,
  }: {
    onSubmit: (data: { doc_date: string; document_type: string }) => Promise<void>;
    onCancel: () => void;
  }) => (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ doc_date: "2026-01-01", document_type: "Drawing" });
      }}
    >
      <button type="submit">Submit DocRef</button>
      <button type="button" onClick={onCancel}>
        Cancel Form
      </button>
    </form>
  ),
}));

const docRef: DocumentReference = {
  id: "dr-1",
  reference_id: "SWA-DR-001",
  project_id: "p-1",
  token_id: null,
  doc_date: "2026-01-05",
  document_type: "Drawing",
  type: "As-Built",
  author_id: null,
  author_name: null,
  user_ref: "Ravi",
  description: "Floor plan",
  revision: "R1",
  status: "Issued",
  remarks: null,
  created_at: "2026-01-05T00:00:00Z",
  updated_at: "2026-01-05T00:00:00Z",
};

function renderList(role: string | undefined, tokenId?: string) {
  useCurrentUserMock.mockReturnValue({ data: role ? { role } : undefined });
  useDocumentReferencesMock.mockReturnValue({
    data: { items: [docRef], total: 1, page: 1, page_size: 100 },
    isLoading: false,
  });
  return render(<DocumentReferenceList projectId="p-1" tokenId={tokenId} />);
}

describe("DocumentReferenceList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    createMutationMock.mutateAsync.mockResolvedValue(undefined);
  });

  it("shows the New Document Reference button for writers and hides it for viewers", () => {
    const { unmount } = renderList("designer");
    expect(screen.getByRole("button", { name: /new document reference/i })).toBeInTheDocument();
    unmount();

    renderList("viewer");
    expect(screen.queryByRole("button", { name: /new document reference/i })).not.toBeInTheDocument();
  });

  it("renders document reference details", () => {
    renderList("pm");
    expect(screen.getByText("SWA-DR-001")).toBeInTheDocument();
    expect(screen.getByText("Drawing")).toBeInTheDocument();
    expect(screen.getByText("R1")).toBeInTheDocument();
    expect(screen.getByText("Issued")).toBeInTheDocument();
    expect(screen.getByText("2026-01-05 · Ravi · As-Built")).toBeInTheDocument();
  });

  it("creates a document reference and shows a toast", async () => {
    const user = userEvent.setup();
    renderList("pm");

    await user.click(screen.getByRole("button", { name: /new document reference/i }));
    await user.click(screen.getByRole("button", { name: "Submit DocRef" }));

    expect(createMutationMock.mutateAsync).toHaveBeenCalledWith(
      expect.objectContaining({ project_id: "p-1", document_type: "Drawing" })
    );
    expect(toastMock).toHaveBeenCalledWith({ title: "Document reference created" });
  });

  it("deletes a document reference after confirmation", async () => {
    const user = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(true);
    renderList("admin");

    await user.click(screen.getByRole("button", { name: /delete document reference/i }));
    expect(deleteMutationMock.mutate).toHaveBeenCalledWith("dr-1");
  });

  it("renders loading and empty states", () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    useDocumentReferencesMock.mockReturnValue({ data: undefined, isLoading: true });
    const { unmount } = render(<DocumentReferenceList projectId="p-1" />);
    expect(screen.getByText("Loading document references...")).toBeInTheDocument();
    unmount();

    useDocumentReferencesMock.mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 100 },
      isLoading: false,
    });
    render(<DocumentReferenceList projectId="p-1" />);
    expect(screen.getByText("No document references yet.")).toBeInTheDocument();
  });
});