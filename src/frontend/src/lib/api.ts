import type {
  LoginRequest,
  TokenResponse,
  AccessTokenResponse,
  MessageResponse,
  UserListResponse,
  UserCreate,
  UserUpdate,
  User,
  ProjectListResponse,
  ProjectStats,
  ClientListResponse,
  Project,
  Client,
  Contact,
  ProjectStatus,
  BOQ,
  BOQListResponse,
  BOQItemListResponse,
  Quote,
  QuoteListResponse,
  Task,
  TaskListResponse,
  TaskCreateRequest,
  TaskUpdateRequest,
  TaskStatus,
  TaskBulkStatusRequest,
  TaskComment,
  TaskStats,
  Vendor,
  VendorContact,
  VendorListResponse,
  Material,
  MaterialCategory,
  MaterialListResponse,
  RFQ,
  RFQListResponse,
  RFQCreatePayload,
  RFQRespondPayload,
  RFQAwardPayload,
  RFQCompareItem,
  SustainabilityMetric,
  SustainabilityMetricCreate,
  SustainabilityMetricUpdate,
  Inquiry,
  InquiryListResponse,
  InquiryCreate,
  InquiryUpdate,
  InquiryConvertPayload,
  InquiryConvertResponse,
  ServiceAgreement,
  ServiceAgreementListResponse,
  ServiceAgreementCreate,
  ServiceAgreementUpdate,
  Token,
  TokenListResponse,
  TokenCreate,
  TokenUpdate,
  DocumentReference,
  DocumentReferenceListResponse,
  DocumentReferenceCreate,
  DocumentReferenceUpdate,
  DocumentReferenceCounters,
  Notification,
} from "@/types/api";
import type {
  DocumentItem,
  DocumentListResponse,
  DocumentFolder,
  DocumentFolderListResponse,
  DocumentSearchResponse,
} from "@/types/document";
import type {
  ComplianceStandard,
  ComplianceChecklistItem,
  ComplianceSummary,
  ProjectComplianceItem,
  ComplianceStatus,
} from "@/types/compliance";
import type {
  TimeEntry,
  TimeEntryCreate,
  TimeEntryUpdate,
  TimeEntryListResponse,
  Timesheet,
  TimesheetListResponse,
} from "@/types/time";
import type {
  Invoice,
  InvoiceCreate,
  InvoiceListResponse,
  ProjectPnL,
  ProjectCost,
  ProjectCostCreate,
  ProjectCostListResponse,
} from "@/types/financial";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./auth";

class ApiError extends Error {
  constructor(public status: number, public body: unknown) {
    super(`API Error: ${status}`);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response = await fetch(path, { ...options, headers });

  if (response.status === 401) {
    const refresh = getRefreshToken();
    if (refresh) {
      try {
        const refreshResponse = await fetch("/api/auth/refresh", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refresh }),
        });
        if (refreshResponse.ok) {
          const tokens: AccessTokenResponse = await refreshResponse.json();
          setTokens(tokens.access_token, refresh);
          headers["Authorization"] = `Bearer ${tokens.access_token}`;
          response = await fetch(path, { ...options, headers });
        } else {
          clearTokens();
          window.location.href = "/login";
          throw new ApiError(401, null);
        }
      } catch {
        clearTokens();
        window.location.href = "/login";
        throw new ApiError(401, null);
      }
    }
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body);
  }

  return response.json();
}

export const api = {
  login: (data: LoginRequest) =>
    request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  refresh: (refreshToken: string) =>
    request<AccessTokenResponse>("/api/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),

  logout: () =>
    request<MessageResponse>("/api/auth/logout", { method: "POST" }),

  me: () => request<User>("/api/auth/me"),

  listUsers: (params?: { page?: number; page_size?: number; q?: string; role?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    if (params?.role) searchParams.set("role", params.role);
    const query = searchParams.toString();
    return request<UserListResponse>(`/api/users${query ? `?${query}` : ""}`);
  },

  /** Active users for assignee pickers — any authenticated role (not ADMIN-only). */
  listAssignees: (params?: { page_size?: number; q?: string; role?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    if (params?.role) searchParams.set("role", params.role);
    const query = searchParams.toString();
    return request<{ items: User[]; total: number }>(
      `/api/users/assignees${query ? `?${query}` : ""}`,
    );
  },

  createUser: (data: UserCreate) =>
    request<User>("/api/users", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getUser: (id: string) => request<User>(`/api/users/${id}`),

  updateUser: (id: string, data: UserUpdate) =>
    request<User>(`/api/users/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteUser: (id: string) =>
    request<void>(`/api/users/${id}`, { method: "DELETE" }),

  getProjectStats: () => request<ProjectStats>("/api/projects/stats"),

  listProjects: (params?: {
    page?: number;
    page_size?: number;
    q?: string;
    status?: string;
    client_id?: string;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    if (params?.status) searchParams.set("status", params.status);
    if (params?.client_id) searchParams.set("client_id", params.client_id);
    const query = searchParams.toString();
    return request<ProjectListResponse>(`/api/projects${query ? `?${query}` : ""}`);
  },

  getProject: (id: string) => request<Project>(`/api/projects/${id}`),

  createProject: (data: Partial<Project>) =>
    request<Project>("/api/projects", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateProject: (id: string, data: Partial<Project>) =>
    request<Project>(`/api/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  transitionProject: (id: string, status: ProjectStatus) =>
    request<Project>(`/api/projects/${id}/transition`, {
      method: "POST",
      body: JSON.stringify({ to_status: status }),
    }),

  listClients: (params?: { page?: number; page_size?: number; q?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    const query = searchParams.toString();
    return request<ClientListResponse>(`/api/clients${query ? `?${query}` : ""}`);
  },

  getClient: (id: string) => request<Client>(`/api/clients/${id}`),

  createClient: (data: Partial<Client>) =>
    request<Client>("/api/clients", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateClient: (id: string, data: Partial<Client>) =>
    request<Client>(`/api/clients/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteClient: (id: string) =>
    request<void>(`/api/clients/${id}`, { method: "DELETE" }),

  deleteContact: (clientId: string, contactId: string) =>
    request<void>(`/api/clients/${clientId}/contacts/${contactId}`, { method: "DELETE" }),

  addContact: (clientId: string, data: Partial<Contact>) =>
    request<Contact>(`/api/clients/${clientId}/contacts`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  listBoqs: (projectId: string, params?: { page?: number; page_size?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    const query = searchParams.toString();
    return request<BOQListResponse>(`/api/projects/${projectId}/boqs${query ? `?${query}` : ""}`);
  },

  getBoq: (id: string) => request<BOQ>(`/api/boqs/${id}`),

  getBoqItems: (id: string, params?: { page?: number; page_size?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    const query = searchParams.toString();
    return request<BOQItemListResponse>(`/api/boqs/${id}/items${query ? `?${query}` : ""}`);
  },

  uploadBoq: async (projectId: string, file: File, notes?: string): Promise<BOQ> => {
    const form = new FormData();
    form.append("file", file);
    if (notes) form.append("notes", notes);
    const token = getAccessToken();
    const response = await fetch(`/api/projects/${projectId}/boqs`, {
      method: "POST",
      body: form,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new ApiError(response.status, body);
    }
    return response.json();
  },

  deleteBoq: (id: string) => request<void>(`/api/boqs/${id}`, { method: "DELETE" }),

  listQuotes: (projectId: string, params?: { page?: number; page_size?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    const query = searchParams.toString();
    return request<QuoteListResponse>(`/api/projects/${projectId}/quotes${query ? `?${query}` : ""}`);
  },

  getQuote: (id: string) => request<Quote>(`/api/quotes/${id}`),

  createQuote: (projectId: string, data: {
    boq_id: string;
    markup_percent?: number;
    tax_percent?: number;
    terms?: string;
    validity_days?: number;
  }) =>
    request<Quote>(`/api/projects/${projectId}/quotes`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateQuote: (id: string, data: Partial<Quote>) =>
    request<Quote>(`/api/quotes/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteQuote: (id: string) => request<void>(`/api/quotes/${id}`, { method: "DELETE" }),

  submitQuote: (id: string) =>
    request<Quote>(`/api/quotes/${id}/submit`, { method: "POST" }),

  approveQuote: (id: string) =>
    request<Quote>(`/api/quotes/${id}/approve`, { method: "POST" }),

  sendQuote: (id: string) =>
    request<Quote>(`/api/quotes/${id}/send`, { method: "POST" }),

  respondQuote: (id: string, data: { response: "accepted" | "rejected"; notes?: string }) =>
    request<Quote>(`/api/quotes/${id}/respond`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  cloneQuote: (id: string) =>
    request<Quote>(`/api/quotes/${id}/clone`, { method: "POST" }),

  downloadQuotePdf: (id: string) =>
    fetch(`/api/quotes/${id}/pdf`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    }),

  listTasks: (projectId: string, params?: { page?: number; page_size?: number; status?: string; assignee_id?: string; priority?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.status) searchParams.set("status", params.status);
    if (params?.assignee_id) searchParams.set("assignee_id", params.assignee_id);
    if (params?.priority) searchParams.set("priority", params.priority);
    const query = searchParams.toString();
    return request<TaskListResponse>(`/api/projects/${projectId}/tasks${query ? `?${query}` : ""}`);
  },

  getTask: (taskId: string) => request<Task>(`/api/tasks/${taskId}`),

  createTask: (projectId: string, data: TaskCreateRequest) =>
    request<Task>(`/api/projects/${projectId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTask: (taskId: string, data: TaskUpdateRequest) =>
    request<Task>(`/api/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteTask: (taskId: string) =>
    request<void>(`/api/tasks/${taskId}`, { method: "DELETE" }),

  transitionTask: (taskId: string, toStatus: TaskStatus) =>
    request<Task>(`/api/tasks/${taskId}/transition`, {
      method: "POST",
      body: JSON.stringify({ to_status: toStatus }),
    }),

  reorderTask: (taskId: string, status: TaskStatus, sortOrder: number) =>
    request<Task>(`/api/tasks/${taskId}/reorder`, {
      method: "POST",
      body: JSON.stringify({ status, sort_order: sortOrder }),
    }),

  bulkUpdateStatus: (data: TaskBulkStatusRequest) =>
    request<MessageResponse>("/api/tasks/bulk-status", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  assignTask: (taskId: string, assigneeId: string) =>
    request<Task>(`/api/tasks/${taskId}/assign`, {
      method: "POST",
      body: JSON.stringify({ assignee_id: assigneeId }),
    }),

  unassignTask: (taskId: string) =>
    request<Task>(`/api/tasks/${taskId}/unassign`, {
      method: "POST",
    }),

  getMyTasks: (params?: { page?: number; page_size?: number; status?: string; priority?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.status) searchParams.set("status", params.status);
    if (params?.priority) searchParams.set("priority", params.priority);
    const query = searchParams.toString();
    return request<TaskListResponse>(`/api/tasks/my-tasks${query ? `?${query}` : ""}`);
  },

  getProjectTaskStats: (projectId: string) =>
    request<TaskStats>(`/api/projects/${projectId}/tasks/stats`),

  addComment: (taskId: string, content: string) =>
    request<TaskComment>(`/api/tasks/${taskId}/comments`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),

  listComments: (taskId: string) =>
    request<TaskComment[]>(`/api/tasks/${taskId}/comments`),

  listVendors: (params?: { page?: number; page_size?: number; q?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    const query = searchParams.toString();
    return request<VendorListResponse>(`/api/vendors${query ? `?${query}` : ""}`);
  },

  getVendor: (id: string) => request<Vendor>(`/api/vendors/${id}`),

  createVendor: (data: Partial<Vendor>) =>
    request<Vendor>("/api/vendors", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateVendor: (id: string, data: Partial<Vendor>) =>
    request<Vendor>(`/api/vendors/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteVendor: (id: string) =>
    request<void>(`/api/vendors/${id}`, { method: "DELETE" }),

  addVendorContact: (vendorId: string, data: Partial<VendorContact>) =>
    request<VendorContact>(`/api/vendors/${vendorId}/contacts`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteVendorContact: (vendorId: string, contactId: string) =>
    request<void>(`/api/vendors/${vendorId}/contacts/${contactId}`, { method: "DELETE" }),

  listMaterials: (params?: { page?: number; page_size?: number; q?: string; category_id?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    if (params?.category_id) searchParams.set("category_id", params.category_id);
    const query = searchParams.toString();
    return request<MaterialListResponse>(`/api/materials${query ? `?${query}` : ""}`);
  },

  getMaterial: (id: string) => request<Material>(`/api/materials/${id}`),

  createMaterial: (data: Partial<Material>) =>
    request<Material>("/api/materials", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateMaterial: (id: string, data: Partial<Material>) =>
    request<Material>(`/api/materials/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteMaterial: (id: string) =>
    request<void>(`/api/materials/${id}`, { method: "DELETE" }),

  listMaterialCategories: () =>
    request<MaterialCategory[]>("/api/material-categories"),

  createMaterialCategory: (data: Partial<MaterialCategory>) =>
    request<MaterialCategory>("/api/material-categories", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  listDocuments: (projectId: string, params?: { folder_id?: string; page?: number; page_size?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.folder_id) searchParams.set("folder_id", params.folder_id);
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    const query = searchParams.toString();
    return request<DocumentListResponse>(`/api/projects/${projectId}/documents${query ? `?${query}` : ""}`);
  },

  getDocument: (documentId: string) => request<DocumentItem>(`/api/documents/${documentId}`),

  uploadDocument: async (projectId: string, file: File, folderId?: string, tags?: string[]): Promise<DocumentItem> => {
    const form = new FormData();
    form.append("file", file);
    if (folderId) form.append("folder_id", folderId);
    if (tags && tags.length > 0) form.append("tags", JSON.stringify(tags));
    const token = getAccessToken();
    const response = await fetch(`/api/projects/${projectId}/documents`, {
      method: "POST",
      body: form,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new ApiError(response.status, body);
    }
    return response.json();
  },

  deleteDocument: (documentId: string) =>
    request<void>(`/api/documents/${documentId}`, { method: "DELETE" }),

  renameDocument: (documentId: string, name: string) =>
    request<DocumentItem>(`/api/documents/${documentId}/rename`, {
      method: "PUT",
      body: JSON.stringify({ name }),
    }),

  moveDocuments: (documentIds: string[], folderId: string | null) =>
    request<MessageResponse>("/api/documents/move", {
      method: "PUT",
      body: JSON.stringify({ document_ids: documentIds, folder_id: folderId }),
    }),

  searchDocuments: (projectId: string, params: { q?: string; tags?: string; folder_id?: string }) => {
    const searchParams = new URLSearchParams();
    if (params.q) searchParams.set("q", params.q);
    if (params.tags) searchParams.set("tags", params.tags);
    if (params.folder_id) searchParams.set("folder_id", params.folder_id);
    const query = searchParams.toString();
    return request<DocumentSearchResponse>(`/api/projects/${projectId}/documents/search${query ? `?${query}` : ""}`);
  },

  listFolders: (projectId: string, parentId?: string) => {
    const searchParams = new URLSearchParams();
    if (parentId) searchParams.set("parent_id", parentId);
    const query = searchParams.toString();
    return request<DocumentFolderListResponse>(`/api/projects/${projectId}/folders${query ? `?${query}` : ""}`);
  },

  createFolder: (projectId: string, data: { name: string; parent_id?: string }) =>
    request<DocumentFolder>(`/api/projects/${projectId}/folders`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteFolder: (folderId: string) =>
    request<void>(`/api/folders/${folderId}`, { method: "DELETE" }),

  listTimeEntries: (params?: { page?: number; page_size?: number; project_id?: string; start_date?: string; end_date?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.project_id) searchParams.set("project_id", params.project_id);
    if (params?.start_date) searchParams.set("start_date", params.start_date);
    if (params?.end_date) searchParams.set("end_date", params.end_date);
    const query = searchParams.toString();
    return request<TimeEntryListResponse>(`/api/time-entries${query ? `?${query}` : ""}`);
  },

  createTimeEntry: (data: TimeEntryCreate) =>
    request<TimeEntry>("/api/time-entries", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTimeEntry: (id: string, data: TimeEntryUpdate) =>
    request<TimeEntry>(`/api/time-entries/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteTimeEntry: (id: string) =>
    request<void>(`/api/time-entries/${id}`, { method: "DELETE" }),

  listTimesheets: (params?: { page?: number; page_size?: number; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.status) searchParams.set("status", params.status);
    const query = searchParams.toString();
    return request<TimesheetListResponse>(`/api/timesheets${query ? `?${query}` : ""}`);
  },

  getTimesheet: (id: string) => request<Timesheet>(`/api/timesheets/${id}`),

  generateTimesheet: (weekStart: string) =>
    request<Timesheet>("/api/timesheets", {
      method: "POST",
      body: JSON.stringify({ week_start: weekStart }),
    }),

  submitTimesheet: (id: string) =>
    request<Timesheet>(`/api/timesheets/${id}/submit`, { method: "POST" }),

  approveTimesheet: (id: string) =>
    request<Timesheet>(`/api/timesheets/${id}/approve`, { method: "POST" }),

  rejectTimesheet: (id: string) =>
    request<Timesheet>(`/api/timesheets/${id}/reject`, { method: "POST" }),

  listProjectInvoices: (projectId: string, params?: { page?: number; page_size?: number; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.status) searchParams.set("status", params.status);
    const query = searchParams.toString();
    return request<InvoiceListResponse>(`/api/projects/${projectId}/invoices${query ? `?${query}` : ""}`);
  },

  getInvoice: (id: string) => request<Invoice>(`/api/invoices/${id}`),

  createInvoice: (projectId: string, data: InvoiceCreate) =>
    request<Invoice>(`/api/projects/${projectId}/invoices`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  generateInvoiceFromTime: (projectId: string, startDate: string, endDate: string) =>
    request<Invoice>(`/api/projects/${projectId}/invoices/generate-from-time`, {
      method: "POST",
      body: JSON.stringify({ start_date: startDate, end_date: endDate }),
    }),

  updateInvoiceStatus: (id: string, status: "draft" | "sent" | "paid") =>
    request<Invoice>(`/api/invoices/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  deleteInvoice: (id: string) =>
    request<void>(`/api/invoices/${id}`, { method: "DELETE" }),

  getProjectPnL: (projectId: string) =>
    request<ProjectPnL>(`/api/projects/${projectId}/pnl`),

  listProjectCosts: (projectId: string, params?: { page?: number; page_size?: number; category?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.category) searchParams.set("category", params.category);
    const query = searchParams.toString();
    return request<ProjectCostListResponse>(`/api/projects/${projectId}/costs${query ? `?${query}` : ""}`);
  },

  addProjectCost: (projectId: string, data: ProjectCostCreate) =>
    request<ProjectCost>(`/api/projects/${projectId}/costs`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteProjectCost: (projectId: string, costId: string) =>
    request<void>(`/api/projects/${projectId}/costs/${costId}`, { method: "DELETE" }),

  listStandards: () =>
    request<ComplianceStandard[]>("/api/compliance/standards"),

  getChecklistItems: (standardId: string) =>
    request<ComplianceChecklistItem[]>(`/api/compliance/standards/${standardId}/checklist`),

  getComplianceSummary: (projectId: string) =>
    request<ComplianceSummary>(`/api/projects/${projectId}/compliance/summary`),

  listComplianceItems: (projectId: string, standardId?: string) => {
    const searchParams = new URLSearchParams();
    if (standardId) searchParams.set("standard_id", standardId);
    const query = searchParams.toString();
    return request<ProjectComplianceItem[]>(
      `/api/projects/${projectId}/compliance/items${query ? `?${query}` : ""}`
    );
  },

  updateComplianceItem: (itemId: string, data: { status?: ComplianceStatus; notes?: string; evidence_document_id?: string | null }) =>
    request<ProjectComplianceItem>(`/api/compliance/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  reviewComplianceItem: (itemId: string, data?: { notes?: string }) =>
    request<ProjectComplianceItem>(`/api/compliance/items/${itemId}/review`, {
      method: "POST",
      body: JSON.stringify(data ?? {}),
    }),

  bulkCreateComplianceItems: (projectId: string, standardId: string) =>
    request<MessageResponse>(`/api/projects/${projectId}/compliance/items/bulk/${standardId}`, {
      method: "POST",
    }),

  listProjectRfqs: (projectId: string, params?: { page?: number; page_size?: number; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.status) searchParams.set("status", params.status);
    const query = searchParams.toString();
    return request<RFQListResponse>(`/api/projects/${projectId}/rfqs${query ? `?${query}` : ""}`);
  },

  getRfq: (rfqId: string) => request<RFQ>(`/api/rfqs/${rfqId}`),

  createRfq: (projectId: string, data: RFQCreatePayload) =>
    request<RFQ>(`/api/projects/${projectId}/rfqs`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  sendRfq: (rfqId: string) =>
    request<RFQ>(`/api/rfqs/${rfqId}/send`, { method: "POST" }),

  respondRfq: (rfqId: string, data: RFQRespondPayload) =>
    request<RFQ>(`/api/rfqs/${rfqId}/respond`, {
      method: "POST",
      // Backend expects a bare list of response items
      body: JSON.stringify(data.items),
    }),

  awardRfq: (rfqId: string, data?: RFQAwardPayload) =>
    request<RFQ>(`/api/rfqs/${rfqId}/award`, {
      method: "POST",
      body: JSON.stringify(data ?? {}),
    }),

  closeRfq: (rfqId: string) =>
    request<RFQ>(`/api/rfqs/${rfqId}/close`, { method: "POST" }),

  cancelRfq: (rfqId: string) =>
    request<RFQ>(`/api/rfqs/${rfqId}/cancel`, { method: "POST" }),

  compareRfqs: (projectId: string, materialIds?: string[]) => {
    const searchParams = new URLSearchParams();
    if (materialIds?.length) searchParams.set("material_ids", materialIds.join(","));
    const query = searchParams.toString();
    return request<RFQCompareItem[]>(`/api/projects/${projectId}/rfqs/compare${query ? `?${query}` : ""}`);
  },

  listSustainabilityMetrics: (projectId: string, referenceId?: string) => {
    const searchParams = new URLSearchParams();
    if (referenceId) searchParams.set("reference_id", referenceId);
    const query = searchParams.toString();
    return request<SustainabilityMetric[]>(
      `/api/projects/${projectId}/sustainability/metrics${query ? `?${query}` : ""}`
    );
  },

  createSustainabilityMetric: (projectId: string, data: SustainabilityMetricCreate) =>
    request<SustainabilityMetric>(`/api/projects/${projectId}/sustainability/metrics`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateSustainabilityMetric: (projectId: string, metricId: string, data: SustainabilityMetricUpdate) =>
    request<SustainabilityMetric>(`/api/projects/${projectId}/sustainability/metrics/${metricId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteSustainabilityMetric: (projectId: string, metricId: string) =>
    request<void>(`/api/projects/${projectId}/sustainability/metrics/${metricId}`, {
      method: "DELETE",
    }),

  listInquiries: (params?: { page?: number; page_size?: number; q?: string; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.q) searchParams.set("q", params.q);
    if (params?.status) searchParams.set("status", params.status);
    const query = searchParams.toString();
    return request<InquiryListResponse>(`/api/inquiries${query ? `?${query}` : ""}`);
  },

  getInquiry: (id: string) => request<Inquiry>(`/api/inquiries/${id}`),

  createInquiry: (data: InquiryCreate) =>
    request<Inquiry>("/api/inquiries", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateInquiry: (id: string, data: InquiryUpdate) =>
    request<Inquiry>(`/api/inquiries/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteInquiry: (id: string) =>
    request<void>(`/api/inquiries/${id}`, { method: "DELETE" }),

  convertInquiry: (id: string, data: InquiryConvertPayload) =>
    request<InquiryConvertResponse>(`/api/inquiries/${id}/convert`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  listAgreements: (params?: { page?: number; page_size?: number; client_id?: string; inquiry_id?: string; status?: string; q?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.client_id) searchParams.set("client_id", params.client_id);
    if (params?.inquiry_id) searchParams.set("inquiry_id", params.inquiry_id);
    if (params?.status) searchParams.set("status", params.status);
    if (params?.q) searchParams.set("q", params.q);
    const query = searchParams.toString();
    return request<ServiceAgreementListResponse>(`/api/service-agreements${query ? `?${query}` : ""}`);
  },

  getAgreement: (id: string) => request<ServiceAgreement>(`/api/service-agreements/${id}`),

  createAgreement: (data: ServiceAgreementCreate) =>
    request<ServiceAgreement>("/api/service-agreements", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateAgreement: (id: string, data: ServiceAgreementUpdate) =>
    request<ServiceAgreement>(`/api/service-agreements/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteAgreement: (id: string) =>
    request<void>(`/api/service-agreements/${id}`, { method: "DELETE" }),

  listTokens: (params?: { page?: number; page_size?: number; agreement_id?: string; project_id?: string; status?: string; q?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.agreement_id) searchParams.set("agreement_id", params.agreement_id);
    if (params?.project_id) searchParams.set("project_id", params.project_id);
    if (params?.status) searchParams.set("status", params.status);
    if (params?.q) searchParams.set("q", params.q);
    const query = searchParams.toString();
    return request<TokenListResponse>(`/api/tokens${query ? `?${query}` : ""}`);
  },

  getToken: (id: string) => request<Token>(`/api/tokens/${id}`),

  createToken: (data: TokenCreate) =>
    request<Token>("/api/tokens", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateToken: (id: string, data: TokenUpdate) =>
    request<Token>(`/api/tokens/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteToken: (id: string) =>
    request<void>(`/api/tokens/${id}`, { method: "DELETE" }),

  listDocumentReferences: (params?: { page?: number; page_size?: number; project_id?: string; token_id?: string; document_type?: string; q?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    if (params?.project_id) searchParams.set("project_id", params.project_id);
    if (params?.token_id) searchParams.set("token_id", params.token_id);
    if (params?.document_type) searchParams.set("document_type", params.document_type);
    if (params?.q) searchParams.set("q", params.q);
    const query = searchParams.toString();
    return request<DocumentReferenceListResponse>(`/api/document-references${query ? `?${query}` : ""}`);
  },

  getDocumentReferenceCounters: () =>
    request<DocumentReferenceCounters>("/api/document-references/counters"),

  getDocumentReference: (id: string) => request<DocumentReference>(`/api/document-references/${id}`),

  createDocumentReference: (data: DocumentReferenceCreate) =>
    request<DocumentReference>("/api/document-references", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateDocumentReference: (id: string, data: DocumentReferenceUpdate) =>
    request<DocumentReference>(`/api/document-references/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteDocumentReference: (id: string) =>
    request<void>(`/api/document-references/${id}`, { method: "DELETE" }),

  listNotifications: (params?: { unread_only?: boolean; page?: number; page_size?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.unread_only) searchParams.set("unread_only", "true");
    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.page_size) searchParams.set("page_size", String(params.page_size));
    const query = searchParams.toString();
    return request<Notification[]>(`/api/tasks/notifications${query ? `?${query}` : ""}`);
  },

  markNotificationRead: (id: string) =>
    request<void>(`/api/tasks/notifications/${id}/read`, { method: "POST" }),
};

export { ApiError };
