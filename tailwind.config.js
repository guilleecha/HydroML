/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    // 1. Scans your local project templates
    './**/templates/**/*.html',
    
    // 2. Scans for the crispy-tailwind templates within any site-packages folder
    '**/site-packages/crispy_tailwind/**/*.html',
  ],
  theme: {
    extend: {
      // HydroML Design System - Supabase-inspired
      colors: {
        // One Dark Theme Colors (PyCharm-inspired)
        onedark: {
          background: '#282c34',    // Dark bluish-gray main background
          foreground: '#abb2bf',    // Light gray/cyan text
          accent1: '#61afef',       // Blue
          accent2: '#c678dd',       // Purple
          accent3: '#98c379',       // Green
          accent4: '#e5c07b',       // Yellow/Gold
          muted: '#5c6370',         // Muted text
          border: '#3e4451',        // Borders
          hover: '#2c313c',         // Hover states
        },

        // PyCharm Darcula Theme Colors
        darcula: {
          background: '#2B2B2B',    // Main dark background
          'background-darker': '#1E1E1E', // Darker backgrounds (panels, cards)
          'background-lighter': '#3C3F41', // Lighter backgrounds (hover states)
          foreground: '#A9B7C6',    // Main text color (light gray-blue)
          'foreground-bright': '#FFFFFF', // Bright white text
          'foreground-muted': '#808080', // Muted text (gray)
          'foreground-subtle': '#5F5F5F', // Very subtle text
          accent: '#FFC66D',        // Amber/gold accents and highlights
          string: '#6A8759',        // Green for success states
          keyword: '#CC7832',       // Orange for keywords/warnings
          comment: '#629755',       // Green for comments
          error: '#BC3F3C',         // Red for errors
          selection: '#214283',     // Blue selection background
          border: '#555555',        // Border color
          'border-light': '#404040', // Lighter border
          gutter: '#313335',        // Line number background
        },

        // Background Colors - Neutral palette for surfaces
        background: {
          'primary': '#ffffff',      // Main background (white)
          'secondary': '#f8fafc',    // Secondary surfaces (slate-50)
          'tertiary': '#f1f5f9',     // Cards, panels (slate-100)
          'accent': '#e2e8f0',       // Subtle borders, dividers (slate-200)
          'muted': '#64748b',        // Disabled/muted backgrounds (slate-500)
          'dark': '#0f172a',         // Dark mode primary (slate-900)
          'dark-secondary': '#1e293b', // Dark mode secondary (slate-800)
        },
        
        // Foreground Colors - Text and content
        foreground: {
          'default': '#0f172a',      // Primary text (slate-900)
          'secondary': '#334155',    // Secondary text (slate-700)
          'muted': '#64748b',        // Muted text (slate-500)
          'subtle': '#94a3b8',       // Subtle text (slate-400)
          'placeholder': '#cbd5e1',  // Placeholder text (slate-300)
          'inverse': '#ffffff',      // Text on dark backgrounds
        },
        
        // HydroML Brand Colors - Blue-based palette
        brand: {
          50: '#eff6ff',   // Lightest blue
          100: '#dbeafe',  // Very light blue
          200: '#bfdbfe',  // Light blue
          300: '#93c5fd',  // Medium light blue
          400: '#60a5fa',  // Medium blue
          500: '#3b82f6',  // Primary brand color
          600: '#2563eb',  // Darker primary (hover states)
          700: '#1d4ed8',  // Dark blue
          800: '#1e40af',  // Very dark blue
          900: '#1e3a8a',  // Darkest blue
          950: '#172554',  // Ultra dark blue
        },
        
        // Semantic State Colors
        success: {
          50: '#f0fdf4',   // Light green background
          100: '#dcfce7',  // Very light green
          500: '#22c55e',  // Primary success color
          600: '#16a34a',  // Darker success (hover)
          700: '#15803d',  // Dark success
          900: '#14532d',  // Very dark success
        },
        
        warning: {
          50: '#fffbeb',   // Light amber background
          100: '#fef3c7',  // Very light amber
          500: '#f59e0b',  // Primary warning color
          600: '#d97706',  // Darker warning (hover)
          700: '#b45309',  // Dark warning
          900: '#78350f',  // Very dark warning
        },
        
        danger: {
          50: '#fef2f2',   // Light red background
          100: '#fee2e2',  // Very light red
          500: '#ef4444',  // Primary danger color
          600: '#dc2626',  // Darker danger (hover)
          700: '#b91c1c',  // Dark danger
          900: '#7f1d1d',  // Very dark danger
        },
        
        // Data Visualization Colors - For charts and graphs
        data: {
          'primary': '#3b82f6',    // Blue
          'secondary': '#10b981',  // Emerald
          'tertiary': '#f59e0b',   // Amber
          'quaternary': '#ef4444', // Red
          'quinary': '#8b5cf6',    // Violet
          'senary': '#06b6d4',     // Cyan
        },
        
        // Border Colors
        border: {
          'default': '#e2e8f0',    // Default borders (slate-200)
          'muted': '#f1f5f9',      // Subtle borders (slate-100)
          'strong': '#cbd5e1',     // Prominent borders (slate-300)
          'accent': '#3b82f6',     // Accent borders (brand-500)
        },
      },
      
      // Typography - Clean, modern font stack
      fontFamily: {
        'sans': [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'Noto Sans',
          'sans-serif',
          'Apple Color Emoji',
          'Segoe UI Emoji',
          'Segoe UI Symbol',
          'Noto Color Emoji'
        ],
        'mono': [
          'JetBrains Mono',
          'Fira Code',
          'ui-monospace',
          'SFMono-Regular',
          'Monaco',
          'Consolas',
          'Liberation Mono',
          'Courier New',
          'monospace'
        ],
      },
      
      // Enhanced spacing for consistent layouts
      spacing: {
        '18': '4.5rem',   // 72px
        '88': '22rem',    // 352px
        '128': '32rem',   // 512px
      },
      
      // Enhanced border radius for modern look
      borderRadius: {
        'xl': '0.75rem',  // 12px
        '2xl': '1rem',    // 16px
        '3xl': '1.5rem',  // 24px
      },
      
      // Box shadows for depth and elevation
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'DEFAULT': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        'inner': 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
        'none': 'none',
        // Custom shadows for HydroML components
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px 0 rgb(0 0 0 / 0.06)',
        'dropdown': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -2px rgb(0 0 0 / 0.05)',
        'modal': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04)',
      },
      
      // Animation and transitions
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}