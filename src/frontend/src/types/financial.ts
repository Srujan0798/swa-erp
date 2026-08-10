export interface Invoice {
  id: string;
  project_id: string;
  invoice_number: string;
  status: "draft" | "sent" | "paid";
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  gst_percent: number;
  gst_amount: number;
  total: number;
  currency: string;
  due_date: string | null;
  notes: string | null;
  created_by: string;
  paid_at: string | null;
  created_at: string;
  items: InvoiceItem[];
  project_name?: string;
  created_by_name?: string;
}

export interface InvoiceItem {
  id: string;
  invoice_id: string;
  description: string;
  quantity: number;
  rate: number;
  amount: number;
  category: string | null;
  time_entry_id: string | null;
}

export interface InvoiceCreate {
  /** Path param on create; optional in body for FE convenience. */
  project_id?: string;
  invoice_number?: string;
  tax_rate?: number;
  due_date?: string;
  notes?: string;
  items: InvoiceItemCreate[];
}

export interface InvoiceItemCreate {
  description: string;
  quantity: number;
  rate: number;
  category?: string;
  time_entry_id?: string;
}

export interface InvoiceListResponse {
  items: Invoice[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProjectPnL {
  project_id: string;
  project_name: string;
  total_revenue: number;
  total_costs: number;
  net_profit: number;
  margin_pct: number;
  cost_breakdown: CostBreakdownItem[];
}

export interface CostBreakdownItem {
  category: string;
  amount: number;
  count: number;
  percentage: number;
}

export interface ProjectCost {
  id: string;
  project_id: string;
  category: string;
  description: string;
  amount: number;
  date: string;
  created_at: string;
}

export interface ProjectCostCreate {
  category: string;
  description: string;
  amount: number;
  date: string;
}

export interface ProjectCostListResponse {
  items: ProjectCost[];
  total: number;
  page: number;
  page_size: number;
}
