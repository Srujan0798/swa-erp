# Graph Report - swa-erp  (2026-09-22)

## Corpus Check
- Large corpus: 735 files · ~387,510 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 4959 nodes · 15104 edges · 238 communities (167 shown, 71 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1164 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 111
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 124
- Community 125
- Community 126
- Community 127
- Community 128
- Community 129
- Community 130
- Community 131
- Community 132
- Community 133
- Community 134
- Community 136
- Community 137
- Community 138
- Community 140
- Community 141
- Community 142
- Community 143
- Community 144
- Community 145
- Community 146
- Community 147
- Community 148
- Community 149
- Community 150
- Community 151
- Community 152
- Community 153
- Community 154
- Community 155
- Community 156
- Community 157
- Community 158
- Community 159
- Community 160
- Community 161
- Community 162
- Community 163
- Community 164
- Community 165
- Community 166
- Community 167
- Community 168
- Community 169
- Community 170
- Community 171
- Community 172
- Community 173
- Community 174
- Community 175
- Community 176
- Community 177
- Community 178
- Community 179
- Community 180
- Community 181
- Community 182
- Community 183
- Community 184
- Community 185
- Community 186
- Community 187
- Community 188
- Community 189
- Community 190
- Community 191
- Community 192
- Community 193
- Community 194
- Community 195
- Community 196
- Community 197
- Community 198
- Community 199
- Community 200
- Community 201
- Community 202
- Community 203
- Community 204
- Community 205
- Community 206
- Community 207
- Community 208
- Community 209
- Community 210
- Community 211
- Community 212
- Community 213
- Community 226
- Community 227
- Community 228
- Community 229
- Community 230
- Community 231
- Community 232
- Community 233
- Community 234
- Community 235
- Community 236
- Community 237

## God Nodes (most connected - your core abstractions)
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

## Surprising Connections (you probably didn't know these)
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

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI Workflow Jobs** — github_workflows_ci_backend_lint, github_workflows_ci_backend_test, github_workflows_ci_frontend_build, github_workflows_ci_validators [EXTRACTED 1.00]
- **Security Workflow Jobs** — github_workflows_security, github_workflows_perf_regression, github_workflows_evals [INFERRED 0.85]
- **SWA Business Chain Entities** — domain_inquiry, domain_client, domain_project, domain_service_agreement, domain_token, domain_document_reference, domain_time_tracking [EXTRACTED 1.00]
- **Core Business Chain Flow Components** — concept_core_business_chain, concept_reference_id_format, concept_yearly_id_reset, concept_client_names, concept_no_leads_module, concept_gst_invoicing [EXTRACTED 0.95]
- **Handover Documentation Package** — deliverables_handover_admin_guide, deliverables_handover_architecture_overview, deliverables_handover_training_one_pager, deliverables_handover_user_guide [EXTRACTED 0.95]
- **Architecture Decision Records** — docs_decisions_0001_tech_stack, docs_decisions_0002_core_id_chain_gap, docs_decisions_0003_soft_delete_exceptions, docs_decisions_0004_api_versioning_idempotency [EXTRACTED 0.95]
- **RBAC Role Hierarchy** — docs_flows_02_auth_rbac_role_admin, docs_flows_02_auth_rbac_role_pm, docs_flows_02_auth_rbac_role_designer, docs_flows_02_auth_rbac_role_auditor, docs_flows_02_auth_rbac_role_viewer [EXTRACTED 1.00]
- **Multi-Agent Audit Tools** — docs_historical_agent_dispatch_guide_review_security, docs_historical_agent_dispatch_guide_review, docs_historical_agent_dispatch_guide_review_bugbot, docs_historical_agent_dispatch_guide_graphify, docs_historical_agent_dispatch_guide_create_hook, docs_historical_agent_dispatch_guide_create_rule, docs_historical_agent_dispatch_guide_loop [EXTRACTED 1.00]
- **Advanced Audit Phases** — prompts_advanced_audit_v2_phase_0_metrics, prompts_advanced_audit_v2_phase_1_tools, prompts_advanced_audit_v2_phase_2_deep_dives, prompts_advanced_audit_v2_phase_3_triage, prompts_advanced_audit_v2_phase_4_fix_verify [EXTRACTED 1.00]
- **FINAL-CLOSE documentation pack** — work_final_close_readme_md, work_final_close_anti_fabrication_md, work_final_close_definition_of_done_md, work_final_close_human_playbook_md, work_final_close_protocols_md, work_final_close_task_categories_md, work_final_close_ultimate_close_guide_md, work_final_close_prompts_continue_sessions_md, work_final_close_prompts_paste_to_claude_md [EXTRACTED 1.00]
- **Level 1 dispatch reports** — work_reports_dispatch_24h_agent_1_md, work_reports_dispatch_24h_agent_l1_a_md, work_reports_dispatch_24h_agent_l1_b_md, work_reports_dispatch_24h_agent_l1_c_md, work_reports_dispatch_24h_agent_l1_d_md, work_reports_dispatch_24h_agent_l1_e_md, work_reports_dispatch_24h_agent_l1_f_md [EXTRACTED 1.00]
- **Close phases sequence** — work_final_close_protocols_md, work_final_close_ultimate_close_guide_md, work_final_close_definition_of_done_md, work_reports_completion_handoff_verdict_md, work_reports_final_close_report_md [INFERRED 0.95]
- **24-Hour Dispatch Level Completion Sequence** — level_2_completion, level_3_completion, level_4_completion, level_5_completion, level_6_completion, level_10_completion [EXTRACTED 1.00]
- **L6 Security Audit and Fixes** — work_reports_dispatch_24h_agent_l6_a, work_reports_dispatch_24h_agent_l6_b, work_reports_dispatch_24h_agent_l6_c, work_reports_dispatch_24h_agent_l6_d, work_reports_dispatch_24h_agent_l6_fix [EXTRACTED 1.00]
- **Worktree Merge Conflict Resolution** — wt_l2_7, wt_l2_9, wt_l2_10, wt_l2_11, wt_l3_b, wt_l3_d, wt_l3_e [EXTRACTED 1.00]
- **Wave-48 Hardening Tasks** — work_reports_wave_48_02_pagination_idempotency, work_reports_wave_48_03_token_security_hygiene, work_reports_wave_48_04_service_layer_logging, work_reports_wave_48_05_frontend_loading_states_and_bundle_splitting [EXTRACTED 0.95]
- **Dispatch-24h Agent Sequence** — work_reports_dispatch_24h_agent_l7_a, work_reports_dispatch_24h_agent_l7_b, work_reports_dispatch_24h_agent_l7_c, work_reports_dispatch_24h_agent_l7_d, work_reports_dispatch_24h_agent_l8_a, work_reports_dispatch_24h_agent_l8_b, work_reports_dispatch_24h_agent_l8_c, work_reports_dispatch_24h_agent_l8_d, work_reports_dispatch_24h_agent_l9_a, work_reports_dispatch_24h_agent_l9_b, work_reports_dispatch_24h_agent_l9_c [EXTRACTED 0.95]
- **Service Layer Logging Modules** — src_backend_services_import_service, src_backend_services_invoice_service, src_backend_services_quote_service, src_backend_services_inquiry_service [EXTRACTED 0.95]
- **Wave-48 Production Hardening Tasks** — work_wave_48_01_production_hardening, work_wave_48_02_pagination_idempotency, work_wave_48_03_token_security_hygiene, work_wave_48_04_service_layer_logging, work_wave_48_05_frontend_loading_states_and_bundle_splitting [EXTRACTED 1.00]
- **Security Hardening Concerns** — rate_limiting_gap, audit_trail_gap, csp_gap, refresh_token_rotation_gap, job_idor, unauthenticated_metrics [INFERRED 0.85]
- **Wave Dependency Chain 32-38** — work_wave_32_01_real_ci_quality_gates, work_wave_33_01_backend_coverage, work_wave_34_01_frontend_test_suite, work_wave_35_01_performance_load_validation, work_wave_36_01_observability, work_wave_37_01_independent_review, work_wave_38_01_submission_package [EXTRACTED 1.00]

## Communities (238 total, 71 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (131): @tanstack/react-query, @testing-library/react, @testing-library/user-event, vitest, item, uploadBoqMock, useBoqItemsMock, canWriteMock (+123 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (111): class-variance-authority, @hookform/resolvers, react, react-hook-form, zod, AgreementForm(), AgreementFormData, AgreementFormProps (+103 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (115): add_contact(), create_vendor(), delete_contact(), delete_vendor(), get_vendor(), list_contacts(), list_vendors(), get (+107 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (113): PnlDashboardProps, TimeEntryFormProps, TimeEntryListProps, TimesheetSummaryProps, TimesheetViewProps, ApiError, formatApiError(), request() (+105 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (68): concurrent_futures, create_document_reference(), delete_document_reference(), get_document_reference(), get_document_reference_counters(), list_document_references(), get, patch (+60 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (78): NewVendorPage, AgreementsTab(), AgreementsTabProps, agreement, createMutationMock, deleteMutationMock, toastMock, useAgreementsMock (+70 more)

### Community 6 - "Community 6"
Cohesion: 0.03
Nodes (63): create_test_user(), login_user(), fixture, Session, Tests for RBAC and auth gap fixes - Wave 22, Test that Admin can add cost entry, Test that PM can add cost entry (aligned with DELETE — ADMIN+PM), VIEWER must not delete project costs (+55 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (87): demo_package_json(), financial_report_pdf(), project_slides_pdf(), project_summary_pdf(), date, get, Response, Session (+79 more)

### Community 8 - "Community 8"
Cohesion: 0.03
Nodes (4): alembic, collections_abc, sqlalchemy_dialects, # NOTE: document_folders.deleted_at already exists (migration 0010);

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (90): contextvars, openpyxl, _agreement_by_ref(), _client_by_code(), _client_by_name(), _doc_by_ref(), _ensure_client(), _ensure_import_user() (+82 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (87): approve_quote_endpoint(), clone_quote_endpoint(), create_quote_endpoint(), delete_quote_endpoint(), download_quote_pdf_endpoint(), get_quote_endpoint(), list_quotes_endpoint(), Any (+79 more)

### Community 11 - "Community 11"
Cohesion: 0.05
Nodes (62): _assert(), grader_001_inquiry_conversion(), grader_002_id_chain(), grader_003_rbac(), grader_004_time_aggregation(), grader_005_gst(), Session, Verification: - all reference_ids match /^SWA-\\d{4}-[A-Z]+-\\d{3}$/ -… (+54 more)

### Community 12 - "Community 12"
Cohesion: 0.08
Nodes (80): approve_timesheet(), create_time_entry(), delete_time_entry(), generate_timesheet(), get_time_entry(), get_timesheet(), _is_admin(), list_time_entries() (+72 more)

### Community 13 - "Community 13"
Cohesion: 0.07
Nodes (60): create_agreement(), delete_agreement(), get_agreement(), list_agreements(), get, patch, post, Session (+52 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (74): _check_project_exists(), create_folder_endpoint(), delete_document_endpoint(), delete_folder_endpoint(), download_document_endpoint(), get_document_endpoint(), get_version_history_endpoint(), list_documents_endpoint() (+66 more)

### Community 15 - "Community 15"
Cohesion: 0.03
Nodes (60): react-dom, AgreementsPage, App(), ClientDetailPage, ClientsPage, CompliancePage, DashboardPage, DocumentReferencesPage (+52 more)

### Community 16 - "Community 16"
Cohesion: 0.05
Nodes (69): fastapi_responses, given, hashlib, hypothesis, eslint:recommended, plugin:react-hooks/recommended, plugin:@typescript-eslint/recommended, create_invoice_endpoint() (+61 more)

### Community 17 - "Community 17"
Cohesion: 0.04
Nodes (59): argparse, _load_task_ids(), main(), evals/run_evals.py — the eval runner. Runs the wave-43 eval tests…, Return ordered task IDs from the YAML specs., Run one eval task as a pytest test. Returns result dict., _run_pytest(), write_outcomes() (+51 more)

### Community 18 - "Community 18"
Cohesion: 0.14
Nodes (33): datetime, decimal, DeclarativeBase, evals/graders/code_based.py — deterministic graders for wave-43 evals. Each…, _login(), evals/wave_43_evals.py — eval tasks as pytest tests (runs via the existing…, Login synchronously-wrapped async — returns token string., re (+25 more)

### Community 19 - "Community 19"
Cohesion: 0.05
Nodes (59): celery, celery_result, contextlib, Depends, FastAPI, fastapi_middleware_cors, fastapi_security, middleware (+51 more)

### Community 20 - "Community 20"
Cohesion: 0.08
Nodes (48): client_summary(), executive(), project_health(), date, get, Session, revenue(), utilization() (+40 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (42): lucide-react, BOQItemTable(), BOQItemTableProps, BOQVersionList(), BOQVersionListProps, InvoiceDetailProps, STATUS_COLORS, InvoiceListProps (+34 more)

### Community 22 - "Community 22"
Cohesion: 0.10
Nodes (46): create_token(), delete_token(), get_token(), list_tokens(), get, patch, post, Session (+38 more)

### Community 23 - "Community 23"
Cohesion: 0.09
Nodes (49): convert(), create_inquiry(), delete_inquiry(), get_inquiry(), list_inquiries(), Any, get, patch (+41 more)

### Community 24 - "Community 24"
Cohesion: 0.06
Nodes (40): react-router-dom, RecentClients(), RecentProjects(), statusColors, StatsCards(), client, emptyList(), mockAllCountsZero() (+32 more)

### Community 25 - "Community 25"
Cohesion: 0.11
Nodes (61): bulk_create_items(), compliance_summary(), create_item(), initialize(), list_checklist(), list_project_items(), list_standards(), get (+53 more)

### Community 26 - "Community 26"
Cohesion: 0.13
Nodes (56): sqlalchemy_exc, create_material_category(), create_material_endpoint(), delete_material_category(), delete_material_endpoint(), get_material_endpoint(), list_material_categories(), list_materials() (+48 more)

### Community 27 - "Community 27"
Cohesion: 0.08
Nodes (52): validate_transition(), model_validator, add_comment_service(), assign_task_service(), bulk_update_status_service(), delete_task_service(), get_project_task_stats_service(), get_task_counts_service() (+44 more)

### Community 28 - "Community 28"
Cohesion: 0.05
Nodes (51): Accessibility, Architecture Diagram, Audit Trail, Audit Trail Gap, Auth Assertion Bug (403 vs 401), BACKLOG, Core ID Chain Workflow, Deferred Security Risks (+43 more)

### Community 29 - "Community 29"
Cohesion: 0.05
Nodes (15): Reference IDs must be well-formed + monotonically increasing + FK-wired., test_002_agreement_token_docref_chain(), create(), get_by_id(), get_by_reference_id(), list_inquiries(), Any, Session (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.07
Nodes (45): fcntl, redis, hash_password(), TestClient, _acquire_schema_lock(), admin_user(), _alembic_head(), auditor_user() (+37 more)

### Community 31 - "Community 31"
Cohesion: 0.09
Nodes (32): ComplianceChecklist(), ComplianceChecklistProps, STATUS_FILTERS, ComplianceDashboard(), ComplianceDashboardProps, ComplianceItemStatus(), ComplianceItemStatusProps, STATUS_CONFIG (+24 more)

### Community 32 - "Community 32"
Cohesion: 0.08
Nodes (20): auth_headers(), client(), _create_project(), db_session(), _file_upload(), _override_db(), override_get_db(), pm_headers() (+12 more)

### Community 33 - "Community 33"
Cohesion: 0.10
Nodes (27): Enum, NotificationRepository, Notification, Task, NotificationRead, NotificationType, BaseModel, list_notifications_service() (+19 more)

### Community 34 - "Community 34"
Cohesion: 0.15
Nodes (39): add_cost(), cost_breakdown(), list_costs(), pnl_summary(), get, post, Session, UUID (+31 more)

### Community 35 - "Community 35"
Cohesion: 0.15
Nodes (31): builtins, assign_task(), bulk_update_status(), create_comment(), create_task(), get_by_id(), get_task_counts_by_project(), get_task_counts_by_user() (+23 more)

### Community 36 - "Community 36"
Cohesion: 0.14
Nodes (37): create_user(), delete_user(), get_user(), list_assignees(), list_users(), get, patch, post (+29 more)

### Community 37 - "Community 37"
Cohesion: 0.17
Nodes (33): Invoice with 3 line items: GST 18% exact, money stays Decimal., test_005_invoice_gst_correctness(), _execute(), _execute(), create_invoice(), generate_invoice_number(), get_invoice_by_id(), get_invoice_with_items() (+25 more)

### Community 38 - "Community 38"
Cohesion: 0.18
Nodes (31): create_metric(), delete_metric(), get_metric(), list_metrics(), get, patch, post, Session (+23 more)

### Community 39 - "Community 39"
Cohesion: 0.18
Nodes (31): field_validator, add_comment_endpoint(), assign_task_endpoint(), bulk_update_status_endpoint(), create_task_endpoint(), get_task_endpoint(), list_tasks_endpoint(), my_tasks_endpoint() (+23 more)

### Community 40 - "Community 40"
Cohesion: 0.09
Nodes (17): minio_error, requires_minio, src_backend_core, get_storage(), MinIOStorage, Return the configured storage backend, built once at first use., S3-compatible object storage backend (MinIO) via the ``minio`` client.…, local_backend() (+9 more)

### Community 41 - "Community 41"
Cohesion: 0.13
Nodes (24): pypdf, _fmt_date(), _fmt_decimal(), generate_quote_pdf(), datetime, Decimal, FPDF, QuotePDF (+16 more)

### Community 42 - "Community 42"
Cohesion: 0.06
Nodes (31): autoprefixer, clsx, @dnd-kit/utilities, eslint, eslint-plugin-react-hooks, eslint-plugin-react-refresh, jsdom, postcss (+23 more)

### Community 43 - "Community 43"
Cohesion: 0.17
Nodes (27): auth_login(), auth_logout(), auth_me(), auth_refresh(), get_client_info(), get, post, Request (+19 more)

### Community 44 - "Community 44"
Cohesion: 0.11
Nodes (25): QuoteActions(), QuoteActionsProps, STATUS_CONFIG, QuoteList(), approveQuoteMock, cloneQuoteMock, deleteQuoteMock, quote (+17 more)

### Community 45 - "Community 45"
Cohesion: 0.15
Nodes (25): Billable time entries surface in timesheet + generate-from-time invoice., test_004_time_log_to_dashboard(), TimeEntry, UUID, Tests for Invoicing (Task 03)., Helper: create a client and project, return project_id., Return this invoice's status-change audit rows, newest first., _seed_time_entries() (+17 more)

### Community 46 - "Community 46"
Cohesion: 0.24
Nodes (22): add_contact(), create_client(), delete_client(), delete_contact(), get_client(), list_clients(), get, patch (+14 more)

### Community 47 - "Community 47"
Cohesion: 0.12
Nodes (10): LocalStorage, Path, Filesystem backend wrapping the historical ``uploads/<key>`` layout. ``save``…, Map a key or legacy stored path onto a location under ``root``. Relative keys…, TestLocalStorage, Path, Wave-37 — LocalStorage path traversal guards., test_rejects_absolute_key_on_save() (+2 more)

### Community 48 - "Community 48"
Cohesion: 0.14
Nodes (20): VendorDetailPage, VendorContactForm(), VendorDetail(), mockCategory, mockContact, mockMaterial, mockVendor, useAddVendorContact() (+12 more)

### Community 49 - "Community 49"
Cohesion: 0.12
Nodes (20): approveTimesheetMock, createMutationMock, entries, projects, rejectTimesheetMock, submitTimesheetMock, timesheet, updateMutationMock (+12 more)

### Community 50 - "Community 50"
Cohesion: 0.14
Nodes (19): mockTask, mockComment, mockTask, TaskFilters, useAddComment(), useAssignTask(), useBulkUpdateStatus(), useCreateTask() (+11 more)

### Community 51 - "Community 51"
Cohesion: 0.09
Nodes (24): Backend Coverage Gaps, Fake CI Gates (|| true pattern), CI Quality Gates, Code Review Ultra Tool, Coverage Gates, GitHub CI Workflow, GitHub Security Workflow, GitHub Test Workflow (+16 more)

### Community 52 - "Community 52"
Cohesion: 0.10
Nodes (16): client(), db_session(), fixture, Shared fixtures for the wave-43 evals harness. Reuses the project's real test…, Drop + recreate public schema and all tables (fresh start for the session)., Reset every table + reference_counters (restart identity) to fresh state., Fresh DB with all rows wiped; yields a session bound to the eval engine., AsyncClient bound to the live app with get_db overridden to the eval session. (+8 more)

### Community 53 - "Community 53"
Cohesion: 0.26
Nodes (23): award_rfq_endpoint(), cancel_rfq_endpoint(), close_rfq_endpoint(), compare_project_rfqs_endpoint(), compare_rfqs_endpoint(), create_rfq_endpoint(), get_rfq_endpoint(), list_rfqs_endpoint() (+15 more)

### Community 54 - "Community 54"
Cohesion: 0.08
Nodes (24): dependencies, class-variance-authority, clsx, @dnd-kit/core, @dnd-kit/sortable, @dnd-kit/utilities, @hookform/resolvers, lucide-react (+16 more)

### Community 55 - "Community 55"
Cohesion: 0.14
Nodes (23): Tests for Time Tracking (Task 01) and Timesheet Workflow (Task 02)., Helper: create a client and project, return project_id., Viewer must be denied 403 on POST /api/time-entries., Viewer must be denied 403 on PATCH /api/time-entries/{id}. Entry is created via…, Viewer must be denied 403 on DELETE /api/time-entries/{id}. Entry created via…, Time Logging Sheet high-frequency columns round-trip on create., _setup_project(), test_approve_timesheet() (+15 more)

### Community 56 - "Community 56"
Cohesion: 0.11
Nodes (23): IT Decision Log, Open Items from Client Meetings, Docker Compose Deployment, Evals harness (code-based graders, LLM judge), Backend Test Job, E2E Workflow, Evals Workflow, Performance Regression Workflow (+15 more)

### Community 57 - "Community 57"
Cohesion: 0.11
Nodes (21): importlib, _rate_limit_middleware_active(), Wave-18 production security hardening tests. Covers four areas: 1. SECRET_KEY…, main.py's CORS middleware must use settings.CORS_ORIGINS, not a hardcoded list.…, In dev mode (default), the insecure default is allowed., 0.7% cases: subtotal=333.33, gst=18% -> 60.00 (rounded to .01)., In prod (APP_ENV != dev), the default secret must reject at construction time.…, CORS_ORIGINS must come from the env, not be hardcoded. (+13 more)

### Community 58 - "Community 58"
Cohesion: 0.09
Nodes (23): devDependencies, autoprefixer, eslint, eslint-plugin-react-hooks, eslint-plugin-react-refresh, jsdom, @playwright/test, postcss (+15 more)

### Community 59 - "Community 59"
Cohesion: 0.17
Nodes (22): asyncio, test_create_category_with_parent(), test_create_material(), test_create_material_category(), test_create_material_duplicate_code(), test_create_material_with_category(), test_delete_category_with_children_fails(), test_delete_material() (+14 more)

### Community 60 - "Community 60"
Cohesion: 0.13
Nodes (16): @dnd-kit/core, @dnd-kit/sortable, ColumnDef, COLUMNS, KanbanBoard(), KanbanBoardProps, TaskColumn(), TaskColumnProps (+8 more)

### Community 61 - "Community 61"
Cohesion: 0.09
Nodes (11): PMUser, Project Manager - Full access user. Typical PM workflow: 1. Check executive…, Primary dashboard - most frequent PM action., Project health report., List projects with pagination., View a specific project detail., View a specific client detail., List timesheets for approval. (+3 more)

### Community 62 - "Community 62"
Cohesion: 0.13
Nodes (21): Admin Bypass of Project Membership IDOR, Celery Export UI Hook, Configuration Module, Documents API, Exports API, Jobs API, Level 10 Implementation Completion, Level 6 Implementation Completion (+13 more)

### Community 63 - "Community 63"
Cohesion: 0.12
Nodes (21): API Versioning Header Strategy, Client Names APEX INNER INSUDESIGN, Compliance Standards NBC ECBC IGBC IS, Core Business Chain Flow, Docker Compose Stack Components, Excel to ERP Migration Tool, GST Invoicing Implementation, Idempotency Keys Implementation (+13 more)

### Community 64 - "Community 64"
Cohesion: 0.20
Nodes (19): get_grader(), _as(), parametrize, Session, Wave-43 code-based evals — runnable pytest harness. Each task is executed…, Task 001 needs two existing clients sharing a name to trigger the 300 branch., Run one task for DEFAULT_TRIALS independent trials; record + assert. A real…, Write measured pass@k / pass^k to the outcomes JSON (per task). (+11 more)

### Community 65 - "Community 65"
Cohesion: 0.25
Nodes (20): add_comment_endpoint(), assign_task_endpoint(), bulk_update_status_endpoint(), create_task_endpoint(), get_task_endpoint(), list_tasks_endpoint(), my_tasks_endpoint(), get (+12 more)

### Community 66 - "Community 66"
Cohesion: 0.29
Nodes (19): BOQCreate, BOQItemCreate, BOQItemListResponse, BOQItemRead, BOQListRead, BOQListResponse, BOQRead, BaseModel (+11 more)

### Community 67 - "Community 67"
Cohesion: 0.15
Nodes (15): DocumentReferenceForm(), DocumentReferenceList(), DocumentReferenceListProps, createMutationMock, deleteMutationMock, docRef, toastMock, useCurrentUserMock (+7 more)

### Community 68 - "Community 68"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+12 more)

### Community 69 - "Community 69"
Cohesion: 0.16
Nodes (19): _add_committed_task(), _add_task(), authed_committed_client(), eager_celery(), asyncio, fixture, Wave-31 task 02: Celery background PDF jobs. Tests run Celery in eager mode…, Authenticated client for the committed_project's PM user. Uses a dedicated… (+11 more)

### Community 70 - "Community 70"
Cohesion: 0.14
Nodes (20): Admin Sidebar, Orchestrator Kernel Documentation, Orchestrator Kernel Documentation, Delivery Sidebar, Client Entity, Document Reference Entity, Inquiry Entity, Project Entity (+12 more)

### Community 71 - "Community 71"
Cohesion: 0.12
Nodes (15): io, Protocol, SEC-01: LocalStorage path traversal vulnerability, SEC-02: /metrics endpoint unauthenticated access, SEC-07: Job IDOR (export job ownership), SF-1: Hardcoded hourly rate in invoice generation, SF-2: Hardcoded rate in PnL/export, Persist content at ``key`` and return the stored path/URL. (+7 more)

### Community 72 - "Community 72"
Cohesion: 0.11
Nodes (19): ADR for Major Decisions, Archive Instead of Delete, Audit Log Principle, Schema-First BOQ Ingestion, Versioned Compliance Standards, Dependabot Configuration, Short-Lived JWT Tokens, Money as Decimal(18,2) (+11 more)

### Community 73 - "Community 73"
Cohesion: 0.20
Nodes (19): Close protocols P01-P20 (executable), FINAL-CLOSE pack (project close-out), Verification before completion (no DONE without evidence), Wave-37 independent adversarial review, Wave-38 professional submission package, ANTI-FABRICATION.md (anti-fabrication protocol), Anti-fabrication protocol (no fake reports), Definition of Done criteria (A-E) (+11 more)

### Community 74 - "Community 74"
Cohesion: 0.11
Nodes (19): JWT Authentication, Rate Limiting, RBAC Role Hierarchy, Admin Role, Auditor Role, Designer Role, PM Role, Viewer Role (+11 more)

### Community 75 - "Community 75"
Cohesion: 0.16
Nodes (11): AuthRateLimitMiddleware, ExpensiveEndpointRateLimitMiddleware, IPRateLimiter, BaseHTTPMiddleware, Request, Response, _rate_limit_disabled(), Bypass flag for the test suite (env var) and explicit dev toggles. (+3 more)

### Community 76 - "Community 76"
Cohesion: 0.17
Nodes (17): Wave 5 — RFQ Workflow end-to-end tests., Create client, project, vendor, and material using admin client (ADMIN…, Full lifecycle: draft -> sent -> responded -> awarded -> closed., Only PM and above can award., _setup_project_and_vendor(), test_cannot_close_draft(), test_compare_vendors(), test_create_rfq() (+9 more)

### Community 77 - "Community 77"
Cohesion: 0.17
Nodes (18): Backend Test Coverage, CHANGELOG.md: Project changelog, 100+ Concurrent Users Claim, Definition of Done criteria A-E, Frontend Test Coverage, Load Testing with Locust, Locust Load Testing Tool, EXECUTION.md: Execution plan tracking (+10 more)

### Community 78 - "Community 78"
Cohesion: 0.21
Nodes (7): _create_project(), _file_upload(), Session, TestReuploadCreatesVersion, TestSearchDocuments, TestUpdateDocumentMetadata, _upload_doc()

### Community 79 - "Community 79"
Cohesion: 0.19
Nodes (8): AsyncSession, sqlalchemy_ext_asyncio, UUID, Transitive closure: all tasks that task_id depends on (direct + indirect)., Transitive closure: all tasks that depend on task_id (direct + indirect)., Check if there's a path from from_task to to_task (cycle detection)., TaskDependencyRepository, TaskDependency

### Community 80 - "Community 80"
Cohesion: 0.18
Nodes (17): Auth Service, Content Security Policy, Content Security Policy Gap, Dependencies Module, JWT Token Version Mechanism, Migration 0036 Token Version Rename, Refresh Token Repository, Refresh Token Rotation (+9 more)

### Community 81 - "Community 81"
Cohesion: 0.37
Nodes (16): _require_pm_or_admin(), User, AsyncClient, asyncio, test_assign_audit_log(), test_assign_inactive_user(), test_assign_invalid_user(), test_assign_task() (+8 more)

### Community 82 - "Community 82"
Cohesion: 0.31
Nodes (15): create(), get_by_id(), list_clients(), date, Session, UUID, soft_delete(), update() (+7 more)

### Community 83 - "Community 83"
Cohesion: 0.17
Nodes (13): InvoiceDetail(), InvoiceList(), deleteInvoiceMock, invoice, updateStatusMock, mockInvoice, useCreateInvoice(), useDeleteInvoice() (+5 more)

### Community 84 - "Community 84"
Cohesion: 0.14
Nodes (6): jwt, decode_token(), Any, test_expired_token_rejected(), test_logout_invalidates_access_token(), test_role_hierarchy()

### Community 85 - "Community 85"
Cohesion: 0.41
Nodes (14): create(), delete(), get_by_id(), list_by_client(), Session, UUID, update(), Contact (+6 more)

### Community 86 - "Community 86"
Cohesion: 0.19
Nodes (7): DesignerUser, task, Designer - Project execution focused. Typical Designer workflow: 1. View…, List tasks for a project., Log time entry (periodic write)., Generate weekly timesheet., View project documents.

### Community 87 - "Community 87"
Cohesion: 0.23
Nodes (15): AsyncClient, test_admin_can_create_user(), test_admin_can_list_users(), test_admin_cannot_delete_self(), test_audit_log_on_create(), test_create_user_duplicate_email(), test_create_user_short_password(), test_pagination() (+7 more)

### Community 88 - "Community 88"
Cohesion: 0.12
Nodes (9): Tests for Prometheus /metrics endpoint (auth required)., Anonymous scrape must not succeed on the app port., Verify /metrics returns 200 when authenticated., Verify /metrics returns Prometheus text format., Verify http_requests_total metric is present., Verify http_request_duration_seconds metric is present., Verify http_requests_in_flight metric is present., Verify counters increment when requests are made. (+1 more)

### Community 89 - "Community 89"
Cohesion: 0.18
Nodes (15): eager_celery(), enqueued_job_id(), pm_b_client(), asyncio, fixture, Wave-50 task 01 (SEC-07): export-job ownership. User A (PM) enqueues an async…, Jobs with no ownership row keep the legacy pending/404 handling., Second PM's client sharing the same overridden test DB session. (+7 more)

### Community 90 - "Community 90"
Cohesion: 0.18
Nodes (15): Auth test fixes (401 vs 403 HTTPBearer behavior), SWA Consultancy ERP Submission Package, Technical Report - SWA Consultancy ERP, SWA ERP Architecture Documentation, SWA ERP Conventions, ADR-0001 Tech Stack Selection, ADR-0002 Core ID Chain Gap, Decision Soft Delete Exceptions (+7 more)

### Community 91 - "Community 91"
Cohesion: 0.13
Nodes (14): collections, dataclasses, auth_rate_limiter(), _Bucket, _env_limit(), install_auth_rate_limiter(), install_expensive_rate_limiters(), _is_export_request() (+6 more)

### Community 92 - "Community 92"
Cohesion: 0.18
Nodes (14): TAVILY_API_KEY, npx, context7, filesystem, git, postgres, sequential-thinking, tavily (+6 more)

### Community 93 - "Community 93"
Cohesion: 0.23
Nodes (12): mockDocument, mockFolder, useCreateFolder(), useDeleteDocument(), useDeleteFolder(), useDocument(), useDocuments(), useFolders() (+4 more)

### Community 94 - "Community 94"
Cohesion: 0.13
Nodes (15): _dev_column_exists(), _dev_query(), _get_dev_engine(), parametrize, Each column added by migrations 0031/0032/0033 must be present., All core tables exist in the dev DB., Get or create the dev DB engine (singleton)., Run a query against the dev DB and return result rows. (+7 more)

### Community 95 - "Community 95"
Cohesion: 0.17
Nodes (12): auth_headers(), client(), db_session(), _override_db(), override_get_db(), fixture, UUID, Tests for Wave 6 Task 02 — Document Management (CRUD, versioning, move, rename,… (+4 more)

### Community 96 - "Community 96"
Cohesion: 0.14
Nodes (14): Adaptoid OS Validators, Block Secrets Hook, CI quality gates (ruff, black, mypy, pytest), CI Workflow, Backend Lint Job, Frontend Build Job, Validators Job, Security Workflow (+6 more)

### Community 97 - "Community 97"
Cohesion: 0.20
Nodes (14): DBR KDR Shared Counter Mechanism, Document Reference Service, DocumentReferenceForm Component, Migration 0037 Nullable Project, Nullable Project for Time Entry and Document Reference, Sustainability Recorded After Project Completes, SustainabilityManager Component, Migration Tests (+6 more)

### Community 98 - "Community 98"
Cohesion: 0.34
Nodes (13): delete_boq_endpoint(), download_boq_endpoint(), get_boq_endpoint(), get_boq_items_endpoint(), list_boqs_endpoint(), get, post, Response (+5 more)

### Community 99 - "Community 99"
Cohesion: 0.18
Nodes (9): Scrub PII and secrets from Sentry events before sending. This is critical as…, scrub_pii(), Tests for Sentry error tracking integration., scrub_pii should redact Authorization header., scrub_pii should redact Cookie header., scrub_pii should redact password fields in exception frames., scrub_pii should redact Indian tax IDs., App should not crash when triggering an error without SENTRY_DSN. (+1 more)

### Community 100 - "Community 100"
Cohesion: 0.43
Nodes (13): count_items(), create_boq(), get_by_id(), get_next_version_number(), list_by_project(), list_items_paginated(), list_versions_with_counts(), Session (+5 more)

### Community 101 - "Community 101"
Cohesion: 0.25
Nodes (13): Tests for Project P&L (Task 04)., Helper: create a client and project, return project_id., _setup_project(), test_add_manual_cost(), test_cost_breakdown_by_category(), test_delete_cost(), test_margin_calculation(), test_pnl_empty_project() (+5 more)

### Community 102 - "Community 102"
Cohesion: 0.24
Nodes (8): bcrypt, create_access_token(), create_refresh_token(), UUID, Return True when the token's embedded version matches the DB current version., verify_token_version(), asyncio, TestAgreementApi

### Community 103 - "Community 103"
Cohesion: 0.15
Nodes (12): Instrumentator, prometheus_client, prometheus_fastapi_instrumentator, Prometheus metrics for SWA ERP. Exposes /metrics endpoint with: - HTTP request…, Update database connection pool metrics from SQLAlchemy pool., Record a Celery task completion., Record an HTTP 5xx response., Configure and install Prometheus metrics instrumentation. Two-phase setup: -… (+4 more)

### Community 104 - "Community 104"
Cohesion: 0.15
Nodes (12): logging, Observability Stack, sentry_sdk, sentry_sdk_integrations_fastapi, sentry_sdk_integrations_logging, sentry_sdk_integrations_sqlalchemy, add_breadcrumb(), capture_message() (+4 more)

### Community 105 - "Community 105"
Cohesion: 0.15
Nodes (5): Viewer - Read-only access. Typical Viewer workflow: 1. Check dashboards 2.…, Check executive dashboard., Check utilization report., Check revenue report., ViewerUser

### Community 107 - "Community 107"
Cohesion: 0.31
Nodes (12): _add_boq_with_items(), _add_task(), asyncio, fixture, test_client_id(), test_demo_package_json(), test_financial_report_pdf(), test_nonexistent_project_404() (+4 more)

### Community 108 - "Community 108"
Cohesion: 0.30
Nodes (12): Bootstrap Real Importer Script, Bootstrap Real Script, Core Sheets Import Inquiries Clients Agreements Projects, Excel Sheets Inventory Documentation, Import Real Sheets Script, Import Service, Level 5 Implementation Completion, AGENT-L5-A: Core Sheet Import Dry Run (+4 more)

### Community 109 - "Community 109"
Cohesion: 0.20
Nodes (7): HttpUser, AuthenticatedUser, Base class with authentication handling., Login and fetch reference data on start., Authenticate and store tokens., Refresh the access token., Fetch project and client IDs for use in subsequent requests.

### Community 110 - "Community 110"
Cohesion: 0.30
Nodes (10): can_transition(), ProjectStatus, StrEnum, get_project_stats(), Any, Session, UUID, Dashboard aggregates over active, non-deleted projects. Lives here (not in the… (+2 more)

### Community 111 - "Community 111"
Cohesion: 0.39
Nodes (11): _boq_item(), _make_boq_json(), asyncio, fixture, test_client_id(), test_list_versions(), test_project_id(), test_soft_delete_version() (+3 more)

### Community 112 - "Community 112"
Cohesion: 0.25
Nodes (11): Agreement Service, Audit Logging System, Inquiry to Project Convert Flow, Inquiry Service, Invoice Service, Wave 48 Production Hardening Tests, Wave 7 Invoicing Tests, Wave 9 Agreements Tests (+3 more)

### Community 113 - "Community 113"
Cohesion: 0.25
Nodes (11): AgreementForm Component, AgreementsTab Component, AgreementsTab Test, Frontend Forms Test, TokensPage Test, Wave 9 Token Tests, Token Project Ownership Validation, Token Service (+3 more)

### Community 114 - "Community 114"
Cohesion: 0.22
Nodes (9): authMock, mockUser, mockUsersResponse, navigateMock, useCreateUser(), useDeleteUser(), useUpdateUser(), useUsers() (+1 more)

### Community 115 - "Community 115"
Cohesion: 0.35
Nodes (10): _create_client(), _pdf_text(), asyncio, Extract the (decompressed) text content of an FPDF document., test_financial_report_uses_real_costs_not_ratio(), test_financial_report_zero_costs_when_none(), test_project_optimistic_locking_rejects_stale_update(), test_project_stats_total_estimated_value_is_decimal() (+2 more)

### Community 116 - "Community 116"
Cohesion: 0.18
Nodes (7): skipif, Liveness probe should always return 200 ok., Readiness probe should return 200 when all deps are healthy., Readiness probe should return 503 when DB is down., Verify readyz response structure., Tests for /healthz and /readyz endpoints., TestHealthEndpoints

### Community 117 - "Community 117"
Cohesion: 0.24
Nodes (9): add_listener, random, on_locust_init(), on_test_start(), on_test_stop(), Realistic load profile for SWA ERP based on actual user journeys. User roles…, Called when Locust starts., Called when a new test starts. (+1 more)

### Community 118 - "Community 118"
Cohesion: 0.22
Nodes (10): 10-level agent ladder dispatch system, ASSIGN-L4-L10.md (levels 4-10 dispatch), ASSIGN-LEVELS.md (10-level agent ladder), AGENT-1.md (dispatch report), AGENT-L1-A.md (dispatch report), AGENT-L1-B.md (dispatch report), AGENT-L1-C.md (dispatch report), AGENT-L1-D.md (dispatch report) (+2 more)

### Community 119 - "Community 119"
Cohesion: 0.22
Nodes (10): App Component Routing, Delete Zero Rule, Historical Documentation Archive, DOCS_MAP Documentation, Level 4 Implementation Completion, TimesheetView Component, AGENT-L4-A: Archive Duplicate Meeting Handoff Docs, AGENT-L4-B: Archive Work Dispatch Plan (+2 more)

### Community 120 - "Community 120"
Cohesion: 0.20
Nodes (10): BOQ Ingestion JSON Excel Support, Compliance Standards (NBC/ECBC/IGBC/IS), Level 2 Implementation Completion, No Direct rfq2boq Call Rule, TimeEntryForm Component, AGENT-L2-B: Files and Drawings Integration, AGENT-L2-C: Tasks Compliance Sustainability Users, AGENT-L2-D: Vendors Materials RFQs Reports BOQ Quotes (+2 more)

### Community 121 - "Community 121"
Cohesion: 0.22
Nodes (7): pydantic, src_backend_db, src_backend_schemas, ErrorResponse, Pagination, BaseModel, src_backend_services

### Community 122 - "Community 122"
Cohesion: 0.42
Nodes (9): BOQParseError, _build_row(), _cell_to_decimal(), _normalize_header(), parse_excel(), parse_json(), Decimal, Exception (+1 more)

### Community 123 - "Community 123"
Cohesion: 0.49
Nodes (9): create(), find_valid(), _hash_token(), Session, UUID, revoke_all_for_user(), revoke_single(), _verify_token() (+1 more)

### Community 124 - "Community 124"
Cohesion: 0.39
Nodes (9): Demo & Show Guide for Viraj & IT, Viraj Decision Log - Action Required, Demo Script - 5-10 Minutes, SWA ERP Administrator Guide, Architecture Overview for Viraj to Forward to IT, SWA ERP Getting Started One Pager, SWA ERP User Guide, Meeting and Go-Live Guide (+1 more)

### Community 125 - "Community 125"
Cohesion: 0.22
Nodes (9): Review Agent, Review Security Agent, Anti-Fabrication Rules, Multi-Agent Review Framework, Phase 0 Context Gathering, Phase 1 Multi-Agent Tools, Phase 2 Specialized Deep Dives, Phase 3 Findings Triage (+1 more)

### Community 126 - "Community 126"
Cohesion: 0.28
Nodes (9): Idempotency, Idempotency Gap, Pagination, Compliance API, Sustainability Metrics API, Tokens API, Idempotency Module, Unbounded List Endpoints (+1 more)

### Community 127 - "Community 127"
Cohesion: 0.25
Nodes (7): get_sentry_initialized(), init_sentry(), Check if Sentry has been initialized., Initialize Sentry SDK if SENTRY_DSN is configured. Returns True if initialized,…, lifespan(), init_sentry() should return False when no DSN is set., init_sentry() should return True when DSN is set.

### Community 128 - "Community 128"
Cohesion: 0.33
Nodes (9): StrEnum, TaskCreate, TaskPriority, TaskStatus, create_task_service(), test_create_task_happy(), test_create_task_inactive_assignee_raises(), test_create_task_invalid_assignee_raises() (+1 more)

### Community 129 - "Community 129"
Cohesion: 0.22
Nodes (9): scripts, build, dev, lint, preview, test, test:coverage, test:watch (+1 more)

### Community 131 - "Community 131"
Cohesion: 0.22
Nodes (8): RFQ, RFQAwardPayload, RFQCompareItem, RFQCreatePayload, RFQItem, RFQListResponse, RFQRespondPayload, RFQStatus

### Community 132 - "Community 132"
Cohesion: 0.22
Nodes (8): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, strict, include

### Community 133 - "Community 133"
Cohesion: 0.33
Nodes (8): Wave-18 dedicated invoice GST tests. Focuses only on the GST breakdown aspect…, Edge: empty items list rejected at schema level (min_length=1)., If tax_rate is omitted entirely, default 18% should apply., _setup_project(), test_gst_default_when_tax_rate_omitted(), test_gst_included_in_total_amount(), test_gst_line_in_list_view(), test_gst_zero_when_no_items()

### Community 134 - "Community 134"
Cohesion: 0.31
Nodes (8): AsyncClient, skipif, DB connection works (test DB uses create_all, not migrations)., test_cors_preflight(), test_healthz(), test_readyz_db_ok(), test_request_id_header(), test_user_model_has_required_columns()

### Community 136 - "Community 136"
Cohesion: 0.39
Nodes (8): Health Endpoints, Observability Gap, Prometheus Metrics, Sentry Error Tracking, Errors Module, Metrics Module, Wave-36 Observability, Wave-36 Post Merge Fixes

### Community 137 - "Community 137"
Cohesion: 0.39
Nodes (4): HTTPException, ClientError, IntegrationError, ServerError

### Community 138 - "Community 138"
Cohesion: 0.25
Nodes (5): Test materials endpoint authentication fixes, Test that material-categories endpoint requires auth, Test that materials endpoint requires auth, Test that materials/{id} endpoint requires auth, TestMaterialsAuth

### Community 140 - "Community 140"
Cohesion: 0.29
Nodes (7): client(), fixture, Wave-36 Observability Tests Tests for: - /metrics endpoint returns valid…, Test client with app lifespan (initializes metrics and Sentry)., Reset Sentry state between tests., reset_sentry(), unittest_mock

### Community 141 - "Community 141"
Cohesion: 0.36
Nodes (7): asyncio, Wave-50 task 01 (SF-4 / SEC-02): /metrics auth gate + METRICS_REQUIRE_AUTH. -…, Toggling the flag is runtime-dynamic (guard reads settings per request)., test_metrics_auth_restored_after_flag_reset(), test_metrics_authenticated_returns_prometheus_text(), test_metrics_open_when_flag_false(), test_metrics_unauthenticated_rejected_by_default()

### Community 142 - "Community 142"
Cohesion: 0.32
Nodes (8): AGENT-L10-C: Worktree Merge Planning, Worktree Merge Strategy, Worktree L2-10, Worktree L2-11, Worktree L2-7, Worktree L2-9, Worktree L3-B Service Agreement Changes, Worktree L3-D Nullable Project Changes

### Community 143 - "Community 143"
Cohesion: 0.33
Nodes (7): Core Chain Screens, Frontend Custom Hooks, Frontend Role-Gating Bug, Frontend Test Suite, Role-Gating Behaviour, Wave-34 Frontend Test Suite, Wave-34 Frontend Page Coverage

### Community 144 - "Community 144"
Cohesion: 0.48
Nodes (7): Dev Docker Compose Overrides, Production Docker Compose File, Base Docker Compose File, Deployment Checklist Production, Install on Company Server No IT Department, Full Project and Deployment Brief for IT, AGENT-L7-A: Windows Server installation docs

### Community 145 - "Community 145"
Cohesion: 0.29
Nodes (7): Handoff Protocol, Dispatch Ladder, Bugfix Recipe, New Wave Recipe, Orchestrator-Workers Pattern, Communication Process Feedback, Open Decisions List

### Community 146 - "Community 146"
Cohesion: 0.33
Nodes (6): format_report(), Any, evals/graders/llm_judge.py — rubric-based grading for subjective evaluation…, Format an LLM-judge score dict into a human-readable string., Score a single trial transcript against a rubric. Args: transcript: dict from…, score_transcript()

### Community 147 - "Community 147"
Cohesion: 0.29
Nodes (7): Agreement-Token-DocRef Chain Eval, Time Log to Dashboard Eval, Invoice GST Correctness Eval, Core ID Chain, MVP Definition, Client Core Flow, ID Format Specifications

### Community 148 - "Community 148"
Cohesion: 0.33
Nodes (6): load_tasks(), evals/tasks/loader.py — loads task YAML specs for reference/validation. The…, Load all .task.yaml files from evals/tasks/., Look up a task by its id prefix., task_by_id(), yaml

### Community 149 - "Community 149"
Cohesion: 0.29
Nodes (5): capture_exception(), Exception, Capture an exception with request context. Safe to call even if Sentry is not…, capture_exception should not crash when Sentry not initialized., capture_exception should work when Sentry is initialized.

### Community 150 - "Community 150"
Cohesion: 0.38
Nodes (3): SustainabilityMetric, test_delete_sustainability_metric(), test_list_sustainability_metrics_scoped_by_project()

### Community 151 - "Community 151"
Cohesion: 0.29
Nodes (5): parametrize, Verify scrubber covers all sensitive field types., scrub_pii should redact all known sensitive key patterns., scrub_pii should redact regardless of case., TestScrubberCoverage

### Community 152 - "Community 152"
Cohesion: 0.48
Nodes (6): Idempotency keys on money-moving invoice POSTs (migration 0042). - Same key +…, _setup_project(), test_create_replay_no_duplicate(), test_no_key_behaves_normally(), test_same_key_different_body_rejected(), test_status_update_replay()

### Community 154 - "Community 154"
Cohesion: 0.40
Nodes (6): Sidebar Test, Five MVP Modules Product Story, Level 3 Implementation Completion, Sidebar Component, AGENT-L3-E: Five MVP Modules Sidebar Grouping, Worktree L3-E Sidebar MVP Grouping

### Community 156 - "Community 156"
Cohesion: 0.47
Nodes (6): ensure_users(), link_chain(), main(), _norm(), Session, wipe()

### Community 157 - "Community 157"
Cohesion: 0.33
Nodes (4): Integration tests requiring full stack., Verify metrics can be scraped while handling requests., Verify X-Request-ID is present in response headers., TestIntegration

### Community 158 - "Community 158"
Cohesion: 0.60
Nodes (5): Bundle Splitting Gap, Code Splitting, Loading States, Loading States Gap, Wave-48 Frontend Loading States and Bundle Splitting

### Community 159 - "Community 159"
Cohesion: 0.50
Nodes (5): HIERARCHY.md, Load Test Artifacts, Repository Organization, Repository Sprawl, Wave-39 Repo Organization

### Community 160 - "Community 160"
Cohesion: 0.50
Nodes (3): ref_path, vite, @vitejs/plugin-react

### Community 161 - "Community 161"
Cohesion: 0.40
Nodes (4): locked_at, $schema, skills, version

### Community 162 - "Community 162"
Cohesion: 0.40
Nodes (4): generated, $schema, skills, version

### Community 163 - "Community 163"
Cohesion: 0.40
Nodes (4): BaseHTTPMiddleware, Request, Response, RequestIdMiddleware

### Community 164 - "Community 164"
Cohesion: 0.50
Nodes (3): BaseSettings, model_validator, Settings

### Community 165 - "Community 165"
Cohesion: 0.50
Nodes (4): Content-Security-Policy header middleware, Pagination envelope (items, total, page, page_size), Wave-48 Task 02: Pagination idempotency, Wave-48 Task 03: Token security hygiene

### Community 166 - "Community 166"
Cohesion: 0.50
Nodes (4): Decision Index, IT Decisions Log, Open Items from Meetings, Viraj Decisions Log

### Community 168 - "Community 168"
Cohesion: 0.83
Nodes (3): _hard_timeout(), parse_summary(), generate_metrics.sh script

### Community 169 - "Community 169"
Cohesion: 0.67
Nodes (3): Dispatch-24h agent reports (46 reports), FINAL_VERIFICATION.md (submission readiness), STATE.md (orchestrator state tracking)

### Community 170 - "Community 170"
Cohesion: 0.67
Nodes (3): Review Bugbot Agent, Conftest Architecture Problem, DROP SCHEMA Deadlock

### Community 171 - "Community 171"
Cohesion: 0.67
Nodes (3): Repository Hierarchy, Data Flow Pattern, Backend Module Layout

### Community 172 - "Community 172"
Cohesion: 0.67
Nodes (3): Frontend bundle splitting with React.lazy, React App.tsx (lazy routes), Wave-48 Task 05: Frontend loading states and bundle splitting

### Community 174 - "Community 174"
Cohesion: 0.67
Nodes (3): fixture, Create a temporary DB, run alembic upgrade head, yield engine., scratch_db()

## Knowledge Gaps
- **619 isolated node(s):** `@modelcontextprotocol/server-filesystem`, `@modelcontextprotocol/server-git`, `@modelcontextprotocol/server-postgres`, `@modelcontextprotocol/server-sequential-thinking`, `@upstash/context7-mcp` (+614 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1452 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **71 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Community 81` to `Community 128`, `Community 2`, `Community 4`, `Community 134`, `Community 7`, `Community 6`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 22`, `Community 23`, `Community 25`, `Community 26`, `Community 27`, `Community 156`, `Community 30`, `Community 32`, `Community 33`, `Community 34`, `Community 35`, `Community 36`, `Community 37`, `Community 38`, `Community 39`, `Community 43`, `Community 45`, `Community 46`, `Community 53`, `Community 65`, `Community 69`, `Community 95`, `Community 98`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `Refresh Token Rotation` connect `Community 80` to `Community 165`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `Wave-48 Task 03: Token security hygiene` connect `Community 165` to `Community 80`, `Community 19`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 241 inferred relationships involving `User` (e.g. with `create_agreement()` and `delete_agreement()`) actually correct?**
  _`User` has 241 INFERRED edges - model-reasoned connections that need verification._
- **Are the 124 inferred relationships involving `Role` (e.g. with `create_agreement()` and `delete_agreement()`) actually correct?**
  _`Role` has 124 INFERRED edges - model-reasoned connections that need verification._
- **What connects `@modelcontextprotocol/server-filesystem`, `@modelcontextprotocol/server-git`, `@modelcontextprotocol/server-postgres` to the rest of the system?**
  _619 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.018021493524386884 - nodes in this community are weakly interconnected._