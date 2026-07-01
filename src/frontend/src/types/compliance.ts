export interface ComplianceStandard {
  id: string;
  name: string;
  version: string;
  description: string | null;
}

export interface ComplianceChecklistItem {
  id: string;
  standard_id: string;
  category: string;
  requirement: string;
  description: string | null;
  is_mandatory: boolean;
}

export type ComplianceStatus = "pending" | "compliant" | "non_compliant" | "na";

export interface ProjectComplianceItem {
  id: string;
  project_id: string;
  checklist_item_id: string;
  status: ComplianceStatus;
  evidence_document_id: string | null;
  notes: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  standard_name: string;
  category: string;
  requirement: string;
  is_mandatory: boolean;
}

export interface ComplianceDashboardStandard {
  standard_name: string;
  total_items: number;
  compliant_count: number;
  non_compliant_count: number;
  pending_count: number;
  na_count: number;
  compliance_percentage: number;
}

export interface ComplianceSummary {
  project_id: string;
  standards: ComplianceDashboardStandard[];
  overall_percentage: number;
}
