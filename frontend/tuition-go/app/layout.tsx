import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const viewport = {
  themeColor: '#1B3A5C',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
}

export const metadata: Metadata = {
  title: 'EduMatch - Find Your Perfect Tutor in Singapore',
  description: 'Connect with qualified, verified tutors for O-Level, A-Level, and IB subjects in Singapore. Book sessions, learn via Google Meet, and excel in your exams.',
  generator: 'v0.app',
  keywords: ['tuition', 'tutor', 'Singapore', 'O-Level', 'A-Level', 'IB', 'education', 'online learning'],
  openGraph: {
    title: 'EduMatch - Find Your Perfect Tutor in Singapore',
    description: 'Connect with qualified, verified tutors for O-Level, A-Level, and IB subjects.',
    type: 'website',
  },
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
        <Analytics />
      </body>
    </html>
  )
}
