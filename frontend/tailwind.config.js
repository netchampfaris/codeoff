import frappeUIPreset from 'frappe-ui/tailwind'

export default {
  // presets: [frappeUIPreset],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
    '../node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
    '../frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'ui-monospace',
          'SFMono-Regular',
          'Menlo',
          'Consolas',
          'monospace',
        ],
      },
      // fontSize: {
      //   '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      //   '5xl': ['3rem', { lineHeight: '1' }],
      //   '6xl': ['3.75rem', { lineHeight: '1' }],
      //   '7xl': ['4.5rem', { lineHeight: '1' }],
      //   '8xl': ['6rem', { lineHeight: '1' }],
      //   '9xl': ['8rem', { lineHeight: '1' }],
      // },
    },
  },
}
