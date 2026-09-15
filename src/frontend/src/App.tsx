import { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { Skeleton } from "@/components/ui/skeleton";
import { LoginPage } from "@/pages/LoginPage";

// Helper for lazy-loading pages that use named exports.
// React.lazy requires a default export, so we wrap the named export.
const lazyNamed = (
  factory: () => Promise<Record<string, unknown>>,
  name: string,
) =>
  lazy(() =>
    factory().then((module) => ({
      default: module[name] as React.ComponentType,
    })),
  );

// Route-based code splitting: each page is lazy-loaded so the initial
// bundle stays small and pages are fetched on demand.
const DashboardPage = lazyNamed(() => import("@/pages/DashboardPage"), "DashboardPage");
const UsersPage = lazyNamed(() => import("@/pages/UsersPage"), "UsersPage");
const ClientsPage = lazyNamed(() => import("@/pages/ClientsPage"), "ClientsPage");
const NewClientPage = lazyNamed(() => import("@/pages/NewClientPage"), "NewClientPage");
const ProjectsPage = lazyNamed(() => import("@/pages/ProjectsPage"), "ProjectsPage");
const ProjectDetailPage = lazyNamed(() => import("@/pages/ProjectDetailPage"), "ProjectDetailPage");
const NewProjectPage = lazyNamed(() => import("@/pages/NewProjectPage"), "NewProjectPage");
const VendorsPage = lazyNamed(() => import("@/pages/VendorsPage"), "VendorsPage");
const VendorDetailPage = lazyNamed(() => import("@/pages/VendorDetailPage"), "VendorDetailPage");
const NewVendorPage = lazyNamed(() => import("@/pages/NewVendorPage"), "NewVendorPage");
const DocumentsPage = lazyNamed(() => import("@/pages/DocumentsPage"), "DocumentsPage");
const CompliancePage = lazyNamed(() => import("@/pages/CompliancePage"), "CompliancePage");
const SustainabilityPage = lazyNamed(() => import("@/pages/SustainabilityPage"), "SustainabilityPage");
const TasksPage = lazyNamed(() => import("@/pages/TasksPage"), "TasksPage");
const TaskDetailPage = lazyNamed(() => import("@/pages/TaskDetailPage"), "TaskDetailPage");
const ClientDetailPage = lazyNamed(() => import("@/pages/ClientDetailPage"), "ClientDetailPage");
const InvoicesPage = lazyNamed(() => import("@/pages/InvoicesPage"), "InvoicesPage");
const MaterialsPage = lazyNamed(() => import("@/pages/MaterialsPage"), "MaterialsPage");
const RFQsPage = lazyNamed(() => import("@/pages/RFQsPage"), "RFQsPage");
const ReportsPage = lazyNamed(() => import("@/pages/ReportsPage"), "ReportsPage");
const TimeTrackingPage = lazy(() => import("@/pages/TimeTrackingPage"));
const InquiriesPage = lazyNamed(() => import("@/pages/InquiriesPage"), "InquiriesPage");
const InquiryDetailPage = lazyNamed(() => import("@/pages/InquiryDetailPage"), "InquiryDetailPage");
const AgreementsPage = lazyNamed(() => import("@/pages/AgreementsPage"), "AgreementsPage");
const TokensPage = lazyNamed(() => import("@/pages/TokensPage"), "TokensPage");
const DocumentReferencesPage = lazyNamed(() => import("@/pages/DocumentReferencesPage"), "DocumentReferencesPage");

/** Fallback shown while a lazy route chunk loads. */
function PageLoader() {
  return (
    <div className="space-y-4 p-6">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-4 w-full max-w-md" />
      <div className="grid gap-4 pt-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route
          path="/dashboard"
          element={
            <Suspense fallback={<PageLoader />}>
              <DashboardPage />
            </Suspense>
          }
        />
        <Route
          path="/users"
          element={
            <ProtectedRoute requiredRole="admin">
              <Suspense fallback={<PageLoader />}>
                <UsersPage />
              </Suspense>
            </ProtectedRoute>
          }
        />
        <Route
          path="/clients"
          element={
            <Suspense fallback={<PageLoader />}>
              <ClientsPage />
            </Suspense>
          }
        />
        <Route
          path="/clients/new"
          element={
            <Suspense fallback={<PageLoader />}>
              <NewClientPage />
            </Suspense>
          }
        />
        <Route
          path="/clients/:id"
          element={
            <Suspense fallback={<PageLoader />}>
              <ClientDetailPage />
            </Suspense>
          }
        />
        <Route
          path="/agreements"
          element={
            <Suspense fallback={<PageLoader />}>
              <AgreementsPage />
            </Suspense>
          }
        />
        <Route
          path="/tokens"
          element={
            <Suspense fallback={<PageLoader />}>
              <TokensPage />
            </Suspense>
          }
        />
        <Route
          path="/document-references"
          element={
            <Suspense fallback={<PageLoader />}>
              <DocumentReferencesPage />
            </Suspense>
          }
        />
        <Route
          path="/projects"
          element={
            <Suspense fallback={<PageLoader />}>
              <ProjectsPage />
            </Suspense>
          }
        />
        <Route
          path="/projects/new"
          element={
            <Suspense fallback={<PageLoader />}>
              <NewProjectPage />
            </Suspense>
          }
        />
        <Route
          path="/projects/:id"
          element={
            <Suspense fallback={<PageLoader />}>
              <ProjectDetailPage />
            </Suspense>
          }
        />
        <Route
          path="/vendors"
          element={
            <Suspense fallback={<PageLoader />}>
              <VendorsPage />
            </Suspense>
          }
        />
        <Route
          path="/vendors/new"
          element={
            <Suspense fallback={<PageLoader />}>
              <NewVendorPage />
            </Suspense>
          }
        />
        <Route
          path="/vendors/:id"
          element={
            <Suspense fallback={<PageLoader />}>
              <VendorDetailPage />
            </Suspense>
          }
        />
        <Route
          path="/documents"
          element={
            <Suspense fallback={<PageLoader />}>
              <DocumentsPage />
            </Suspense>
          }
        />
        <Route
          path="/compliance"
          element={
            <Suspense fallback={<PageLoader />}>
              <CompliancePage />
            </Suspense>
          }
        />
        <Route
          path="/sustainability"
          element={
            <Suspense fallback={<PageLoader />}>
              <SustainabilityPage />
            </Suspense>
          }
        />
        <Route
          path="/tasks"
          element={
            <Suspense fallback={<PageLoader />}>
              <TasksPage />
            </Suspense>
          }
        />
        <Route
          path="/tasks/:id"
          element={
            <Suspense fallback={<PageLoader />}>
              <TaskDetailPage />
            </Suspense>
          }
        />
        <Route
          path="/invoices"
          element={
            <Suspense fallback={<PageLoader />}>
              <InvoicesPage />
            </Suspense>
          }
        />
        <Route
          path="/materials"
          element={
            <Suspense fallback={<PageLoader />}>
              <MaterialsPage />
            </Suspense>
          }
        />
        <Route
          path="/rfqs"
          element={
            <Suspense fallback={<PageLoader />}>
              <RFQsPage />
            </Suspense>
          }
        />
        <Route
          path="/reports"
          element={
            <Suspense fallback={<PageLoader />}>
              <ReportsPage />
            </Suspense>
          }
        />
        <Route
          path="/time-tracking"
          element={
            <Suspense fallback={<PageLoader />}>
              <TimeTrackingPage />
            </Suspense>
          }
        />
        <Route
          path="/inquiries"
          element={
            <Suspense fallback={<PageLoader />}>
              <InquiriesPage />
            </Suspense>
          }
        />
        <Route
          path="/inquiries/:id"
          element={
            <Suspense fallback={<PageLoader />}>
              <InquiryDetailPage />
            </Suspense>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;