import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useDocuments(projectId: string, folderId?: string, page = 1, pageSize = 50) {
  return useQuery({
    queryKey: ["documents", projectId, folderId, page, pageSize],
    queryFn: () => api.listDocuments(projectId, { folder_id: folderId, page, page_size: pageSize }),
    enabled: !!projectId,
  });
}

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ["document", documentId],
    queryFn: () => api.getDocument(documentId),
    enabled: !!documentId,
  });
}

export function useUploadDocument(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ file, folderId, tags }: { file: File; folderId?: string; tags?: string[] }) =>
      api.uploadDocument(projectId, file, folderId, tags),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
    },
  });
}

export function useDeleteDocument(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
    },
  });
}

export function useRenameDocument(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ documentId, name }: { documentId: string; name: string }) =>
      api.renameDocument(documentId, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
    },
  });
}

export function useMoveDocuments(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ documentIds, folderId }: { documentIds: string[]; folderId: string | null }) =>
      api.moveDocuments(documentIds, folderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
    },
  });
}

export function useSearchDocuments(projectId: string, query: string, tags?: string, folderId?: string) {
  return useQuery({
    queryKey: ["documents", "search", projectId, query, tags, folderId],
    queryFn: () => api.searchDocuments(projectId, { q: query, tags, folder_id: folderId }),
    enabled: !!projectId && (!!query || !!tags),
  });
}

export function useFolders(projectId: string, parentId?: string) {
  return useQuery({
    queryKey: ["folders", projectId, parentId],
    queryFn: () => api.listFolders(projectId, parentId),
    enabled: !!projectId,
  });
}

export function useCreateFolder(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ name, parentId }: { name: string; parentId?: string }) =>
      api.createFolder(projectId, { name, parent_id: parentId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["folders", projectId] });
    },
  });
}

export function useDeleteFolder(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteFolder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["folders", projectId] });
      queryClient.invalidateQueries({ queryKey: ["documents", projectId] });
    },
  });
}
