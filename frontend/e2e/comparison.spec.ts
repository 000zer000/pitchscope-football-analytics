import { test, expect, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import type { Comparison } from "../src/types";
const fmt = (v: unknown, digits = 2) =>
  typeof v === "number"
    ? v.toLocaleString("en-GB", {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
      })
    : "N/A";
export async function assertCharts(page: Page, data: Comparison) {
  for (const key of ["shots_p90", "xg_p90", "passes_p90"] as const) {
    const chart = page.getByTestId("chart-" + key);
    const positive = data.players.filter((p) => (p[key] ?? 0) > 0);
    const bars = chart.locator(".recharts-bar-rectangle .recharts-rectangle");
    // Assert actual, visible, coloured SVG geometry, not a heading or an axis.
    await expect(bars).toHaveCount(positive.length);
    const widths: number[] = [];
    for (const bar of await bars.all()) {
      const box = await bar.boundingBox();
      expect(box!.width).toBeGreaterThan(1);
      expect(box!.height).toBeGreaterThan(10);
      expect(await bar.getAttribute("fill")).toMatch(/^#(2c7259|668bc0)$/);
      widths.push(box!.width);
    }
    if (widths.length === 2)
      expect(widths[0] / widths[1]).toBeCloseTo(
        positive[0][key]! / positive[1][key]!,
        1,
      );
    for (const [i, p] of data.players.entries()) {
      await expect(
        page.getByTestId(`${key}-chart-value-${p.id}`),
      ).toContainText(`${i + 1}: ${fmt(p[key])}`);
      if (Object.keys(p.percentiles ?? {}).length)
        await expect(page.getByTestId(`percentile-${key}-${p.id}`)).toHaveText(
          typeof p.percentiles?.[key] === "number"
            ? `P${fmt(p.percentiles[key], 0)}`
            : "N/A",
        );
    }
  }
  await expect(page.locator(".charts")).not.toContainText("$P{");
  await expect(page.locator(".charts")).not.toContainText("shots_p90");
  for (const p of data.players)
    await expect(
      page.getByRole("list", { name: "Player colour legend" }),
    ).toContainText(p.name);
}

test("comparison bars, rates and percentiles agree with API at 1440 and 390 pixels", async ({
  page,
  request,
}) => {
  const rows = (
    await (
      await request.get("/api/players?role=Forward&size=100&sort=minutes")
    ).json()
  ).items;
  const real =
    (await (await request.get("/api/coverage")).json()).complete === true;
  const query = `left=${rows[0].id}&right=${rows[1].id}&role=Forward&min_minutes=${real ? 180 : 0}`;
  const api: Comparison = await (
    await request.get("/api/compare?" + query)
  ).json();
  if (real) {
    const study = JSON.parse(readFileSync("../docs/case-study.json", "utf8"));
    expect(api.population).toEqual(study.population);
    for (const p of api.players)
      for (const key of [
        "shots_p90",
        "xg_p90",
        "passes_p90",
        "xg",
        "minutes",
        "percentiles",
      ]) {
        const expected = study.players.find(
          (s: { id: number }) => s.id === p.id,
        )[key];
        const actual = p[key as keyof typeof p];
        if (key === "percentiles") {
          for (const [metric, value] of Object.entries(expected))
            expect(p.percentiles![metric]).toBeCloseTo(value as number, 8);
        } else expect(actual).toBeCloseTo(expected, 8);
      }
  }
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1050 });
    await page.goto(
      `/?view=compare&left=${rows[0].id}&right=${rows[1].id}&role=Forward&min=${real ? 180 : 0}`,
    );
    await expect(page.getByTestId("xg-" + rows[0].id)).toHaveText(
      fmt(api.players[0].xg),
    );
    for (const p of api.players)
      for (const m of api.metrics)
        await expect(page.getByTestId(m.key + "-" + p.id)).toHaveText(
          fmt(p[m.key]),
        );
    await assertCharts(page, api);
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBe(width);
    await page.screenshot({
      path: `test-results/comparison-${width === 1440 ? "desktop" : "mobile"}.png`,
      fullPage: true,
    });
    // All controls remain reachable; mobile table scroll stays inside its container.
    await expect(
      page.getByRole("link", { name: "Export PDF report" }),
    ).toBeVisible();
    await page
      .getByRole("combobox", { name: "Comparison threshold" })
      .selectOption("600");
    const next = await (
      await request.get(
        `/api/compare?left=${rows[0].id}&right=${rows[1].id}&role=Forward&min_minutes=600`,
      )
    ).json();
    await expect(
      page.getByText(next.population.count + " reference players", {
        exact: true,
      }),
    ).toBeVisible();
    await expect(page.locator(".percentile-player").first()).toContainText(
      "Unavailable",
    );
  }
});

test("zero, null and long accented names keep their meaning on a narrow screen", async ({
  page,
  request,
}) => {
  const rows = (
    await (
      await request.get("/api/players?role=Forward&size=100&sort=minutes")
    ).json()
  ).items;
  const data: Comparison = await (
    await request.get(
      `/api/compare?left=${rows[0].id}&right=${rows[1].id}&role=Forward&min_minutes=0`,
    )
  ).json();
  data.players[0] = {
    ...data.players[0],
    name: "TEST Vinícius José Paixão de Oliveira Júnior Pašalić",
    shots_p90: 0,
    xg_p90: null,
    passes_p90: 0,
    percentiles: { shots_p90: 0, passes_p90: 0 },
  };
  data.players[1] = { ...data.players[1], percentiles: {} };
  await page.route("**/api/compare?*", (route) =>
    route.fulfill({ json: data }),
  );
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(
    `/?view=compare&left=${rows[0].id}&right=${rows[1].id}&role=Forward&min=0`,
  );
  await expect(page.getByTestId("xg_p90-" + rows[0].id)).toHaveText("N/A");
  await assertCharts(page, data);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(
    390,
  );
});
