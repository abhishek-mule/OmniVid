# Development Guide

## Prerequisites

- Node.js 18+
- npm 9+ or yarn 1.22+
- Git

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd omnivid/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Update the values in .env.local
   ```

4. **Start the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   The app will be available at http://localhost:3000

## Development Workflow

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `chore/` - Maintenance tasks

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

### Pull Requests

1. Create a new branch from `main`
2. Make your changes
3. Run tests and linters
4. Push your branch and create a PR
5. Request review from at least one team member
6. Address review comments
7. Squash and merge when approved

## Code Style

- **JavaScript/TypeScript**: Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- **React**: Follow the [React Style Guide](https://reactjs.org/docs/faq-structure.html)
- **CSS**: Follow [BEM](http://getbem.com/) methodology for class naming

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run coverage
npm test -- --coverage
```

### Writing Tests

- Place test files next to the component they test with `.test.tsx` extension
- Use `@testing-library/react` for component testing
- Mock external dependencies
- Test user interactions, not implementation details

## Linting and Formatting

```bash
# Run ESLint
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format
```

## Deployment

### Staging

Merging to the `staging` branch triggers a deployment to the staging environment.

### Production

Merging to the `main` branch triggers a production deployment.

## Troubleshooting

### Common Issues

1. **Dependency issues**
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install`

2. **Type errors**
   - Run `npm run type-check` to identify issues
   - Check for missing type definitions

3. **Environment variables**
   - Ensure `.env.local` exists and has all required variables
   - Restart the development server after changing environment variables

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
