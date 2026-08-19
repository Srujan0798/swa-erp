import { describe, it, expect, beforeEach } from "vitest";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "../auth";

describe("auth token helpers", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("returns null when no tokens stored", () => {
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });

  it("stores and reads access and refresh tokens", () => {
    setTokens("access-1", "refresh-1");
    expect(getAccessToken()).toBe("access-1");
    expect(getRefreshToken()).toBe("refresh-1");
  });

  it("clears both tokens", () => {
    setTokens("access-1", "refresh-1");
    clearTokens();
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });
});