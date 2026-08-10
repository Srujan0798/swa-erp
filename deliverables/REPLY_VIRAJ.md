# Reply to Viraj — SWA ERP Data Questions (2026-08-11)

Hi Viraj,

Thanks for the quick answers! This clears up everything for the ID chain and service agreement setup.

## Summary of your answers (locked in the system):

✅ **Service Agreement type:** APEX and INNER are client names, INSUDESIGN is the service name.  
✅ **ID sequence:** Yearly reset everywhere — SWA-2025-SA-011 → SWA-2026-SA-001.  
✅ **Leads/`LDI-*`:** No Leads sheet exists (removed due to maintenance complexity).  

## Regarding `LDI-*` example you asked for:

You mentioned you'd like an example of the `LDI-*` format. Here's what I found in the source data:

The `LDI` format appears to be a legacy ID scheme for the same concept we now call "Inquiry". For example:
- An inquiry might have been recorded as `SWA-2025-LDI-001` in older systems
- Today, new inquiries use `SWA-2025-INQ-001` 
- The importer will map any `LDI-*` values from the Excel sheets into the `Inquiry` table

This means your team can continue using `LDI-*` in legacy Excel sheets, and the system will treat them as inquiries during import.

## Next steps:

1. **System is ready** — Your answers confirm the design. No code changes needed.
2. **Deployment** — When you have bandwidth, we'll fill in the server details (Docker, ports, HTTPS, etc.) for deployment.
3. **Excel import** — Once deployed, we can run the importer against your real data. Just let me know who should run it when we're ready.

No rush on the server questions — the system is complete and ready to go live whenever you're ready to deploy.

Best,
Srujan