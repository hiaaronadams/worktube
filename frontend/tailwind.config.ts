import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        tomato: {
          50: "#fff3f0",
          100: "#ffe0d9",
          500: "#ef4123",
          600: "#d6361b",
          700: "#b22a14",
        },
      },
    },
  },
  plugins: [],
};

export default config;
