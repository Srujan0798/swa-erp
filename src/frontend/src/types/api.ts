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