# Statistical conventions — transformation 1.3.0

## Scope and provenance

One complete historical tournament: FIFA World Cup 2022, competition 43 / season
106, 64 expected matches. No totals are extrapolated to unimported fixtures.
`data/source-lock.json` pins the commit, match IDs and SHA-256 hashes of 130 JSON
files. Each import records the match-list/event/lineup hashes, UTC timestamp,
transformation version and lineup metadata. Each event retains its original ID,
index, match, team, player, period, coordinates and attributes in JSONB.
Migrations 001 and 002 bootstrap an empty database without manual SQL.

## Playing time and roles

Elapsed time is the sum of Half End clocks for periods 1–2, plus periods 3–4
for extra time. Two team-specific Half End events represent the same instant;
an inconsistency greater than one second makes time uncertain. Periods must
be [1,2] or [1,2,3,4]. Stoppage time is included; breaks and period 5 are not.
These are elapsed minutes, not nominal 90/120-minute totals.

Starting XI opens an appearance. Substitution closes the outgoing player and
opens the replacement at the period clock plus preceding period durations.
Red Card or Second Yellow in Foul Committed or Bad Behaviour closes presence.
A card to an unused substitute does not create an appearance. Player Off/On
subtract temporary absences; a substitution during an absence closes it.
Missing period ends or entries, inconsistent returns and actions outside
reconstructed presence produce unavailable minutes with a reason. Never impute 90.

The role group uses the first position in each match's provider lineup. If absent,
it falls back to the entry event's position. Groups are Goalkeeper, Defender,
Midfielder and Forward. The role remains constant for the appearance; tactical
changes do not split its counters. Team and role belong to appearances, not to
one global player record. Version 1.2.0 changes role labels to English without
changing event counts or playing-time conventions. Version 1.3.0 replaces the catch-all
Forward fallback with explicit provider position names. Missing/unrecognized positions
are stored as Unknown, remain visible in overall statistics and are excluded from
the four named-role comparison cohorts. No playing time is invented or removed
because a role is unknown. An explicit atomic rebuild is required.

## Counts and denominators

- Appearance: participation attested by Starting XI or an entry/substitution.
- Shot: a Shot event in periods 1–4.
- Goal: Shot with outcome Goal; in-match penalties included.
- Own goal: a distinct event, not a goal credited to the shooter. The match
  score remains the provider's score, excluding the shootout.
- xG: sum of provider `shot.statsbomb_xg`. No model was trained. Missing xG
  makes the corresponding total unavailable rather than zero.
- Passes: all Pass events, including crosses and set pieces. Completion
  means no `pass.outcome` attribute. Completion rate = 100 × total completed /
  total attempted, never an average of match percentages. Zero attempts => N/A.
- Shootout: period 5 remains inspectable but contributes no shots, goals, xG,
  passes or minutes to aggregates. In-match penalties are treated differently.
- Per 90: 90 × metric total from reliable appearances / their total minutes.
  Raw totals retain uncertain appearances, identified separately. Unknown or
  zero minutes => N/A. Missing reliable xG also makes xG/90 unavailable.

## Reference group and limitations

A comparison specifies tournament/season, role group and minimum reliable minutes.
It aggregates appearances in that role; the explorer's team filter is not applied
to the reference group. Its size is visible. Fewer than 20 reliable values => no
percentile. Otherwise empirical percentile = 100 × (strictly lower values + half
the tied values) / non-missing population. A player below the threshold retains
figures and a warning, but receives no rank. Samples below 450 minutes are flagged.
No global talent score, tactical narrative or future-potential prediction.

StatsBomb coordinates use a 120 × 80 pitch, origin at the top left. Shot locations
are already oriented towards the right. Marker radius = 1.15 + 4√xG in graphical
units, with a minimum visible marker. Events are discrete observations, not
tracking or reconstructed trajectories. Volumes are not adjusted for possession,
opponent strength or score state, and do not establish causal or scouting quality.
