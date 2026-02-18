import { render, screen } from '@testing-library/react';
import StatCard from '../dashboard/StatCard';

describe('StatCard Component', () => {
    test('renders title and value', () => {
        render(<StatCard title="Total Price" value="€500.000" />);
        expect(screen.getByText('Total Price')).toBeInTheDocument();
        expect(screen.getByText('€500.000')).toBeInTheDocument();
    });

    test('renders trend if provided', () => {
        render(<StatCard title="Growth" value="5%" trend={2.5} />);
        expect(screen.getByText('2.5%')).toBeInTheDocument();
        // Check for trend icon/color indirectly or just content
    });

    test('renders subtitle if provided', () => {
        render(<StatCard title="Stats" value="100" subtitle="Per year" />);
        expect(screen.getByText('Per year')).toBeInTheDocument();
    });
});
