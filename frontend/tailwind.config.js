/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Primary Brand Colors
                primary: {
                    50: '#eff6ff',
                    100: '#dbeafe',
                    200: '#bfdbfe',
                    300: '#93c5fd',
                    400: '#60a5fa',
                    500: '#3b82f6',
                    600: '#2563eb', // Deep Cobalt Blue - Main
                    700: '#1d4ed8',
                    800: '#1e40af',
                    900: '#1e3a8a',
                    950: '#172554',
                },
                // Background Colors
                surface: {
                    50: '#f9fafb',  // Off-white
                    100: '#f3f4f6',
                    200: '#e5e7eb',
                    300: '#d1d5db',
                },
                // Semantic Colors
                success: {
                    50: '#ecfdf5',
                    100: '#d1fae5',
                    200: '#a7f3d0',
                    400: '#34d399',
                    500: '#10b981', // Emerald
                    600: '#059669',
                    700: '#047857',
                },
                warning: {
                    50: '#fffbeb',
                    100: '#fef3c7',
                    200: '#fde68a',
                    400: '#fbbf24',
                    500: '#f59e0b', // Amber
                    600: '#d97706',
                    700: '#b45309',
                },
                danger: {
                    50: '#fef2f2',
                    100: '#fee2e2',
                    200: '#fecaca',
                    400: '#f87171',
                    500: '#ef4444',
                    600: '#dc2626', // Crimson
                    700: '#b91c1c',
                },
                // Slate for text
                slate: {
                    900: '#1a202c', // Primary text
                    800: '#2d3748',
                    700: '#4a5568',
                    600: '#718096',
                    500: '#a0aec0',
                    400: '#cbd5e0',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
                display: ['Inter', 'system-ui', 'sans-serif'],
            },
            fontSize: {
                'xxs': ['0.625rem', { lineHeight: '0.875rem' }],
                'display-xl': ['4.5rem', { lineHeight: '1', letterSpacing: '-0.02em' }],
                'display-lg': ['3.75rem', { lineHeight: '1.05', letterSpacing: '-0.02em' }],
                'display-md': ['3rem', { lineHeight: '1.1', letterSpacing: '-0.01em' }],
            },
            fontWeight: {
                black: '900',
            },
            spacing: {
                '18': '4.5rem',
                '88': '22rem',
                '112': '28rem',
                '128': '32rem',
            },
            borderRadius: {
                '4xl': '2rem',
                '5xl': '2.5rem',
            },
            boxShadow: {
                'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
                'glass-lg': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
                'premium': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                'premium-lg': '0 35px 60px -12px rgba(0, 0, 0, 0.3)',
                'inner-glow': 'inset 0 2px 4px 0 rgba(255, 255, 255, 0.06)',
                'score-green': '0 0 40px rgba(16, 185, 129, 0.3)',
                'score-yellow': '0 0 40px rgba(245, 158, 11, 0.3)',
                'score-red': '0 0 40px rgba(239, 68, 68, 0.3)',
            },
            backdropBlur: {
                'xs': '2px',
            },
            animation: {
                'blob': 'blob 7s infinite',
                'blob-slow': 'blob 10s infinite',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'slide-up': 'slideUp 0.5s ease-out',
                'slide-down': 'slideDown 0.3s ease-out',
                'slide-in-right': 'slideInRight 0.4s ease-out',
                'slide-in-left': 'slideInLeft 0.4s ease-out',
                'fade-in': 'fadeIn 0.4s ease-out',
                'scale-in': 'scaleIn 0.3s ease-out',
                'float': 'float 6s ease-in-out infinite',
                'shimmer': 'shimmer 2s linear infinite',
                'count-up': 'countUp 0.6s ease-out forwards',
                'draw-circle': 'drawCircle 1s ease-out forwards',
                'spin-slow': 'spin 3s linear infinite',
            },
            keyframes: {
                blob: {
                    '0%': { transform: 'translate(0px, 0px) scale(1)' },
                    '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
                    '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
                    '100%': { transform: 'translate(0px, 0px) scale(1)' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                slideDown: {
                    '0%': { transform: 'translateY(-10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                slideInRight: {
                    '0%': { transform: 'translateX(20px)', opacity: '0' },
                    '100%': { transform: 'translateX(0)', opacity: '1' },
                },
                slideInLeft: {
                    '0%': { transform: 'translateX(-20px)', opacity: '0' },
                    '100%': { transform: 'translateX(0)', opacity: '1' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                scaleIn: {
                    '0%': { transform: 'scale(0.95)', opacity: '0' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-20px)' },
                },
                shimmer: {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
                countUp: {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                drawCircle: {
                    '0%': { strokeDashoffset: '100' },
                    '100%': { strokeDashoffset: '0' },
                },
            },
            transitionTimingFunction: {
                'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
                'shimmer': 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%)',
                'glass-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0))',
            },
        },
    },
    plugins: [],
}
