export interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type Role = "admin" | "pm" | "designer" | "auditor" | "viewer";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface AccessTokenResponse {
  access_token: string;
}

export interface MessageResponse {
  message: string;
}

export interface UserListResponse {
  items: User[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserCreate {
  email: string;
  name: string;
  password: string;
  role: Role;
}

export interface UserUpdate {
  name?: string;
  role?: Role;
  is_active?: boolean;
}

export interface ApiError {
  detail: string;
  code?: string;
}

export type ProjectStatus = "Lead" | "Quote" | "Awarded" | "Design" | "Vendor" | "Execution" | "Validation" | "Closed";

export interface Project {
  id: string;
  client_id: string;
  name: string;
  code: string;
  description: string | null;
  status: ProjectStatus;
  pm_id: string | null;
  designer_id: string | null;
  auditor_id: string | null;
  location: string | null;
  estimated_value: number | null;
  actual_value: number | null;
  start_date: string | null;
  target_end_date: string | null;
  actual_end_date: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  client_name: string | null;
  pm_name: string | null;
  designer_name: string | null;
  auditor_name: string | null;
}

export interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProjectStats {
  total_active: number;
  by_status: Record<ProjectStatus, number>;
  total_estimated_value: number;
}

export interface Client {
  id: string;
  name: string;
  code: string;
  address: string | null;
  city: string | null;
  state: string | null;
  pincode: string | null;
  country: string;
  gst_number: string | null;
  primary_email: string;
  primary_phone: string | null;
  notes: string | null;
  is_active: boolean;
  industry?: string | null;
  client_status?: string | null;
  first_inquiry_id?: string | null;
  created_at: string;
  updated_at: string;
  contacts: Contact[];
}

export interface Contact {
  id: string;
  client_id: string;
  name: string;
  email: string | null;
  phone: string | null;
  designation: string | null;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientListResponse {
  items: Client[];
  total: number;
  page: number;
  page_size: number;
}

export interface BOQ {
  id: string;
  project_id: string;
  version_number: number;
  file_name: string;
  parsed_at: string;
  parsed_by: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  file_path?: string | null;
  items?: BOQItem[];
}

export interface BOQItem {
  id: string;
  boq_id: string;
  line_number: number;
  category: string | null;
  description: string;
  specification: string | null;
  unit: string;
  quantity: number;
  rate: number;
  amount: number;
}

export interface BOQListRead {
  id: string;
  project_id: string;
  version_number: number;
  file_name: string;
  parsed_at: string;
  parsed_by: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  item_count: number;
}

export interface BOQListResponse {
  items: BOQListRead[];
  total: number;
  page: number;
  page_size: number;
}

export interface BOQItemListResponse {
  items: BOQItem[];
  total: number;
  page: number;
  page_size: number;
}


export type QuoteStatus = "draft" | "pending_approval" | "approved" | "sent" | "accepted" | "rejected";

export interface Quote {
  id: string;
  project_id: string;
  boq_id: string;
  version_number: number;
  status: QuoteStatus;
  subtotal: number;
  markup_percent: number;
  markup_amount: number;
  tax_percent: number;
  tax_amount: number;
  total_amount: number;
  terms: string | null;
  validity_days: number;
  valid_until: string | null;
  created_by_name: string | null;
  approved_by_name: string | null;
  approved_at: string | null;
  sent_at: string | null;
  client_response: string | null;
  client_response_at: string | null;
  client_response_notes: string | null;
  created_at: string;
}

export interface QuoteItem {
  id: string;
  quote_id: string;
  line_number: number;
  category: string | null;
  description: string;
  specification: string | null;
  unit: string;
  quantity: number;
  rate: number;
  amount: number;
}

export interface QuoteListResponse {
  items: Quote[];
  total: number;
  page: number;
  page_size: number;
}

export interface QuoteItemListResponse {
  items: QuoteItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface Vendor {
  id: string;
  name: string;
  code: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  gst_number?: string;
  pan_number?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  contacts: VendorContact[];
}

export interface VendorContact {
  id: string;
  vendor_id: string;
  name: string;
  designation?: string;
  email?: string;
  phone?: string;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export interface VendorListResponse {
  items: Vendor[];
  total: number;
  page: number;
  page_size: number;
}

export interface Material {
  id: string;
  name: string;
  code: string;
  description?: string;
  category_id?: string;
  category_name?: string;
  unit: string;
  is_active: boolean;
  created_at: string;
}

export interface MaterialCategory {
  id: string;
  name: string;
  parent_id?: string;
  children?: MaterialCategory[];
}

export interface MaterialListResponse {
  items: Material[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProjectHealthReport {
  total_projects: number;
  by_status: Record<string, number>;
  overdue_tasks: number;
  budget_variance_total: number;
  at_risk_projects: { id: string; name: string; status: string; variance: number }[];
}

export interface MemberUtilization {
  user_id: string;
  name: string;
  billable_hours: number;
  non_billable_hours: number;
  utilization_pct: number;
}

export interface UtilizationReport {
  period_start: string;
  period_end: string;
  members: MemberUtilization[];
}

export interface MonthlyRevenue {
  month: string;
  revenue: number;
}

export interface ForecastEntry {
  project_id: string;
  project_name: string;
  pipeline_value: number;
  probability: number;
  expected_value: number;
}

export interface RevenueForecast {
  monthly_revenue: MonthlyRevenue[];
  forecast: ForecastEntry[];
}

export interface ClientSummary {
  client_id: string;
  client_name: string;
  project_count: number;
  total_revenue: number;
}

export interface ExecutiveKPIs {
  active_projects: number;
  total_revenue_mtd: number;
  avg_utilization: number;
  overdue_tasks: number;
  pipeline_value: number;
}

export type TaskStatus = "todo" | "in_progress" | "done";
export type TaskPriority = "low" | "medium" | "high" | "critical";

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id: string | null;
  due_date: string | null;
  sort_order: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  assignee_name: string | null;
  created_by_name: string;
  comment_count: number;
}

export interface TaskComment {
  id: string;
  task_id: string;
  user_id: string;
  content: string;
  created_at: string;
  user_name: string;
}

export interface TaskListResponse {
  items: Task[];
  total: number;
  page: number;
  page_size: number;
}

export interface TaskStats {
  todo: number;
  in_progress: number;
  done: number;
  total: number;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  priority?: TaskPriority;
  assignee_id?: string;
  due_date?: string;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  assignee_id?: string;
  due_date?: string;
}

export interface TaskTransitionRequest {
  to_status: TaskStatus;
}

export interface TaskReorderRequest {
  status: TaskStatus;
  sort_order: number;
}

export interface TaskBulkStatusRequest {
  task_ids: string[];
  new_status: TaskStatus;
}

export type RFQStatus = "draft" | "sent" | "responded" | "compared" | "awarded" | "closed" | "cancelled";

export interface RFQ {
  id: string;
  project_id: string;
  vendor_id: string;
  vendor_name: string;
  status: RFQStatus;
  rfq_number: string;
  created_by: string;
  created_by_name: string;
  sent_at?: string;
  responded_at?: string;
  awarded_at?: string;
  notes?: string;
  created_at: string;
  items: RFQItem[];
}

export interface RFQItem {
  id: string;
  material_id: string;
  material_name: string;
  material_unit: string;
  quantity: number;
  vendor_rate?: number;
  notes?: string;
}

export interface RFQCompareItem {
  material_id: string;
  material_name: string;
  unit: string;
  quantity: number;
  vendor_rates: {
    rfq_id: string;
    vendor_id: string;
    vendor_name: string;
    rate: number;
  }[];
}

export interface RFQListResponse {
  items: RFQ[];
  total: number;
  page: number;
  page_size: number;
}

export interface RFQCreatePayload {
  project_id?: string;
  vendor_id: string;
  notes?: string;
  items: {
    material_id: string;
    quantity: number;
    notes?: string;
  }[];
}

export interface RFQRespondPayload {
  items: {
    item_id: string;
    vendor_rate: number;
    notes?: string;
  }[];
}

export interface RFQAwardPayload {
  notes?: string;
}

export interface SustainabilityMetric {
  id: string;
  project_id: string;
  reference_id: string | null;
  recorded_date: string | null;
  compliant_with_green_standards: boolean | null;
  energy_saved_kwh: number | null;
  co2_avoided_tco2e: number | null;
  lifecycle_cost_savings_inr: number | null;
  insulation_efficiency_ratio: number | null;
  payback_period_months: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface SustainabilityMetricCreate {
  project_id: string;
  reference_id?: string | null;
  recorded_date?: string | null;
  compliant_with_green_standards?: boolean | null;
  energy_saved_kwh?: number | null;
  co2_avoided_tco2e?: number | null;
  lifecycle_cost_savings_inr?: number | null;
  insulation_efficiency_ratio?: number | null;
  payback_period_months?: number | null;
  notes?: string | null;
}

export type SustainabilityMetricUpdate = Partial<SustainabilityMetricCreate>;

export type InquiryStatus = "New" | "Contacted" | "Converted" | "Dropped";

export interface Inquiry {
  id: string;
  reference_id: string;
  inquiry_date: string;
  inquiry_type: string | null;
  inquiry_source: string | null;
  client_name: string;
  requirement_summary: string | null;
  estimated_value: number | null;
  priority: string | null;
  status: string;
  owner_id: string | null;
  technical_lead: string | null;
  notes: string | null;
  converted_client_id: string | null;
  converted_project_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface InquiryListResponse {
  items: Inquiry[];
  total: number;
  page: number;
  page_size: number;
}

export interface InquiryCreate {
  inquiry_date: string;
  inquiry_type?: string;
  inquiry_source?: string;
  client_name: string;
  requirement_summary?: string;
  estimated_value?: number;
  priority?: string;
  status?: string;
  owner_id?: string;
  technical_lead?: string;
  notes?: string;
}

export interface InquiryUpdate {
  inquiry_date?: string;
  inquiry_type?: string;
  inquiry_source?: string;
  client_name?: string;
  requirement_summary?: string;
  estimated_value?: number;
  priority?: string;
  status?: string;
  owner_id?: string;
  technical_lead?: string;
  notes?: string;
}

export interface InquiryCandidateClient {
  id: string;
  name: string;
  code: string;
}

export interface InquiryConvertPayload {
  project_name: string;
  project_code?: string;
  project_description?: string;
  project_status?: string;
  pm_id?: string;
  designer_id?: string;
  auditor_id?: string;
  location?: string;
  estimated_value?: number;
  start_date?: string;
  target_end_date?: string;
  client_id?: string;
  client_address?: string;
  client_city?: string;
  client_state?: string;
  client_pincode?: string;
  client_country?: string;
  client_industry?: string;
  client_gst_number?: string;
  client_primary_email?: string;
  client_primary_phone?: string;
}

export interface InquiryConvertResponse {
  inquiry: Inquiry;
  client_id: string;
  project_id: string;
}

export type ServiceAgreementStatus = "Active" | "Completed" | "Cancelled";

export interface ServiceAgreement {
  id: string;
  reference_id: string;
  client_id: string;
  inquiry_id: string | null;
  service_name: string;
  start_date: string;
  end_date: string | null;
  total_tokens: number | null;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  client_name?: string | null;
}

export interface ServiceAgreementListResponse {
  items: ServiceAgreement[];
  total: number;
  page: number;
  page_size: number;
}

export interface ServiceAgreementCreate {
  client_id: string;
  inquiry_id?: string;
  service_name: string;
  start_date: string;
  end_date?: string;
  total_tokens?: number;
  status?: string;
  notes?: string;
}

export interface ServiceAgreementUpdate {
  service_name?: string;
  start_date?: string;
  end_date?: string;
  total_tokens?: number;
  status?: string;
  notes?: string;
}

export type TokenStatus = "In Progress" | "Completed" | "Cancelled";

export interface Token {
  id: string;
  reference_id: string;
  agreement_id: string;
  token_date: string;
  token_type: string | null;
  description: string | null;
  token_status: string;
  tokens_used: number;
  swa_employee_id: string | null;
  project_owner_id: string | null;
  swa_employee_name: string | null;
  project_owner_name: string | null;
  client_employee_name: string | null;
  project_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface TokenListResponse {
  items: Token[];
  total: number;
  page: number;
  page_size: number;
}

export interface TokenCreate {
  agreement_id: string;
  token_date: string;
  token_type?: string;
  description?: string;
  token_status?: string;
  tokens_used?: number;
  swa_employee_id?: string;
  project_owner_id?: string;
  swa_employee_name?: string;
  project_owner_name?: string;
  client_employee_name?: string;
  project_id?: string;
}

export interface TokenUpdate {
  token_date?: string;
  token_type?: string;
  description?: string;
  token_status?: string;
  tokens_used?: number;
  swa_employee_id?: string;
  project_owner_id?: string;
  swa_employee_name?: string;
  project_owner_name?: string;
  client_employee_name?: string;
  project_id?: string;
}

export type DocumentReferenceStatus = "Draft" | "Issued" | "Approved" | "Superseded";

export interface DocumentReference {
  id: string;
  reference_id: string;
  project_id: string;
  token_id: string | null;
  doc_date: string;
  document_type: string;
  type: string | null;
  author_id: string | null;
  author_name: string | null;
  user_ref: string | null;
  description: string | null;
  revision: string;
  status: string;
  remarks: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentReferenceListResponse {
  items: DocumentReference[];
  total: number;
  page: number;
  page_size: number;
}

export interface DocumentReferenceCreate {
  project_id: string;
  token_id?: string;
  doc_date: string;
  document_type: string;
  type?: string;
  author_id?: string;
  author_name?: string;
  user_ref?: string;
  description?: string;
  revision?: string;
  status?: string;
  remarks?: string;
}

export interface DocumentReferenceUpdate {
  doc_date?: string;
  document_type?: string;
  type?: string;
  author_id?: string;
  author_name?: string;
  user_ref?: string;
  description?: string;
  revision?: string;
  status?: string;
  remarks?: string;
}

export interface Notification {
  id: string;
  user_id: string;
  notification_type: string;
  title: string;
  message: string;
  reference_type: string | null;
  reference_id: string | null;
  is_read: boolean;
  created_at: string;
  read_at: string | null;
}