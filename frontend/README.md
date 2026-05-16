# Bob Sentinel Frontend Dashboard

React + TypeScript + Vite dashboard for Bob Sentinel - Autonomous DevSecOps Assistant.

## Features

- 🛡️ **Overview Dashboard** - Real-time security metrics and incident summary
- 🔍 **Findings Table** - Detailed view of all security findings from Rust scanner
- 🎯 **Incident Analysis** - Correlated incidents with confidence scoring
- 🕸️ **Attack Path Visualization** - Interactive graph showing attack chains
- 🤖 **IBM Bob AI Analysis** - Advanced reasoning and remediation recommendations
- 📊 **Incident Reports** - Markdown-formatted security reports
- 🧠 **AI Memory Viewer** - Prevention rules and learned patterns
- 🔧 **Generated Security Tests** - Automated test generation
- 📝 **PR Draft Generator** - Ready-to-use pull request templates

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **ReactFlow** - Attack path visualization
- **Lucide React** - Icon library
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd frontend
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          # API client with mock data
│   │   └── types.ts            # TypeScript type definitions
│   ├── components/
│   │   ├── OverviewCards.tsx   # Dashboard metrics cards
│   │   ├── FindingsTable.tsx   # Security findings table
│   │   ├── IncidentDetail.tsx  # Incident details view
│   │   ├── AttackPathGraph.tsx # Attack path visualization
│   │   ├── BobAnalysis.tsx     # Bob AI analysis display
│   │   ├── ReportViewer.tsx    # Incident report viewer
│   │   ├── MemoryViewer.tsx    # AI memory patterns
│   │   └── PRDraftViewer.tsx   # PR draft display
│   ├── pages/
│   │   └── DashboardPage.tsx   # Main dashboard page
│   ├── App.tsx                 # Root component
│   └── main.tsx                # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```

## Mock Data Mode

By default, the dashboard runs in **mock data mode** with pre-populated security incidents. This allows you to explore the UI without a backend.

To switch to backend mode, edit `src/api/client.ts`:

```typescript
const USE_MOCK_DATA = false; // Change to false
```

## API Integration

When connected to the backend, the dashboard expects these endpoints:

- `GET /api/findings` - List all security findings
- `GET /api/incidents` - List all correlated incidents
- `GET /api/incidents/:id` - Get incident details
- `POST /api/incidents/:id/analyze-with-bob` - Trigger Bob AI analysis

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Demo Scenario

The mock data demonstrates a critical security incident:

1. **Hardcoded API Key** detected in legacy code
2. **Abandoned Export API** still accessible
3. **Suspicious Requests** to the old endpoint
4. **Database Read Spike** on users table
5. **Possible Data Leak** identified

Bob AI correlates these signals and provides:
- Attack explanation and confidence assessment
- Recommended fixes (immediate, code, API, config)
- Generated security tests
- Incident report in Markdown
- AI memory for future prevention
- PR draft ready for review

## TypeScript Types

All types match the backend JSON contracts:

- `Finding` - Individual security finding
- `Incident` - Correlated security incident
- `AttackPath` - Graph nodes and edges
- `BobOutput` - AI analysis results
- `AIMemory` - Prevention rules
- `PRDraft` - Pull request template

## Styling

The dashboard uses inline styles with a dark theme inspired by GitHub's design system:

- Background: `#0f1419`
- Cards: `#161b22`
- Borders: `#30363d`
- Text: `#e6edf3`
- Accent: `#58a6ff`

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Troubleshooting

### TypeScript Errors

The TypeScript errors you see before running `npm install` are expected. They will be resolved once dependencies are installed.

### Port Already in Use

If port 3000 is in use, Vite will automatically try the next available port.

### API Connection Issues

Check that:
1. Backend is running on the correct port
2. CORS is configured properly
3. `VITE_API_BASE_URL` is set correctly

## Contributing

This is part of the Bob Sentinel hackathon project. Follow the team's Git workflow:

1. Work in your feature branch
2. Open PR into `develop`, not `main`
3. Keep backend JSON fields in `snake_case`
4. Use TypeScript for all code (no plain JavaScript)

## License

Hackathon Project - IBM Bob Sentinel Team