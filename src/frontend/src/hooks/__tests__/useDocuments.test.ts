import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useDocuments,
  useDocument,
  useUploadDocument,
  useDeleteDocument,
  useRenameDocument,
  useMoveDocuments,
  useSearchDocuments,
  useFolders,
  useCreateFolder,
  useDeleteFolder,
} from "../useDocuments";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listDocuments: vi.fn(),
    getDocument: vi.fn(),
    uploadDocument: vi.fn(),
    deleteDocument: vi.fn(),
    renameDocument: vi.fn(),
    moveDocuments: vi.fn(),
    searchDocuments: vi.fn(),
    listFolders: vi.fn(),
    createFolder: vi.fn(),
    deleteFolder: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockDocument = {
  id: "doc-1",
  project_id: "proj-1",
  folder_id: null,
  name: "drawing.pdf",
  file_name: "drawing.pdf",
  size: 1024,
  mime_type: "application/pdf",
  path: "/uploads/drawing.pdf",
  created_at: "2025-01-01T00:00:00Z",
  created_by: "user-1",
};

const mockFolder = {
  id: "folder-1",
  project_id: "proj-1",
  name: "Drawings",
  parent_id: null,
  created_at: "2025-01-01T00:00:00Z",
};

describe("useDocuments", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches documents for project", async () => {
    const response = { items: [mockDocument], total: 1, page: 1, page_size: 50 };
    vi.mocked(api.listDocuments).mockResolvedValue(response);

    const { result } = renderHook(() => useDocuments("proj-1", undefined, 1, 50), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listDocuments).toHaveBeenCalledWith("proj-1", {
      folder_id: undefined,
      page: 1,
      page_size: 50,
    });
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useDocuments("", undefined, 1, 50), { wrapper: createWrapper() });
    expect(api.listDocuments).not.toHaveBeenCalled();
  });
});

describe("useDocument", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single document by id", async () => {
    vi.mocked(api.getDocument).mockResolvedValue(mockDocument);

    const { result } = renderHook(() => useDocument("doc-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockDocument);
    expect(api.getDocument).toHaveBeenCalledWith("doc-1");
  });

  it("does not fetch when documentId is empty", () => {
    renderHook(() => useDocument(""), { wrapper: createWrapper() });
    expect(api.getDocument).not.toHaveBeenCalled();
  });
});

describe("useUploadDocument", () => {
  beforeEach(() => vi.clearAllMocks());

  it("uploads document with file", async () => {
    const file = new File(["content"], "doc.pdf", { type: "application/pdf" });
    vi.mocked(api.uploadDocument).mockResolvedValue(mockDocument);

    const { result } = renderHook(() => useUploadDocument("proj-1"), { wrapper: createWrapper() });

    result.current.mutate({ file, folderId: "folder-1", tags: ["drawings"] });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.uploadDocument).toHaveBeenCalledWith("proj-1", file, "folder-1", ["drawings"]);
  });
});

describe("useDeleteDocument", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes document by id", async () => {
    vi.mocked(api.deleteDocument).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteDocument("proj-1"), { wrapper: createWrapper() });

    result.current.mutate("doc-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteDocument).toHaveBeenCalledWith("doc-1", expect.anything());
  });
});

describe("useRenameDocument", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renames document", async () => {
    vi.mocked(api.renameDocument).mockResolvedValue({ ...mockDocument, name: "renamed.pdf" });

    const { result } = renderHook(() => useRenameDocument("proj-1"), { wrapper: createWrapper() });

    result.current.mutate({ documentId: "doc-1", name: "renamed.pdf" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.renameDocument).toHaveBeenCalledWith("doc-1", "renamed.pdf");
  });
});

describe("useMoveDocuments", () => {
  beforeEach(() => vi.clearAllMocks());

  it("moves documents to folder", async () => {
    const response = { message: "Moved" };
    vi.mocked(api.moveDocuments).mockResolvedValue(response);

    const { result } = renderHook(() => useMoveDocuments("proj-1"), { wrapper: createWrapper() });

    result.current.mutate({ documentIds: ["doc-1", "doc-2"], folderId: "folder-1" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.moveDocuments).toHaveBeenCalledWith(["doc-1", "doc-2"], "folder-1");
  });

  it("moves documents to root (null folder)", async () => {
    const response = { message: "Moved" };
    vi.mocked(api.moveDocuments).mockResolvedValue(response);

    const { result } = renderHook(() => useMoveDocuments("proj-1"), { wrapper: createWrapper() });

    result.current.mutate({ documentIds: ["doc-1"], folderId: null });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.moveDocuments).toHaveBeenCalledWith(["doc-1"], null);
  });
});

describe("useSearchDocuments", () => {
  beforeEach(() => vi.clearAllMocks());

  it("searches documents with query", async () => {
    const response = { items: [mockDocument], total: 1, page: 1, page_size: 10 };
    vi.mocked(api.searchDocuments).mockResolvedValue(response);

    const { result } = renderHook(() => useSearchDocuments("proj-1", "drawing"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.searchDocuments).toHaveBeenCalledWith("proj-1", {
      q: "drawing",
      tags: undefined,
      folder_id: undefined,
    });
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useSearchDocuments("", "drawing"), { wrapper: createWrapper() });
    expect(api.searchDocuments).not.toHaveBeenCalled();
  });

  it("does not fetch when query and tags are empty", () => {
    renderHook(() => useSearchDocuments("proj-1", ""), { wrapper: createWrapper() });
    expect(api.searchDocuments).not.toHaveBeenCalled();
  });
});

describe("useFolders", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches folders for project", async () => {
    vi.mocked(api.listFolders).mockResolvedValue([mockFolder]);

    const { result } = renderHook(() => useFolders("proj-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([mockFolder]);
    expect(api.listFolders).toHaveBeenCalledWith("proj-1", undefined);
  });

  it("does not fetch when projectId is empty", () => {
    renderHook(() => useFolders(""), { wrapper: createWrapper() });
    expect(api.listFolders).not.toHaveBeenCalled();
  });
});

describe("useCreateFolder", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates folder with name", async () => {
    vi.mocked(api.createFolder).mockResolvedValue(mockFolder);

    const { result } = renderHook(() => useCreateFolder("proj-1"), { wrapper: createWrapper() });

    result.current.mutate({ name: "Drawings" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createFolder).toHaveBeenCalledWith("proj-1", { name: "Drawings", parent_id: undefined });
  });
});

describe("useDeleteFolder", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes folder by id", async () => {
    vi.mocked(api.deleteFolder).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteFolder("proj-1"), { wrapper: createWrapper() });

    result.current.mutate("folder-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteFolder).toHaveBeenCalledWith("folder-1", expect.anything());
  });
});
