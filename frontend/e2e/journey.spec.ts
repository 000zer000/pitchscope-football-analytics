import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { statSync } from "node:fs";
import path from "node:path";
test("search, filter, compare, inspect a match, export verified PDF", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const rows = (
    await (
      await request.get("/api/players?role=Forward&size=100&sort=minutes")
    ).json()
  ).items;
  expect(rows.length).toBeGreaterThanOrEqual(2);
  const [a, b] = rows;
  await page.goto("/");
  await page
    .getByRole("combobox", { name: "Role group", exact: true })
    .selectOption("Forward");
  await page
    .getByRole("combobox", { name: "Minimum minutes", exact: true })
    .selectOption("0");
  await page.getByRole("textbox", { name: "Search players" }).fill(a.name);
  await expect(
    page.getByRole("button", {
      name: "Open profile for " + a.name,
      exact: true,
    }),
  ).toBeVisible();
  await page
    .getByRole("checkbox", { name: "Select " + a.name, exact: true })
    .check();
  await page.getByRole("textbox", { name: "Search players" }).fill(b.name);
  await page
    .getByRole("checkbox", { name: "Select " + b.name, exact: true })
    .check();
  await page
    .getByRole("button", { name: "Compare players", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "The numbers, side by side" }),
  ).toBeVisible();
  const api = await (
    await request.get(
      "/api/compare?left=" +
        a.id +
        "&right=" +
        b.id +
        "&role=Forward&min_minutes=180",
    )
  ).json();
  for (const p of api.players) {
    const value = Number(p.xg).toLocaleString("en-GB", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    await expect(page.getByTestId("xg-" + p.id)).toHaveText(value);
  }
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("link", { name: "Export PDF report" }).click(),
  ]);
  const file = await download.path();
  expect(file).toBeTruthy();
  expect(statSync(file!).size).toBeGreaterThan(5000);
  const python = process.env.PYTHON_BIN || path.resolve("../.venv/bin/python");
  const text = execFileSync(
    python,
    [
      "-c",
      'from pypdf import PdfReader; import sys; print("\\n".join(p.extract_text() for p in PdfReader(sys.argv[1]).pages))',
      file!,
    ],
    { encoding: "utf8" },
  );
  expect(text).toContain(a.name);
  expect(text).toContain(b.name);
  for (const p of api.players) expect(text).toContain(p.xg.toFixed(2));
  await page
    .getByRole("button", { name: "Open profile", exact: true })
    .first()
    .click();
  await page.getByRole("button").filter({ hasText: /min ·/ }).first().click();
  await expect(
    page.getByRole("heading", { name: "Shot map", exact: true }),
  ).toBeVisible();
  const point = page.getByRole("button", { name: /minute,/ }).first();
  await point.click();
  await expect(
    page.getByRole("heading", { name: "Source event ID" }),
  ).toBeVisible();
  expect(await page.locator(".event-detail code").textContent()).toBeTruthy();
  await page.screenshot({
    path: "test-results/match-desktop.png",
    fullPage: true,
  });
  await page.goto("/?view=players");
  await page
    .getByRole("button", { name: "Open profile for " + a.name, exact: true })
    .waitFor();
  await page.screenshot({
    path: "test-results/explorer-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/?view=players");
  await expect(
    page.getByRole("textbox", { name: "Search players" }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(390);
  await page.screenshot({
    path: "test-results/explorer-mobile.png",
    fullPage: true,
  });
  expect(errors).toEqual([]);
});
