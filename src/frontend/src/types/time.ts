export interface TimeEntry {
  id: string;
  project_id: string;
  task_id: string | null;
  user_id: string;
  date: string;
  hours: number;
  description: string;
  is_billable: boolean;
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
}

export interface TimeEntryUpdate {
  project_id?: string;
  task_id?: string;
  date?: string;
  hours?: number;
  description?: string;
  is_billable?: boolean;
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
