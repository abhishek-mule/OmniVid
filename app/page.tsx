"use client";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to OmniVid
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Create amazing videos with AI-powered tools
          </p>
          <div className="space-x-4">
            <a
              href="/generate"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Get Started
            </a>
            <a
              href="/features"
              className="bg-white text-blue-600 px-6 py-3 rounded-lg border border-blue-600 hover:bg-blue-50 transition-colors"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}