import type { Metadata } from "next";
import { ChatSidebar } from "../components/ChatSidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "DocuStream",
  description: "AI-powered document extraction",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="flex h-screen overflow-hidden bg-white text-zinc-900 dark:bg-black dark:text-zinc-100">
        <ChatSidebar />
        <main className="flex-1 overflow-hidden relative">
          {children}
        </main>
      </body>
    </html>
  );
}
