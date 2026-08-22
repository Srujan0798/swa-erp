import { Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { LoginPage } from "@/pages/LoginPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { UsersPage } from "@/pages/UsersPage";
import { ClientsPage } from "@/pages/ClientsPage";
import { NewClientPage } from "@/pages/NewClientPage";
import { ProjectsPage } from "@/pages/ProjectsPage";
import { ProjectDetailPage } from "@/pages/ProjectDetailPage";
import { NewProjectPage } from "@/pages/NewProjectPage";
import { VendorsPage } from "@/pages/VendorsPage";
import { VendorDetailPage } from "@/pages/VendorDetailPage";
import { NewVendorPage } from "@/pages/NewVendorPage";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { CompliancePage } from "@/pages/CompliancePage";
import { SustainabilityPage } from "@/pages/SustainabilityPage";
import { TasksPage } from "@/pages/TasksPage";
import { TaskDetailPage } from "@/pages/TaskDetailPage";
import { ClientDetailPage } from "@/pages/ClientDetailPage";
import { InvoicesPage } from "@/pages/InvoicesPage";
import { MaterialsPage } from "@/pages/MaterialsPage";
import { RFQsPage } from "@/pages/RFQsPage";
import { ReportsPage } from "@/pages/ReportsPage";
import TimeTrackingPage from "@/pages/TimeTrackingPage";
import { InquiriesPage } from "@/pages/InquiriesPage";
import { InquiryDetailPage } from "@/pages/InquiryDetailPage";
import { AgreementsPage } from "@/pages/AgreementsPage";
import { TokensPage } from "@/pages/TokensPage";
import { DocumentReferencesPage } from "@/pages/DocumentReferencesPage";

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
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route
          path="/users"
          element={
            <ProtectedRoute requiredRole="admin">
              <UsersPage />
            </ProtectedRoute>
          }
        />
        <Route path="/clients" element={<ClientsPage />} />
        <Route path="/clients/new" element={<NewClientPage />} />
        <Route path="/clients/:id" element={<ClientDetailPage />} />
        <Route path="/agreements" element={<AgreementsPage />} />
        <Route path="/tokens" element={<TokensPage />} />
        <Route path="/document-references" element={<DocumentReferencesPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/new" element={<NewProjectPage />} />
        <Route path="/projects/:id" element={<ProjectDetailPage />} />
        <Route path="/vendors" element={<VendorsPage />} />
        <Route path="/vendors/new" element={<NewVendorPage />} />
        <Route path="/vendors/:id" element={<VendorDetailPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/compliance" element={<CompliancePage />} />
        <Route path="/sustainability" element={<SustainabilityPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/tasks/:id" element={<TaskDetailPage />} />
        <Route path="/invoices" element={<InvoicesPage />} />
        <Route path="/materials" element={<MaterialsPage />} />
        <Route path="/rfqs" element={<RFQsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/time-tracking" element={<TimeTrackingPage />} />
        <Route path="/inquiries" element={<InquiriesPage />} />
        <Route path="/inquiries/:id" element={<InquiryDetailPage />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
