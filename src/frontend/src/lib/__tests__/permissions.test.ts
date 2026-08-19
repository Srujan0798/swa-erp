import { describe, it, expect } from "vitest";
import { roleAtLeast, canWrite, canManageCommercial, canAdmin, canManageProjects } from "../permissions";

describe("roleAtLeast", () => {
  it("returns false for missing or empty role", () => {
    expect(roleAtLeast(null, "viewer")).toBe(false);
    expect(roleAtLeast(undefined, "viewer")).toBe(false);
    expect(roleAtLeast({ role: "" }, "viewer")).toBe(false);
  });

  it("returns true when role equals or exceeds the required role", () => {
    expect(roleAtLeast({ role: "admin" }, "viewer")).toBe(true);
    expect(roleAtLeast({ role: "pm" }, "pm")).toBe(true);
    expect(roleAtLeast({ role: "designer" }, "viewer")).toBe(true);
    expect(roleAtLeast({ role: "auditor" }, "viewer")).toBe(true);
  });

  it("returns false when role is below the required role", () => {
    expect(roleAtLeast({ role: "viewer" }, "pm")).toBe(false);
    expect(roleAtLeast({ role: "designer" }, "pm")).toBe(false);
    expect(roleAtLeast({ role: "pm" }, "admin")).toBe(false);
  });

  it("treats role case-insensitively and ignores unknown roles", () => {
    expect(roleAtLeast({ role: "ADMIN" }, "pm")).toBe(true);
    expect(roleAtLeast({ role: "superuser" }, "viewer")).toBe(false);
  });
});

describe("canWrite", () => {
  it("denies viewers and anonymous users", () => {
    expect(canWrite({ role: "viewer" })).toBe(false);
    expect(canWrite(null)).toBe(false);
    expect(canWrite({ role: "" })).toBe(false);
  });

  it("allows every non-viewer role", () => {
    expect(canWrite({ role: "admin" })).toBe(true);
    expect(canWrite({ role: "pm" })).toBe(true);
    expect(canWrite({ role: "designer" })).toBe(true);
    expect(canWrite({ role: "auditor" })).toBe(true);
  });
});

describe("canManageCommercial", () => {
  it("allows admin and pm only", () => {
    expect(canManageCommercial({ role: "admin" })).toBe(true);
    expect(canManageCommercial({ role: "pm" })).toBe(true);
  });

  it("denies designer, auditor, viewer, and unknown", () => {
    expect(canManageCommercial({ role: "designer" })).toBe(false);
    expect(canManageCommercial({ role: "auditor" })).toBe(false);
    expect(canManageCommercial({ role: "viewer" })).toBe(false);
    expect(canManageCommercial(null)).toBe(false);
  });
});

describe("canAdmin", () => {
  it("allows only admin", () => {
    expect(canAdmin({ role: "admin" })).toBe(true);
    expect(canAdmin({ role: "pm" })).toBe(false);
    expect(canAdmin({ role: "viewer" })).toBe(false);
  });
});

describe("canManageProjects", () => {
  it("allows admin and pm only", () => {
    expect(canManageProjects({ role: "admin" })).toBe(true);
    expect(canManageProjects({ role: "pm" })).toBe(true);
    expect(canManageProjects({ role: "designer" })).toBe(false);
  });
});