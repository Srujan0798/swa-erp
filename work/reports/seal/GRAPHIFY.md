# work/reports/seal/GRAPHIFY.md

> Session seal Phase 0. Graph: graphify-out/graph.json (built prior session; queried this session).
> Commands run this session with exit codes where shown.

## Required queries (output extracts)

### `graphify query "Inquiry to Invoice ID chain"`
```
Graph: graphify-out/graph.json (4959 nodes) | Traversal: BFS depth=2 | Start: ['Inquiry', 'Invoice', 'smoke_chain.py'] | 333 nodes found
[!] TRUNCATED: showing 49 of 333 nodes (~1500-token budget). The answer may be among the 284 cut nodes — raise the token budget (CLI: --budget) or narrow the query (e.g. context_filter=['call'], or get_node for a specific symbol).
NODE Inquiry [src=src/backend/models/inquiry.py loc=L12 community=Community 29]
NODE Invoice [src=src/backend/models/invoice.py loc=L12 community=Community 37]
NODE smoke_chain.py [src=scripts/smoke_chain.py loc=L1 community=Community 17]
NODE datetime [src= loc= community=Community 18]
NODE Base [src=src/backend/db/base.py loc=L4 community=Community 18]
NODE uuid [src= loc= community=Community 18]
NODE models/__init__.py [src=src/backend/models/__init__.py loc=L1 community=Community 18]
NODE invoice_service.py [src=src/backend/services/invoice_service.py loc=L1 community=Community 37]
NODE inquiry_service.py [src=src/backend/services/inquiry_service.py loc=L1 community=Community 29]
NODE test_invoicing.py [src=tests/wave-7/test_invoicing.py loc=L1 community=Community 45]
NODE test_reports_service.py [src=tests/wave-8/test_reports_service.py loc=L1 community=Community 20]
NODE project_pnl_service.py [src=src/backend/services/project_pnl_service.py loc=L1 community=Community 34]
NODE test_migrations.py [src=tests/test_migrations.py loc=L1 community=Community 18]
NODE code_based.py [src=evals/graders/code_based.py loc=L1 community=Community 18]
NODE test_agreements.py [src=tests/wave-9/test_agreements.py loc=L1 community=Community 13]
NODE convert_inquiry() [src=src/backend/services/inquiry_service.py loc=L47 community=Community 23]
NODE wave_43_evals.py [src=evals/wave_43_evals.py loc=L1 community=Community 18]
NODE create_inquiry_service() [src=src/backend/services/inquiry_service.py loc=L207 community=Community 23]
NODE report_repo.py [src=src/backend/db/repositories/report_repo.py loc=L1 community=Community 18]
NODE models/inquiry.py [src=src/backend/models/inquiry.py loc=L1 community=Community 18]
NODE seed_demo.py [src=scripts/seed_demo.py loc=L1 community=Community 11]
NODE invoice_repo.py [src=src/backend/db/repositories/invoice_repo.py loc=L1 community=Community 37]
NODE os [src= loc= community=Community 17]
NODE models/invoice.py [src=src/backend/models/invoice.py loc=L1 community=Community 18]
NODE inquiry_repo.py [src=src/backend/db/repositories/inquiry_repo.py loc=L1 community=Community 29]
NODE main() [src=scripts/seed_demo.py loc=L20 community=Community 11]
NODE generate_from_time_entries() [src=src/backend/services/invoice_service.py loc=L144 community=Community 37]
NODE update_inquiry_service() [src=src/backend/services/inquiry_service.py loc=L234 community=Community 23]
NODE grader_002_id_chain() [src=evals/graders/code_based.py loc=L142 community=Community 11]
NODE get_by_id() [src=src/backend/db/repositories/inquiry_repo.py loc=L36 community=Community 29]
NODE get_inquiry_service() [src=src/backend/services/inquiry_service.py loc=L203 community=Community 23]
NODE _invoice_to_read() [src=src/backend/services/invoice_service.py loc=L41 community=Community 37]
NODE httpx [src= loc= community=Community 52]
NODE get_invoice_with_items() [src=src/backend/db/repositories/invoice_repo.py loc=L101 community=Community 37]
NODE sys [src= loc= community=Community 17]
NODE grader_001_inquiry_conversion() [src=evals/graders/code_based.py loc=L80 community=Community 11]
NODE create_invoice() [src=src/backend/db/repositories/invoice_repo.py loc=L30 community=Community 37]
NODE soft_delete_invoice() [src=src/backend/db/repositories/invoice_repo.py loc=L149 community=Community 37]
NODE update_invoice_status() [src=src/backend/db/repositories/invoice_repo.py loc=L127 community=Community 37]
NODE list_inquiries_service() [src=src/backend/services/inquiry_service.py loc=L192 community=Community 23]
NODE test_scratch_db_core_chain_works() [src=tests/test_migrations.py loc=L260 community=Community 11]
NODE test_generate_rolls_back_flags_on_failure() [src=tests/wave-7/test_invoicing.py loc=L217 community=Community 11]
NODE test_002_agreement_token_docref_chain() [src=evals/wave_43_evals.py loc=L110 community=Community 29]
NODE update() [src=src/backend/db/repositories/inquiry_repo.py loc=L56 community=Community 29]
NODE client_summary_query() [src=src/backend/db/repositories/report_repo.py loc=L181 community=Community 20]
NODE grader_004_time_aggregation() [src=evals/graders/code_based.py loc=L244 community=Community 11]
NODE test_001_inquiry_to_client_conversion() [src=evals/wave_43_evals.py loc=L40 community=Community 11]
NODE create() [src=src/backend/db/repositories/inquiry_repo.py loc=L48 community=Community 29]
NODE get_invoice_by_id() [src=src/backend/db/repositories/invoice_repo.py loc=L90 community=Community 37]
... (truncated — 284 more nodes cut by ~1500-token budget. Narrow with context_filter=['call'] or use get_node for a specific symbol)
```

### `graphify query "RBAC enforcement points"`
```
Graph: graphify-out/graph.json (4959 nodes) | Traversal: BFS depth=2 | Start: ['RBAC Enforcement Eval', 'RBAC Role Hierarchy', 'Unbounded List Endpoints', 'Role-Based Access Control'] | 39 nodes found
[i] Complete answer over budget: all 39 nodes and 45 edges shown (~2589 tokens vs the requested ~1500-token budget). Edges are never dropped once every node fits, so this is already the full answer — raising --budget further will not shrink it. Narrow with context_filter=['call'] or use get_node for a specific symbol to reduce size instead.
NODE RBAC Enforcement Eval [src=evals/tasks/003-rbac-enforcement.task.yaml loc=None community=Community 74]
NODE RBAC Role Hierarchy [src=docs/flows/02_auth_rbac.md loc=None community=Community 74]
NODE Unbounded List Endpoints [src=work/wave-48/02-pagination-idempotency.md loc=None community=Community 126]
NODE Role-Based Access Control [src=work/reports/dispatch-24h/AGENT-L2-A.md loc=None community=Community 62]
NODE AGENT-L6-A: Role Matrix RBAC Verification [src=work/reports/dispatch-24h/AGENT-L6-A.md loc=None community=Community 62]
NODE Wave-48 Pagination Idempotency [src=work/wave-48/02-pagination-idempotency.md loc=None community=Community 126]
NODE JWT Authentication [src=docs/flows/02_auth_rbac.md loc=None community=Community 74]
NODE Wave-22 RBAC Hardening [src=docs/historical/CHANGELOG.md loc=None community=Community 74]
NODE AGENT-L10-D: Core Chain Completion Status [src=work/reports/dispatch-24h/AGENT-L10-D.md loc=None community=Community 62]
NODE AGENT-L2-A: RBAC Implementation [src=work/reports/dispatch-24h/AGENT-L2-A.md loc=None community=Community 62]
NODE Pagination [src=work/wave-48/02-pagination-idempotency.md loc=None community=Community 126]
NODE Access Control Matrix [src=resources/MEETINGS_MASTER.md loc=None community=Community 74]
NODE Admin Role [src=docs/flows/02_auth_rbac.md loc=None community=Community 74]
NODE Auditor Role [src=docs/flows/02_auth_rbac.md loc=None community=Community 74]
NODE Designer Role [src=docs/flows/02_auth_rbac.md loc=None community=Community 74]
NODE PM Role [src=docs/flows/02_auth_rbac.md loc=None community=Community 74]
NODE Viewer Role [src=docs/flows/02_auth_rbac.md loc=None community=Community 74]
NODE Auth and RBAC Architecture [src=plan/ARCHITECTURE.md loc=None community=Community 74]
NODE Level 2 Implementation Completion [src=work/reports/dispatch-24h/AGENT-L2-A.md loc=None community=Community 120]
NODE Level 6 Implementation Completion [src=work/reports/dispatch-24h/AGENT-L6-A.md loc=None community=Community 62]
NODE Level 10 Implementation Completion [src=work/reports/dispatch-24h/AGENT-L10-A.md loc=None community=Community 62]
NODE Viewer Role Read-Only Enforcement [src=work/reports/dispatch-24h/AGENT-L2-A.md loc=None community=Community 62]
NODE Admin Bypass of Project Membership IDOR [src=work/reports/dispatch-24h/AGENT-L6-A.md loc=None community=Community 62]
NODE Wave Status Tracking [src=plan/EXECUTION.md loc=None community=Community 74]
NODE Documents API [src=work/reports/dispatch-24h/AGENT-L6-C.md loc=None community=Community 62]
NODE Jobs API [src=work/reports/dispatch-24h/AGENT-L6-A.md loc=None community=Community 62]
NODE Exports API [src=work/reports/dispatch-24h/AGENT-L6-A.md loc=None community=Community 62]
NODE Idempotency [src=work/wave-48/02-pagination-idempotency.md loc=None community=Community 126]
NODE Idempotency Gap [src=work/wave-48/02-pagination-idempotency.md loc=None community=Community 126]
NODE Project Repository [src=work/reports/dispatch-24h/AGENT-L6-A.md loc=None community=Community 62]
NODE Celery Export UI Hook [src=work/reports/dispatch-24h/AGENT-L10-D.md loc=None community=Community 62]
NODE Rate Limiting [src=docs/flows/02_auth_rbac.md loc=None community=Community 74]
NODE Export Endpoint 403 Bug [src=docs/historical/BACKEND_TEST_AUDIT_REPORT.md loc=None community=Community 74]
NODE Wave-31 Deferred Features [src=docs/historical/CHANGELOG.md loc=None community=Community 74]
NODE Compliance API [src=work/wave-48/02-pagination-idempotency.md loc=None community=Community 126]
NODE Sustainability Metrics API [src=work/wave-48/02-pagination-idempotency.md loc=None community=Community 126]
NODE Tokens API [src=work/wave-48/02-pagination-idempotency.md loc=None community=Community 126]
NODE Idempotency Module [src=work/wave-48/02-pagination-idempotency.md loc=None community=Community 126]
NODE Wave 22 RBAC Gaps Tests [src=work/reports/dispatch-24h/AGENT-L6-A.md loc=None community=Community 62]
EDGE AGENT-L10-D: Core Chain Completion Status --references [EXTRACTED]--> Role-Based Access Control
EDGE AGENT-L2-A: RBAC Implementation --references [EXTRACTED]--> Role-Based Access Control
EDGE AGENT-L6-A: Role Matrix RBAC Verification --references [EXTRACTED]--> Role-Based Access Control
EDGE RBAC Role Hierarchy --implements [EXTRACTED]--> Admin Role
EDGE RBAC Role Hierarchy --implements [EXTRACTED]--> Auditor Role
EDGE RBAC Role Hierarchy --implements [EXTRACTED]--> Designer Role
EDGE RBAC Role Hierarchy --implements [EXTRACTED]--> PM Role
EDGE RBAC Role Hierarchy --implements [EXTRACTED]--> Viewer Role
EDGE JWT Authentication --rationale_for [EXTRACTED]--> RBAC Role Hierarchy
EDGE Access Control Matrix --rationale_for [EXTRACTED]--> RBAC Role Hierarchy
EDGE Wave-22 RBAC Hardening --references [INFERRED]--> RBAC Role Hierarchy
EDGE Auth and RBAC Architecture --semantically_similar_to [INFERRED]--> RBAC Role Hierarchy
EDGE RBAC Enforcement Eval --references [INFERRED]--> Access Control Matrix
EDGE Wave-48 Pagination Idempotency --addresses [EXTRACTED]--> Unbounded List Endpoints
EDGE Unbounded List Endpoints --rationale_for [EXTRACTED]--> Pagination
EDGE Export Endpoint 403 Bug --rationale_for [INFERRED]--> Wave-22 RBAC Hardening
EDGE Wave Status Tracking --references [INFERRED]--> Wave-22 RBAC Hardening
EDGE Wave-48 Pagination Idempotency --addresses [EXTRACTED]--> Idempotency Gap
EDGE Wave-48 Pagination Idempotency --creates [EXTRACTED]--> Idempotency Module
```

### `graphify query "GST invoice calculation"`
```
Graph: graphify-out/graph.json (4959 nodes) | Traversal: BFS depth=2 | Start: ['Invoice', 'Invoice GST Correctness Eval', 'Invoice with 3 line items: GST 18% exact, money stays Decimal.', '.test_calculation()', 'GST Invoicing Implementation'] | 201 nodes found
[!] TRUNCATED: showing 48 of 201 nodes (~1500-token budget). The answer may be among the 153 cut nodes — raise the token budget (CLI: --budget) or narrow the query (e.g. context_filter=['call'], or get_node for a specific symbol).
NODE Invoice [src=src/backend/models/invoice.py loc=L12 community=Community 37]
NODE Invoice GST Correctness Eval [src=evals/tasks/005-invoice-gst-correctness.task.yaml loc=None community=Community 147]
NODE Invoice with 3 line items: GST 18% exact, money stays Decimal. [src=evals/wave_43_evals.py loc=L332 community=Community 37]
NODE .test_calculation() [src=tests/wave-8/test_reports_service.py loc=L163 community=Community 20]
NODE GST Invoicing Implementation [src=docs/conventions.md loc=None community=Community 63]
NODE Base [src=src/backend/db/base.py loc=L4 community=Community 18]
NODE models/__init__.py [src=src/backend/models/__init__.py loc=L1 community=Community 18]
NODE invoice_service.py [src=src/backend/services/invoice_service.py loc=L1 community=Community 37]
NODE test_invoicing.py [src=tests/wave-7/test_invoicing.py loc=L1 community=Community 45]
NODE test_reports_service.py [src=tests/wave-8/test_reports_service.py loc=L1 community=Community 20]
NODE project_pnl_service.py [src=src/backend/services/project_pnl_service.py loc=L1 community=Community 34]
NODE code_based.py [src=evals/graders/code_based.py loc=L1 community=Community 18]
NODE wave_43_evals.py [src=evals/wave_43_evals.py loc=L1 community=Community 18]
NODE report_repo.py [src=src/backend/db/repositories/report_repo.py loc=L1 community=Community 18]
NODE invoice_repo.py [src=src/backend/db/repositories/invoice_repo.py loc=L1 community=Community 37]
NODE models/invoice.py [src=src/backend/models/invoice.py loc=L1 community=Community 18]
NODE generate_from_time_entries() [src=src/backend/services/invoice_service.py loc=L144 community=Community 37]
NODE _invoice_to_read() [src=src/backend/services/invoice_service.py loc=L41 community=Community 37]
NODE get_invoice_with_items() [src=src/backend/db/repositories/invoice_repo.py loc=L101 community=Community 37]
NODE create_invoice() [src=src/backend/db/repositories/invoice_repo.py loc=L30 community=Community 37]
NODE soft_delete_invoice() [src=src/backend/db/repositories/invoice_repo.py loc=L149 community=Community 37]
NODE update_invoice_status() [src=src/backend/db/repositories/invoice_repo.py loc=L127 community=Community 37]
NODE test_generate_rolls_back_flags_on_failure() [src=tests/wave-7/test_invoicing.py loc=L217 community=Community 11]
NODE _seed_client() [src=tests/wave-8/test_reports_service.py loc=L38 community=Community 20]
NODE _seed_project() [src=tests/wave-8/test_reports_service.py loc=L52 community=Community 20]
NODE client_summary_query() [src=src/backend/db/repositories/report_repo.py loc=L181 community=Community 20]
NODE Core Business Chain Flow [src=docs/ARCHITECTURE.md loc=None community=Community 63]
NODE grader_004_time_aggregation() [src=evals/graders/code_based.py loc=L244 community=Community 11]
NODE get_invoice_by_id() [src=src/backend/db/repositories/invoice_repo.py loc=L90 community=Community 37]
NODE list_invoices() [src=src/backend/db/repositories/invoice_repo.py loc=L108 community=Community 37]
NODE _get_revenue() [src=src/backend/services/project_pnl_service.py loc=L33 community=Community 34]
NODE _seed_user() [src=tests/wave-8/test_reports_service.py loc=L23 community=Community 20]
NODE grader_005_gst() [src=evals/graders/code_based.py loc=L310 community=Community 11]
NODE test_004_time_log_to_dashboard() [src=evals/wave_43_evals.py loc=L261 community=Community 45]
NODE revenue_query() [src=src/backend/db/repositories/report_repo.py loc=L130 community=Community 20]
NODE test_005_invoice_gst_correctness() [src=evals/wave_43_evals.py loc=L331 community=Community 37]
NODE _seed_invoice() [src=tests/wave-8/test_reports_service.py loc=L101 community=Community 20]
NODE TestUtilization [src=tests/wave-8/test_reports_service.py loc=L162 community=Community 20]
NODE _seed_time_entry() [src=tests/wave-8/test_reports_service.py loc=L86 community=Community 20]
NODE MVP Definition [src=plan/PRD.md loc=None community=Community 147]
NODE User [src=src/backend/models/user.py loc=L11 community=Community 81]
NODE sqlalchemy_orm [src= loc= community=Community 18]
NODE sqlalchemy [src= loc= community=Community 18]
NODE datetime [src= loc= community=Community 18]
NODE Project [src=src/backend/models/project.py loc=L12 community=Community 11]
NODE create_entry() [src=src/backend/db/repositories/audit_repo.py loc=L41 community=Community 2]
NODE uuid [src= loc= community=Community 18]
NODE Client [src=src/backend/models/client.py loc=L11 community=Community 11]
... (truncated — 153 more nodes cut by ~1500-token budget. Narrow with context_filter=['call'] or use get_node for a specific symbol)
```

### `graphify query "Excel sheet importer"`
```
Graph: graphify-out/graph.json (4959 nodes) | Traversal: BFS depth=2 | Start: ['Excel -> ERP importer. Usage: python3 scripts/import_excel.py <sheet_type>…', 'Excel Sheets Wave Mapping', 'Excel Sheets Inventory Documentation', 'Excel to ERP Migration Tool', 'Bootstrap Real Importer Script', '_sheet()'] | 93 nodes found
[!] TRUNCATED: showing 44 of 93 nodes (~1500-token budget). The answer may be among the 49 cut nodes — raise the token budget (CLI: --budget) or narrow the query (e.g. context_filter=['call'], or get_node for a specific symbol).
NODE Excel -> ERP importer. Usage: python3 scripts/import_excel.py <sheet_type>… [src=scripts/import_excel.py loc=L1 community=Community 17]
NODE Excel Sheets Wave Mapping [src=resources/EXCEL_SHEETS_INVENTORY.md loc=None community=Community 74]
NODE Excel Sheets Inventory Documentation [src=work/reports/dispatch-24h/AGENT-L5-C.md loc=None community=Community 108]
NODE Excel to ERP Migration Tool [src=docs/REAL_DATA.md loc=None community=Community 63]
NODE Bootstrap Real Importer Script [src=work/reports/dispatch-24h/AGENT-L5-A.md loc=None community=Community 108]
NODE _sheet() [src=tests/wave-33/test_import_service.py loc=L67 community=Community 9]
NODE wave-33/test_import_service.py [src=tests/wave-33/test_import_service.py loc=L1 community=Community 9]
NODE SWA ERP Product v1.0.1 [src=deliverables/SUBMISSION.md loc=None community=Community 63]
NODE import_excel.py [src=scripts/import_excel.py loc=L1 community=Community 17]
NODE AGENT-L5-A: Core Sheet Import Dry Run [src=work/reports/dispatch-24h/AGENT-L5-A.md loc=None community=Community 108]
NODE Import Service [src=work/reports/dispatch-24h/AGENT-L5-A.md loc=None community=Community 108]
NODE Viraj Founder Client [src=decisions/VIRAJ_DECISIONS.md loc=None community=Community 63]
NODE Import Real Sheets Script [src=work/reports/dispatch-24h/AGENT-L5-A.md loc=None community=Community 108]
NODE Wave Status Tracking [src=plan/EXECUTION.md loc=None community=Community 74]
NODE AGENT-L5-C: Independent Sheets MVP Exclusion [src=work/reports/dispatch-24h/AGENT-L5-C.md loc=None community=Community 108]
NODE Bootstrap Real Script [src=work/reports/dispatch-24h/AGENT-L5-C.md loc=None community=Community 108]
NODE test_bad_inquiry_date_reports_error() [src=tests/wave-33/test_import_service.py loc=L213 community=Community 9]
NODE test_clients_update_path() [src=tests/wave-33/test_import_service.py loc=L343 community=Community 9]
NODE test_doc_ref_missing_project_reports_error() [src=tests/wave-33/test_import_service.py loc=L235 community=Community 9]
NODE test_document_reference_import_is_idempotent() [src=tests/wave-33/test_import_service.py loc=L287 community=Community 9]
NODE test_dry_run_does_not_commit() [src=tests/wave-33/test_import_service.py loc=L332 community=Community 9]
NODE test_ensure_client_stub_created_when_stubs_allowed() [src=tests/wave-33/test_import_service.py loc=L151 community=Community 9]
NODE test_ensure_project_stub_created_for_doc_ref() [src=tests/wave-33/test_import_service.py loc=L179 community=Community 9]
NODE test_missing_key_fields_report_row_errors() [src=tests/wave-33/test_import_service.py loc=L201 community=Community 9]
NODE test_project_missing_client_reports_error() [src=tests/wave-33/test_import_service.py loc=L246 community=Community 9]
NODE test_stub_creation_refused_when_stubs_disabled() [src=tests/wave-33/test_import_service.py loc=L168 community=Community 9]
NODE test_sustainability_green_string_falls_back_to_true() [src=tests/wave-33/test_import_service.py loc=L268 community=Community 9]
NODE test_time_logs_duplicate_row_skipped() [src=tests/wave-33/test_import_service.py loc=L303 community=Community 9]
NODE test_time_logs_unknown_ref_reports_error() [src=tests/wave-33/test_import_service.py loc=L257 community=Community 9]
NODE test_token_missing_agreement_reports_error() [src=tests/wave-33/test_import_service.py loc=L224 community=Community 9]
NODE Sheet Relationships [src=resources/MEETINGS_MASTER.md loc=None community=Community 74]
NODE sqlalchemy [src= loc= community=Community 18]
NODE datetime [src= loc= community=Community 18]
NODE Base [src=src/backend/db/base.py loc=L4 community=Community 18]
NODE import_service.py [src=src/backend/services/import_service.py loc=L1 community=Community 9]
NODE pytest [src= loc= community=Community 52]
NODE TimeEntry [src=src/backend/models/time_tracking.py loc=L12 community=Community 45]
NODE session.py [src=src/backend/db/session.py loc=L1 community=Community 19]
NODE import_sheet() [src=src/backend/services/import_service.py loc=L1035 community=Community 9]
NODE base.py [src=src/backend/db/base.py loc=L1 community=Community 18]
NODE ServiceAgreement [src=src/backend/models/agreement.py loc=L11 community=Community 18]
NODE models/client.py [src=src/backend/models/client.py loc=L1 community=Community 18]
NODE models/project.py [src=src/backend/models/project.py loc=L1 community=Community 18]
NODE DocumentReference [src=src/backend/models/document_reference.py loc=L11 community=Community 4]
... (truncated — 49 more nodes cut by ~1500-token budget. Narrow with context_filter=['call'] or use get_node for a specific symbol)
```

### `graphify query "soft delete audit_log"`
```
Graph: graphify-out/graph.json (4959 nodes) | Traversal: BFS depth=2 | Start: ['delete()', 'Soft Delete Policy and Exceptions', 'Soft-Delete Pattern', 'Audit Trail Gap', 'LoginPage.tsx'] | 280 nodes found
[!] TRUNCATED: showing 48 of 280 nodes (~1500-token budget). The answer may be among the 232 cut nodes — raise the token budget (CLI: --budget) or narrow the query (e.g. context_filter=['call'], or get_node for a specific symbol).
NODE delete() [src=src/backend/db/repositories/contact_repo.py loc=L47 community=Community 85]
NODE Soft Delete Policy and Exceptions [src=docs/decisions/0003-soft-delete-exceptions.md loc=None community=Community 63]
NODE Soft-Delete Pattern [src=.specify/memory/constitution.md loc=None community=Community 72]
NODE Audit Trail Gap [src=work/wave-48/01-production-hardening.md loc=None community=Community 28]
NODE LoginPage.tsx [src=src/frontend/src/pages/LoginPage.tsx loc=L1 community=Community 1]
NODE react [src=src/frontend/package.json loc=L34 community=Community 1]
NODE button.tsx [src=src/frontend/src/components/ui/button.tsx loc=L1 community=Community 1]
NODE Button [src=src/frontend/src/components/ui/button.tsx loc=L38 community=Community 1]
NODE App.tsx [src=src/frontend/src/App.tsx loc=L1 community=Community 15]
NODE card.tsx [src=src/frontend/src/components/ui/card.tsx loc=L1 community=Community 21]
NODE Card [src=src/frontend/src/components/ui/card.tsx loc=L4 community=Community 21]
NODE useAuth.ts [src=src/frontend/src/hooks/useAuth.ts loc=L1 community=Community 21]
NODE CardContent [src=src/frontend/src/components/ui/card.tsx loc=L40 community=Community 21]
NODE CardHeader [src=src/frontend/src/components/ui/card.tsx loc=L15 community=Community 1]
NODE CardTitle [src=src/frontend/src/components/ui/card.tsx loc=L22 community=Community 1]
NODE input.tsx [src=src/frontend/src/components/ui/input.tsx loc=L1 community=Community 1]
NODE label.tsx [src=src/frontend/src/components/ui/label.tsx loc=L1 community=Community 1]
NODE Input [src=src/frontend/src/components/ui/input.tsx loc=L6 community=Community 1]
NODE Label [src=src/frontend/src/components/ui/label.tsx loc=L5 community=Community 1]
NODE contact_service.py [src=src/backend/services/contact_service.py loc=L1 community=Community 85]
NODE SWA ERP Constitution [src=.specify/memory/constitution.md loc=None community=Community 72]
NODE Contact [src=src/backend/models/contact.py loc=L11 community=Community 85]
NODE contact_repo.py [src=src/backend/db/repositories/contact_repo.py loc=L1 community=Community 85]
NODE useAuth() [src=src/frontend/src/hooks/useAuth.ts loc=L7 community=Community 15]
NODE Wave-48 Production Hardening [src=work/wave-48/01-production-hardening.md loc=None community=Community 28]
NODE SWA ERP Product v1.0.1 [src=deliverables/SUBMISSION.md loc=None community=Community 63]
NODE @hookform/resolvers [src=src/frontend/package.json loc=L20 community=Community 1]
NODE react-hook-form [src=src/frontend/package.json loc=L36 community=Community 1]
NODE zod [src=src/frontend/package.json loc=L39 community=Community 1]
NODE unassign_task_endpoint() [src=src/backend/api/boqs_new.py loc=L183 community=Community 65]
NODE delete_document_endpoint() [src=src/backend/api/documents.py loc=L135 community=Community 14]
NODE delete_folder_endpoint() [src=src/backend/api/documents.py loc=L340 community=Community 14]
NODE unassign_task_endpoint() [src=src/backend/api/tasks.py loc=L183 community=Community 39]
NODE delete_contact_service() [src=src/backend/services/contact_service.py loc=L108 community=Community 85]
NODE delete_contact() [src=src/backend/api/clients.py loc=L139 community=Community 46]
NODE delete_metric() [src=src/backend/api/sustainability_metrics.py loc=L92 community=Community 38]
NODE delete_agreement() [src=src/backend/api/agreements.py loc=L104 community=Community 13]
NODE delete_boq_endpoint() [src=src/backend/api/boqs.py loc=L158 community=Community 98]
NODE delete_client() [src=src/backend/api/clients.py loc=L93 community=Community 46]
NODE delete_document_reference() [src=src/backend/api/document_references.py loc=L153 community=Community 4]
NODE delete_inquiry() [src=src/backend/api/inquiries.py loc=L87 community=Community 23]
NODE delete_material_category() [src=src/backend/api/materials.py loc=L82 community=Community 26]
NODE delete_material_endpoint() [src=src/backend/api/materials.py loc=L175 community=Community 26]
NODE remove_cost() [src=src/backend/api/project_pnl.py loc=L59 community=Community 34]
NODE delete_project() [src=src/backend/api/projects.py loc=L102 community=Community 7]
NODE delete_quote_endpoint() [src=src/backend/api/quotes.py loc=L115 community=Community 10]
NODE delete_time_entry() [src=src/backend/api/time_tracking.py loc=L109 community=Community 12]
NODE delete_token() [src=src/backend/api/tokens.py loc=L103 community=Community 22]
... (truncated — 232 more nodes cut by ~1500-token budget. Narrow with context_filter=['call'] or use get_node for a specific symbol)
```

### `graphify query "JWT refresh rotation"`
```
Graph: graphify-out/graph.json (4959 nodes) | Traversal: BFS depth=2 | Start: ['jwt', 'Refresh Token Rotation Gap', 'Refresh Token Rotation'] | 66 nodes found
[!] TRUNCATED: showing 49 of 66 nodes (~1500-token budget). The answer may be among the 17 cut nodes — raise the token budget (CLI: --budget) or narrow the query (e.g. context_filter=['call'], or get_node for a specific symbol).
NODE jwt [src= loc= community=Community 84]
NODE Refresh Token Rotation Gap [src=work/wave-48/03-token-security-hygiene.md loc=None community=Community 80]
NODE Refresh Token Rotation [src=work/reports/dispatch-24h/AGENT-L6-B.md loc=None community=Community 80]
NODE security.py [src=src/backend/core/security.py loc=L1 community=Community 102]
NODE test_auth.py [src=tests/wave-1/test_auth.py loc=L1 community=Community 84]
NODE AGENT-L6-B: JWT Logout Token Version Refresh Rotation [src=work/reports/dispatch-24h/AGENT-L6-B.md loc=None community=Community 80]
NODE Wave-48 Token Security Hygiene [src=work/wave-48/03-token-security-hygiene.md loc=None community=Community 80]
NODE AGENT-L6-FIX: Refresh Token Race and Viewer Time Entry Gate [src=work/reports/dispatch-24h/AGENT-L6-FIX.md loc=None community=Community 80]
NODE Wave-48 Task 03: Token security hygiene [src=work/reports/wave-48/03-token-security-hygiene.report.md loc=None community=Community 165]
NODE Auth Service [src=work/reports/dispatch-24h/AGENT-L6-B.md loc=None community=Community 80]
NODE Refresh Token Repository [src=work/reports/dispatch-24h/AGENT-L6-FIX.md loc=None community=Community 80]
NODE Role [src=src/backend/core/roles.py loc=L4 community=Community 53]
NODE sqlalchemy [src= loc= community=Community 18]
NODE datetime [src= loc= community=Community 18]
NODE uuid [src= loc= community=Community 18]
NODE main.py [src=src/backend/main.py loc=L1 community=Community 19]
NODE typing [src= loc= community=Community 29]
NODE tests/conftest.py [src=tests/conftest.py loc=L1 community=Community 30]
NODE pytest [src= loc= community=Community 52]
NODE deps.py [src=src/backend/core/deps.py loc=L1 community=Community 19]
NODE roles.py [src=src/backend/core/roles.py loc=L1 community=Community 19]
NODE test_migrations.py [src=tests/test_migrations.py loc=L1 community=Community 18]
NODE get_by_id() [src=src/backend/db/repositories/user_repo.py loc=L13 community=Community 36]
NODE hash_password() [src=src/backend/core/security.py loc=L11 community=Community 30]
NODE auth_service.py [src=src/backend/services/auth_service.py loc=L1 community=Community 43]
NODE user_service.py [src=src/backend/services/user_service.py loc=L1 community=Community 36]
NODE test_rbac_gaps.py [src=tests/wave-22/test_rbac_gaps.py loc=L1 community=Community 6]
NODE bootstrap_real.py [src=scripts/bootstrap_real.py loc=L1 community=Community 18]
NODE create_access_token() [src=src/backend/core/security.py loc=L24 community=Community 102]
NODE config.py [src=src/backend/core/config.py loc=L1 community=Community 19]
NODE test_inquiry_conversion_atomicity.py [src=tests/wave-49/test_inquiry_conversion_atomicity.py loc=L1 community=Community 23]
NODE role_includes() [src=src/backend/core/roles.py loc=L21 community=Community 19]
NODE decode_token() [src=src/backend/core/security.py loc=L59 community=Community 84]
NODE 03-notifications-e2e.py [src=tests/wave-4/03-notifications-e2e.py loc=L1 community=Community 18]
NODE Level 6 Implementation Completion [src=work/reports/dispatch-24h/AGENT-L6-A.md loc=None community=Community 62]
NODE create_refresh_token() [src=src/backend/core/security.py loc=L47 community=Community 102]
NODE Viewer Role Read-Only Enforcement [src=work/reports/dispatch-24h/AGENT-L2-A.md loc=None community=Community 62]
NODE JWT Token Version Mechanism [src=work/reports/dispatch-24h/AGENT-L6-B.md loc=None community=Community 80]
NODE UUID [src= loc= community=Community 102]
NODE verify_token_version() [src=src/backend/core/security.py loc=L63 community=Community 102]
NODE verify_password() [src=src/backend/core/security.py loc=L15 community=Community 43]
NODE Main Application Entry [src=work/wave-36/01-observability.md loc=None community=Community 80]
NODE test_role_hierarchy() [src=tests/wave-1/test_auth.py loc=L134 community=Community 84]
NODE Content Security Policy [src=work/wave-48/03-token-security-hygiene.md loc=None community=Community 80]
NODE Content Security Policy Gap [src=work/wave-48/03-token-security-hygiene.md loc=None community=Community 80]
NODE Dependencies Module [src=work/reports/dispatch-24h/AGENT-L6-B.md loc=None community=Community 80]
NODE Migration 0036 Token Version Rename [src=work/reports/dispatch-24h/AGENT-L6-B.md loc=None community=Community 80]
NODE Security Module [src=work/reports/dispatch-24h/AGENT-L6-B.md loc=None community=Community 80]
NODE test_expired_token_rejected() [src=tests/wave-1/test_auth.py loc=L141 community=Community 84]
... (truncated — 17 more nodes cut by ~1500-token budget. Narrow with context_filter=['call'] or use get_node for a specific symbol)
```

### god_nodes / graph_stats / shortest_path attempts
```
graphify path InquiryCreate InvoicePersist → No node matching 'InvoicePersist' (symbol name differs; see query results for real callables)
nodes=4959 sample_keys=['id', 'label', '_callable', '_callable_class', '_origin', 'community', 'community_name', 'file_type', 'norm_label', 'source_file', 'source_location']
top_degree:
```


## Graph report excerpts (from graphify-out/GRAPH_REPORT.md)

God Nodes (most connected - your core abstractions)
1. `User` - 319 edges
2. `Role` - 165 edges
3. `react` - 90 edges
4. `Base` - 88 edges
5. `@tanstack/react-query` - 88 edges
6. `Project` - 87 edges
7. `create_entry()` - 86 edges
8. `api` - 85 edges
9. `Client` - 78 edges
10. `vitest` - 78 edges



Surprising Connections (you probably didn't know these)
- `Orchestrator Kernel Documentation` --semantically_similar_to--> `Orchestrator Kernel Documentation`  [INFERRED] [semantically similar]
  AGENTS.md → CLAUDE.md
- `Orchestrator Kernel Documentation` --semantically_similar_to--> `Orchestrator Kernel Documentation`  [INFERRED] [semantically similar]
  AGENTS.md → KIMI.md
- `SWA Consultancy ERP Brief for IT Team` --semantically_similar_to--> `Full Project and Deployment Brief for IT`  [INFERRED] [semantically similar]
  deliverables/SEND_IT.md → docs/IT_BRIEF.md
- `Auth and RBAC Architecture` --semantically_similar_to--> `RBAC Role Hierarchy`  [INFERRED] [semantically similar]
  plan/ARCHITECTURE.md → docs/flows/02_auth_rbac.md
- `test_delete_contact()` --uses--> `Contact`  [INFERRED]
  tests/wave-2/test_clients.py → src/backend/models/contact.py



Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Community 81` to `Community 128`, `Community 2`, `Community 4`, `Community 134`, `Community 7`, `Community 6`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 22`, `Community 23`, `Community 25`, `Community 26`, `Community 27`, `Community 156`, `Community 30`, `Community 32`, `Community 33`, `Community 34`, `Community 35`, `Community 36`, `Community 37`, `Community 38`, `Community 39`, `Community 43`, `Community 45`, `Community 46`, `Community 53`, `Community 65`, `Community 69`, `Community 95`, `Community 98`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `Refresh Token Rotation` connect `Community 80` to `Community 165`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `Wave-48 Task 03: Token security hygiene` connect `Community 165` to `Community 80`, `Community 19`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 241 inferred relationships involving `User` (e.g. with `create_agreement()` and `delete_agreement()`) actually correct?**
  _`User` has 241 INFERRED edges - model-reasoned connections that need verification._
- **Are the 124 inferred relationships involving `Role` (e.g. with `create_agreement()` 

