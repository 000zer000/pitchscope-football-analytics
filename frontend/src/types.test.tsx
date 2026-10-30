import { describe, it, expect } from "vitest";
import { format } from "./types";
describe("metric presentation contract", () => {
  it("distinguishes unavailable values from measured zero", () => {
    expect(format(null)).toBe("N/A");
    expect(format(undefined)).toBe("N/A");
    expect(format(0)).toBe("0.00");
  });
  it("preserves the API rounding convention to two decimals", () => {
    expect(format(1.234)).toBe("1.23");
    expect(format(85.678, 1)).toBe("85.7");
  });
});
