import { AuthProvider } from '../contexts/AuthContext';
import Navigation from '../components/Navigation';
import ChatButton from '../components/chat/ChatButton';
import '../styles/globals.css';

// Footer component
function Footer() {
  return (
    <footer className="bg-gray-800 dark:bg-gray-800 text-white py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <p className="text-sm">© 2026 TodoX. All rights reserved.</p>
          <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">A modern todo application with authentication and task management</p>
        </div>
      </div>
    </footer>
  );
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col bg-gray-900 dark:bg-gray-900 dark:text-white transition-colors duration-300">
        <AuthProvider>
          <Navigation />
          <main className="flex-grow">
            {children}
          </main>
          <Footer />
          {/* Global Chat Button - available on all pages */}
          <ChatButton />
        </AuthProvider>
      </body>
    </html>
  );
}