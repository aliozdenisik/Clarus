/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: "#007bff",
        "primary-hover": "#0062cc",
        "background-light": "#f5f7f8",
        "background-dark": "#0f1923",
        "surface-light": "#ffffff",
        "surface-dark": "#1a2733",
        "border-light": "#e2e8f0",
        "border-dark": "#2d3b48",
        "text-main": "#111418",
        "text-secondary": "#617589",
      },
      fontFamily: {
        display: ["Inter", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "0.125rem",
        sm: "0.125rem",
        md: "0.25rem",
        lg: "0.5rem",
      },
      animation: {
        blink: "blink 1s step-end infinite",
        shimmer: "shimmer 1.5s infinite",
        "bounce-dot": "bounce 0.6s infinite",
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
      },
      keyframes: {
        blink: {
          "50%": { opacity: "0" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
}
