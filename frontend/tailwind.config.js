/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Primary Brand Colors - Electric Cobalt
                primary: {
                    50: '#f0f7ff',
                    100: '#e0f0ff',
                    200: '#b9e0fe',
                    300: '#7cc5fd',
                    400: '#36a6fa',
                    500: '#0c87eb',
                    600: '#0066d6', // Main electric blue
                    700: '#0052ae',
                    800: '#04468c',
                    900: '#0a3c74',
                    950: '#07264d',
                },
                // Dark mode surface colors
                dark: {
                    50: '#f7f7f8',
                    100: '#ececf1',
                    200: '#d9d9e3',
                    300: '#c5c5d2',
                    400: '#acacbe',
                    500: '#8e8ea0',
                    600: '#565674',
                    700: '#3d3d56',
                    800: '#202033',
                    900: '#0f0f1a',
                    950: '#080810',
                },
                // Background Colors
                surface: {
                    50: '#fafbfc',
                    100: '#f4f6f8',
                    200: '#eaedf2',
                    300: '#d5dbe3',
                },
                // Semantic Colors - Enhanced
                success: {
                    50: '#ecfdf5',
                    100: '#d1fae5',
                    200: '#a7f3d0',
                    300: '#6ee7b7',
                    400: '#34d399',
                    500: '#10b981',
                    600: '#059669',
                    700: '#047857',
                    800: '#065f46',
                    900: '#064e3b',
                },
                warning: {
                    50: '#fffbeb',
                    100: '#fef3c7',
                    200: '#fde68a',
                    300: '#fcd34d',
                    400: '#fbbf24',
                    500: '#f59e0b',
                    600: '#d97706',
                    700: '#b45309',
                    800: '#92400e',
                    900: '#78350f',
                },
                danger: {
                    50: '#fef2f2',
                    100: '#fee2e2',
                    200: '#fecaca',
                    300: '#fca5a5',
                    400: '#f87171',
                    500: '#ef4444',
                    600: '#dc2626',
                    700: '#b91c1c',
                    800: '#991b1b',
                    900: '#7f1d1d',
                },
                // Aurora gradient colors
                aurora: {
                    blue: '#3b82f6',
                    purple: '#8b5cf6',
                    cyan: '#06b6d4',
                    pink: '#ec4899',
                    green: '#10b981',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
                display: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
            },
            fontSize: {
                'xxs': ['0.625rem', { lineHeight: '0.875rem' }],
                '2xs': ['0.6875rem', { lineHeight: '1rem' }],
                'display-2xl': ['5rem', { lineHeight: '1', letterSpacing: '-0.03em' }],
                'display-xl': ['4.5rem', { lineHeight: '1', letterSpacing: '-0.02em' }],
                'display-lg': ['3.75rem', { lineHeight: '1.05', letterSpacing: '-0.02em' }],
                'display-md': ['3rem', { lineHeight: '1.1', letterSpacing: '-0.01em' }],
                'display-sm': ['2.25rem', { lineHeight: '1.15', letterSpacing: '-0.01em' }],
            },
            fontWeight: {
                thin: '100',
                extralight: '200',
                light: '300',
                normal: '400',
                medium: '500',
                semibold: '600',
                bold: '700',
                extrabold: '800',
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
                '6xl': '3rem',
            },
            boxShadow: {
                'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
                'glass-lg': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
                'premium': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                'premium-lg': '0 35px 60px -12px rgba(0, 0, 0, 0.3)',
                'glow': '0 0 40px rgba(59, 130, 246, 0.3)',
                'glow-lg': '0 0 60px rgba(59, 130, 246, 0.4)',
                'glow-success': '0 0 40px rgba(16, 185, 129, 0.4)',
                'glow-warning': '0 0 40px rgba(245, 158, 11, 0.4)',
                'glow-danger': '0 0 40px rgba(239, 68, 68, 0.4)',
                'inner-glow': 'inset 0 2px 4px 0 rgba(255, 255, 255, 0.06)',
                'dark': '0 20px 60px -15px rgba(0, 0, 0, 0.5)',
                'dark-lg': '0 30px 80px -20px rgba(0, 0, 0, 0.6)',
                'card': '0 2px 8px -2px rgba(0, 0, 0, 0.05), 0 4px 16px -4px rgba(0, 0, 0, 0.08)',
                'card-hover': '0 8px 24px -4px rgba(0, 0, 0, 0.1), 0 16px 48px -8px rgba(0, 0, 0, 0.12)',
                'bento': '0 0 0 1px rgba(255, 255, 255, 0.05), 0 2px 4px rgba(0, 0, 0, 0.1), 0 12px 24px rgba(0, 0, 0, 0.15)',
                'bento-hover': '0 0 0 1px rgba(255, 255, 255, 0.1), 0 8px 16px rgba(0, 0, 0, 0.15), 0 24px 48px rgba(0, 0, 0, 0.2)',
            },
            backdropBlur: {
                'xs': '2px',
                '2xl': '24px',
                '3xl': '40px',
            },
            animation: {
                'blob': 'blob 7s infinite',
                'blob-slow': 'blob 12s infinite',
                'blob-slower': 'blob 18s infinite',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
                'slide-up': 'slideUp 0.6s ease-out',
                'slide-down': 'slideDown 0.3s ease-out',
                'slide-in-right': 'slideInRight 0.5s ease-out',
                'slide-in-left': 'slideInLeft 0.5s ease-out',
                'fade-in': 'fadeIn 0.5s ease-out',
                'fade-in-up': 'fadeInUp 0.6s ease-out',
                'scale-in': 'scaleIn 0.4s ease-out',
                'scale-in-bounce': 'scaleInBounce 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
                'float': 'float 6s ease-in-out infinite',
                'float-slow': 'float 10s ease-in-out infinite',
                'shimmer': 'shimmer 2s linear infinite',
                'shimmer-slow': 'shimmer 3s linear infinite',
                'count-up': 'countUp 0.6s ease-out forwards',
                'draw-circle': 'drawCircle 1.5s ease-out forwards',
                'spin-slow': 'spin 4s linear infinite',
                'spin-reverse': 'spinReverse 8s linear infinite',
                'gradient-x': 'gradientX 8s ease infinite',
                'gradient-y': 'gradientY 8s ease infinite',
                'gradient-xy': 'gradientXY 8s ease infinite',
                'aurora': 'aurora 15s ease infinite',
                'aurora-fast': 'aurora 8s ease infinite',
                'ticker': 'ticker 30s linear infinite',
                'glow-pulse': 'glowPulse 2s ease-in-out infinite',
                'ring-pulse': 'ringPulse 1.5s ease-out forwards',
                'score-fill': 'scoreFill 1.2s ease-out forwards',
                'typewriter': 'typewriter 3s steps(40) infinite',
                'bounce-subtle': 'bounceSubtle 2s ease-in-out infinite',
                'wiggle': 'wiggle 1s ease-in-out infinite',
                'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
            },
            keyframes: {
                blob: {
                    '0%': { transform: 'translate(0px, 0px) scale(1)' },
                    '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
                    '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
                    '100%': { transform: 'translate(0px, 0px) scale(1)' },
                },
                pulseGlow: {
                    '0%, 100%': { opacity: '1', filter: 'brightness(1)' },
                    '50%': { opacity: '0.8', filter: 'brightness(1.2)' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(30px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                slideDown: {
                    '0%': { transform: 'translateY(-10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                slideInRight: {
                    '0%': { transform: 'translateX(30px)', opacity: '0' },
                    '100%': { transform: 'translateX(0)', opacity: '1' },
                },
                slideInLeft: {
                    '0%': { transform: 'translateX(-30px)', opacity: '0' },
                    '100%': { transform: 'translateX(0)', opacity: '1' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                fadeInUp: {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                scaleIn: {
                    '0%': { transform: 'scale(0.9)', opacity: '0' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
                scaleInBounce: {
                    '0%': { transform: 'scale(0)', opacity: '0' },
                    '50%': { transform: 'scale(1.1)' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
                    '50%': { transform: 'translateY(-20px) rotate(2deg)' },
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
                    '0%': { strokeDashoffset: '283' },
                    '100%': { strokeDashoffset: '0' },
                },
                spinReverse: {
                    '0%': { transform: 'rotate(360deg)' },
                    '100%': { transform: 'rotate(0deg)' },
                },
                gradientX: {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                },
                gradientY: {
                    '0%, 100%': { backgroundPosition: '50% 0%' },
                    '50%': { backgroundPosition: '50% 100%' },
                },
                gradientXY: {
                    '0%, 100%': { backgroundPosition: '0% 0%' },
                    '25%': { backgroundPosition: '100% 0%' },
                    '50%': { backgroundPosition: '100% 100%' },
                    '75%': { backgroundPosition: '0% 100%' },
                },
                aurora: {
                    '0%, 100%': {
                        backgroundPosition: '50% 50%',
                        transform: 'rotate(0deg) scale(1)'
                    },
                    '25%': {
                        backgroundPosition: '0% 50%',
                        transform: 'rotate(3deg) scale(1.02)'
                    },
                    '50%': {
                        backgroundPosition: '50% 100%',
                        transform: 'rotate(0deg) scale(1)'
                    },
                    '75%': {
                        backgroundPosition: '100% 50%',
                        transform: 'rotate(-3deg) scale(1.02)'
                    },
                },
                ticker: {
                    '0%': { transform: 'translateX(0)' },
                    '100%': { transform: 'translateX(-50%)' },
                },
                glowPulse: {
                    '0%, 100%': {
                        boxShadow: '0 0 20px rgba(59, 130, 246, 0.3), 0 0 40px rgba(59, 130, 246, 0.2)'
                    },
                    '50%': {
                        boxShadow: '0 0 30px rgba(59, 130, 246, 0.5), 0 0 60px rgba(59, 130, 246, 0.3)'
                    },
                },
                ringPulse: {
                    '0%': {
                        transform: 'scale(0.8)',
                        opacity: '0.8'
                    },
                    '100%': {
                        transform: 'scale(1.3)',
                        opacity: '0'
                    },
                },
                scoreFill: {
                    '0%': {
                        strokeDashoffset: '283',
                        filter: 'drop-shadow(0 0 0px currentColor)'
                    },
                    '100%': {
                        strokeDashoffset: 'var(--score-offset)',
                        filter: 'drop-shadow(0 0 8px currentColor)'
                    },
                },
                typewriter: {
                    '0%, 100%': { width: '0' },
                    '50%': { width: '100%' },
                },
                bounceSubtle: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-5px)' },
                },
                wiggle: {
                    '0%, 100%': { transform: 'rotate(-3deg)' },
                    '50%': { transform: 'rotate(3deg)' },
                },
            },
            transitionTimingFunction: {
                'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
                'smooth-out': 'cubic-bezier(0.22, 1, 0.36, 1)',
                'elastic': 'cubic-bezier(0.68, -0.6, 0.32, 1.6)',
            },
            transitionDuration: {
                '400': '400ms',
                '600': '600ms',
                '800': '800ms',
                '900': '900ms',
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
                'shimmer': 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%)',
                'glass-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0))',
                'aurora-gradient': 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 25%, #06b6d4 50%, #10b981 75%, #3b82f6 100%)',
                'mesh-gradient': 'radial-gradient(at 40% 20%, hsla(228,86%,86%,1) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(189,100%,86%,1) 0px, transparent 50%), radial-gradient(at 0% 50%, hsla(355,100%,93%,1) 0px, transparent 50%)',
                'hero-dark': 'radial-gradient(ellipse at top, rgba(59, 130, 246, 0.15) 0%, transparent 50%), radial-gradient(ellipse at bottom right, rgba(139, 92, 246, 0.1) 0%, transparent 50%)',
            },
            backgroundImage: {
                'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E\")",
            },
            maskImage: {
                'gradient-fade-bottom': 'linear-gradient(to bottom, black 80%, transparent 100%)',
                'gradient-fade-top': 'linear-gradient(to top, black 80%, transparent 100%)',
            },
        },
    },
    plugins: [],
}