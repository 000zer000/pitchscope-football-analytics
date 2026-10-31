# Real ~92-second recruiter demonstration

The v1.1.0 release contains a genuine Chromium recording of the running app,
with burned-in English captions and an optional WebVTT track. It uses the pinned
complete real tournament, not CI fixtures. There is no voice-over and no public
application hosting claim. No raw JSON disclosure is expanded in the recording.

- 0-5 s: real player explorer and coverage.
- 5-13 s: Forward / 180-minute filter and Messi search.
- 13-23 s: profile and appearances behind the totals.
- 23-35 s: select Messi, search/select Mbappé and compare 69 reference players.
- 35-59 s: visible per-90 bars, numeric percentiles and the volume/quality caveat.
- 59-74 s: Argentina-France shot map and selected source event metadata.
- 74-82 s: return to the comparison and the matching xG values.
- 82-92 s: actual PDF download, provenance and limitations captions.

Actual cue timings are recorded with the video, rather than guessed from the
script. Each stage waits for real controls and verified data. The test fails if
source coverage, source event, numeric percentile or PDF download is missing.

```bash
# Start the real app first. Chromium must be installed.
cd frontend
RECORD_VIDEO=true npm run e2e -- demo.spec.ts
```

`frontend/e2e/demo.spec.ts` produces the WebM, captions and timing JSON.
The real-data CI run renders the captioned MP4 with FFmpeg and checks its duration
with ffprobe (88-115 s bound). Default required CI uses synthetic fixtures and
runs regression tests without creating a misleading real-data demo.

Direct comparison: `/?view=compare&left=5503&right=3009&role=Forward&min=180`.
Final: `/?view=matches&match=3869685`.
