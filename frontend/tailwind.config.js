/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "bg-deep": "var(--bg-deep)",
        "bg-phone": "var(--bg-phone)",
        "bg-card": "var(--bg-card)",
        "bg-card-hover": "var(--bg-card-hover)",
        "text-primary": "var(--text-primary)",
        "text-muted": "var(--text-muted)",
        accent: "var(--accent)",
        "accent-glow": "var(--accent-glow)",
        "dot-art": "var(--dot-art)",
        "dot-sport": "var(--dot-sport)",
        "dot-music": "var(--dot-music)",
        "dot-food": "var(--dot-food)",
        "dot-social": "var(--dot-social)",
        "dot-nature": "var(--dot-nature)",
        "dot-study": "var(--dot-study)",
        "dot-nightlife": "var(--dot-nightlife)",
        "dot-wellness": "var(--dot-wellness)",
        "dot-comedy": "var(--dot-comedy)",
        "dot-tech": "var(--dot-tech)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      fontSize: {
        "time-display": ["4.5rem", { lineHeight: "1" }],
      },
    },
  },
  plugins: [],
};
