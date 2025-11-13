export default function DocsPage() {
  return (
    <div className="container py-10">
      <h1 className="text-4xl font-bold mb-8">Developer Documentation</h1>
      <div className="grid gap-8 md:grid-cols-4">
        <div className="md:col-span-1">
          <div className="sticky top-20 space-y-2">
            <h3 className="font-semibold mb-4">Getting Started</h3>
            <a href="#introduction" className="block text-muted-foreground hover:text-foreground">Introduction</a>
            <a href="#authentication" className="block text-muted-foreground hover:text-foreground">Authentication</a>
            <a href="#rate-limiting" className="block text-muted-foreground hover:text-foreground">Rate Limiting</a>
            
            <h3 className="font-semibold mt-8 mb-4">API Reference</h3>
            <a href="#video-api" className="block text-muted-foreground hover:text-foreground">Video API</a>
            <a href="#projects-api" className="block text-muted-foreground hover:text-foreground">Projects API</a>
            <a href="#webhooks" className="block text-muted-foreground hover:text-foreground">Webhooks</a>
          </div>
        </div>
        <div className="md:col-span-3 space-y-12">
          <section id="introduction">
            <h2 className="text-2xl font-bold mb-4">Introduction</h2>
            <p className="text-muted-foreground">
              Welcome to the OmniVid API documentation. This guide will help you integrate our video generation 
              and editing capabilities into your applications.
            </p>
          </section>

          <section id="authentication">
            <h2 className="text-2xl font-bold mb-4">Authentication</h2>
            <p className="text-muted-foreground mb-4">
              All API requests require authentication using your API key. Include it in the Authorization header:
            </p>
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
              <code>Authorization: Bearer YOUR_API_KEY</code>
            </pre>
          </section>

          {/* More documentation sections would go here */}
        </div>
      </div>
    </div>
  );
}
