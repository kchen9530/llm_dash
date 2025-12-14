# LLM Local Ops Center - Frontend

Modern web interface for managing LLM deployments.

## Features

- 🎨 Modern UI with Shadcn/ui components
- 📊 Real-time system monitoring
- 🚀 One-click model deployment
- 💬 Interactive chat interface
- 📝 Live log streaming
- 🌙 Dark mode by default

## Quick Start

### Install Dependencies

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Tech Stack

- **React 18**: UI framework
- **Vite**: Build tool
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Shadcn/ui**: Component library
- **Zustand**: State management
- **React Router**: Routing
- **xterm.js**: Terminal emulation

## Project Structure

```
src/
├── components/        # Reusable components
│   ├── ui/           # Shadcn UI components
│   ├── Layout.tsx    # Main layout
│   ├── StatusBadge.tsx
│   └── SystemStats.tsx
├── pages/            # Page components
│   ├── Dashboard.tsx
│   ├── Deploy.tsx
│   └── Chat.tsx
├── lib/              # Utilities
│   ├── api.ts        # API client
│   └── utils.ts      # Helper functions
├── store/            # State management
│   ├── useModelStore.ts
│   └── useSystemStore.ts
├── App.tsx           # Root component
└── main.tsx          # Entry point
```

## API Integration

The frontend communicates with the backend API at `http://localhost:7860`.

Key endpoints:
- `/api/system/status` - System metrics
- `/api/models/deploy` - Deploy models
- `/api/models/list` - List models
- `/api/chat/completions` - Chat with models
- `ws://localhost:7860/api/models/ws/logs/{id}` - Live logs

## Customization

### Theme

Edit `src/index.css` to customize colors and design tokens.

### Add New Pages

1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation item in `src/components/Layout.tsx`

## License

MIT

