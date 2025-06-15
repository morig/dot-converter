import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Dot Converter',
  description: 'Convert any image to dot art.',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
