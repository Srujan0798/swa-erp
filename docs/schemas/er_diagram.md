---
title: SWA ERP — Entity Relationship Diagram
description: 25 SQLAlchemy models → 34 PostgreSQL tables. All tables verified present in migrated database.
generated: 2026-08-28
---

# SWA ERP — Entity Relationship Diagram (ERD)

25 ORM models map to 34 PostgreSQL tables (includes junction, audit, and ordinal tables).

**Status:** BUILT — all 34 tables verified present via `psql -h localhost -p 5432 -U swa -d swa_erp -c "\dt"` on 2026-08-28.

**Legend:**
- 🟢 = table exists in DB (verified)
- Solid line = foreign key
- Open diamond (}o--||) = many-to-one / belongs_to
- crow's foot (||--o{}) = one-to-many

---

## Full ERD

```mermaid
erDiagram
    %% ═══════════════════════════════════════════
    %% CORE CHAIN — Inquiry → Client → SA → Token → DocRef → TimeLog → Sustainability
    %% ═══════════════════════════════════════════

    USERS["users<br/>id PK · email · hashed_password · full_name · role · is_active · created_at · updated_at"] 
        ||--o{ CONTACTS : ""
        ||--o{ REFRESH_TOKENS : ""
        ||--o{ NOTIFICATIONS : "receives"
        ||--o{ TASKS : "assigned"
        ||--o{ TIME_ENTRIES : "logs"
        ||--o{ TOKENS : "issued"
        ||--o{ AUDIT_LOG : "actor"

    CLIENTS["clients<br/>id PK · code · name · industry · client_status · first_inquiry_id · first_lead_id ·<br/>address · contact_person · phone · email · created_at · updated_at · deleted_at"] 
        ||--o{ CONTACTS : ""
        ||--o{ PROJECTS : "spawns"
        ||--o{ INQUIRIES : "source"
        ||--o{ SERVICE_AGREEMENTS : "signs"
        ||--o{ QUOTES : "receives"
        ||--o{ INQUIRIES : "converted_from"
        ||--o{ INVOICES : "billed_for"

    INQUIRIES["inquiries<br/>id PK · reference_id · inquiry_date · inquiry_type · inquiry_source · client_name ·<br/>requirement_summary · estimated_value · priority · status · owner_id · technical_lead_id ·<br/>notes · converted_client_id · converted_project_id · created_at · updated_at · deleted_at"] 
        ||--o{ SERVICE_AGREEMENTS : "becomes"
        ||--o{ PROJECTS : "converted_to"
        ||--o{ TOKENS : "generates"

    SERVICE_AGREEMENTS["service_agreements<br/>id PK · reference_id · client_id · inquiry_id · service_name · start_date · end_date ·<br/>total_tokens · status · notes · created_at · updated_at · deleted_at"] 
        ||--o{ TOKENS : "authorizes"
        ||--o{ PROJECTS : "covers"

    TOKENS["tokens<br/>id PK · reference_id · client_id · service_agreement_id · project_id · token_type ·<br/>token_number · issue_date · expiry_date · status · created_at · updated_at · deleted_at"] 
        ||--o{ DOCUMENT_REFERENCES : "attaches"
        ||--o{ RFQS : "receives"
        ||--o{ PROJECTS : "linked_to"
        ||--o{ INVOICES : "against"

    DOCUMENT_REFERENCES["document_references<br/>id PK · reference_id · client_id · project_id · token_id · document_type · doc_code ·<br/>doc_number · title · description · status · created_at · updated_at · deleted_at"] 
        ||--o{ DOCUMENTS : "has"
        ||--o{ DOCUMENT_FOLDERS : "organizes"

    PROJECTS["projects<br/>id PK · reference_id · client_id · name · description · status · start_date · end_date ·<br/>budget · actual_cost · version · created_at · updated_at · deleted_at"] 
        ||--o{ PROJECT_COSTS : "has"
        ||--o{ QUOTES : "receives"
        ||--o{ TASKS : "contains"
        ||--o{ RFQS : "issues"
        ||--o{ BOQS : "has"
        ||--o{ INQUIRIES : "converted_from"
        ||--o{ SERVICE_AGREEMENTS : "covered_by"
        ||--o{ TIME_ENTRIES : "tracked_in"
        ||--o{ SUSTAINABILITY_METRICS : "has"
        ||--o{ INVOICES : "billed_for"
        ||--o{ DOCUMENT_REFERENCES : "has"

    PROJECT_COSTS["project_costs<br/>id PK · project_id FK · cost_type · amount · description · incurred_at · created_at · updated_at · deleted_at"] 
        }o--|| PROJECTS : "belongs_to"

    QUOTES["quotes<br/>id PK · reference_id · project_id · client_id · title · description · line_items ·<br/>total_amount · status · version · created_at · updated_at · deleted_at"] 
        ||--o{ QUOTE_ITEMS : "has"
        ||--o{ PROJECTS : "for"

    QUOTE_ITEMS["quote_items<br/>id PK · quote_id FK · description · quantity · unit_price · total · created_at · updated_at"] 
        }o--|| QUOTES : "belongs_to"

    RFQS["rfqs<br/>id PK · reference_id · project_id · vendor_id · token_id · rfq_number · title · description ·<br/>status · created_at · updated_at · deleted_at"] 
        ||--o{ RFQ_ITEMS : "has"
        ||--o{ VENDORS : "sent_to"
        ||--o{ PROJECTS : "for"

    RFQ_ITEMS["rfq_items<br/>id PK · rfq_id FK · description · quantity · unit · unit_price · created_at · updated_at"] 
        }o--|| RFQS : "belongs_to"

    BOQS["boqs<br/>id PK · reference_id · project_id · title · description · line_items · total_amount ·<br/>status · version · created_at · updated_at · deleted_at"] 
        ||--o{ BOQ_ITEMS : "has"
        ||--o{ PROJECTS : "for"

    BOQ_ITEMS["boq_items<br/>id PK · boq_id FK · description · quantity · unit_price · total · created_at · updated_at"] 
        }o--|| BOQS : "belongs_to"

    %% ═══════════════════════════════════════════
    %% VENDORS + MATERIALS
    %% ═══════════════════════════════════════════

    VENDORS["vendors<br/>id PK · code · name · contact_person · email · phone · address · status · created_at · updated_at · deleted_at"] 
        ||--o{ VENDOR_CONTACTS : ""
        ||--o{ MATERIALS : "supplies"
        ||--o{ RFQS : "receives"

    VENDOR_CONTACTS["vendor_contacts<br/>id PK · vendor_id FK · name · email · phone · role · created_at · updated_at"] 
        }o--|| VENDORS : "belongs_to"

    MATERIALS["materials<br/>id PK · code · name · category_id · vendor_id · unit · unit_price · stock_quantity ·<br/>min_stock · status · created_at · updated_at"] 
        ||--o{ MATERIAL_CATEGORIES : "categorized"
        ||--o{ VENDORS : "supplied_by"

    MATERIAL_CATEGORIES["material_categories<br/>id PK · name · parent_id · created_at"] 
        ||--o{ MATERIALS : "contains"

    %% ═══════════════════════════════════════════
    %% COMPLIANCE
    %% ═══════════════════════════════════════════

    COMPLIANCE_STANDARDS["compliance_standards<br/>id PK · code · name · version · description · created_at"] 
        ||--o{ COMPLIANCE_CHECKLIST_ITEMS : ""
        ||--o{ PROJECT_COMPLIANCE_ITEMS : ""

    COMPLIANCE_CHECKLIST_ITEMS["compliance_checklist_items<br/>id PK · standard_id FK · item_code · description · requirement · created_at"] 
        }o--|| COMPLIANCE_STANDARDS : "belongs_to"

    PROJECT_COMPLIANCE_ITEMS["project_compliance_items<br/>id PK · project_id FK · standard_id FK · item_id FK · status · reviewed_by · reviewed_at ·<br/>notes · created_at · updated_at"] 
        }o--|| PROJECTS : "belongs_to"
        }o--|| COMPLIANCE_CHECKLIST_ITEMS : "checks"

    %% ═══════════════════════════════════════════
    %% TIME + NOTIFICATIONS
    %% ═══════════════════════════════════════════

    NOTIFICATIONS["notifications<br/>id PK · user_id FK · title · message · type · read · created_at"] 
        }o--|| USERS : "for"
    
    %% NOTE: notifications router is BUILT (mounted in main.py) but handlers are STUBS
    %% list_notifications → [], mark_read → {} — wave-24 item #6

    TIME_ENTRIES["time_entries<br/>id PK · project_id FK · user_id FK · hours · description · billable · date · created_at · updated_at"] 
        }o--|| PROJECTS : "logged_to"
        }o--|| USERS : "by"

    TIMESHEETS["timesheets<br/>id PK · user_id FK · period_start · period_end · status · created_at · updated_at"] 
        ||--o{ TIME_ENTRIES : "aggregates"
        ||--o{ USERS : "belongs_to"

    SUSTAINABILITY_METRICS["sustainability_metrics<br/>id PK · reference_id · project_id · compliant_with_green_standards · green_standard ·<br/>insulation_efficiency · energy_rating · carbon_footprint · payback_period_months · created_at · updated_at"] 
        }o--|| PROJECTS : "for"

    %% ═══════════════════════════════════════════
    %% DOCUMENTS + FOLDERS
    %% ═══════════════════════════════════════════

    DOCUMENTS["documents<br/>id PK · document_folder_id FK · file_name · file_path · mime_type · size · uploaded_by · created_at"] 
        }o--|| DOCUMENT_FOLDERS : "stored_in"

    DOCUMENT_FOLDERS["document_folders<br/>id PK · name · parent_id · created_at"] 
        ||--o{ DOCUMENTS : "contains"
        ||--o{ DOCUMENT_REFERENCES : "organizes"

    %% ═══════════════════════════════════════════
    %% AUDIT + ORDINAL
    %% ═══════════════════════════════════════════

    REFERENCE_COUNTERS["reference_counters<br/>id PK · entity_type · year · sequence · created_at · updated_at"] 
        }o--|| RID : "tracked_by"
    %% RID = reference_id_service.py (NOT a table — shown as dependency)

    AUDIT_LOG["audit_log<br/>id PK · actor_id FK · action · entity_type · entity_id · old_values JSON · new_values JSON · created_at"] 
        }o--|| USERS : "by"
        }o--|| PROJECTS : "of"
        }o--|| CLIENTS : "of"

    TASK_DEPENDENCIES["task_dependencies<br/>id PK · task_id FK · depends_on_task_id FK · created_at"] 
        }o--|| TASKS : "depends_on"
        }o--|| TASKS : "required_by"

    TASK_COMMENTS["task_comments<br/>id PK · task_id FK · user_id FK · content · created_at · updated_at"] 
        }o--|| TASKS : "on"
        }o--|| USERS : "by"

    INVOICES["invoices<br/>id PK · reference_id · project_id · client_id · token_id · invoice_number · issue_date ·<br/>due_date · amount · gst_amount · total_amount · status · created_at · updated_at · deleted_at"] 
        ||--o{ INVOICE_ITEMS : "has"
        ||--o{ PROJECTS : "for"
        ||--o{ TOKENS : "against"

    INVOICE_ITEMS["invoice_items<br/>id PK · invoice_id FK · description · quantity · unit_price · amount · created_at · updated_at"] 
        }o--|| INVOICES : "belongs_to"

    TIMESHEET_AUDIT_LOG["timesheet_audit_log<br/>id PK · timesheet_id FK · action · actor_id FK · old_values JSON · new_values JSON · created_at"] 
        }o--|| TIMESHEETS : "audits"
        }o--|| USERS : "by"

    %% ═══════════════════════════════════════════
    %% TASKS (standalone, not part of core chain)
    %% ═══════════════════════════════════════════

    TASKS["tasks<br/>id PK · project_id FK · title · description · status · assignee_id · priority · due_date ·<br/>created_at · updated_at · deleted_at"] 
        ||--o{ TASK_COMMENTS : ""
        ||--o{ TASK_DEPENDENCIES : "depends_on"
        ||--o{ NOTIFICATIONS : ""
```

---

## Table inventory (all 34, verified present in DB 2026-08-28)

| # | Table | Source model | Notes |
|---|-------|-------------|-------|
| 1 | users | models/user.py | RBAC roles: admin/pm/designer/auditor/viewer |
| 2 | clients | models/client.py | SWA-{year}-CLT-{seq} reference ID |
| 3 | contacts | models/contact.py | Client + vendor contacts |
| 4 | inquiries | models/inquiry.py | SWA-{year}-INQ-{seq} |
| 5 | service_agreements | models/agreement.py | SWA-{year}-SA-{seq}, free-text service_name |
| 6 | tokens | models/token.py | SWA-{year}-TKN-{seq} |
| 7 | document_references | models/document_reference.py | SWA-{year}-DBR-{seq}, KDR shares counter |
| 8 | documents | models/document.py | File metadata (path in storage) |
| 9 | document_folders | models/ | Folder hierarchy for documents |
| 10 | projects | models/project.py | SWA-{year}-PRJ-{seq} (via reference_id_service) |
| 11 | project_costs | models/project_cost.py | Junction: project ↔ cost entries |
| 12 | quotes | models/quote.py | Quotation to client |
| 13 | quote_items | models/ | Quote line items |
| 14 | rfqs | models/rfq.py | Request for quote to vendor |
| 15 | rfq_items | models/ | RFQ line items |
| 16 | boqs | models/boq.py | Bill of quantities |
| 17 | boq_items | models/ | BOQ line items |
| 18 | vendors | models/vendor.py | Vendor database |
| 19 | vendor_contacts | models/ | Vendor contact people |
| 20 | materials | models/material.py | Material catalog |
| 21 | material_categories | models/ | Category hierarchy |
| 22 | compliance_standards | models/compliance.py | NBC/ECBC/IGBC/IS |
| 23 | compliance_checklist_items | models/ | Checklist items per standard |
| 24 | project_compliance_items | models/ | Project ↔ checklist item status |
| 25 | notifications | models/notification.py | 🟡 Router BUILT, handlers STUB (returns []/{}) |
| 26 | time_entries | models/time_tracking.py | 15-min increments, billable flag |
| 27 | timesheets | models/ | Timesheet aggregate |
| 28 | timesheet_audit_log | models/ | Audit trail for timesheet changes |
| 29 | sustainability_metrics | models/sustainability_metric.py | SWA-{year}-SM-{seq} |
| 30 | invoices | models/invoice.py | With GST (wave-18, commit 2073c36) |
| 31 | invoice_items | models/ | Invoice line items |
| 32 | reference_counters | models/reference_counter.py | Per-year sequence tracking |
| 33 | refresh_tokens | models/refresh_token.py | JWT refresh |
| 34 | audit_log | models/audit_log.py | Entity audit trail |

**Summary:** 25 model files → 34 tables. junction/audit/ordinal tables: project_costs, quote_items, rfq_items, boq_items, vendor_contacts, material_categories, compliance_checklist_items, project_compliance_items, task_dependencies, task_comments, invoice_items, timesheet_audit_log, documents, document_folders (14 non-model tables).

## Reference ID scheme (BUILT, atomic)

```
SWA-{year}-{TYPE}-{seq:03d}
```

Generated by `src/backend/services/reference_id_service.py:generate_reference_id(db, entity_type)`.
Counters tracked in `reference_counters` table, keyed by `(entity_type, year)`. Resets each calendar year — confirmed by Viraj (ADR-0002).

Entity types: INQ, CLT, SA, TKN, DRB (DBR/KDR share counter), SM, PRJ.

## BUILT vs TARGET-STATE

- **BUILT:** All 34 tables, 25 models, reference_id_service, Alembic migrations (33 versions), Celery workers, async export, GST on invoices, StorageBackend
- **TARGET-STATE:** MinIO active by default (currently opt-in only), Windows Server deployment (IT blocker), NBC/ECBC/IGBC/IS compliance standard versions (ADR-0002 #5 still open)
