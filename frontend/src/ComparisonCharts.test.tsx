import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import { ComparisonCharts } from "./ComparisonCharts";
import type { Comparison, Player } from "./types";
afterEach(cleanup);
const data = {
  players: [
    {
      id: 1,
      name: "TEST Long Áccented Name Cuccittini",
      shots_p90: 0,
      xg_p90: null,
      passes_p90: 42.213,
      percentiles: { shots_p90: 0, passes_p90: 90.58 },
    },
    {
      id: 2,
      name: "TEST Pašalić",
      shots_p90: 2,
      xg_p90: 0.5,
      passes_p90: 20,
      percentiles: {},
    },
  ] as Player[],
  metrics: [
    { key: "shots_p90", label: "Shots / 90", unit: "shots/90 min" },
    { key: "xg_p90", label: "xG / 90", unit: "xG/90 min" },
    { key: "passes_p90", label: "Passes / 90", unit: "passes/90 min" },
  ],
} as Comparison;
it("renders API percentiles with readable labels, including zero and missing metrics", () => {
  const { container } = render(<ComparisonCharts data={data} />);
  expect(screen.getByTestId("percentile-shots_p90-1").textContent).toBe("P0");
  expect(screen.getByTestId("percentile-passes_p90-1").textContent).toBe("P91");
  expect(screen.getByTestId("percentile-xg_p90-1").textContent).toBe("N/A");
  expect(container.textContent).not.toMatch(/\$P|format\(v|shots_p90/);
  expect(screen.getByText(/Unavailable: reference group/)).toBeTruthy();
  expect(
    screen.getByRole("list", { name: "Player colour legend" }).textContent,
  ).toContain(data.players[0].name);
});
it("keeps measured zero distinct from unavailable and prints precise chart values", () => {
  render(<ComparisonCharts data={data} />);
  expect(screen.getByTestId("shots_p90-chart-value-1").textContent).toBe(
    "1: 0.00",
  );
  expect(screen.getByTestId("xg_p90-chart-value-1").textContent).toBe(
    "1: N/A (unavailable)",
  );
  expect(screen.getByTestId("passes_p90-chart-value-1").textContent).toBe(
    "1: 42.21",
  );
});
