import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query";
import {
  Activity,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Check,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  Download,
  ExternalLink,
  FileText,
  Filter,
  GitCompareArrows,
  LayoutGrid,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Target,
  Users,
  X,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { Player, Match, Coverage, Comparison, SourceEvent } from "./types";
import { format } from "./types";
import "./style.css";

const client = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 60000, retry: 1, refetchOnWindowFocus: false },
  },
});
async function get<T>(path: string): Promise<T> {
  const response = await fetch("/api/" + path);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : "Request failed (" + response.status + ")",
    );
  }
  return response.json();
}
function useLocation() {
  const [search, setSearch] = useState(location.search);
  React.useEffect(() => {
    const update = () => setSearch(location.search);
    addEventListener("popstate", update);
    return () => removeEventListener("popstate", update);
  }, []);
  const params = new URLSearchParams(search);
  function update(values: Record<string, string | number | null>) {
    const next = new URLSearchParams(location.search);
    for (const [key, value] of Object.entries(values)) {
      if (value === null || value === "") next.delete(key);
      else next.set(key, String(value));
    }
    history.pushState({}, "", location.pathname + "?" + next.toString());
    setSearch(location.search);
  }
  return { params, update };
}
function useDebounce(value: string) {
  const [v, setV] = useState(value);
  React.useEffect(() => {
    const timer = setTimeout(() => setV(value), 250);
    return () => clearTimeout(timer);
  }, [value]);
  return v;
}
async function options(role: string) {
  const first = await get<{ items: Player[]; total: number }>(
    "players?size=100&role=" + encodeURIComponent(role) + "&sort=minutes",
  );
  const rest = await Promise.all(
    Array.from({ length: Math.ceil(first.total / 100) - 1 }, (_, i) =>
      get<{ items: Player[] }>(
        "players?size=100&role=" +
          encodeURIComponent(role) +
          "&sort=minutes&page=" +
          (i + 2),
      ),
    ),
  );
  return { items: [...first.items, ...rest.flatMap((p) => p.items)] };
}
function Status({
  loading,
  error,
}: {
  loading?: boolean;
  error?: Error | null;
}) {
  return loading ? (
    <div className="status" role="status">
      <Activity className="spin" />
      Loading verified data…
    </div>
  ) : error ? (
    <div className="status error" role="alert">
      {error.message}
      <button onClick={() => client.invalidateQueries()}>Retry</button>
    </div>
  ) : null;
}
function App() {
  const { params, update } = useLocation();
  const page = params.get("view") || "players";
  const coverage = useQuery({
    queryKey: ["coverage"],
    queryFn: () => get<Coverage>("coverage"),
  });
  const [selection, setSelection] = useState<number[]>(() =>
    [params.get("left"), params.get("right")].filter(Boolean).map(Number),
  );
  const [mobile, setMobile] = useState(false);
  const nav = (view: string) => {
    update({ view, profile: null, match: null });
    setMobile(false);
  };
  const select = (id: number) =>
    setSelection((old) =>
      old.includes(id)
        ? old.filter((x) => x !== id)
        : old.length < 2
          ? [...old, id]
          : [old[1], id],
    );
  return (
    <div className="app">
      <a className="skip" href="#main">
        Skip to content
      </a>
      <aside className={mobile ? "sidebar open" : "sidebar"}>
        <a className="brand" href="?view=players">
          <span className="brand-icon">
            <Target size={25} />
          </span>
          PitchScope<span className="brand-dot">.</span>
        </a>
        <div className="workspace">
          <span className="workspace-icon">PS</span>
          <div>
            Analysis workspace<small>Research project</small>
          </div>
          <span className="tag">V1</span>
        </div>
        <div className="nav-label">EXPLORE THE GAME</div>
        <nav aria-label="Main navigation">
          {[
            ["players", "Player explorer", Users],
            ["compare", "Comparison", GitCompareArrows],
            ["matches", "Match centre", LayoutGrid],
            ["method", "Methodology", ShieldCheck],
          ].map(([id, label, Icon]) => {
            const I = Icon as typeof Users;
            return (
              <button
                key={String(id)}
                onClick={() => nav(String(id))}
                className={page === id ? "nav-item active" : "nav-item"}
              >
                <I size={19} />
                {String(label)}
                {page === id && <span className="active-dot" />}
              </button>
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <div className="source-card">
            <span className="live-dot" />
            HISTORICAL DATA<h4>Football, backed by evidence.</h4>
            <p>Trace every observation to a match event.</p>
            <button onClick={() => nav("method")}>
              View sources <ArrowUpRight size={15} />
            </button>
          </div>
          <div className="attribution">
            <img src="/statsbomb.png" alt="StatsBomb" />
            <span>Open Data · Research</span>
          </div>
          <div className="profile-mini">
            <span>PS</span>
            <div>
              PitchScope<small>Football Intelligence</small>
            </div>
            <CircleHelp size={17} />
          </div>
        </div>
      </aside>
      <div className="body">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setMobile(!mobile)}
            aria-label="Open menu"
          >
            <SlidersHorizontal />
          </button>
          <span className="breadcrumb">
            Analysis workspace <ChevronRight size={13} />{" "}
            <strong>
              {(
                {
                  players: "Explorer",
                  compare: "Comparison",
                  matches: "Matchs",
                  method: "Methodology",
                } as Record<string, string>
              )[page] || "Explorer"}
            </strong>
          </span>
          <div className="top-meta">
            <span className="live-dot" />
            Pinned source <span className="separator" />{" "}
            <span className="avatar">PS</span>
          </div>
        </header>
        <main id="main">
          <Status loading={coverage.isLoading} error={coverage.error} />
          {coverage.data && coverage.data.imported_matches === 0 ? (
            <div className="empty">
              No matches imported. Run the local import command documented in
              the README.
            </div>
          ) : (
            coverage.data && (
              <>
                <div className="context-line">
                  <span className="eyebrow">FOOTBALL INTELLIGENCE</span>
                  <span className="coverage-badge">
                    <span className="live-dot" />
                    {coverage.data.imported_matches}/
                    {coverage.data.expected_matches} matches imported
                  </span>
                </div>
                {page === "players" ? (
                  params.get("profile") ? (
                    <Profile
                      id={Number(params.get("profile"))}
                      update={update}
                      select={select}
                      selection={selection}
                    />
                  ) : (
                    <Explorer
                      coverage={coverage.data}
                      params={params}
                      update={update}
                      select={select}
                      selection={selection}
                    />
                  )
                ) : page === "compare" ? (
                  <Compare params={params} update={update} />
                ) : page === "matches" ? (
                  <Matches params={params} update={update} />
                ) : (
                  <Method coverage={coverage.data} />
                )}
              </>
            )
          )}
          {selection.length > 0 && page === "players" && (
            <div className="selection-tray">
              <span>
                <GitCompareArrows size={18} />
                {selection.length}/2 players selected
              </span>
              <button className="ghost" onClick={() => setSelection([])}>
                Clear
              </button>
              <button
                className="primary"
                disabled={selection.length !== 2}
                onClick={() =>
                  update({
                    view: "compare",
                    left: selection[0],
                    right: selection[1],
                    profile: null,
                    role: params.get("role") || "Forward",
                  })
                }
              >
                Compare players <ArrowRight size={17} />
              </button>
            </div>
          )}
          <footer className="page-footer">
            <span>PitchScope · From numbers to the pitch.</span>
            <button onClick={() => nav("method")}>
              <img src="/statsbomb.png" alt="StatsBomb" /> Source: StatsBomb
              Open Data <ExternalLink size={12} />
            </button>
          </footer>
        </main>
      </div>
    </div>
  );
}
function Explorer({
  coverage,
  params,
  update,
  select,
  selection,
}: {
  coverage: Coverage;
  params: URLSearchParams;
  update: (v: Record<string, string | number | null>) => void;
  select: (id: number) => void;
  selection: number[];
}) {
  const q = params.get("q") || "";
  const team = params.get("team") || "";
  const role = params.get("role") || "";
  const min = params.get("min") || "0";
  const page = Number(params.get("page") || 1);
  const sort = params.get("sort") || "minutes";
  const desc = params.get("desc") !== "false";
  const searchq = useDebounce(q);
  const query = new URLSearchParams({
    q: searchq,
    min_minutes: min,
    sort,
    desc: String(desc),
    page: String(page),
    size: "15",
  });
  if (team) query.set("team", team);
  if (role) query.set("role", role);
  const result = useQuery({
    queryKey: ["players", query.toString()],
    queryFn: () => get<{ items: Player[]; total: number }>("players?" + query),
  });
  const change = (values: Record<string, string | number | null>) =>
    update({ ...values, page: null });
  const sorting = (key: string) =>
    change({ sort: key, desc: String(sort === key ? !desc : true) });
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>
            The right player. The right context<span>.</span>
          </h1>
          <p>Explore performances. Compare profiles. Verify the evidence.</p>
        </div>
        <button className="outline" onClick={() => update({ view: "method" })}>
          <FileText size={16} /> Data guide
        </button>
      </div>
      <section className="tournament-banner">
        <div className="tournament-icon">
          <Target size={31} />
        </div>
        <div>
          <div className="banner-eyebrow">ANALYSIS SCOPE</div>
          <h2>
            FIFA World Cup <span>2022</span>
          </h2>
          <p>
            International · Men ·{" "}
            {coverage.complete ? "Complete tournament" : "Partial coverage"}
          </p>
        </div>
        <div className="banner-detail">
          <span className="banner-check">
            <Check size={14} /> {coverage.synthetic ? "Synthetic test fixtures" : "Real data"}
          </span>
          <small>Stoppage time included · Shootouts excluded</small>
        </div>
        <div className="pitch-decoration" aria-hidden="true">
          <div />
          <span />
        </div>
      </section>
      <section className="stat-grid" aria-label="Dataset coverage">
        {[
          [
            String(coverage.players),
            "Players analysed",
            Users,
            "From imported match appearances",
          ],
          [
            String(coverage.teams.length),
            "Teams represented",
            ShieldCheck,
            "One competition, shared context",
          ],
          [
            `${coverage.imported_matches} / ${coverage.expected_matches}`,
            "Matches available",
            LayoutGrid,
            "Verifiable coverage, match by match",
          ],
          [
            coverage.events.toLocaleString("en-GB"),
            "Source events",
            Activity,
            "Traceable by StatsBomb event ID",
          ],
        ].map(([value, label, Icon, sub]) => {
          const I = Icon as typeof Users;
          return (
            <div className="stat-card" key={String(label)}>
              <div className="stat-label">
                {String(label)}
                <I size={17} />
              </div>
              <strong>{String(value)}</strong>
              <small>{String(sub)}</small>
            </div>
          );
        })}
      </section>
      <section className="panel explorer">
        <div className="panel-heading">
          <div>
            <h2>
              Player explorer{" "}
              <span className="count">{result.data?.total ?? "…"}</span>
            </h2>
            <p>Select two players to build your comparison.</p>
          </div>
          <span className="subtle">
            <SlidersHorizontal size={15} /> Share filters by URL
          </span>
        </div>
        <div className="filters">
          <label className="search">
            <Search size={18} />
            <input
              aria-label="Search players"
              placeholder="Search players…"
              value={q}
              onChange={(e) => change({ q: e.target.value })}
            />
            {q && (
              <button
                aria-label="Clear search"
                onClick={() => change({ q: null })}
              >
                <X size={14} />
              </button>
            )}
          </label>
          <label>
            <span>Team</span>
            <select
              aria-label="Team"
              value={team}
              onChange={(e) => change({ team: e.target.value })}
            >
              <option value="">All teams</option>
              {coverage.teams.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Role group</span>
            <select
              aria-label="Role group"
              value={role}
              onChange={(e) => change({ role: e.target.value })}
            >
              <option value="">All roles</option>
              {["Goalkeeper", "Defender", "Midfielder", "Forward"].map((r) => (
                <option key={r}>{r}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Minimum reliable minutes</span>
            <select
              aria-label="Minimum minutes"
              value={min}
              onChange={(e) => change({ min: e.target.value })}
            >
              {[0, 90, 180, 270, 450, 600].map((n) => (
                <option key={n} value={n}>
                  {n} minutes
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="table-meta">
          <span>
            <Filter size={13} /> {result.data?.total ?? "…"} players match your
            filters
          </span>
          <button
            className="text-button"
            onClick={() =>
              change({
                q: null,
                team: null,
                role: null,
                min: null,
                sort: null,
                desc: null,
              })
            }
          >
            Reset filters
          </button>
        </div>
        <Status loading={result.isLoading} error={result.error} />
        {result.data && (
          <>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th aria-label="Selection" />
                    <th>
                      <button onClick={() => sorting("name")}>PLAYER</button>
                    </th>
                    <th>ROLE(S)</th>
                    {[
                      ["minutes", "MINUTES"],
                      ["shots", "SHOTS"],
                      ["goals", "GOALS"],
                      ["xg", "xG"],
                      ["pass_pct", "PASS %"],
                    ].map(([key, label]) => (
                      <th key={key} className="numeric">
                        <button onClick={() => sorting(key)}>
                          {label}
                          {sort === key && (
                            <ArrowDown
                              size={12}
                              style={{
                                transform: desc ? "" : "rotate(180deg)",
                              }}
                            />
                          )}
                        </button>
                      </th>
                    ))}
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {result.data.items.map((p, i) => (
                    <tr
                      key={p.id}
                      className={selection.includes(p.id) ? "selected" : ""}
                    >
                      <td>
                        <input
                          type="checkbox"
                          aria-label={"Select " + p.name}
                          checked={selection.includes(p.id)}
                          onChange={() => select(p.id)}
                        />
                      </td>
                      <td>
                        <button
                          className="player-name"
                          onClick={() => update({ profile: p.id })}
                        >
                          <span className={"player-avatar tone-" + (i % 4)}>
                            {p.name
                              .split(" ")
                              .filter(Boolean)
                              .map((n) => n[0])
                              .slice(0, 2)
                              .join("")}
                          </span>
                          <span>
                            {p.name}
                            <small>
                              {p.teams.join(" · ")} · {p.appearances} matches
                            </small>
                          </span>
                        </button>
                      </td>
                      <td>
                        <span className="role-tag">{p.roles.join(" / ")}</span>
                      </td>
                      <td className="numeric">
                        {format(p.minutes, 0)}
                        {p.uncertain_appearances > 0 && (
                          <span title="Some playing times are uncertain">
                            {" "}
                            *
                          </span>
                        )}
                      </td>
                      <td className="numeric">{p.shots}</td>
                      <td className="numeric">
                        <strong>{p.goals}</strong>
                      </td>
                      <td className="numeric xg">{format(p.xg)}</td>
                      <td className="numeric">
                        {format(p.pass_pct, 1)}
                        <small className="unit"> %</small>
                      </td>
                      <td>
                        <button
                          className="icon-button"
                          aria-label={"Open profile for " + p.name}
                          onClick={() => update({ profile: p.id })}
                        >
                          <ArrowUpRight size={17} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {result.data.items.length === 0 && (
                <div className="empty">
                  <Search />
                  No players match these filters. Try a lower minutes threshold.
                </div>
              )}
            </div>
            <div className="pagination">
              <span>
                Page {page} of {Math.max(1, Math.ceil(result.data.total / 15))}{" "}
                · {result.data.total} players
              </span>
              <div>
                <button
                  aria-label="Previous page"
                  disabled={page === 1}
                  onClick={() => update({ page: page - 1 })}
                >
                  <ChevronLeft size={16} />
                </button>
                <span>{page}</span>
                <button
                  aria-label="Next page"
                  disabled={page * 15 >= result.data.total}
                  onClick={() => update({ page: page + 1 })}
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </>
        )}
        <div className="table-note">
          <CircleHelp size={15} />
          <span>
            xG supplied by StatsBomb. Minutes include stoppage time. Goals and
            shots exclude penalty shootouts.
          </span>
        </div>
      </section>
      <div className="insight-strip">
        <ShieldCheck size={21} />
        <div>
          <strong>One number cannot describe a player.</strong>
          <span>Context, role and sample size are part of the analysis.</span>
        </div>
        <button onClick={() => update({ view: "method" })}>
          Our methodology <ArrowRight size={15} />
        </button>
      </div>
    </>
  );
}
function Profile({
  id,
  update,
  select,
  selection,
}: {
  id: number;
  update: (v: Record<string, string | number | null>) => void;
  select: (id: number) => void;
  selection: number[];
}) {
  const r = useQuery({
    queryKey: ["profile", id],
    queryFn: () => get<{ player: Player; matches: Match[] }>("players/" + id),
  });
  return (
    <>
      <button className="back" onClick={() => update({ profile: null })}>
        <ArrowLeft size={15} /> Back to player explorer
      </button>
      <Status loading={r.isLoading} error={r.error} />
      {r.data && (
        <>
          <div className="page-heading">
            <div>
              <h1>{r.data.player.name}</h1>
              <p>
                {r.data.player.teams.join(" · ")} ·{" "}
                {r.data.player.roles.join(" / ")}
              </p>
            </div>
            <button className="primary" onClick={() => select(id)}>
              {selection.includes(id)
                ? "Remove from comparison"
                : "Select to compare"}
            </button>
          </div>
          <div className="stat-grid">
            {[
              ["minutes", "Reliable minutes"],
              ["shots", "Shots"],
              ["goals", "Goals"],
              ["xg", "StatsBomb xG"],
            ].map(([k, label]) => (
              <div className="stat-card" key={k}>
                <span>{label}</span>
                <strong>{format(r.data!.player[k as keyof Player])}</strong>
              </div>
            ))}
          </div>
          {r.data.player.rate_note && (
            <p className="warning">{r.data.player.rate_note}</p>
          )}
          <section className="panel">
            <div className="panel-heading">
              <h2>Appearances and match evidence</h2>
            </div>
            <MatchList matches={r.data.matches} update={update} />
          </section>
        </>
      )}
    </>
  );
}
function Compare({
  params,
  update,
}: {
  params: URLSearchParams;
  update: (v: Record<string, string | number | null>) => void;
}) {
  const role = params.get("role") || "Forward",
    min = params.get("min") || "180";
  const defaults: Record<string, number[]> = {
    Forward: [5503, 3009],
    Midfielder: [7797, 5487],
    Defender: [5507, 4445],
    Goalkeeper: [6909, 3099],
  };
  const left = Number(
      params.get("left") || (defaults[role] || defaults.Forward)[0],
    ),
    right = Number(
      params.get("right") || (defaults[role] || defaults.Forward)[1],
    );
  const list = useQuery({
    queryKey: ["compare-options", role],
    queryFn: () => options(role),
  });
  const query = new URLSearchParams({
    left: String(left),
    right: String(right),
    role,
    min_minutes: min,
  });
  const r = useQuery({
    queryKey: ["compare", query.toString()],
    queryFn: () => get<Comparison>("compare?" + query),
  });
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>
            Compare, with context<span>.</span>
          </h1>
          <p>An explicit reference group. Common units. No talent score.</p>
        </div>
        <a
          className={"primary " + (!r.data ? "disabled" : "")}
          aria-disabled={!r.data}
          href={r.data ? "/api/report.pdf?" + query : undefined}
        >
          <Download size={16} /> Export PDF report
        </a>
      </div>
      <div className="panel compare-filters">
        <label>
          Reference group
          <select
            aria-label="Comparison role"
            value={role}
            onChange={(e) =>
              update({ role: e.target.value, left: null, right: null })
            }
          >
            {["Goalkeeper", "Defender", "Midfielder", "Forward"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label>
          Minimum minutes
          <select
            aria-label="Comparison threshold"
            value={min}
            onChange={(e) => update({ min: e.target.value })}
          >
            {[0, 90, 180, 270, 450, 600].map((x) => (
              <option key={x} value={x}>
                {x} minutes
              </option>
            ))}
          </select>
        </label>
        {[
          ["left", left],
          ["right", right],
        ].map(([key, id], i) => (
          <label key={key}>
            Player {i + 1}
            <select
              aria-label={"Player " + (i + 1)}
              value={id}
              onChange={(e) => update({ [key]: e.target.value })}
            >
              {list.data?.items.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
      <Status
        loading={r.isLoading || list.isLoading}
        error={r.error || list.error}
      />
      {r.data && (
        <>
          <div className="population">
            <Users size={18} />
            <strong>{r.data.population.count} reference players</strong>
            <span>
              FIFA World Cup 2022 · {role} · ≥ {min} reliable minutes
            </span>
          </div>
          {r.data.warnings.map((w) => (
            <p className="warning" key={w}>
              {w}
            </p>
          ))}
          <div className="comparison-cards">
            {r.data.players.map((p, i) => (
              <div className={"panel comparison-player color-" + i} key={p.id}>
                <span className="eyebrow">PLAYER {i + 1}</span>
                <h2>{p.name}</h2>
                <p>
                  {p.teams.join(" · ")} · {p.appearances} matches ·{" "}
                  {format(p.minutes, 0)} reliable minutes
                </p>
                {p.rate_note && <p className="warning">{p.rate_note}</p>}
                <button
                  className="text-button"
                  onClick={() => update({ view: "players", profile: p.id })}
                >
                  Open profile <ArrowUpRight size={15} />
                </button>
              </div>
            ))}
          </div>
          <div className="compare-layout">
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>The numbers, side by side</h2>
                  <p>Totals from appearances in the selected role group.</p>
                </div>
              </div>
              <div className="table-scroll">
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th>METRIC / UNIT</th>
                      <th>PLAYER 1</th>
                      <th>PLAYER 2</th>
                    </tr>
                  </thead>
                  <tbody>
                    {r.data.metrics.map((m) => (
                      <tr key={m.key}>
                        <td>
                          {m.label}
                          <small className="unit"> {m.unit}</small>
                        </td>
                        {r.data!.players.map((p) => (
                          <td
                            className="numeric"
                            key={p.id}
                            data-testid={m.key + "-" + p.id}
                          >
                            {format(p[m.key])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
            <section className="panel charts">
              <h2>Volumes per 90 minutes</h2>
              <p>Reliable playing-time appearances only.</p>
              {[
                ["shots_p90", "Shots / 90 min"],
                ["xg_p90", "xG / 90 min"],
                ["passes_p90", "Passes / 90 min"],
              ].map(([key, label]) => (
                <div className="bar-section" key={key}>
                  <strong>{label}</strong>
                  <div className="bar-chart">
                    <ResponsiveContainer width="100%" height={112}>
                      <BarChart
                        data={r.data!.players.map((p, i) => ({
                          name: "Player " + (i + 1),
                          value: p[key as keyof Player],
                          fill: i === 0 ? "#2c7259" : "#668bc0",
                        }))}
                        layout="vertical"
                        margin={{ left: 0, right: 20, top: 8, bottom: 4 }}
                      >
                        <CartesianGrid
                          strokeDasharray="3 3"
                          horizontal={false}
                        />
                        <XAxis type="number" fontSize={10} />
                        <YAxis
                          type="category"
                          dataKey="name"
                          width={66}
                          fontSize={11}
                        />
                        <Tooltip formatter={(v) => format(v)} />
                        <Bar
                          dataKey="value"
                          radius={[0, 3, 3, 0]}
                          barSize={18}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ))}
              <p className="table-note">
                Scales differ between metrics; each chart shows its unit.
              </p>
              <h3>Volume percentiles</h3>
              {r.data.players.map((p) => (
                <p key={p.id}>
                  <strong>{p.name}</strong>
                  <br />
                  {Object.keys(p.percentiles || {}).length
                    ? Object.entries(p.percentiles!)
                        .map(
                          ([k, v]) =>
                            `${k.replace("_p90", " /90")} : $P{format(v, 0)}`,
                        )
                        .join(" · ")
                    : "Unavailable: reference group too small or player below the threshold."}
                </p>
              ))}
              <small>
                Empirical percentile with tied midranks. More volume does not
                imply greater quality.
              </small>
            </section>
          </div>
        </>
      )}
    </>
  );
}
function MatchList({
  matches,
  update,
}: {
  matches: Match[];
  update: (v: Record<string, string | number | null>) => void;
}) {
  return (
    <div className="match-list">
      {matches.map((m) => (
        <button
          key={m.id}
          onClick={() =>
            update({ view: "matches", match: m.id, profile: null })
          }
        >
          <span className="match-date">
            {m.date}
            <small>{m.stage}</small>
          </span>
          <strong>
            {m.home}{" "}
            <span className="score">
              {m.home_score} : {m.away_score}
            </span>{" "}
            {m.away}
          </strong>
          <span>
            {m.minutes !== undefined
              ? format(m.minutes, 1) + " min · " + m.role
              : format(m.duration, 1) + " elapsed min"}{" "}
            <ArrowUpRight size={16} />
          </span>
        </button>
      ))}
    </div>
  );
}
function Matches({
  params,
  update,
}: {
  params: URLSearchParams;
  update: (v: Record<string, string | number | null>) => void;
}) {
  const id = params.get("match");
  const r = useQuery({
    queryKey: ["matches"],
    queryFn: () => get<Match[]>("matches"),
  });
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>
            From numbers to the action<span>.</span>
          </h1>
          <p>
            Explore shots, the timeline and the attributes behind every event.
          </p>
        </div>
      </div>
      <Status loading={r.isLoading} error={r.error} />
      {id ? (
        <MatchView id={Number(id)} params={params} update={update} />
      ) : (
        r.data && (
          <section className="panel">
            <div className="panel-heading">
              <h2>
                Imported matches <span className="count">{r.data.length}</span>
              </h2>
            </div>
            <MatchList matches={r.data} update={update} />
          </section>
        )
      )}
    </>
  );
}
function MatchView({
  id,
  params,
  update,
}: {
  id: number;
  params: URLSearchParams;
  update: (v: Record<string, string | number | null>) => void;
}) {
  const [selected, setSelected] = useState<SourceEvent | null>(null);
  const team = params.get("event_team") || "",
    player = params.get("event_player") || "";
  const all = useQuery({
    queryKey: ["shots", id],
    queryFn: () =>
      get<{
        match: Match;
        items: SourceEvent[];
        total: number;
        summary: {
          team_id: number;
          team: string;
          shots: number;
          xg: number | null;
        }[];
      }>("matches/" + id + "/events?kind=Shot&size=500"),
  });
  const actionsPage = Number(params.get("event_page") || 1);
  const actions = useQuery({
    queryKey: ["actions", id, actionsPage],
    queryFn: () =>
      get<{ items: SourceEvent[]; total: number }>(
        "matches/" + id + "/events?kind=all&size=500&page=" + actionsPage,
      ),
  });
  const shots =
    all.data?.items.filter(
      (e) =>
        (!team || e.team_id === Number(team)) &&
        (!player || e.player_id === Number(player)),
    ) || [];
  const players = [
    ...new Map(
      all.data?.items
        .filter((e) => e.player_id)
        .map((e) => [
          e.player_id,
          { id: e.player_id, name: e.attributes.player?.name },
        ]),
    ).values(),
  ];
  const m = all.data?.match;
  return (
    <>
      <button
        className="back"
        onClick={() =>
          update({
            match: null,
            event_team: null,
            event_player: null,
            event_page: null,
          })
        }
      >
        <ArrowLeft size={15} /> All matches
      </button>
      <Status loading={all.isLoading} error={all.error} />
      {m && (
        <>
          <div className="match-hero panel">
            <span className="eyebrow">
              {m.stage} · {m.date}
            </span>
            <h2>
              {m.home}{" "}
              <span className="big-score">
                {m.home_score} - {m.away_score}
              </span>{" "}
              {m.away}
            </h2>
            <p>
              {format(m.duration, 2)} elapsed minutes excluding breaks · Score
              excludes shootouts
            </p>
            <div className="match-summary">
              {all.data?.summary?.map((s) => (
                <span key={s.team_id}>
                  {s.team} : <strong>{format(s.xg)} xG</strong> · {s.shots}{" "}
                  shots
                </span>
              ))}
            </div>
          </div>
          <div className="filters panel">
            <label>
              Team
              <select
                aria-label="Match team"
                value={team}
                onChange={(e) => {
                  setSelected(null);
                  update({ event_team: e.target.value });
                }}
              >
                <option value="">Both teams</option>
                <option value={m.home_id}>{m.home}</option>
                <option value={m.away_id}>{m.away}</option>
              </select>
            </label>
            <label>
              Shooter
              <select
                aria-label="Match player"
                value={player}
                onChange={(e) => {
                  setSelected(null);
                  update({ event_player: e.target.value });
                }}
              >
                <option value="">All shooters</option>
                {players.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </label>
            <span>
              {shots.filter((e) => e.period <= 4).length} non-shootout shots ·{" "}
              {shots.filter((e) => e.period === 5).length} shootout shots
            </span>
          </div>
          <div className="match-layout">
            <section className="panel pitch-panel">
              <h2>Shot map</h2>
              <p>Size = StatsBomb xG · Goal: filled dot · Shootouts hidden</p>
              <svg
                className="pitch"
                viewBox="-4 -4 128 88"
                role="group"
                aria-label="StatsBomb 120 by 80 pitch, shooting to the right"
              >
                <rect
                  x="0"
                  y="0"
                  width="120"
                  height="80"
                  rx="1"
                  fill="#e6eee5"
                />
                <g stroke="#94aa95" strokeWidth=".4" fill="none">
                  <rect x="0" y="0" width="120" height="80" />
                  <path d="M60 0V80" />
                  <circle cx="60" cy="40" r="10" />
                  <path d="M0 18H18V62H0M120 18H102V62H120M0 30H6V50H0M120 30H114V50H120" />
                  <circle cx="12" cy="40" r=".7" />
                  <circle cx="108" cy="40" r=".7" />
                </g>
                {shots
                  .filter((e) => e.period <= 4 && e.x !== null && e.y !== null)
                  .map((e) => (
                    <circle
                      key={e.id}
                      cx={e.x!}
                      cy={e.y!}
                      r={
                        1.15 +
                        4 * Math.sqrt(e.attributes.shot?.statsbomb_xg || 0)
                      }
                      fill={
                        e.attributes.shot?.outcome.name === "Goal"
                          ? e.team_id === m.home_id
                            ? "#236342"
                            : "#597db5"
                          : "#ffffff"
                      }
                      stroke={e.team_id === m.home_id ? "#236342" : "#597db5"}
                      strokeWidth={selected?.id === e.id ? 1.2 : 0.55}
                      tabIndex={0}
                      role="button"
                      aria-label={`${e.attributes.player?.name}, ${e.minute} minute, ${e.attributes.shot?.outcome.name}`}
                      onClick={() => setSelected(e)}
                      onKeyDown={(ev) => {
                        if (ev.key === "Enter" || ev.key === " ") {
                          ev.preventDefault();
                          setSelected(e);
                        }
                      }}
                    >
                      <title>
                        {e.attributes.player?.name} · {e.minute}' · xG{" "}
                        {format(e.attributes.shot?.statsbomb_xg)}
                      </title>
                    </circle>
                  ))}
              </svg>
              <div className="pitch-legend">
                <span>
                  <i className="green-dot" />
                  {m.home}
                </span>
                <span>
                  <i className="blue-dot" />
                  {m.away}
                </span>
                <span>Attack → · coordinates in StatsBomb units</span>
              </div>
            </section>
            <section className="panel event-detail">
              <h2>Event inspector</h2>
              {selected ? (
                <>
                  <span className="role-tag">
                    {selected.kind} · P{selected.period} · {selected.minute}:
                    {String(selected.second).padStart(2, "0")}
                  </span>
                  <h3>{selected.attributes.player?.name || "Team event"}</h3>
                  <p>{selected.attributes.team.name}</p>
                  {selected.attributes.shot && (
                    <div className="event-numbers">
                      <div>
                        StatsBomb xG
                        <strong>
                          {format(selected.attributes.shot.statsbomb_xg, 4)}
                        </strong>
                      </div>
                      <div>
                        Outcome
                        <strong>{selected.attributes.shot.outcome.name}</strong>
                      </div>
                    </div>
                  )}
                  <h4>Source event ID</h4>
                  <code>{selected.id}</code>
                  <a
                    className="text-button"
                    href={`https://github.com/hudl/open-data/blob/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/data/events/${id}.json`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Open source file <ExternalLink size={13} />
                  </a>
                  <details>
                    <summary>Available attributes (JSON)</summary>
                    <pre>{JSON.stringify(selected.attributes, null, 2)}</pre>
                  </details>
                </>
              ) : (
                <div className="empty">
                  <Target />
                  Select a shot or action to inspect its source.
                </div>
              )}
            </section>
          </div>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>Shots and shootout</h2>
                <p>
                  Period 5 shots remain available separately and are excluded
                  from aggregates.
                </p>
              </div>
            </div>
            <div className="timeline">
              {shots.map((e) => (
                <button
                  key={e.id}
                  onClick={() => setSelected(e)}
                  className={selected?.id === e.id ? "active" : ""}
                >
                  <time>
                    {e.minute}'<small>P{e.period}</small>
                  </time>
                  <div>
                    <strong>{e.attributes.player?.name}</strong>
                    <small>
                      {e.attributes.team.name} ·{" "}
                      {e.attributes.shot?.outcome.name} ·{" "}
                      {e.period === 5
                        ? "Shootout excluded"
                        : "xG " + format(e.attributes.shot?.statsbomb_xg)}
                    </small>
                  </div>
                  <ArrowUpRight size={15} />
                </button>
              ))}
            </div>
            {shots.length === 0 && (
              <p className="empty">No shots match these filters.</p>
            )}
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>Action timeline</h2>
                <p>Source events in order · 500 actions per page.</p>
              </div>
            </div>
            <Status loading={actions.isLoading} error={actions.error} />
            <div className="action-scroll timeline">
              {actions.data?.items
                .filter(
                  (e) =>
                    (!team || e.team_id === Number(team)) &&
                    (!player || e.player_id === Number(player)),
                )
                .map((e) => (
                  <button key={e.id} onClick={() => setSelected(e)}>
                    <time>
                      {e.minute}'<small>P{e.period}</small>
                    </time>
                    <div>
                      <strong>
                        {e.kind} ·{" "}
                        {e.attributes.player?.name || e.attributes.team.name}
                      </strong>
                      <small>Event {e.index}</small>
                    </div>
                    <ArrowUpRight size={14} />
                  </button>
                ))}
            </div>
            <div className="pagination">
              <span>
                {actions.data?.total} events · Page {actionsPage}
              </span>
              <div>
                <button
                  disabled={actionsPage === 1}
                  onClick={() => update({ event_page: actionsPage - 1 })}
                >
                  Previous
                </button>
                <button
                  disabled={actionsPage * 500 >= (actions.data?.total || 0)}
                  onClick={() => update({ event_page: actionsPage + 1 })}
                >
                  Next
                </button>
              </div>
            </div>
          </section>
        </>
      )}
    </>
  );
}
function Method({ coverage: c }: { coverage: Coverage }) {
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>
            Results you can verify<span>.</span>
          </h1>
          <p>Coverage, conventions and limitations are part of the result.</p>
        </div>
      </div>
      <div className="method-grid">
        <section className="panel prose">
          <span className="eyebrow">01 / COVERAGE</span>
          <h2>One tournament, one context</h2>
          <p>
            FIFA World Cup 2022:{" "}
            <strong>
              {c.imported_matches}/{c.expected_matches} matches
            </strong>
            .{" "}
            {c.complete
              ? "The complete tournament has been imported."
              : "Figures cover imported matches only."}{" "}
            {c.players} players with appearances,{" "}
            {c.events.toLocaleString("en-GB")} events.
          </p>
          <p>
            {c.uncertain_appearances} appearances have uncertain playing time.
            Browsing requires no provider downloads.
          </p>
          <h3>Pinned provenance</h3>
          <code>{c.source_commit}</code>
          <p>
            SHA-256 hashes and import dates are available in the inventory
            below. Transformations:{" "}
            {Array.from(
              new Set(c.imports?.map((r) => r.transform_version)),
            ).join(", ")}
            .
          </p>
        </section>
        <section className="panel prose">
          <span className="eyebrow">02 / PLAYING TIME</span>
          <h2>Reconstructed minutes</h2>
          <p>
            Elapsed clocks from periods 1–4 through Half End events. Stoppage
            time and extra time are included; breaks and shootouts are excluded.
            Temporary absences are deducted.
          </p>
          <p>
            Presence is reconstructed from Starting XI, Substitution, Player
            Off/On and Red Card / Second Yellow events. Missing period ends or
            inconsistent entries make minutes unavailable. Missing time is never
            replaced with 90 minutes.
          </p>
          <p>
            The role group comes from the first position in each appearance's
            StatsBomb lineup, falling back to the entry-event position. Later
            tactical changes do not reclassify that appearance.
          </p>
        </section>
        <section className="panel prose">
          <span className="eyebrow">03 / METRICS</span>
          <h2>Explicit definitions</h2>
          <p>
            Shot = Shot event outside period 5. Goal = Shot with outcome Goal.
            Own goals are not credited to a shooter; the match score remains the
            provider's score.
          </p>
          <p>
            xG is the sum of supplied statsbomb_xg values, including in-match
            penalties. Shootout attempts are excluded from aggregate shots,
            goals and xG. A missing xG makes the corresponding total
            unavailable.
          </p>
          <p>
            A completed pass is a Pass event without an outcome attribute. All
            Pass events count as attempts, including crosses and set pieces.
            Completion = total completions / total attempts. A zero denominator
            gives N/A.
          </p>
        </section>
        <section className="panel prose">
          <span className="eyebrow">04 / COMPARISON</span>
          <h2>Volume, with its limits</h2>
          <p>
            Per 90 = 90 × total metric from reliable appearances / their total
            minutes. Raw totals retain uncertain appearances; per-90 rates
            exclude them.
          </p>
          <p>
            The reference group specifies tournament, role group and minimum
            minutes. Its figures cover appearances in that role. Empirical
            percentiles use tied midranks when at least 20 reliable values are
            available. They measure volume, never talent.
          </p>
          <p>
            A short tournament provides small samples and different opponents.
            No tracking, distance, speed, ML model or prediction of future
            potential is inferred.
          </p>
        </section>
        <section className="panel prose">
          <span className="eyebrow">05 / MAPS</span>
          <h2>The StatsBomb coordinate system</h2>
          <p>
            The pitch measures 120 × 80 units, with the origin at the top left.
            Positions are already oriented by the team in possession. Shots are
            plotted towards the goal on the right, without reconstructed
            trajectories. Marker radius depends on the square root of supplied
            xG.
          </p>
          <p>
            Points represent discrete events, not continuous player positions.
          </p>
        </section>
        <section className="panel prose">
          <span className="eyebrow">06 / RIGHTS AND SOURCE</span>
          <h2>StatsBomb Open Data</h2>
          <img className="method-logo" src="/statsbomb.png" alt="StatsBomb" />
          <p>
            Local research analysis using the official repository. Original code
            is MIT licensed; data and logo retain their StatsBomb rights.
          </p>
          <p>
            The Public Data User Agreement governs redistribution and commercial
            use. The raw cache is excluded from Git. Public distribution must
            comply with the provider's terms.
          </p>
          <a
            href="https://github.com/hudl/open-data"
            target="_blank"
            rel="noreferrer"
          >
            Official repository and terms ↗
          </a>
        </section>
      </div>
      <section className="panel">
        <div className="panel-heading">
          <h2>Import inventory and hashes</h2>
        </div>
        <div className="inventory">
          {c.imports?.map((r) => (
            <details key={r.match_id}>
              <summary>
                Match {r.match_id} · imported{" "}
                {new Date(r.imported_at).toLocaleString("en-GB", {
                  timeZone: "UTC",
                })}{" "}
                UTC · v{r.transform_version}
              </summary>
              {Object.entries(r.hashes).map(([path, hash]) => (
                <p key={path}>
                  {path}
                  <code>{hash}</code>
                </p>
              ))}
            </details>
          ))}
        </div>
      </section>
    </>
  );
}
const root = createRoot(document.getElementById("root")!);
root.render(
  <React.StrictMode>
    <QueryClientProvider client={client}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
if (import.meta.hot) import.meta.hot.dispose(() => root.unmount());
