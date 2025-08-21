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
      // ===== ENHANCED DESIGN TOKEN SYSTEM =====
      
      colors: {
        // CSS Custom Property Integration
        'surface': 'var(--color-background-surface)',
        'primary': 'var(--color-background-primary)',
        'secondary': 'var(--color-background-secondary)',
        'tertiary': 'var(--color-background-tertiary)',
        'quaternary': 'var(--color-background-quaternary)',
        'inverse': 'var(--color-background-inverse)',
        
        // Text colors using custom properties
        'text-primary': 'var(--color-foreground-primary)',
        'text-secondary': 'var(--color-foreground-secondary)',
        'text-tertiary': 'var(--color-foreground-tertiary)',
        'text-quaternary': 'var(--color-foreground-quaternary)',
        'text-disabled': 'var(--color-foreground-disabled)',
        'text-placeholder': 'var(--color-foreground-placeholder)',
        'text-inverse': 'var(--color-foreground-inverse)',
        
        // Border colors using custom properties
        'border-primary': 'var(--color-border-primary)',
        'border-secondary': 'var(--color-border-secondary)',
        'border-focus': 'var(--color-border-focus)',
        'border-error': 'var(--color-border-error)',
        'border-success': 'var(--color-border-success)',
        'border-warning': 'var(--color-border-warning)',
        
        // Brand colors using custom properties
        'brand-primary': 'var(--color-brand-primary)',
        'brand-primary-hover': 'var(--color-brand-primary-hover)',
        'brand-primary-active': 'var(--color-brand-primary-active)',
        'brand-primary-subtle': 'var(--color-brand-primary-subtle)',
        'brand-secondary': 'var(--color-brand-secondary)',
        'brand-secondary-hover': 'var(--color-brand-secondary-hover)',
        
        // Semantic colors using custom properties
        'success': 'var(--color-success)',
        'success-hover': 'var(--color-success-hover)',
        'success-subtle': 'var(--color-success-subtle)',
        'success-muted': 'var(--color-success-muted)',
        
        'warning': 'var(--color-warning)',
        'warning-hover': 'var(--color-warning-hover)',
        'warning-subtle': 'var(--color-warning-subtle)',
        'warning-muted': 'var(--color-warning-muted)',
        
        'error': 'var(--color-error)',
        'error-hover': 'var(--color-error-hover)',
        'error-subtle': 'var(--color-error-subtle)',
        'error-muted': 'var(--color-error-muted)',
        
        'info': 'var(--color-info)',
        'info-hover': 'var(--color-info-hover)',
        'info-subtle': 'var(--color-info-subtle)',
        'info-muted': 'var(--color-info-muted)',
        
        // Preserve existing color scales for backward compatibility
        // Blue Scale - Primary Brand
        blue: {
          50: 'var(--color-blue-50)',
          100: 'var(--color-blue-100)',
          200: 'var(--color-blue-200)',
          300: 'var(--color-blue-300)',
          400: 'var(--color-blue-400)',
          500: 'var(--color-blue-500)',
          600: 'var(--color-blue-600)',
          700: 'var(--color-blue-700)',
          800: 'var(--color-blue-800)',
          900: 'var(--color-blue-900)',
          950: 'var(--color-blue-950)',
        },
        
        // Gray Scale - Neutrals
        gray: {
          50: 'var(--color-gray-50)',
          100: 'var(--color-gray-100)',
          200: 'var(--color-gray-200)',
          300: 'var(--color-gray-300)',
          400: 'var(--color-gray-400)',
          500: 'var(--color-gray-500)',
          600: 'var(--color-gray-600)',
          700: 'var(--color-gray-700)',
          800: 'var(--color-gray-800)',
          900: 'var(--color-gray-900)',
          950: 'var(--color-gray-950)',
        },
        
        // Green Scale - Success
        green: {
          50: 'var(--color-green-50)',
          100: 'var(--color-green-100)',
          200: 'var(--color-green-200)',
          300: 'var(--color-green-300)',
          400: 'var(--color-green-400)',
          500: 'var(--color-green-500)',
          600: 'var(--color-green-600)',
          700: 'var(--color-green-700)',
          800: 'var(--color-green-800)',
          900: 'var(--color-green-900)',
          950: 'var(--color-green-950)',
        },
        
        // Red Scale - Error/Danger
        red: {
          50: 'var(--color-red-50)',
          100: 'var(--color-red-100)',
          200: 'var(--color-red-200)',
          300: 'var(--color-red-300)',
          400: 'var(--color-red-400)',
          500: 'var(--color-red-500)',
          600: 'var(--color-red-600)',
          700: 'var(--color-red-700)',
          800: 'var(--color-red-800)',
          900: 'var(--color-red-900)',
          950: 'var(--color-red-950)',
        },
        
        // Amber Scale - Warning
        amber: {
          50: 'var(--color-amber-50)',
          100: 'var(--color-amber-100)',
          200: 'var(--color-amber-200)',
          300: 'var(--color-amber-300)',
          400: 'var(--color-amber-400)',
          500: 'var(--color-amber-500)',
          600: 'var(--color-amber-600)',
          700: 'var(--color-amber-700)',
          800: 'var(--color-amber-800)',
          900: 'var(--color-amber-900)',
          950: 'var(--color-amber-950)',
        },
        
        // Cyan Scale - Info
        cyan: {
          50: 'var(--color-cyan-50)',
          100: 'var(--color-cyan-100)',
          200: 'var(--color-cyan-200)',
          300: 'var(--color-cyan-300)',
          400: 'var(--color-cyan-400)',
          500: 'var(--color-cyan-500)',
          600: 'var(--color-cyan-600)',
          700: 'var(--color-cyan-700)',
          800: 'var(--color-cyan-800)',
          900: 'var(--color-cyan-900)',
          950: 'var(--color-cyan-950)',
        },
        
        // Purple Scale - Accent
        purple: {
          50: 'var(--color-purple-50)',
          100: 'var(--color-purple-100)',
          200: 'var(--color-purple-200)',
          300: 'var(--color-purple-300)',
          400: 'var(--color-purple-400)',
          500: 'var(--color-purple-500)',
          600: 'var(--color-purple-600)',
          700: 'var(--color-purple-700)',
          800: 'var(--color-purple-800)',
          900: 'var(--color-purple-900)',
          950: 'var(--color-purple-950)',
        },

        // Legacy color support for backward compatibility
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
      
      // Typography - Enhanced with design tokens
      fontFamily: {
        'sans': 'var(--font-family-sans)',
        'mono': 'var(--font-family-mono)',
        'serif': 'var(--font-family-serif)',
      },
      
      fontSize: {
        'xs': 'var(--font-size-xs)',
        'sm': 'var(--font-size-sm)',
        'base': 'var(--font-size-base)',
        'lg': 'var(--font-size-lg)',
        'xl': 'var(--font-size-xl)',
        '2xl': 'var(--font-size-2xl)',
        '3xl': 'var(--font-size-3xl)',
        '4xl': 'var(--font-size-4xl)',
        '5xl': 'var(--font-size-5xl)',
        '6xl': 'var(--font-size-6xl)',
        '7xl': 'var(--font-size-7xl)',
        '8xl': 'var(--font-size-8xl)',
        '9xl': 'var(--font-size-9xl)',
      },
      
      fontWeight: {
        'thin': 'var(--font-weight-thin)',
        'extralight': 'var(--font-weight-extralight)',
        'light': 'var(--font-weight-light)',
        'normal': 'var(--font-weight-normal)',
        'medium': 'var(--font-weight-medium)',
        'semibold': 'var(--font-weight-semibold)',
        'bold': 'var(--font-weight-bold)',
        'extrabold': 'var(--font-weight-extrabold)',
        'black': 'var(--font-weight-black)',
      },
      
      lineHeight: {
        'none': 'var(--line-height-none)',
        'tight': 'var(--line-height-tight)',
        'snug': 'var(--line-height-snug)',
        'normal': 'var(--line-height-normal)',
        'relaxed': 'var(--line-height-relaxed)',
        'loose': 'var(--line-height-loose)',
      },
      
      letterSpacing: {
        'tighter': 'var(--letter-spacing-tighter)',
        'tight': 'var(--letter-spacing-tight)',
        'normal': 'var(--letter-spacing-normal)',
        'wide': 'var(--letter-spacing-wide)',
        'wider': 'var(--letter-spacing-wider)',
        'widest': 'var(--letter-spacing-widest)',
      },
      
      // Enhanced spacing using design tokens
      spacing: {
        '0': 'var(--space-0)',
        'px': 'var(--space-px)',
        '0.5': 'var(--space-0-5)',
        '1': 'var(--space-1)',
        '1.5': 'var(--space-1-5)',
        '2': 'var(--space-2)',
        '2.5': 'var(--space-2-5)',
        '3': 'var(--space-3)',
        '3.5': 'var(--space-3-5)',
        '4': 'var(--space-4)',
        '5': 'var(--space-5)',
        '6': 'var(--space-6)',
        '7': 'var(--space-7)',
        '8': 'var(--space-8)',
        '9': 'var(--space-9)',
        '10': 'var(--space-10)',
        '11': 'var(--space-11)',
        '12': 'var(--space-12)',
        '14': 'var(--space-14)',
        '16': 'var(--space-16)',
        '18': 'var(--space-18)',
        '20': 'var(--space-20)',
        '24': 'var(--space-24)',
        '28': 'var(--space-28)',
        '32': 'var(--space-32)',
        '36': 'var(--space-36)',
        '40': 'var(--space-40)',
        '44': 'var(--space-44)',
        '48': 'var(--space-48)',
        '52': 'var(--space-52)',
        '56': 'var(--space-56)',
        '60': 'var(--space-60)',
        '64': 'var(--space-64)',
        '72': 'var(--space-72)',
        '80': 'var(--space-80)',
        '96': 'var(--space-96)',
        // Legacy spacing for backward compatibility
        '88': '22rem',    // 352px
        '128': '32rem',   // 512px
      },
      
      // Enhanced border radius using design tokens
      borderRadius: {
        'none': 'var(--radius-none)',
        'sm': 'var(--radius-sm)',
        'DEFAULT': 'var(--radius-base)',
        'md': 'var(--radius-md)',
        'lg': 'var(--radius-lg)',
        'xl': 'var(--radius-xl)',
        '2xl': 'var(--radius-2xl)',
        '3xl': 'var(--radius-3xl)',
        'full': 'var(--radius-full)',
      },
      
      // Enhanced shadows using design tokens
      boxShadow: {
        'none': 'var(--shadow-none)',
        'sm': 'var(--shadow-sm)',
        'DEFAULT': 'var(--shadow-base)',
        'md': 'var(--shadow-md)',
        'lg': 'var(--shadow-lg)',
        'xl': 'var(--shadow-xl)',
        '2xl': 'var(--shadow-2xl)',
        'inner': 'var(--shadow-inner)',
        // Component-specific shadows
        'card': 'var(--shadow-card)',
        'dropdown': 'var(--shadow-dropdown)',
        'modal': 'var(--shadow-modal)',
        'tooltip': 'var(--shadow-tooltip)',
        'focus': 'var(--shadow-focus)',
        'focus-error': 'var(--shadow-focus-error)',
        'focus-success': 'var(--shadow-focus-success)',
      },
      
      // Z-index using design tokens
      zIndex: {
        'auto': 'var(--z-index-auto)',
        '0': 'var(--z-index-base)',
        '10': 'var(--z-index-above)',
        '20': 'var(--z-index-dropdown)',
        '30': 'var(--z-index-sticky)',
        '40': 'var(--z-index-header)',
        '50': 'var(--z-index-overlay)',
        '60': 'var(--z-index-modal)',
        '70': 'var(--z-index-popover)',
        '80': 'var(--z-index-tooltip)',
        '90': 'var(--z-index-toast)',
        '9999': 'var(--z-index-max)',
      },
      
      // Enhanced transitions using design tokens
      transitionProperty: {
        'none': 'none',
        'all': 'all',
        'colors': 'color, background-color, border-color, text-decoration-color, fill, stroke',
        'opacity': 'opacity',
        'shadow': 'box-shadow',
        'transform': 'transform',
        'theme': 'color, background-color, border-color, box-shadow',
      },
      
      transitionDuration: {
        'instant': 'var(--duration-instant)',
        'fast': 'var(--duration-fast)',
        'DEFAULT': 'var(--duration-normal)',
        'normal': 'var(--duration-normal)',
        'slow': 'var(--duration-slow)',
        'slower': 'var(--duration-slower)',
      },
      
      transitionTimingFunction: {
        'linear': 'var(--ease-linear)',
        'in': 'var(--ease-in)',
        'out': 'var(--ease-out)',
        'in-out': 'var(--ease-in-out)',
      },
      
      // Enhanced animations
      animation: {
        'none': 'none',
        'fade-in': 'fadeIn var(--duration-slow) var(--ease-out)',
        'slide-up': 'slideUp var(--duration-normal) var(--ease-out)',
        'scale-in': 'scaleIn var(--duration-fast) var(--ease-out)',
        'spin': 'spin 1s linear infinite',
        'ping': 'ping 1s cubic-bezier(0, 0, 0.2, 1) infinite',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce': 'bounce 1s infinite',
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
        spin: {
          'to': { transform: 'rotate(360deg)' },
        },
        ping: {
          '75%, 100%': { transform: 'scale(2)', opacity: '0' },
        },
        pulse: {
          '50%': { opacity: '.5' },
        },
        bounce: {
          '0%, 100%': {
            transform: 'translateY(-25%)',
            animationTimingFunction: 'cubic-bezier(0.8,0,1,1)',
          },
          '50%': {
            transform: 'none',
            animationTimingFunction: 'cubic-bezier(0,0,0.2,1)',
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}