# Meeting 1 — Client Flow & Document Reference System (Clean)

**Date:** [Insert Date]  
**Participants:** Viraj, Balram, [Software Engineer]  
**Purpose:** Document the current manual flow for client onboarding, document reference generation, token IDs, and sheet relationships.

---

## 1. Core Flow (Linear)

```
Inquiry (ML) 
    ↓
Client Created → Client ID generated
    ↓
Service Agreement Selected (1 of 4)
    ↓
Agreement ID assigned (per client source)
    ↓
Token Number Sheet → Continuous token sequence
    ↓
Document Reference Number (DBR/KDR/Reforge) → Continuous per type
    ↓
Document Generated (Word) → Sent to Client
    ↓
Time Log Entry (Hours worked) → Dashboard
```

---

## 2. Key Entities & IDs

| Entity | ID Format | Source | Notes |
|--------|-----------|--------|-------|
| **Client** | Auto-generated | On inquiry → client conversion | Primary key |
| **Agreement** | Numeric (12, 0.12, 0.9) | Pre-defined per source | 4 total: IESK=12, APEX=0.12, Inner=0.9, [4th?] |
| **Token** | Continuous (1801, 1802...) | Token Sheet | Year-aware (1801=prev year) |
| **DBR** | Continuous (138, 139...) | DBR Sheet | Design Basic Report |
| **KDR** | Continuous (shared with DBR) | Same sequence | Key Design Report |
| **Reforge** | `INNN074` format | Reforge Sheet | Certification projects |

---

## 3. Sheet Relationships (Primary/Foreign Keys)

```
Segmentation Sheet (Source of ML)
    │
    ├─→ Agreement ID Sheet (FK: Agreement ID)
    │       │
    │       └─→ Token Sheet (FK: Agreement ID + Token #)
    │               │
    │               ├─→ DBR Sheet (FK: Token # → DBR #)
    │               ├─→ KDR Sheet (FK: Token # → KDR #)
    │               ├─→ Reforge Sheet (FK: Reforge ID → DPR Sheet)
    │               │       └─→ Time Log Sheet (FK: Reforge ID → Hours)
    │               │
    │               ├─→ DRM Sheet (FK: Token #)
    │               ├─→ Bangalore Sheet (FK: Token #)
    │               └─→ Western Utility Sheet (FK: Token #)
    │
    └─→ Independent Sheets (no FKs)
            ├─→ HR/Admin Sheet (restricted)
            ├─→ Employee Satisfaction (restricted)
            ├─→ Finance Sheet (founder only)
            └─→ Client Satisfaction / Complaints (drop from MVP)
```

**Core 4 Sheets (80% of entries):** Segmentation, Token, DBR/KDR, Time Log  
**Linked Sheets:** DRM, Bangalore, Western Utility, Reforge/DPR  
**Independent (restricted):** HR, Finance, Satisfaction  
**Drop from MVP:** Client Satisfaction, Complaints

---

## 4. Access Control Matrix (Map to RBAC)

| Sheet / Function | Current Restriction | Proposed Role |
|------------------|---------------------|---------------|
| Segmentation (ML entry) | All | PM, Designer |
| Agreement ID lookup | All | PM |
| Token generation | All | PM |
| DBR/KDR generation | All | PM, Designer |
| Reforge/DPR | Certification team | Auditor, Designer |
| Time Log (hours) | Owner only | PM, Designer (own), Admin (all) |
| HR/Admin | HR only | **Drop / Admin only** |
| Finance | Founder only | **Admin only** |
| Employee Satisfaction | HR | **Drop** |
| Client Satisfaction | — | **Drop from MVP** |
| Client Complaints | — | **Drop from MVP** |

---

## 5. Time Logging (Current)

- Per token/project: Date, Token ID, Description, Website/Ref, Hours worked (e.g., 2-3 hrs)
- Stored in "My Dashboard" sheet
- **Future:** Auto-calculate available hours, efficiency metrics

---

## 6. Sustainability Metrics (Future)

- Carbon savings, energy savings, payback period, lifecycle assessment
- Per project, entered when client provides ID

---

## 7. Open Decisions Needed from Viraj

| Decision | Options | Impact |
|----------|---------|--------|
| **4th Agreement ID** | What is the 4th agreement? | Data model |
| **Independent sheets** | Drop HR/Finance/Satisfaction/Complaints from MVP? | Scope |
| **Access control** | Map above matrix to RBAC roles? | Auth design |
| **Token year reset** | Annual reset (1801→2001) or continuous? | DB schema |
| **DBR vs KDR sequence** | Shared counter confirmed? | DB schema |
| **Reforge ID format** | `INNN074` fixed pattern? | Validation |
| **Sustainability metrics** | Required in Wave-4 or Wave-8? | Timeline |

---

## 8. Current Pain Points (Verbatim)

> "We are doing this flow in live. Currently we are doing this flow, but the final flow decided by Viraj."
> "I need clear documentation... how to proceed further. Like I should know how to do this, in a way of a website or any workflow."
> "I have understood the problem and I can do this, but I need that clear documentation."

**→ This ERP *is* that documentation + workflow automation.**