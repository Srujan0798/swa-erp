/**
 * Centralized formatting utilities for SWA ERP.
 * All commercial/operational views must use these formatters.
 * Backend owns authoritative calculation/rounding; frontend displays canonical strings.
 */

export const BUSINESS_LOCALE = "en-IN";
export const BUSINESS_TIMEZONE = "Asia/Kolkata";
export const DEFAULT_CURRENCY = "INR";

/**
 * Format amount as Indian Rupees with proper grouping and decimals.
 * Uses backend-rounded values; frontend only displays canonical strings.
 */
export function formatMoney(
  amount: number | string | null | undefined,
  options: {
    currency?: string;
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
    showSymbol?: boolean;
    accountingNegative?: boolean;
  } = {}
): string {
  const {
    currency = DEFAULT_CURRENCY,
    minimumFractionDigits = 2,
    maximumFractionDigits = 2,
    showSymbol = true,
    accountingNegative = false,
  } = options;

  if (amount === null || amount === undefined || amount === "") {
    return showSymbol ? "₹0.00" : "0.00";
  }

  const num = typeof amount === "string" ? parseFloat(amount) : amount;

  if (Number.isNaN(num)) {
    return showSymbol ? "₹0.00" : "0.00";
  }

  const formatter = new Intl.NumberFormat(BUSINESS_LOCALE, {
    style: showSymbol ? "currency" : "decimal",
    currency,
    minimumFractionDigits,
    maximumFractionDigits,
    currencyDisplay: "symbol",
  });

  let formatted = formatter.format(num);

  if (accountingNegative && num < 0) {
    formatted = `(${formatted.replace("-", "")})`;
  }

  return formatted;
}

/**
 * Format a number with Indian grouping but no currency symbol.
 * For quantities, rates, percentages, etc.
 */
export function formatNumber(
  value: number | string | null | undefined,
  options: {
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
    useGrouping?: boolean;
  } = {}
): string {
  const { minimumFractionDigits = 0, maximumFractionDigits = 2, useGrouping = true } = options;

  if (value === null || value === undefined || value === "") {
    return "0";
  }

  const num = typeof value === "string" ? parseFloat(value) : value;

  if (Number.isNaN(num)) {
    return "0";
  }

  return new Intl.NumberFormat(BUSINESS_LOCALE, {
    minimumFractionDigits,
    maximumFractionDigits,
    useGrouping,
  }).format(num);
}

/**
 * Format date as dd MMM yyyy (e.g., 15 Jan 2026)
 */
export function formatDate(
  date: string | Date | null | undefined,
  options: { format?: "short" | "medium" | "long" } = {}
): string {
  if (!date) return "—";

  const d = typeof date === "string" ? new Date(date) : date;

  if (Number.isNaN(d.getTime())) return "—";

  const { format = "medium" } = options;

  const optionsMap: Record<string, Intl.DateTimeFormatOptions> = {
    short: { day: "2-digit", month: "short", year: "2-digit" },
    medium: { day: "2-digit", month: "short", year: "numeric" },
    long: { day: "2-digit", month: "long", year: "numeric" },
  };

  return new Intl.DateTimeFormat(BUSINESS_LOCALE, optionsMap[format]).format(d);
}

/**
 * Format date and time as dd MMM yyyy, hh:mm a
 */
export function formatDateTime(
  date: string | Date | null | undefined
): string {
  if (!date) return "—";

  const d = typeof date === "string" ? new Date(date) : date;

  if (Number.isNaN(d.getTime())) return "—";

  return new Intl.DateTimeFormat(BUSINESS_LOCALE, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  }).format(d);
}

/**
 * Format short date as dd/MM/yyyy
 */
export function formatShortDate(date: string | Date | null | undefined): string {
  if (!date) return "—";

  const d = typeof date === "string" ? new Date(date) : date;

  if (Number.isNaN(d.getTime())) return "—";

  return new Intl.DateTimeFormat(BUSINESS_LOCALE, {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(d);
}

/**
 * Format relative time (e.g., "2 days ago", "in 3 hours")
 */
export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return "—";

  const d = typeof date === "string" ? new Date(date) : date;

  if (Number.isNaN(d.getTime())) return "—";

  const now = new Date();
  const diffMs = d.getTime() - now.getTime();
  const absMs = Math.abs(diffMs);
  const minutes = Math.floor(absMs / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    return diffMs > 0 ? `in ${days}d` : `${days}d ago`;
  }
  if (hours > 0) {
    return diffMs > 0 ? `in ${hours}h` : `${hours}h ago`;
  }
  if (minutes > 0) {
    return diffMs > 0 ? `in ${minutes}m` : `${minutes}m ago`;
  }
  return "just now";
}

/**
 * Format percentage with 2 decimal places
 */
export function formatPercent(value: number | string | null | undefined): string {
  if (value === null || value === undefined || value === "") return "0.00%";

  const num = typeof value === "string" ? parseFloat(value) : value;

  if (Number.isNaN(num)) return "0.00%";

  return `${num.toFixed(2)}%`;
}

/**
 * Format GST rate (e.g., 18.00%)
 */
export function formatGstRate(value: number | string | null | undefined): string {
  return formatPercent(value);
}

/**
 * Format quantity with appropriate precision
 */
export function formatQuantity(
  value: number | string | null | undefined,
  precision = 2
): string {
  return formatNumber(value, { maximumFractionDigits: precision });
}

/**
 * Format rate (rate per unit)
 */
export function formatRate(value: number | string | null | undefined): string {
  return formatMoney(value, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/**
 * Safely parse a money string back to number
 */
export function parseMoney(value: string | number | null | undefined): number {
  if (value === null || value === undefined || value === "") return 0;

  if (typeof value === "number") return value;

  // Remove currency symbol, commas, parentheses
  const cleaned = value
    .replace(/[₹,\s]/g, "")
    .replace(/\((.*)\)/, "-$1");

  const num = parseFloat(cleaned);
  return Number.isNaN(num) ? 0 : num;
}