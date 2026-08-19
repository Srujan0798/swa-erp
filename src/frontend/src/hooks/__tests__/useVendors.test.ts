import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useVendors,
  useVendor,
  useCreateVendor,
  useUpdateVendor,
  useDeleteVendor,
  useAddVendorContact,
  useDeleteVendorContact,
  useMaterials,
  useMaterial,
  useMaterialCategories,
  useCreateMaterial,
  useUpdateMaterial,
  useDeleteMaterial,
  useCreateMaterialCategory,
} from "../useVendors";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    listVendors: vi.fn(),
    getVendor: vi.fn(),
    createVendor: vi.fn(),
    updateVendor: vi.fn(),
    deleteVendor: vi.fn(),
    addVendorContact: vi.fn(),
    deleteVendorContact: vi.fn(),
    listMaterials: vi.fn(),
    getMaterial: vi.fn(),
    listMaterialCategories: vi.fn(),
    createMaterial: vi.fn(),
    updateMaterial: vi.fn(),
    deleteMaterial: vi.fn(),
    createMaterialCategory: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

const mockVendor = {
  id: "vendor-1",
  name: "Steel Supply Co",
  code: "VEND-001",
  email: "contact@steel.com",
  phone: "+91-9999999999",
  address: "Mumbai",
  city: "Mumbai",
  state: "Maharashtra",
  gst_number: "27ABCDE1234F1Z5",
  pan_number: "ABCDE1234F",
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  contacts: [],
};

const mockMaterial = {
  id: "mat-1",
  name: "TMT Steel",
  code: "MAT-001",
  description: "TMT bars",
  category_id: "cat-1",
  category_name: "Materials",
  unit: "kg",
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
};

const mockCategory = {
  id: "cat-1",
  name: "Materials",
  parent_id: null,
  children: [],
};

const mockContact = {
  id: "contact-1",
  vendor_id: "vendor-1",
  name: "John Smith",
  designation: "Sales",
  email: "john@steel.com",
  phone: "+91-8888888888",
  is_primary: true,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
};

describe("useVendors", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated vendors", async () => {
    const response = { items: [mockVendor], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listVendors).mockResolvedValue(response);

    const { result } = renderHook(() => useVendors({ page: 1, page_size: 20 }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listVendors).toHaveBeenCalledWith({ page: 1, page_size: 20 });
  });
});

describe("useVendor", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single vendor by id", async () => {
    vi.mocked(api.getVendor).mockResolvedValue(mockVendor);

    const { result } = renderHook(() => useVendor("vendor-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockVendor);
    expect(api.getVendor).toHaveBeenCalledWith("vendor-1");
  });

  it("does not fetch when id is empty", () => {
    renderHook(() => useVendor(""), { wrapper: createWrapper() });
    expect(api.getVendor).not.toHaveBeenCalled();
  });
});

describe("useCreateVendor", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates vendor and invalidates list", async () => {
    vi.mocked(api.createVendor).mockResolvedValue(mockVendor);

    const { result } = renderHook(() => useCreateVendor(), { wrapper: createWrapper() });

    result.current.mutate({ name: "Steel Supply Co", code: "VEND-001" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createVendor).toHaveBeenCalledWith({ name: "Steel Supply Co", code: "VEND-001" });
  });
});

describe("useUpdateVendor", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates vendor by id", async () => {
    vi.mocked(api.updateVendor).mockResolvedValue({ ...mockVendor, name: "Updated Name" });

    const { result } = renderHook(() => useUpdateVendor(), { wrapper: createWrapper() });

    result.current.mutate({ id: "vendor-1", data: { name: "Updated Name" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateVendor).toHaveBeenCalledWith("vendor-1", { name: "Updated Name" });
  });
});

describe("useDeleteVendor", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes vendor by id", async () => {
    vi.mocked(api.deleteVendor).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteVendor(), { wrapper: createWrapper() });

    result.current.mutate("vendor-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteVendor).toHaveBeenCalledWith("vendor-1", expect.anything());
  });
});

describe("useAddVendorContact", () => {
  beforeEach(() => vi.clearAllMocks());

  it("adds contact to vendor", async () => {
    vi.mocked(api.addVendorContact).mockResolvedValue(mockContact);

    const { result } = renderHook(() => useAddVendorContact(), { wrapper: createWrapper() });

    result.current.mutate({ vendorId: "vendor-1", data: { name: "John Smith", email: "john@steel.com" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.addVendorContact).toHaveBeenCalledWith("vendor-1", {
      name: "John Smith",
      email: "john@steel.com",
    });
  });
});

describe("useDeleteVendorContact", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes vendor contact", async () => {
    vi.mocked(api.deleteVendorContact).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteVendorContact(), { wrapper: createWrapper() });

    result.current.mutate({ vendorId: "vendor-1", contactId: "contact-1" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteVendorContact).toHaveBeenCalledWith("vendor-1", "contact-1");
  });
});

describe("useMaterials", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches paginated materials", async () => {
    const response = { items: [mockMaterial], total: 1, page: 1, page_size: 20 };
    vi.mocked(api.listMaterials).mockResolvedValue(response);

    const { result } = renderHook(() => useMaterials({ page: 1, page_size: 20 }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(response);
    expect(api.listMaterials).toHaveBeenCalledWith({ page: 1, page_size: 20 });
  });
});

describe("useMaterial", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches single material by id", async () => {
    vi.mocked(api.getMaterial).mockResolvedValue(mockMaterial);

    const { result } = renderHook(() => useMaterial("mat-1"), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockMaterial);
    expect(api.getMaterial).toHaveBeenCalledWith("mat-1");
  });

  it("does not fetch when id is empty", () => {
    renderHook(() => useMaterial(""), { wrapper: createWrapper() });
    expect(api.getMaterial).not.toHaveBeenCalled();
  });
});

describe("useMaterialCategories", () => {
  beforeEach(() => vi.clearAllMocks());

  it("fetches material categories", async () => {
    vi.mocked(api.listMaterialCategories).mockResolvedValue([mockCategory]);

    const { result } = renderHook(() => useMaterialCategories(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([mockCategory]);
    expect(api.listMaterialCategories).toHaveBeenCalled();
  });
});

describe("useCreateMaterial", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates material and invalidates list", async () => {
    vi.mocked(api.createMaterial).mockResolvedValue(mockMaterial);

    const { result } = renderHook(() => useCreateMaterial(), { wrapper: createWrapper() });

    result.current.mutate({ name: "TMT Steel", code: "MAT-001" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createMaterial).toHaveBeenCalledWith({ name: "TMT Steel", code: "MAT-001" });
  });
});

describe("useUpdateMaterial", () => {
  beforeEach(() => vi.clearAllMocks());

  it("updates material by id", async () => {
    vi.mocked(api.updateMaterial).mockResolvedValue({ ...mockMaterial, name: "Updated" });

    const { result } = renderHook(() => useUpdateMaterial(), { wrapper: createWrapper() });

    result.current.mutate({ id: "mat-1", data: { name: "Updated" } });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateMaterial).toHaveBeenCalledWith("mat-1", { name: "Updated" });
  });
});

describe("useDeleteMaterial", () => {
  beforeEach(() => vi.clearAllMocks());

  it("deletes material by id", async () => {
    vi.mocked(api.deleteMaterial).mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteMaterial(), { wrapper: createWrapper() });

    result.current.mutate("mat-1");
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteMaterial).toHaveBeenCalledWith("mat-1", expect.anything());
  });
});

describe("useCreateMaterialCategory", () => {
  beforeEach(() => vi.clearAllMocks());

  it("creates material category and invalidates list", async () => {
    vi.mocked(api.createMaterialCategory).mockResolvedValue(mockCategory);

    const { result } = renderHook(() => useCreateMaterialCategory(), { wrapper: createWrapper() });

    result.current.mutate({ name: "Materials" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createMaterialCategory).toHaveBeenCalledWith({ name: "Materials" });
  });
});
