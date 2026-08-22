export interface TimeEntry {
  id: string;
  project_id: string;
  task_id: string | null;
  user_id: string;
  date: string;
  hours: number;
  description: string;
  is_billable: boolean;
  /** Excel Time Logging Sheet columns */
  employee_name?: string | null;
  employee_role?: string | null;
  work_type?: string | null;
  sheet_reference_id?: string | null;
  revision?: string | null;
  activity_type?: string | null;
  software_used?: string | null;
  work_mode?: string | null;
  billable_hours?: number | null;
  created_at: string;
  deleted_at: string | null;
  user_name?: string;
  project_name?: string;
}

export interface TimeEntryCreate {
  project_id: string;
  task_id?: string;
  date: string;
  hours: number;
  description: string;
  is_billable: boolean;
  employee_name?: string;
  employee_role?: string;
  work_type?: string;
  sheet_reference_id?: string;
  revision?: string;
  activity_type?: string;
  software_used?: string;
  work_mode?: string;
  billable_hours?: number;
}

export interface TimeEntryUpdate {
  project_id?: string;
  task_id?: string;
  date?: string;
  hours?: number;
  description?: string;
  is_billable?: boolean;
  employee_name?: string;
  employee_role?: string;
  work_type?: string;
  sheet_reference_id?: string;
  revision?: string;
  activity_type?: string;
  software_used?: string;
  work_mode?: string;
  billable_hours?: number;
}

export interface TimeEntryListResponse {
  items: TimeEntry[];
  total: number;
  page: number;
  page_size: number;
}

export interface Timesheet {
  id: string;
  user_id: string;
  week_start: string;
  week_end: string;
  status: "draft" | "submitted" | "approved" | "rejected";
  total_hours: number;
  billable_hours: number;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  user_name?: string;
  approved_by_name?: string;
}

export interface TimesheetListResponse {
  items: Timesheet[];
  total: number;
  page: number;
  page_size: number;
}
