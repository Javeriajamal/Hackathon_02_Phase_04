import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-900">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full glass backdrop-blur-md">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h1 className="mt-6 text-4xl font-extrabold text-white sm:text-5xl sm:tracking-tight lg:text-6xl bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-400">
            Stay Organized, Effortlessly
          </h1>
          <p className="mt-8 max-w-2xl mx-auto text-xl text-gray-300">
            A modern task management application with authentication and real-time updates to keep everything in one place — without stress.
          </p>

        </div>

        <div className="mt-16 max-w-3xl mx-auto">
          <div className="glass backdrop-blur-lg rounded-2xl p-8 border border-violet-500/30 shadow-lg shadow-violet-500/20 dark:shadow-violet-500/30">
            <h2 className="text-2xl font-bold text-white mb-6">Get Started</h2>
            <p className="text-gray-300 mb-8">
              Manage your tasks efficiently with our secure and intuitive platform.
              Sign in to access your tasks or create an account to get started.
            </p>

            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link
                href="/login"
                className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 hover:from-cyan-600 hover:via-purple-600 hover:to-pink-600 text-white font-medium py-2.5 px-4 rounded-lg shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transition-all duration-300 transform hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-transparent btn-neon"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-gray-500 to-gray-700 hover:from-gray-600 hover:to-gray-800 shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 btn-neon"
              >
                Create Account
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto backdrop-blur-lg rounded-2xl p-8 ">
          <div className="glass backdrop-blur-md p-6 rounded-xl border border-violet-500/30 shadow-lg shadow-violet-500/20 dark:shadow-violet-500/30  hover:shadow-2xl hover:shadow-purple-950 hover:border-spacing-10 hover:border-violet-500/90  hover:-translate-y-2 duration-300">
            <div className="w-12 h-12 rounded-full glass backdrop-blur-sm flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Task Management</h3>
            <p className="text-gray-300">Create, update, and organize your tasks efficiently with our intuitive interface.</p>
          </div>

          <div className="glass backdrop-blur-md p-6 rounded-xl border border-violet-500/30 shadow-lg shadow-violet-500/20 dark:shadow-violet-500/30  hover:shadow-2xl hover:shadow-purple-950 hover:border-spacing-10 hover:border-violet-500/90 hover:-translate-y-2 duration-300">
            <div className="w-12 h-12 rounded-full glass backdrop-blur-sm flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Secure Authentication</h3>
            <p className="text-gray-300">Your data is protected with industry-standard security practices and authentication.</p>
          </div>

          <div className="glass backdrop-blur-md p-6 rounded-xl border border-violet-500/30 shadow-lg shadow-violet-500/20 dark:shadow-violet-500/30  hover:shadow-2xl hover:shadow-purple-950 hover:border hover:border-violet-500/90 hover:-translate-y-2 duration-300">
            <div className="w-12 h-12 rounded-full glass backdrop-blur-sm flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Responsive Design</h3>
            <p className="text-gray-300">Access your tasks from any device with our fully responsive and mobile-friendly design.</p>
          </div>
        </div>
      </main>
    </div>
  );
}
