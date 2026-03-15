import type { Metadata, Viewport } from "next";
import "./globals.css";
import { ParticleField } from "@/components/particle-field-1";

export const metadata: Metadata = {
  title: "FirstMove - From screen to street",
  description: "Activation engine - we nudge you at the right moment",
  manifest: "/manifest.json",
  icons: { icon: "/icon.svg" },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "FirstMove",
  },
};

export const viewport: Viewport = {
  themeColor: "#f59e0b",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="antialiased">
      <head>
        <meta name="mobile-web-app-capable" content="yes" />
      </head>
      <body className="bg-black text-text-primary font-sans">
        <ParticleField />
        <div className="relative z-10 min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}
