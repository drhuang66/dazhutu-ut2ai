import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '百年AI - 智慧康复知识库',
  description: '每个人的百年AI，是属于自己的大本营',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">{children}</body>
    </html>
  )
}
