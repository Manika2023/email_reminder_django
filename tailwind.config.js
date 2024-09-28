/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',   // All template files in the templates folder
    './scheduler/templates/**/*.html', // Templates in your app folder
    './scheduler/static/**/*.js', // Any JavaScript files in the static folder
    './scheduler/static/**/*.css', // Custom CSS files
    './scheduler/forms.py',  // Python forms that may include Tailwind classes
    './scheduler/views.py',  // Python views that may include Tailwind classes
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

