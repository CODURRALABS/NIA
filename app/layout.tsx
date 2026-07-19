import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NIA — Sovereign Living Assistant",
  description:
    "NIA is a next-generation, local-first AI that thinks, speaks, and executes any action a human can perform on a computing device — and more.",
  keywords: ["AI assistant", "autonomous agent", "sovereign AI", "vibecoding", "NIA"],
  authors: [{ name: "Codurra Labs" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
