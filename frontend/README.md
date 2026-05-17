# Sentinel Dashboard — wired to Security-Analyst backend

Tactical incident triage UI (TanStack Start + React 19 + Tailwind v4) wired to
the Python backend in [warut-cha/Security-Analyst](https://github.com/warut-cha/Security-Analyst)
on the **`uitest`** branch.

## What it talks to

| UI action / signal           | Backend                                            |
| ---------------------------- | -------------------------------------------------- |
| Initial incident list        | `GET  /api/incidents`                              |
| Live updates (new findings,  | `WS   /ws` — messages: `new_incident`,             |
| new incidents, BOB results)  | `attack_detected`, `bob_analysis`, `scan_completed`, `reset` |
| Sidebar **+ Scan** button    | `POST /api/scan` (paths=`["."]`, use_bob=true)     |
| Sidebar **Simulate** button  | `POST /api/simulate-attack`                        |

The wire format is mirrored in `src/lib/api/types.ts` and mapped into the UI's
`Incident` shape by `src/lib/api/adapter.ts`. Replace either file to change the
contract — nothing else needs to know.

## Run

```bash
cp .env.example .env          # edit if your backend isn't on :8000
bun install
bun run dev
```

If the backend is unreachable, the UI falls back to bundled mock incidents so
the dashboard never goes blank; the sidebar pill flips to `Sentinel · offline`
and auto-reconnects with capped backoff.

## Where things live

- `src/routes/index.tsx` — page composition
- `src/components/dashboard/*` — TopBar, IncidentSidebar, IncidentMainStage,
  AttackPath, BobFix, EvidenceTable, BobInspector (ambient mascot),
  AnnotateOverlay (click any region to highlight with L-brackets)
- `src/lib/api/useLiveIncidents.ts` — REST seed + WS subscription + reconnect
- `src/lib/incidents-data.ts` — UI types + mock seed
- `src/styles.css` — design tokens (oklch); customise theme here
