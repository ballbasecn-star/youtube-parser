import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "林克 | Independent Developer / AI Product Builder",
  description:
    "林克的个人网站，一位专注于高表达力网站、AI 产品原型与自动化系统的独立开发者和 AI 产品人。"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="bg-[var(--color-page)] text-[var(--color-ink)] antialiased">{children}</body>
    </html>
  );
}
