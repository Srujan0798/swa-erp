import { describe, it, expect, vi, beforeEach } from "vitest";
import { api } from "@/lib/api";

const fetchMock = vi.hoisted(() => vi.fn());
vi.stubGlobal("fetch", fetchMock);

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function getFetchOptions(): RequestInit {
  return fetchMock.mock.calls[0][1] as RequestInit;
}

describe("api request core", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it("sends requests without an Authorization header when no token", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ id: "u1" }));
    const user = await api.me();
    expect(user).toEqual({ id: "u1" });
    expect(getFetchOptions().headers).not.toHaveProperty("Authorization");
  });

  it("includes the Bearer token when present", async () => {
    localStorage.setItem("access_token", "tok-1");
    fetchMock.mockResolvedValue(jsonResponse({ id: "u1" }));
    await api.me();
    const headers = getFetchOptions().headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer tok-1");
  });

  it("throws ApiError with parsed body on non-OK responses", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ detail: "Not found" }, 404));
    await expect(api.me()).rejects.toMatchObject({
      status: 404,
      body: { detail: "Not found" },
    });
  });

  it("throws ApiError with null body when response JSON is unparseable", async () => {
    fetchMock.mockResolvedValue(new Response("oops", { status: 500 }));
    await expect(api.me()).rejects.toMatchObject({ status: 500, body: null });
  });

  it("refreshes the token on 401 and retries the original request", async () => {
    localStorage.setItem("access_token", "expired");
    localStorage.setItem("refresh_token", "refresh-1");

    fetchMock
      .mockResolvedValueOnce(jsonResponse({ detail: "expired" }, 401))
      .mockResolvedValueOnce(jsonResponse({ access_token: "new-access" }))
      .mockResolvedValueOnce(jsonResponse({ id: "u1" }));

    const user = await api.me();
    expect(user).toEqual({ id: "u1" });
    expect(localStorage.getItem("access_token")).toBe("new-access");
    expect(localStorage.getItem("refresh_token")).toBe("refresh-1");
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("clears tokens and redirects to login when refresh fails", async () => {
    localStorage.setItem("access_token", "expired");
    localStorage.setItem("refresh_token", "refresh-1");

    const originalLocation = window.location;
    Object.defineProperty(window, "location", {
      value: { href: "http://localhost/" },
      writable: true,
    });

    fetchMock
      .mockResolvedValueOnce(jsonResponse({ detail: "expired" }, 401))
      .mockResolvedValueOnce(jsonResponse({ detail: "bad refresh" }, 400));

    await expect(api.me()).rejects.toMatchObject({ status: 401 });
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
    expect(window.location.href).toBe("/login");

    Object.defineProperty(window, "location", { value: originalLocation, writable: true });
  });

  it("redirects to login when the refresh request itself throws", async () => {
    localStorage.setItem("access_token", "expired");
    localStorage.setItem("refresh_token", "refresh-1");

    const originalLocation = window.location;
    Object.defineProperty(window, "location", {
      value: { href: "http://localhost/" },
      writable: true,
    });

    fetchMock
      .mockResolvedValueOnce(jsonResponse({ detail: "expired" }, 401))
      .mockRejectedValueOnce(new Error("network down"));

    await expect(api.me()).rejects.toMatchObject({ status: 401 });
    expect(window.location.href).toBe("/login");

    Object.defineProperty(window, "location", { value: originalLocation, writable: true });
  });
});

describe("api endpoint methods", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    fetchMock.mockImplementation(() => Promise.resolve(jsonResponse({ ok: true })));
  });

  it("auth: login, refresh, logout, me", async () => {
    fetchMock.mockImplementation(() => Promise.resolve(jsonResponse({ access_token: "a", refresh_token: "r", user: {} })));
    await api.login({ email: "e@swa.com", password: "p" });
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/login", expect.objectContaining({ method: "POST" }));

    await api.refresh("r");
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/refresh", expect.objectContaining({ method: "POST" }));

    await api.logout();
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/logout", expect.objectContaining({ method: "POST" }));

    await api.me();
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/me", expect.anything());
  });

  it("users: list, listAssignees, create, get, update, delete", async () => {
    await api.listUsers({ page: 2, page_size: 10, q: "priya", role: "admin" });
    expect(fetchMock).toHaveBeenCalledWith("/api/users?page=2&page_size=10&q=priya&role=admin", expect.anything());

    await api.listAssignees({ page_size: 5, q: "a", role: "pm" });
    expect(fetchMock).toHaveBeenCalledWith("/api/users/assignees?page_size=5&q=a&role=pm", expect.anything());

    await api.createUser({ email: "x@swa.com", name: "X", password: "p", role: "viewer" });
    expect(fetchMock).toHaveBeenCalledWith("/api/users", expect.objectContaining({ method: "POST" }));

    await api.getUser("u1");
    expect(fetchMock).toHaveBeenCalledWith("/api/users/u1", expect.anything());

    await api.updateUser("u1", { role: "pm" });
    expect(fetchMock).toHaveBeenCalledWith("/api/users/u1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteUser("u1");
    expect(fetchMock).toHaveBeenCalledWith("/api/users/u1", expect.objectContaining({ method: "DELETE" }));
  });

  it("projects: stats, list, get, create, update, transition", async () => {
    await api.getProjectStats();
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/stats", expect.anything());

    await api.listProjects({ page: 1, page_size: 20, q: "acme", status: "active", client_id: "c1" });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects?page=1&page_size=20&q=acme&status=active&client_id=c1", expect.anything());

    await api.getProject("p1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1", expect.anything());

    await api.createProject({ name: "P" });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects", expect.objectContaining({ method: "POST" }));

    await api.updateProject("p1", { name: "P2" });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1", expect.objectContaining({ method: "PATCH" }));

    await api.transitionProject("p1", "Design");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/transition", expect.objectContaining({ method: "POST" }));
  });

  it("clients: list, get, create, update, delete, contacts", async () => {
    await api.listClients({ page: 1, page_size: 20, q: "acme" });
    expect(fetchMock).toHaveBeenCalledWith("/api/clients?page=1&page_size=20&q=acme", expect.anything());

    await api.getClient("c1");
    expect(fetchMock).toHaveBeenCalledWith("/api/clients/c1", expect.anything());

    await api.createClient({ name: "Acme" });
    expect(fetchMock).toHaveBeenCalledWith("/api/clients", expect.objectContaining({ method: "POST" }));

    await api.updateClient("c1", { name: "Acme2" });
    expect(fetchMock).toHaveBeenCalledWith("/api/clients/c1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteClient("c1");
    expect(fetchMock).toHaveBeenCalledWith("/api/clients/c1", expect.objectContaining({ method: "DELETE" }));

    await api.addContact("c1", { name: "Ravi" });
    expect(fetchMock).toHaveBeenCalledWith("/api/clients/c1/contacts", expect.objectContaining({ method: "POST" }));

    await api.deleteContact("c1", "ct1");
    expect(fetchMock).toHaveBeenCalledWith("/api/clients/c1/contacts/ct1", expect.objectContaining({ method: "DELETE" }));
  });

  it("boqs: list, get, items, upload, delete", async () => {
    await api.listBoqs("p1", { page: 1, page_size: 20 });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/boqs?page=1&page_size=20", expect.anything());

    await api.getBoq("b1");
    expect(fetchMock).toHaveBeenCalledWith("/api/boqs/b1", expect.anything());

    await api.getBoqItems("b1", { page: 1, page_size: 10 });
    expect(fetchMock).toHaveBeenCalledWith("/api/boqs/b1/items?page=1&page_size=10", expect.anything());

    await api.deleteBoq("b1");
    expect(fetchMock).toHaveBeenCalledWith("/api/boqs/b1", expect.objectContaining({ method: "DELETE" }));

    fetchMock.mockResolvedValue(jsonResponse({ id: "b1" }));
    const boq = await api.uploadBoq("p1", new File(["a"], "b.xlsx"), "notes");
    expect(boq).toEqual({ id: "b1" });
    const [uploadUrl, uploadOpts] = fetchMock.mock.calls.at(-1) as [string, RequestInit];
    expect(uploadUrl).toBe("/api/projects/p1/boqs");
    expect(uploadOpts.method).toBe("POST");

    fetchMock.mockResolvedValue(jsonResponse({ detail: "bad" }, 400));
    await expect(api.uploadBoq("p1", new File(["a"], "b.xlsx"))).rejects.toMatchObject({ status: 400 });
  });

  it("quotes: list, get, create, update, delete, submit, approve, send, respond, clone, pdf", async () => {
    await api.listQuotes("p1", { page: 1, page_size: 20 });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/quotes?page=1&page_size=20", expect.anything());

    await api.getQuote("q1");
    expect(fetchMock).toHaveBeenCalledWith("/api/quotes/q1", expect.anything());

    await api.createQuote("p1", { boq_id: "b1", markup_percent: 10 });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/quotes", expect.objectContaining({ method: "POST" }));

    await api.updateQuote("q1", { terms: "NET 30" });
    expect(fetchMock).toHaveBeenCalledWith("/api/quotes/q1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteQuote("q1");
    expect(fetchMock).toHaveBeenCalledWith("/api/quotes/q1", expect.objectContaining({ method: "DELETE" }));

    await api.submitQuote("q1");
    expect(fetchMock).toHaveBeenCalledWith("/api/quotes/q1/submit", expect.objectContaining({ method: "POST" }));

    await api.approveQuote("q1");
    expect(fetchMock).toHaveBeenCalledWith("/api/quotes/q1/approve", expect.objectContaining({ method: "POST" }));

    await api.sendQuote("q1");
    expect(fetchMock).toHaveBeenCalledWith("/api/quotes/q1/send", expect.objectContaining({ method: "POST" }));

    await api.respondQuote("q1", { response: "accepted" });
    expect(fetchMock).toHaveBeenCalledWith("/api/quotes/q1/respond", expect.objectContaining({ method: "POST" }));

    await api.cloneQuote("q1");
    expect(fetchMock).toHaveBeenCalledWith("/api/quotes/q1/clone", expect.objectContaining({ method: "POST" }));

    localStorage.setItem("access_token", "tok");
    fetchMock.mockResolvedValue(jsonResponse({}));
    await api.downloadQuotePdf("q1");
    expect(fetchMock).toHaveBeenCalledWith("/api/quotes/q1/pdf", expect.objectContaining({ headers: { Authorization: "Bearer tok" } }));
  });

  it("tasks: list, get, create, update, delete, transition, reorder, bulk, assign, unassign, my-tasks, stats, comments", async () => {
    await api.listTasks("p1", { page: 1, page_size: 20, status: "todo", assignee_id: "u1", priority: "high" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/projects/p1/tasks?page=1&page_size=20&status=todo&assignee_id=u1&priority=high",
      expect.anything()
    );

    await api.getTask("t1");
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/t1", expect.anything());

    await api.createTask("p1", { title: "T" } as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/tasks", expect.objectContaining({ method: "POST" }));

    await api.updateTask("t1", { title: "T2" });
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/t1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteTask("t1");
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/t1", expect.objectContaining({ method: "DELETE" }));

    await api.transitionTask("t1", "in_progress");
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/t1/transition", expect.objectContaining({ method: "POST" }));

    await api.reorderTask("t1", "todo", 3);
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/t1/reorder", expect.objectContaining({ method: "POST" }));

    await api.bulkUpdateStatus({ task_ids: ["t1"], status: "done" } as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/bulk-status", expect.objectContaining({ method: "POST" }));

    await api.assignTask("t1", "u2");
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/t1/assign", expect.objectContaining({ method: "POST" }));

    await api.unassignTask("t1");
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/t1/unassign", expect.objectContaining({ method: "POST" }));

    await api.getMyTasks({ page: 1, page_size: 20, status: "todo", priority: "high" });
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/my-tasks?page=1&page_size=20&status=todo&priority=high", expect.anything());

    await api.getProjectTaskStats("p1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/tasks/stats", expect.anything());

    await api.addComment("t1", "hello");
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/t1/comments", expect.objectContaining({ method: "POST" }));

    await api.listComments("t1");
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/t1/comments", expect.anything());
  });

  it("vendors/materials: list, crud, contacts, categories", async () => {
    await api.listVendors({ page: 1, page_size: 20, q: "insul" });
    expect(fetchMock).toHaveBeenCalledWith("/api/vendors?page=1&page_size=20&q=insul", expect.anything());

    await api.getVendor("v1");
    expect(fetchMock).toHaveBeenCalledWith("/api/vendors/v1", expect.anything());

    await api.createVendor({ name: "V" });
    expect(fetchMock).toHaveBeenCalledWith("/api/vendors", expect.objectContaining({ method: "POST" }));

    await api.updateVendor("v1", { name: "V2" });
    expect(fetchMock).toHaveBeenCalledWith("/api/vendors/v1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteVendor("v1");
    expect(fetchMock).toHaveBeenCalledWith("/api/vendors/v1", expect.objectContaining({ method: "DELETE" }));

    await api.addVendorContact("v1", { name: "C" });
    expect(fetchMock).toHaveBeenCalledWith("/api/vendors/v1/contacts", expect.objectContaining({ method: "POST" }));

    await api.deleteVendorContact("v1", "c1");
    expect(fetchMock).toHaveBeenCalledWith("/api/vendors/v1/contacts/c1", expect.objectContaining({ method: "DELETE" }));

    await api.listMaterials({ page: 1, page_size: 20, q: "rock", category_id: "cat1" });
    expect(fetchMock).toHaveBeenCalledWith("/api/materials?page=1&page_size=20&q=rock&category_id=cat1", expect.anything());

    await api.getMaterial("m1");
    expect(fetchMock).toHaveBeenCalledWith("/api/materials/m1", expect.anything());

    await api.createMaterial({ name: "M" });
    expect(fetchMock).toHaveBeenCalledWith("/api/materials", expect.objectContaining({ method: "POST" }));

    await api.updateMaterial("m1", { name: "M2" });
    expect(fetchMock).toHaveBeenCalledWith("/api/materials/m1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteMaterial("m1");
    expect(fetchMock).toHaveBeenCalledWith("/api/materials/m1", expect.objectContaining({ method: "DELETE" }));

    await api.listMaterialCategories();
    expect(fetchMock).toHaveBeenCalledWith("/api/material-categories", expect.anything());

    await api.createMaterialCategory({ name: "Insulation" });
    expect(fetchMock).toHaveBeenCalledWith("/api/material-categories", expect.objectContaining({ method: "POST" }));
  });

  it("documents: list, get, upload, delete, rename, move, search, folders", async () => {
    await api.listDocuments("p1", { folder_id: "f1", page: 1, page_size: 20 });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/documents?folder_id=f1&page=1&page_size=20", expect.anything());

    await api.getDocument("d1");
    expect(fetchMock).toHaveBeenCalledWith("/api/documents/d1", expect.anything());

    fetchMock.mockImplementation(() => Promise.resolve(jsonResponse({ id: "d1" })));
    const doc = await api.uploadDocument("p1", new File(["x"], "a.pdf"), "f1", ["tag1"]);
    expect(doc).toEqual({ id: "d1" });

    fetchMock.mockResolvedValue(jsonResponse({ detail: "bad" }, 400));
    await expect(api.uploadDocument("p1", new File(["x"], "a.pdf"))).rejects.toMatchObject({ status: 400 });
    fetchMock.mockImplementation(() => Promise.resolve(jsonResponse({ ok: true })));

    await api.deleteDocument("d1");
    expect(fetchMock).toHaveBeenCalledWith("/api/documents/d1", expect.objectContaining({ method: "DELETE" }));

    await api.renameDocument("d1", "new.pdf");
    expect(fetchMock).toHaveBeenCalledWith("/api/documents/d1/rename", expect.objectContaining({ method: "PUT" }));

    await api.moveDocuments(["d1"], "f2");
    expect(fetchMock).toHaveBeenCalledWith("/api/documents/move", expect.objectContaining({ method: "PUT" }));

    await api.searchDocuments("p1", { q: "report", tags: "a", folder_id: "f1" });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/documents/search?q=report&tags=a&folder_id=f1", expect.anything());

    await api.listFolders("p1", "parent1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/folders?parent_id=parent1", expect.anything());

    await api.createFolder("p1", { name: "F" });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/folders", expect.objectContaining({ method: "POST" }));

    await api.deleteFolder("f1");
    expect(fetchMock).toHaveBeenCalledWith("/api/folders/f1", expect.objectContaining({ method: "DELETE" }));
  });

  it("time: list, create, update, delete, timesheets lifecycle", async () => {
    await api.listTimeEntries({ page: 1, page_size: 20, project_id: "p1", start_date: "2026-01-01", end_date: "2026-01-31" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/time-entries?page=1&page_size=20&project_id=p1&start_date=2026-01-01&end_date=2026-01-31",
      expect.anything()
    );

    await api.createTimeEntry({ project_id: "p1", date: "2026-01-05", hours: 2, description: "d", is_billable: true });
    expect(fetchMock).toHaveBeenCalledWith("/api/time-entries", expect.objectContaining({ method: "POST" }));

    await api.updateTimeEntry("te1", { hours: 3 });
    expect(fetchMock).toHaveBeenCalledWith("/api/time-entries/te1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteTimeEntry("te1");
    expect(fetchMock).toHaveBeenCalledWith("/api/time-entries/te1", expect.objectContaining({ method: "DELETE" }));

    await api.listTimesheets({ page: 1, page_size: 20, status: "submitted" });
    expect(fetchMock).toHaveBeenCalledWith("/api/timesheets?page=1&page_size=20&status=submitted", expect.anything());

    await api.getTimesheet("ts1");
    expect(fetchMock).toHaveBeenCalledWith("/api/timesheets/ts1", expect.anything());

    await api.generateTimesheet("2026-01-06");
    expect(fetchMock).toHaveBeenCalledWith("/api/timesheets", expect.objectContaining({ method: "POST" }));

    await api.submitTimesheet("ts1");
    expect(fetchMock).toHaveBeenCalledWith("/api/timesheets/ts1/submit", expect.objectContaining({ method: "POST" }));

    await api.approveTimesheet("ts1");
    expect(fetchMock).toHaveBeenCalledWith("/api/timesheets/ts1/approve", expect.objectContaining({ method: "POST" }));

    await api.rejectTimesheet("ts1");
    expect(fetchMock).toHaveBeenCalledWith("/api/timesheets/ts1/reject", expect.objectContaining({ method: "POST" }));
  });

  it("financials: invoices, pnl, costs", async () => {
    await api.listProjectInvoices("p1", { page: 1, page_size: 20, status: "sent" });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/invoices?page=1&page_size=20&status=sent", expect.anything());

    await api.getInvoice("i1");
    expect(fetchMock).toHaveBeenCalledWith("/api/invoices/i1", expect.anything());

    await api.createInvoice("p1", {} as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/invoices", expect.objectContaining({ method: "POST" }));

    await api.generateInvoiceFromTime("p1", "2026-01-01", "2026-01-31");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/invoices/generate-from-time", expect.objectContaining({ method: "POST" }));

    await api.updateInvoiceStatus("i1", "paid");
    expect(fetchMock).toHaveBeenCalledWith("/api/invoices/i1/status", expect.objectContaining({ method: "PATCH" }));

    await api.deleteInvoice("i1");
    expect(fetchMock).toHaveBeenCalledWith("/api/invoices/i1", expect.objectContaining({ method: "DELETE" }));

    await api.getProjectPnL("p1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/pnl", expect.anything());

    await api.listProjectCosts("p1", { page: 1, page_size: 20, category: "material" });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/costs?page=1&page_size=20&category=material", expect.anything());

    await api.addProjectCost("p1", {} as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/costs", expect.objectContaining({ method: "POST" }));

    await api.deleteProjectCost("p1", "cost1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/costs/cost1", expect.objectContaining({ method: "DELETE" }));
  });

  it("compliance: standards, checklist, summary, items, update, review, bulk", async () => {
    await api.listStandards();
    expect(fetchMock).toHaveBeenCalledWith("/api/compliance/standards", expect.anything());

    await api.getChecklistItems("s1");
    expect(fetchMock).toHaveBeenCalledWith("/api/compliance/standards/s1/checklist", expect.anything());

    await api.getComplianceSummary("p1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/compliance/summary", expect.anything());

    await api.listComplianceItems("p1", "s1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/compliance/items?standard_id=s1", expect.anything());

    await api.updateComplianceItem("item1", { status: "compliant" });
    expect(fetchMock).toHaveBeenCalledWith("/api/compliance/items/item1", expect.objectContaining({ method: "PATCH" }));

    await api.reviewComplianceItem("item1", { notes: "ok" });
    expect(fetchMock).toHaveBeenCalledWith("/api/compliance/items/item1/review", expect.objectContaining({ method: "POST" }));

    await api.bulkCreateComplianceItems("p1", "s1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/compliance/items/bulk/s1", expect.objectContaining({ method: "POST" }));
  });

  it("rfqs: list, get, create, send, respond, award, close, cancel, compare", async () => {
    await api.listProjectRfqs("p1", { page: 1, page_size: 20, status: "open" });
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/rfqs?page=1&page_size=20&status=open", expect.anything());

    await api.getRfq("r1");
    expect(fetchMock).toHaveBeenCalledWith("/api/rfqs/r1", expect.anything());

    await api.createRfq("p1", {} as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/rfqs", expect.objectContaining({ method: "POST" }));

    await api.sendRfq("r1");
    expect(fetchMock).toHaveBeenCalledWith("/api/rfqs/r1/send", expect.objectContaining({ method: "POST" }));

    await api.respondRfq("r1", { items: [] } as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/rfqs/r1/respond", expect.objectContaining({ method: "POST" }));

    await api.awardRfq("r1", { vendor_id: "v1" } as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/rfqs/r1/award", expect.objectContaining({ method: "POST" }));

    await api.closeRfq("r1");
    expect(fetchMock).toHaveBeenCalledWith("/api/rfqs/r1/close", expect.objectContaining({ method: "POST" }));

    await api.cancelRfq("r1");
    expect(fetchMock).toHaveBeenCalledWith("/api/rfqs/r1/cancel", expect.objectContaining({ method: "POST" }));

    await api.compareRfqs("p1", ["m1", "m2"]);
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/rfqs/compare?material_ids=m1%2Cm2", expect.anything());
  });

  it("sustainability: list, create, update, delete", async () => {
    await api.listSustainabilityMetrics("p1", "ref1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/sustainability/metrics?reference_id=ref1", expect.anything());

    await api.createSustainabilityMetric("p1", {} as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/sustainability/metrics", expect.objectContaining({ method: "POST" }));

    await api.updateSustainabilityMetric("p1", "m1", {} as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/sustainability/metrics/m1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteSustainabilityMetric("p1", "m1");
    expect(fetchMock).toHaveBeenCalledWith("/api/projects/p1/sustainability/metrics/m1", expect.objectContaining({ method: "DELETE" }));
  });

  it("inquiries: list, get, create, update, delete, convert", async () => {
    await api.listInquiries({ page: 1, page_size: 20, q: "acme", status: "New" });
    expect(fetchMock).toHaveBeenCalledWith("/api/inquiries?page=1&page_size=20&q=acme&status=New", expect.anything());

    await api.getInquiry("inq1");
    expect(fetchMock).toHaveBeenCalledWith("/api/inquiries/inq1", expect.anything());

    await api.createInquiry({ inquiry_date: "2026-01-01", client_name: "Acme" });
    expect(fetchMock).toHaveBeenCalledWith("/api/inquiries", expect.objectContaining({ method: "POST" }));

    await api.updateInquiry("inq1", { status: "Contacted" });
    expect(fetchMock).toHaveBeenCalledWith("/api/inquiries/inq1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteInquiry("inq1");
    expect(fetchMock).toHaveBeenCalledWith("/api/inquiries/inq1", expect.objectContaining({ method: "DELETE" }));

    await api.convertInquiry("inq1", { project_name: "Acme Project" });
    expect(fetchMock).toHaveBeenCalledWith("/api/inquiries/inq1/convert", expect.objectContaining({ method: "POST" }));
  });

  it("agreements/tokens: list, get, create, update, delete", async () => {
    await api.listAgreements({ page: 1, page_size: 20, client_id: "c1", status: "Active", q: "insu" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/service-agreements?page=1&page_size=20&client_id=c1&status=Active&q=insu",
      expect.anything()
    );

    await api.getAgreement("ag1");
    expect(fetchMock).toHaveBeenCalledWith("/api/service-agreements/ag1", expect.anything());

    await api.createAgreement({ client_id: "c1", service_name: "INSU", start_date: "2026-01-01" });
    expect(fetchMock).toHaveBeenCalledWith("/api/service-agreements", expect.objectContaining({ method: "POST" }));

    await api.updateAgreement("ag1", { service_name: "INSU2" });
    expect(fetchMock).toHaveBeenCalledWith("/api/service-agreements/ag1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteAgreement("ag1");
    expect(fetchMock).toHaveBeenCalledWith("/api/service-agreements/ag1", expect.objectContaining({ method: "DELETE" }));

    await api.listTokens({ page: 1, page_size: 20, agreement_id: "ag1", project_id: "p1", status: "In Progress" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/tokens?page=1&page_size=20&agreement_id=ag1&project_id=p1&status=In+Progress",
      expect.anything()
    );

    await api.getToken("tok1");
    expect(fetchMock).toHaveBeenCalledWith("/api/tokens/tok1", expect.anything());

    await api.createToken({ agreement_id: "ag1", token_date: "2026-01-01", token_status: "In Progress", tokens_used: 1 } as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/tokens", expect.objectContaining({ method: "POST" }));

    await api.updateToken("tok1", { tokens_used: 2 });
    expect(fetchMock).toHaveBeenCalledWith("/api/tokens/tok1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteToken("tok1");
    expect(fetchMock).toHaveBeenCalledWith("/api/tokens/tok1", expect.objectContaining({ method: "DELETE" }));
  });

  it("document references: list, get, create, update, delete", async () => {
    await api.listDocumentReferences({ page: 1, page_size: 20, project_id: "p1", document_type: "Drawing", q: "x" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/document-references?page=1&page_size=20&project_id=p1&document_type=Drawing&q=x",
      expect.anything()
    );

    await api.getDocumentReference("dr1");
    expect(fetchMock).toHaveBeenCalledWith("/api/document-references/dr1", expect.anything());

    await api.createDocumentReference({} as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/document-references", expect.objectContaining({ method: "POST" }));

    await api.updateDocumentReference("dr1", {} as never);
    expect(fetchMock).toHaveBeenCalledWith("/api/document-references/dr1", expect.objectContaining({ method: "PATCH" }));

    await api.deleteDocumentReference("dr1");
    expect(fetchMock).toHaveBeenCalledWith("/api/document-references/dr1", expect.objectContaining({ method: "DELETE" }));
  });

  it("notifications: list with unread flag, mark read", async () => {
    await api.listNotifications({ unread_only: true, page: 1, page_size: 10 });
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/notifications?unread_only=true&page=1&page_size=10", expect.anything());

    await api.markNotificationRead("n1");
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/notifications/n1/read", expect.objectContaining({ method: "POST" }));
  });

  it("builds no query string when all params are absent", async () => {
    await api.listUsers();
    expect(fetchMock).toHaveBeenCalledWith("/api/users", expect.anything());
    await api.listInquiries();
    expect(fetchMock).toHaveBeenCalledWith("/api/inquiries", expect.anything());
    await api.listNotifications();
    expect(fetchMock).toHaveBeenCalledWith("/api/tasks/notifications", expect.anything());
  });
});