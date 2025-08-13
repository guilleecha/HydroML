/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      './**/templates/**/*.html'
  ],
  theme: {
    extend: {},
  },
  // --- AÑADE ESTA LÍNEA DENTRO DE LOS CORCHETES ---
  plugins: [
      require('@tailwindcss/forms'),
  ],
}