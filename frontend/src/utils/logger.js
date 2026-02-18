/**
 * Centralized logger for the frontend application.
 * Filters logs based on environment (development vs production).
 */

const IS_PROD = process.env.NODE_ENV === 'production';

const logger = {
    debug: (...args) => {
        if (!IS_PROD) {
            console.debug('[DEBUG]', ...args);
        }
    },

    info: (...args) => {
        if (!IS_PROD) {
            console.info('[INFO]', ...args);
        }
    },

    warn: (...args) => {
        // Warnings are shown in both environments but with a prefix
        console.warn('[WARN]', ...args);
    },

    error: (...args) => {
        // Errors are always shown
        console.error('[ERROR]', ...args);
    },

    // Specifically for API requests/responses in dev
    api: (config, isRequest = true) => {
        if (!IS_PROD) {
            const method = config.method?.toUpperCase();
            const url = config.url;
            if (isRequest) {
                console.debug(`%c[API Request] %c${method} ${url}`, 'color: #3b82f6; font-weight: bold', 'color: inherit');
            } else {
                console.debug(`%c[API Response] %c${config.status} ${method} ${url}`, 'color: #10b981; font-weight: bold', 'color: inherit');
            }
        }
    }
};

export default logger;
