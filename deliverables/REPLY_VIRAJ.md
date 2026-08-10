# Next message to Viraj (WhatsApp / group)

**Context:** He answered the 3 data Qs earlier. Soft follow-up: server Qs “will discuss when time comes.”  
**New instruction:** remove Lead ID columns everywhere — not even historical.

---

## COPY-PASTE

```
Got it Viraj 👍

Lead ID — locked as you said:
• We remove Lead ID / LDI columns everywhere in the system
• Not kept even for historical values
• Excel "First Lead ID" is ignored on import
• New work = Inquiry only (SWA-YYYY-INQ-…)
• No Leads sheet / no Leads module

Already locked from before:
• APEX / INNER = client names
• INSUDESIGN = service name
• Yearly ID reset everywhere (…-2025-…-011 → …-2026-…-001)

Server / install questions — no rush, whenever you have bandwidth (“will discuss when time comes”).

Build stays ready; next step on our side is deploy when server details are free, then one-time Excel import of the live sheets.
```

---

## Do NOT re-ask

- The long 8 server questions (he deferred)  
- LDI examples again (decision is delete, not explain)  

## Next steps for Srujan (internal)

1. Send the reply above  
2. Migration `0030` applied — `first_lead_id` gone from DB  
3. Continue: keep UI on :3100, real import path; wait on server for go-live  
