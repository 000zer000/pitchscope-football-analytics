import { test, expect } from "@playwright/test";

test("search, profile, match filters and PDF remain usable at both required widths", async ({
  page,
  request,
}) => {
  const [player] = (
    await (
      await request.get("/api/players?role=Forward&size=100&sort=minutes")
    ).json()
  ).items;
  const coverage = await (await request.get("/api/coverage")).json();
  const real = coverage.complete === true;
  const match = real ? 3869685 : coverage.matches[0].id;
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1050 });
    await page.goto("/?view=players");
    await page
      .getByRole("combobox", { name: "Role group", exact: true })
      .selectOption("Forward");
    await page
      .getByRole("combobox", { name: "Minimum minutes", exact: true })
      .selectOption(real ? "180" : "0");
    await page
      .getByRole("textbox", { name: "Search players" })
      .fill(player.name);
    await page
      .getByRole("button", {
        name: "Open profile for " + player.name,
        exact: true,
      })
      .click();
    await expect(
      page.getByRole("heading", { name: player.name, exact: true }),
    ).toBeVisible();
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBe(width);
    await page
      .getByRole("button", { name: "Select to compare", exact: true })
      .click();
    await expect(
      page.getByRole("button", { name: "Remove from comparison", exact: true }),
    ).toBeVisible();
    await page.screenshot({
      path: `test-results/profile-${width}.png`,
      fullPage: true,
    });
    await page.goto("/?view=matches&match=" + match);
    await expect(
      page.getByRole("heading", { name: "Shot map", exact: true }),
    ).toBeVisible();
    await expect(page.locator(".breadcrumb strong")).toHaveText("Matches");
    const api = await (
      await request.get(`/api/matches/${match}/events?kind=Shot&size=500`)
    ).json();
    const expected = api.items.filter(
      (e: { period: number }) => e.period < 5,
    ).length;
    const shots = page.locator('.pitch circle[role="button"]');
    await expect(shots).toHaveCount(expected);
    await shots.first().press("Enter");
    await expect(
      page.getByRole("heading", { name: "Source event ID" }),
    ).toBeVisible();
    await expect(page.locator(".event-detail code")).toHaveText(
      api.items.find((e: { period: number }) => e.period < 5).id,
    );
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBe(width);
    await page.screenshot({
      path: `test-results/match-${width === 1440 ? "desktop" : "mobile"}.png`,
      fullPage: true,
    });
    if (real) {
      await page
        .getByRole("combobox", { name: "Match team" })
        .selectOption("771");
      await expect(shots).toHaveCount(10);
      await page.getByRole("combobox", { name: "Match team" }).selectOption("");
      await expect(shots).toHaveCount(30);
      const report = await request.get(
        "/api/report.pdf?left=5207&right=11603&role=Forward&min_minutes=180",
      );
      expect(report.status()).toBe(200);
      const { writeFileSync } = await import("node:fs");
      writeFileSync("test-results/long-names.pdf", await report.body());
    }
    if (width === 390) {
      await page.getByRole("button", { name: "Open menu" }).click();
      await page
        .getByRole("button", { name: "Methodology", exact: true })
        .click();
    } else
      await page
        .getByRole("button", { name: "Methodology", exact: true })
        .click();
    await expect(
      page.getByRole("heading", { name: "Results you can verify." }).first(),
    ).toBeVisible();
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBe(width);
  }
});
