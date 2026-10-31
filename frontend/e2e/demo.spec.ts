import { test, expect } from "@playwright/test";
import { writeFileSync } from "node:fs";

// This optional real-data demonstration records the actual app, never mocked responses.
if (process.env.RECORD_VIDEO === "true") {
  test.describe("recruiter demonstration", () => {
    test.use({ video: { mode: "on", size: { width: 1440, height: 1050 } } });
    test("90-second real search, comparison, evidence and export", async ({
      page,
      request,
    }) => {
      test.setTimeout(150000);
      const coverage = await (await request.get("/api/coverage")).json();
      expect(coverage.complete).toBe(true);
      expect(coverage.synthetic).toBe(false);
      const started = Date.now();
      const cues: { start: number; text: string }[] = [];
      const cue = (text: string) =>
        cues.push({ start: (Date.now() - started) / 1000, text });
      const until = async (seconds: number) => {
        const left = seconds * 1000 - (Date.now() - started);
        if (left > 0) await page.waitForTimeout(left);
      };
      cue(
        "PitchScope: a real, local football analytics application. StatsBomb Open Data; World Cup 2022.",
      );
      await page.goto("/");
      await expect(
        page.getByRole("textbox", { name: "Search players" }),
      ).toBeVisible();
      await until(5);
      await page
        .getByRole("combobox", { name: "Role group", exact: true })
        .selectOption("Forward");
      await page
        .getByRole("combobox", { name: "Minimum minutes", exact: true })
        .selectOption("180");
      cue(
        "Search within an explicit role and minutes threshold. Raw provider files stay outside the repository.",
      );
      await page.getByRole("textbox", { name: "Search players" }).fill("Messi");
      await expect(
        page.getByRole("button", {
          name: "Open profile for Lionel Andrés Messi Cuccittini",
          exact: true,
        }),
      ).toBeVisible();
      await until(13);
      await page
        .getByRole("button", {
          name: "Open profile for Lionel Andrés Messi Cuccittini",
          exact: true,
        })
        .click();
      cue(
        "Open the player profile and inspect the appearances behind the totals.",
      );
      await expect(
        page.getByRole("heading", { name: "Appearances and match evidence" }),
      ).toBeVisible();
      await until(23);
      await page
        .getByRole("button", { name: "Select to compare", exact: true })
        .click();
      await page
        .getByRole("button", { name: "Back to player explorer" })
        .click();
      await page
        .getByRole("textbox", { name: "Search players" })
        .fill("Mbappé");
      await page
        .getByRole("checkbox", {
          name: "Select Kylian Mbappé Lottin",
          exact: true,
        })
        .check();
      await page
        .getByRole("button", { name: "Compare players", exact: true })
        .click();
      await expect(
        page.getByText("69 reference players", { exact: true }),
      ).toBeVisible();
      cue(
        "Compare Messi and Mbappé against 69 forwards with at least 180 reliable minutes. Volume is not talent.",
      );
      await until(35);
      await page
        .getByRole("heading", { name: "Volumes per 90 minutes" })
        .scrollIntoViewIfNeeded();
      await expect(page.getByTestId("percentile-xg_p90-5503")).toHaveText(
        "P98",
      );
      cue(
        "Read visible bars and numeric percentiles. StatsBomb supplies xG; this project did not train that model.",
      );
      await until(49);
      await page
        .getByRole("heading", { name: "Volume percentiles" })
        .scrollIntoViewIfNeeded();
      await until(59);
      await page.goto("/?view=matches&match=3869685");
      await expect(
        page.getByRole("heading", { name: "Shot map", exact: true }),
      ).toBeVisible();
      cue(
        "Inspect Argentina-France. Match shots exclude the shootout; event IDs link observations to their sources.",
      );
      const shot = page.getByRole("button", { name: /minute,/ }).first();
      await shot.press("Enter");
      await page
        .getByRole("heading", { name: "Source event ID" })
        .scrollIntoViewIfNeeded();
      await until(74);
      await page.goto(
        "/?view=compare&left=5503&right=3009&role=Forward&min=180",
      );
      await expect(page.getByTestId("xg-5503")).toHaveText("6.03");
      cue(
        "Export a backend-generated PDF with the same services and values: xG 6.03 and 4.23.",
      );
      await until(82);
      const [download] = await Promise.all([
        page.waitForEvent("download"),
        page.getByRole("link", { name: "Export PDF report" }).click(),
      ]);
      await download.saveAs("test-results/demo-comparison.pdf");
      cue(
        "Reproducible historical analysis, with documented minutes, provenance and limitations. No live hosting is claimed.",
      );
      await until(92);
      const end = (Date.now() - started) / 1000;
      const timestamp = (s: number) =>
        new Date(s * 1000).toISOString().slice(11, 23);
      writeFileSync(
        "test-results/pitchscope-demo.vtt",
        "WEBVTT\n\n" +
          cues
            .map(
              (c, i) =>
                `${timestamp(c.start)} --> ${timestamp(cues[i + 1]?.start ?? end)}\n${c.text}\n`,
            )
            .join("\n"),
      );
      writeFileSync(
        "test-results/demo-timing.json",
        JSON.stringify({ seconds: end, cues }, null, 2),
      );
    });
  });
}
