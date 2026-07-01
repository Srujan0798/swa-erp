export interface DocumentItem {
  id: string;
  project_id: string;
  folder_id: string | null;
  name: string;
  file_path: string;
  file_size: number;
  content_type: string;
  uploaded_by: string;
  uploaded_by_name: string | null;
  tags: string[];
  version: number;
  is_active: boolean;
  created_at: string;
}

export interface DocumentFolder {
  id: string;
  project_id: string;
  name: string;
  parent_id: string | null;
  created_at: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface DocumentFolderListResponse {
  items: DocumentFolder[];
  total: number;
}

export interface DocumentSearchResponse {
  items: DocumentItem[];
  total: number;
}
