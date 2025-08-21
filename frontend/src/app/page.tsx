/**
 * Root page component for Suna AI
 * This file is required by Next.js App Router for the root path
 */
export default function RootPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center max-w-md mx-auto px-6">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">Suna AI</h1>
        <p className="text-xl text-gray-600 mb-8">
          Your intelligent AI assistant platform
        </p>
        <div className="space-y-4">
          <a 
            href="/dashboard" 
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Go to Dashboard
          </a>
          <div>
            <a 
              href="/auth" 
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              Sign In
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}