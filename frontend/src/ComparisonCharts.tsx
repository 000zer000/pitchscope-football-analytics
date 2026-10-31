import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  LabelList,
} from "recharts";
import type { Comparison } from "./types";
import { format } from "./types";

export function ComparisonCharts({ data }: { data: Comparison }) {
  const keys = ["shots_p90", "xg_p90", "passes_p90"] as const;
  const labels = new Map(data.metrics.map((m) => [m.key, m.label]));
  return (
    <section className="panel charts">
      <h2>Volumes per 90 minutes</h2>
      <p>Reliable playing-time appearances only. xG supplied by StatsBomb.</p>
      <ul className="chart-legend" aria-label="Player colour legend">
        {data.players.map((p, i) => (
          <li key={p.id}>
            <span className={i === 0 ? "green-dot" : "blue-dot"} />
            <span>
              {i + 1}. {p.name}
            </span>
          </li>
        ))}
      </ul>
      {keys.map((key) => (
        <div className="bar-section" key={key} data-testid={"chart-" + key}>
          <h3>{labels.get(key)} minutes</h3>
          <div
            className="bar-chart"
            aria-label={labels.get(key) + " comparison"}
          >
            <ResponsiveContainer width="100%" height={112} minWidth={0}>
              <BarChart
                data={data.players.map((p, i) => ({
                  name: String(i + 1),
                  value: p[key],
                  fill: i === 0 ? "#2c7259" : "#668bc0",
                }))}
                layout="vertical"
                margin={{ left: 0, right: 44, top: 8, bottom: 4 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" domain={[0, "auto"]} fontSize={10} />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={18}
                  fontSize={11}
                />
                <Tooltip formatter={(v) => format(v)} />
                <Bar
                  dataKey="value"
                  radius={[0, 3, 3, 0]}
                  barSize={18}
                  isAnimationActive={false}
                >
                  <LabelList
                    dataKey="value"
                    position="right"
                    formatter={(v) => format(v)}
                    fontSize={10}
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-values">
            {data.players.map((p, i) => (
              <span key={p.id} data-testid={key + "-chart-value-" + p.id}>
                {i + 1}: {format(p[key])}
                {p[key] === null ? " (unavailable)" : ""}
              </span>
            ))}
          </div>
        </div>
      ))}
      <p className="table-note">
        Scales differ between metrics; each chart shows its unit. Zero has no
        bar; N/A means unavailable.
      </p>
      <h3>Volume percentiles</h3>
      {data.players.map((p) => (
        <div className="percentile-player" key={p.id}>
          <strong>{p.name}</strong>
          {Object.keys(p.percentiles || {}).length ? (
            <dl>
              {keys.map((key) => (
                <div key={key}>
                  <dt>{labels.get(key)}</dt>
                  <dd data-testid={"percentile-" + key + "-" + p.id}>
                    {typeof p.percentiles?.[key] === "number"
                      ? `P${format(p.percentiles[key], 0)}`
                      : "N/A"}
                  </dd>
                </div>
              ))}
            </dl>
          ) : (
            <p>
              Unavailable: reference group too small or player below the
              threshold.
            </p>
          )}
        </div>
      ))}
      <small>
        Empirical percentile with tied midranks. More volume does not imply
        greater quality.
      </small>
    </section>
  );
}
