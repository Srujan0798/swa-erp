/** Role capability helpers for SWA ERP UI write locks. */

import type { Role } from "@/types/api";

export type { Role };

export interface RoleUser {
  role?: string | null;
}

/**
 * Role privilege hierarchy (higher includes lower for `roleAtLeast` checks).
 * admin ⊃ pm ⊃ designer/auditor ⊃ viewer for commercial/ops gates where noted.
 */
const HIERARCHY: Record<string, Set<string>> = {
  admin: new Set(["admin", "pm", "designer", "auditor", "viewer"]),
  pm: new Set(["pm", "designer", "auditor", "viewer"]),
  designer: new Set(["designer", "viewer"]),
  auditor: new Set(["auditor", "viewer"]),
  viewer: new Set(["viewer"]),
};

export function roleAtLeast(user: RoleUser | null | undefined, required: Role): boolean {
  const r = (user?.role ?? "").toLowerCase();
  if (!r) return false;
  return HIERARCHY[r]?.has(required) ?? false;
}

/** Any authenticated non-viewer may mutate operational data. */
export function canWrite(user: RoleUser | null | undefined): boolean {
  const r = (user?.role ?? "").toLowerCase();
  return r !== "" && r !== "viewer";
}

/** Commercial write: clients create/delete, invoices, costs. Admin or PM. */
export function canManageCommercial(user: RoleUser | null | undefined): boolean {
  return roleAtLeast(user, "pm");
}

/** Admin-only (users admin, destructive system actions). */
export function canAdmin(user: RoleUser | null | undefined): boolean {
  return roleAtLeast(user, "admin");
}

/** Project team assignment / PM-level project management. */
export function canManageProjects(user: RoleUser | null | undefined): boolean {
  return roleAtLeast(user, "pm");
}
