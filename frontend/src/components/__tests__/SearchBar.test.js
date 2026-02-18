import { render, screen, fireEvent } from '@testing-library/react';
import SearchBar from '../search/SearchBar';

describe('SearchBar Component', () => {
    test('renders with placeholder', () => {
        render(<SearchBar placeholder="Test Placeholder" onSearch={() => { }} />);
        expect(screen.getByPlaceholderText('Test Placeholder')).toBeInTheDocument();
    });

    test('updates value on change', () => {
        render(<SearchBar onSearch={() => { }} />);
        const input = screen.getByRole('textbox');
        fireEvent.change(input, { target: { value: 'Milano' } });
        expect(input.value).toBe('Milano');
    });

    test('calls onSearch when submitted', () => {
        const mockSearch = jest.fn();
        render(<SearchBar onSearch={mockSearch} />);
        const input = screen.getByRole('textbox');
        const button = screen.getByRole('button');

        fireEvent.change(input, { target: { value: 'Milano' } });
        fireEvent.click(button);

        expect(mockSearch).toHaveBeenCalledWith('Milano');
    });
});
