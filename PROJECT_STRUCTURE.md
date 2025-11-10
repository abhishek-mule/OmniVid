# OmniVid Frontend Project Structure

This document outlines the structure of the OmniVid frontend project, following Next.js 13+ App Router conventions.

## Directory Structure

```
src/
├── app/                    # Next.js 13+ app directory
│   ├── editor/             # Main video editor/generator
│   │   └── page.tsx        # Editor page component
│   │
│   ├── dashboard/          # User dashboard
│   │   ├── projects/       # User projects
│   │   └── settings/       # User settings
│   │
│   ├── auth/               # Authentication pages
│   │   ├── login/          # Login page
│   │   ├── signup/         # Signup page
│   │   └── profile/        # User profile
│   │
│   ├── templates/          # Template gallery
│   ├── pricing/            # Pricing plans
│   ├── features/           # Feature showcase
│   ├── api/                # API routes
│   │   └── auth/           # Authentication API routes
│   │
│   ├── layout.tsx          # Root layout
│   ├── globals.css         # Global styles
│   └── test/               # Test pages
│
├── components/             # Reusable UI components
│   ├── editor/             # Editor-specific components
│   │   ├── PromptPanel.tsx
│   │   ├── ProgressVisualizer.tsx
│   │   └── TemplateCard.tsx
│   │
│   ├── ui/                 # Base UI components
│   └── shared/             # Shared components
│
└── lib/                    # Utility functions and hooks
    ├── api/                # API client
    ├── hooks/              # Custom React hooks
    └── utils/              # Utility functions
```

## Key Files and Their Purposes

### App Directory (`src/app/`)

- `editor/page.tsx`: Main video editor interface where users create and edit videos
- `dashboard/`: User dashboard with project management
- `auth/`: Authentication pages (login, signup, profile)
- `templates/`: Template gallery for starting new projects
- `api/`: API route handlers
- `layout.tsx`: Root layout component
- `globals.css`: Global styles and Tailwind directives

### Components (`src/components/`)

- `editor/`: Components specific to the video editor
  - `PromptPanel.tsx`: Input for video generation prompts
  - `ProgressVisualizer.tsx`: Shows generation progress
  - `TemplateCard.tsx`: Displays template previews
- `ui/`: Reusable UI components (buttons, inputs, etc.)
- `shared/`: Shared components used across the app

### Lib Directory (`src/lib/`)

- `api/`: API client and request handlers
- `hooks/`: Custom React hooks
- `utils/`: Utility functions and helpers

## Development Workflow

1. **Adding a New Page**:
   - Create a new directory in `src/app/` (e.g., `about/`)
   - Add a `page.tsx` file that exports a React component
   - The route will be available at `/about`

2. **Creating a New Component**:
   - Add to `src/components/` in the appropriate subdirectory
   - Export the component from `src/components/index.ts`
   - Import using `@/components/ComponentName`

3. **API Integration**:
   - Add API routes in `src/app/api/`
   - Use the API client in `src/lib/api/` for frontend requests

## Best Practices

- **Component Organization**: Group related components in feature-based directories
- **State Management**: Use React Context for global state, local state otherwise
- **Styling**: Use Tailwind CSS with component-scoped styles when needed
- **Type Safety**: Use TypeScript interfaces for all props and API responses
- **Performance**: Use dynamic imports for large components with `next/dynamic`

## Testing

- Unit tests: `__tests__` directory next to the component being tested
- Integration tests: `src/__tests__/`
- Run tests: `npm test`

## Deployment

The project is configured for deployment on Vercel. The production build can be created with:

```bash
npm run build
```

## Environment Variables

Copy `.env.local.example` to `.env.local` and update the values:

```bash
cp .env.local.example .env.local
```

## Contributing

1. Create a new branch for your feature: `git checkout -b feature/amazing-feature`
2. Make your changes and commit them: `git commit -m 'Add some amazing feature'`
3. Push to the branch: `git push origin feature/amazing-feature`
4. Open a Pull Request
