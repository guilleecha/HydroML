/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html',
    './**/static/src/**/*.js',
    './**/forms.py', // <-- Opcional: para que Tailwind detecte clases en los widgets de formularios
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}