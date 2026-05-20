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