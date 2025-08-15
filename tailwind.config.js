/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // 1. Escanea tus plantillas locales
    './**/templates/**/*.html',
    
    // 2. Escanea la carpeta de crispy-tailwind de forma más directa y flexible
    './.venv/**/site-packages/crispy_tailwind/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}