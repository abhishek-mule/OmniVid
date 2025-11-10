# Project Architecture

## Directory Structure

```
frontend/
├── public/                 # Static files
│   ├── images/            # Image assets
│   └── fonts/             # Font files
├── src/
│   ├── app/               # App Router pages and layouts
│   │   ├── (auth)/        # Authentication routes
│   │   ├── (dashboard)/   # Dashboard routes
│   │   ├── api/           # API routes
│   │   ├── components/    # Shared components
│   │   ├── lib/           # Library code
│   │   ├── styles/        # Global styles
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utility functions
│   └── app/               # Root layout and global styles
└── tests/                 # Test files
```

## Key Architectural Decisions

1. **App Router**: Using Next.js App Router for file-based routing and React Server Components.
2. **TypeScript**: Strong typing throughout the application for better developer experience.
3. **Component Library**: Using Radix UI primitives with custom styling.
4. **State Management**: React Query for server state and React Context for global UI state.
5. **Styling**: CSS Modules with PostCSS for scoped styles.
6. **Authentication**: NextAuth.js with JWT strategy.
7. **API Layer**: Route handlers in the `app/api` directory.

## Data Flow

1. **Server Components**: Fetch and render data on the server when possible.
2. **Client Components**: Use React Query for client-side data fetching and caching.
3. **Forms**: React Hook Form with Zod validation.
4. **Real-time Updates**: WebSocket connections for real-time features.

## Performance Considerations

1. **Code Splitting**: Automatic code splitting at the route level.
2. **Image Optimization**: Next.js Image component with automatic optimization.
3. **Font Optimization**: Using `next/font` for optimized font loading.
4. **Lazy Loading**: Dynamic imports for heavy components.

## Security

1. **CSP**: Content Security Policy headers.
2. **CORS**: Configured CORS for API routes.
3. **Input Validation**: Zod for runtime type checking.
4. **Authentication**: Secure session management with HTTP-only cookies.
