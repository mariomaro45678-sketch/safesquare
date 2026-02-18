import {
    formatCurrency,
    formatPercentage,
    formatNumber,
    getScoreColor
} from '../formatters';

describe('Formatter Utilities', () => {
    describe('formatCurrency', () => {
        test('formats numbers as Euro currency', () => {
            expect(formatCurrency(1250)).toBe('€1.250');
            expect(formatCurrency(1000000)).toBe('€1.000.000');
        });

        test('handles null or undefined values', () => {
            expect(formatCurrency(null)).toBe('N/A');
            expect(formatCurrency(undefined)).toBe('N/A');
        });
    });

    describe('formatPercentage', () => {
        test('formats numbers as percentages', () => {
            expect(formatPercentage(5.5)).toBe('5.5%');
            expect(formatPercentage(0)).toBe('0.0%');
        });
    });

    describe('getScoreColor', () => {
        test('returns green for high scores', () => {
            expect(getScoreColor(8.5)).toContain('green');
            expect(getScoreColor(10)).toContain('green');
        });

        test('returns yellow for medium scores', () => {
            expect(getScoreColor(6.0)).toContain('yellow');
        });

        test('returns red for low scores', () => {
            expect(getScoreColor(3.5)).toContain('red');
        });
    });
});
