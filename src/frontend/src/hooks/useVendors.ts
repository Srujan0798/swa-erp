import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Vendor, VendorContact, Material, MaterialCategory } from "@/types/api";

export function useVendors(params?: { page?: number; page_size?: number; q?: string }) {
  return useQuery({
    queryKey: ["vendors", params],
    queryFn: () => api.listVendors(params),
  });
}

export function useVendor(id: string) {
  return useQuery({
    queryKey: ["vendor", id],
    queryFn: () => api.getVendor(id),
    enabled: !!id,
  });
}

export function useCreateVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Vendor>) => api.createVendor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vendors"] });
    },
  });
}

export function useUpdateVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Vendor> }) =>
      api.updateVendor(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["vendors"] });
      queryClient.invalidateQueries({ queryKey: ["vendor", variables.id] });
    },
  });
}

export function useDeleteVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteVendor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vendors"] });
    },
  });
}

export function useAddVendorContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ vendorId, data }: { vendorId: string; data: Partial<VendorContact> }) =>
      api.addVendorContact(vendorId, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["vendor", variables.vendorId] });
    },
  });
}

export function useDeleteVendorContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ vendorId, contactId }: { vendorId: string; contactId: string }) =>
      api.deleteVendorContact(vendorId, contactId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["vendor", variables.vendorId] });
    },
  });
}

export function useMaterials(params?: { page?: number; page_size?: number; q?: string; category_id?: string }) {
  return useQuery({
    queryKey: ["materials", params],
    queryFn: () => api.listMaterials(params),
  });
}

export function useMaterial(id: string) {
  return useQuery({
    queryKey: ["material", id],
    queryFn: () => api.getMaterial(id),
    enabled: !!id,
  });
}

export function useMaterialCategories() {
  return useQuery({
    queryKey: ["material-categories"],
    queryFn: api.listMaterialCategories,
  });
}

export function useCreateMaterial() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Material>) => api.createMaterial(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["materials"] });
    },
  });
}

export function useUpdateMaterial() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Material> }) =>
      api.updateMaterial(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["materials"] });
      queryClient.invalidateQueries({ queryKey: ["material", variables.id] });
    },
  });
}

export function useDeleteMaterial() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteMaterial,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["materials"] });
    },
  });
}

export function useCreateMaterialCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<MaterialCategory>) => api.createMaterialCategory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["material-categories"] });
    },
  });
}
