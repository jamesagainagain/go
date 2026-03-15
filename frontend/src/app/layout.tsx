import type { Metadata, Viewport } from "next";
import Link from "next/link";
import Image from "next/image";
import "./globals.css";
import { ParticleField } from "@/components/particle-field-1";

export const metadata: Metadata = {
  title: "From screen to street",
  description: "Activation engine - we nudge you at the right moment",
  manifest: "/manifest.json",
  icons: { icon: "/icon.svg" },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "go!",
  },
};

export const viewport: Viewport = {
  themeColor: "#fdf2ed",
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
      <body className="bg-[#fdf2ed] text-text-primary font-sans">
        <ParticleField />
        <Link
          href="/"
          className="fixed top-4 left-4 z-20 flex items-center shrink-0"
          aria-label="go! home"
        >
          <Image
            src="/icon.svg"
            alt="go!"
            width={36}
            height={36}
            className="rounded-lg object-contain"
          />
        </Link>
        <div className="relative z-10 min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}
