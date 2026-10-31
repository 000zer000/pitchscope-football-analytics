import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "e2e",
  timeout: 60000,
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: process.env.BASE_URL || "http://127.0.0.1:5173",
    headless: true,
    video: "retain-on-failure",
    viewport: { width: 1440, height: 1050 },
    trace: process.env.RECORD_VIDEO === "true" ? "off" : "retain-on-failure",
  },
  reporter: [["list"], ["json", { outputFile: "test-results/results.json" }]],
});
