import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TgSecret Admin',
  description: 'Telegram Userbot Admin Panel',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                  <div className="flex">
                    <div className="flex-shrink-0 flex items-center">
                      <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                        TgSecret Admin
                      </h1>
                    </div>
                    <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
                      <a href="/dashboard" className="border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                        Dashboard
                      </a>
                      <a href="/channels" className="border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                        Channels
                      </a>
                      <a href="/api-keys" className="border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                        API Keys
                      </a>
                      <a href="/media" className="border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                        Media Logs
                      </a>
                      <a href="/session" className="border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                        Session
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </nav>
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {children}
            </main>
          </div>
          <Toaster />
        </Providers>
      </body>
    </html>
  )
}
