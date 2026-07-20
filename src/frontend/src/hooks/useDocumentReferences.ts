import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { DocumentReferenceCreate, DocumentReferenceUpdate } from "@/types/api";

export function useDocumentReferences(params?: { page?: number; page_size?: number; project_id?: string; token_id?: string; document_type?: string; q?: string }) {
  return useQuery({
    queryKey: ["document-references", params],
    queryFn: () => api.listDocumentReferences(params),
  });
}

export function useDocumentReference(id: string | undefined) {
  return useQuery({
    queryKey: ["document-reference", id],
    queryFn: () => api.getDocumentReference(id!),
    enabled: !!id,
  });
}

export function useCreateDocumentReference() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DocumentReferenceCreate) => api.createDocumentReference(data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["document-references"] });
      queryClient.invalidateQueries({ queryKey: ["project-document-references", variables.project_id] });
    },
  });
}

export function useUpdateDocumentReference() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DocumentReferenceUpdate }) =>
      api.updateDocumentReference(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["document-references"] });
      queryClient.invalidateQueries({ queryKey: ["document-reference", variables.id] });
    },
  });
}

export function useDeleteDocumentReference() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteDocumentReference(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["document-references"] });
    },
  });
}
