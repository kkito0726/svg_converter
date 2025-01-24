/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      height: {
        "screen-minus-topbar": "calc(100vh - 56px)",
      },
      width: {
        figure: "calc(100vw-578px)",
        input: "410px",
        sidebar: "136px",
      },
    },
  },
  plugins: [],
};
