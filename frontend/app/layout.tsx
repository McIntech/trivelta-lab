import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import "./globals.css";


export const metadata: Metadata = {
  title: "Trivelta Lab",
  description: "Sportsbook lab frontend — Next.js, TypeScript, TanStack Query",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
