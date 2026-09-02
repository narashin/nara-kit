import type { Config } from "tailwindcss"

const config = {
  content: ["./components/**/*.tsx", "./pages/**/*.tsx"],
  theme: {
    colors: {
      primary: "#3659FF",
      white: "#FFFFFF",
      black: "#000000",
      positive: "#3CC926",
      negative: "#FF334B",
      gray: {
        100: "#FCFCFC",
        200: "#EFEFEF",
        300: "#DFDFDF",
        500: "#949494",
        700: "#555555",
        900: "#111111",
      },
    },
    borderRadius: {
      DEFAULT: "5px",
    },
  },
} satisfies Config

export default config
