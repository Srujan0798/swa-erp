import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import type { Role } from "@/types/api";

interface ProtectedRouteProps {
  children: React.ReactNode;
  /** Exact single role required (legacy). Prefer requiredRoles when multiple allowed. */
  requiredRole?: Role;
  /** User must have one of these roles (exact match). */
  requiredRoles?: Role[];
}

export function ProtectedRoute({
  children,
  requiredRole,
  requiredRoles,
}: ProtectedRouteProps): React.ReactElement {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const role = user?.role;
  if (requiredRole && role !== requiredRole) {
    return <Navigate to="/dashboard" replace />;
  }
  if (requiredRoles && requiredRoles.length > 0 && (!role || !requiredRoles.includes(role))) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
