# Next group message to Viraj (already in the thread)

**Context (do not re-send the big briefs):**  
You already asked the 3 data Qs + 8 server Qs in the WhatsApp group. Viraj answered the 3
and said there is **no IT department** (he'll try the server Qs when free). You already said
"ok no worries."

**Send this next** — short, answers what he asked (show data / LDI example), no pressure on IT.

---

## COPY-PASTE (WhatsApp)

```
Got it Viraj — thanks 👍 locking this in:

1) APEX / INNER = client names. INSUDESIGN = service name. (not a 4th agreement type)
2) Yearly ID reset everywhere — e.g. SWA-2025-SA-011 → next year SWA-2026-SA-001. Already how the system works.
3) Leads sheet removed — understood, we won't build Leads.

Quick example for the LDI thing you asked about:
On the Clients Excel sheet there's a column "First Lead ID" with values like LDI-001 or SWA-2025-LDI-001.
That's separate from Inquiry IDs like SWA-2025-INQ-001.
We'll treat any old LDI values as historical only on import — new work = Inquiry only.

No rush on the server questions — whenever you have bandwidth (or whoever handles the Windows server / VPN). Build is ready either way.

One soft question for later: when we go live, who should run the one-time Excel import of the real sheets — you / someone on your team, or me on a short call with you?
```

---

## If he asks "show the data" for Q1 (optional second bubble)

Only if he pushes for verification from the sample files:

```
From the sample Service Agreements sheet: Service Name column has values like INSUDESIGN.
APEX / INNER show up as client-side names in the verbal notes / client context — not as SA "types" in the live ID scheme (live IDs are SWA-YYYY-SA-NNN).
So we're aligning the app to: clients = APEX/INNER/etc, service_name free text = INSUDESIGN (and any other product names later).
```

---

## Do NOT send again

- Full `SEND_VIRAJ.md` / `SEND_IT.md` walls of text  
- "Please answer the 8 IT questions" follow-ups while he said he's busy and no IT dept  
- Re-asking year reset or Leads  

## When he's free later (server)

If he opens the topic, use a **minimal** list (not the original long IT brief):

```
Whenever useful for install on the company server, only these matter:
1) Can we use Docker (free Engine) + WSL2 on that Windows box?
2) What hostname/IP should staff open? (e.g. erp.swa.local or an IP)
3) Prefer everything in Docker (DB+Redis+app), or DB outside Docker?
4) HTTPS: company cert or self-signed OK on VPN for v1?
5) Who can remote in for the first install + how you'll want updates later?

Defaults if you don't care yet: all-in-Docker, self-signed on VPN, we use backup scripts until company backup is decided.
```
