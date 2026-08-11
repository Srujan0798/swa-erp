export type RFQStatus = "draft" | "sent" | "responded" | "compared" | "awarded" | "closed" | "cancelled";

export interface RFQ {
  id: string;
  project_id: string;
  vendor_id: string;
  vendor_name: string;
  status: RFQStatus;
  rfq_number: string;
  created_by: string;
  created_by_name: string;
  sent_at?: string;
  responded_at?: string;
  awarded_at?: string;
  notes?: string;
  created_at: string;
  items: RFQItem[];
}

export interface RFQItem {
  id: string;
  material_id: string;
  material_name: string;
  material_unit: string;
  quantity: number;
  vendor_rate?: number;
  notes?: string;
}

export interface RFQCompareItem {
  material_id: string;
  material_name: string;
  unit: string;
  quantity: number;
  vendor_rates: {
    rfq_id: string;
    vendor_id: string;
    vendor_name: string;
    rate: number;
  }[];
}

export interface RFQListResponse {
  items: RFQ[];
  total: number;
  page: number;
  page_size: number;
}

export interface RFQCreatePayload {
  project_id?: string;
  vendor_id: string;
  notes?: string;
  items: {
    material_id: string;
    quantity: number;
    notes?: string;
  }[];
}

export interface RFQRespondPayload {
  items: {
    item_id: string;
    vendor_rate: number;
    notes?: string;
  }[];
}

export interface RFQAwardPayload {
  notes?: string;
}
