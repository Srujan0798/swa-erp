/* eslint-disable @typescript-eslint/no-explicit-any */import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { api } from "@/lib/api";

const useCurrentUserMock = vi.hoisted(() => vi.fn());

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/lib/api", () => ({
  api: {
    listMaterials: vi.fn(),
    listMaterialCategories: vi.fn(),
    createMaterial: vi.fn(),
    deleteMaterial: vi.fn(),
  },
}));

const material = {
  id: "m1",
  name: "Steel Beam",
  unit: "kg",
  category_name: "Structural",
  description: "Heavy duty",
};
const category = { id: "cat1", name: "Structural" };

async function renderPage() {
  const { MaterialsPage } = await import("@/pages/MaterialsPage");
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MaterialsPage />
    </QueryClientProvider>
  );
}

describe("MaterialsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useCurrentUserMock.mockReturnValue({ data: { role: "pm" } });
    vi.mocked(api.listMaterials).mockResolvedValue({ items: [], total: 0 } as never);
    vi.mocked(api.listMaterialCategories).mockResolvedValue([category] as never);
  });

  it("renders header", async () => {
    await renderPage();
    expect(screen.getByText("Materials")).toBeInTheDocument();
    expect(screen.getByText(/Manage material catalog/)).toBeInTheDocument();
  });

  it("shows New Material button for write users", async () => {
    await renderPage();
    expect(screen.getByText("New Material")).toBeInTheDocument();
  });

  it("hides New Material for viewer users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage();
    expect(screen.queryByText("New Material")).not.toBeInTheDocument();
  });

  it("displays materials in table", async () => {
    vi.mocked(api.listMaterials).mockResolvedValue({ items: [material], total: 1 } as never);
    await renderPage();
    expect(await screen.findByText("Steel Beam")).toBeInTheDocument();
    expect(screen.getByText("kg")).toBeInTheDocument();
  });

  it("shows loading state", async () => {
    vi.mocked(api.listMaterials).mockReturnValue(new Promise(() => {}));
    await renderPage();
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("shows error banner", async () => {
    vi.mocked(api.listMaterials).mockRejectedValue(new Error("boom"));
    await renderPage();
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  it("shows empty state for writer", async () => {
    await renderPage();
    expect(await screen.findByText(/No materials yet/)).toBeInTheDocument();
    expect(screen.getByText("Create the first material")).toBeInTheDocument();
  });

  it("shows empty state for viewer without create link", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    await renderPage();
    expect(await screen.findByText(/No materials yet/)).toBeInTheDocument();
    expect(screen.queryByText("Create the first material")).not.toBeInTheDocument();
  });

  it("opens create material dialog", async () => {
    await renderPage();
    await userEvent.click(screen.getByText("New Material"));
    expect(screen.getByText("Description")).toBeInTheDocument();
  });

  it("shows search input", async () => {
    await renderPage();
    expect(screen.getByPlaceholderText("Search materials...")).toBeInTheDocument();
  });

  it("shows category filter", async () => {
    await renderPage();
    expect(screen.getByText("All categories")).toBeInTheDocument();
  });

  it("shows delete button for write users", async () => {
    vi.mocked(api.listMaterials).mockResolvedValue({ items: [material], total: 1 } as never);
    await renderPage();
    expect(await screen.findByText("Delete")).toBeInTheDocument();
  });

  it("hides delete button for viewer users", async () => {
    useCurrentUserMock.mockReturnValue({ data: { role: "viewer" } });
    vi.mocked(api.listMaterials).mockResolvedValue({ items: [material], total: 1 } as never);
    await renderPage();
    expect(await screen.findByText("Steel Beam")).toBeInTheDocument();
    expect(screen.queryByText("Delete")).not.toBeInTheDocument();
  });

  it("shows uncategorized for material without category", async () => {
    vi.mocked(api.listMaterials).mockResolvedValue({
      items: [{ ...material, category_name: null }],
      total: 1,
    } as never);
    await renderPage();
    expect(await screen.findByText("Uncategorized")).toBeInTheDocument();
  });
});
