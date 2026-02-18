import React, { useState, useEffect, useRef } from 'react';
import { locationAPI } from '../../services/api';
import logger from '../../utils/logger';

const SearchBar = ({
    onSearch,
    placeholder = 'Search by municipality, province, or region...',
    size = 'default',
    showSuggestions = true
}) => {
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(-1);
    const inputRef = useRef(null);
    const dropdownRef = useRef(null);

    // Debounced search for suggestions
    useEffect(() => {
        if (!showSuggestions || query.length < 2) {
            setSuggestions([]);
            return;
        }

        const debounceTimer = setTimeout(async () => {
            try {
                const result = await locationAPI.search(query);
                if (result && result.found && result.municipality) {
                    setSuggestions([{
                        id: result.municipality.id,
                        name: result.municipality.name,
                        province: result.municipality.province_name,
                        region: result.municipality.region_name,
                        score: result.municipality.investment_score
                    }]);
                } else {
                    setSuggestions([]);
                }
            } catch (err) {
                logger.error('Suggestion fetch error:', err);
                setSuggestions([]);
            }
        }, 300);

        return () => clearTimeout(debounceTimer);
    }, [query, showSuggestions]);

    // Close dropdown on outside click
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target) &&
                inputRef.current && !inputRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsLoading(true);
        setShowDropdown(false);
        try {
            await onSearch(query.trim());
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setQuery(suggestion.name);
        setShowDropdown(false);
        onSearch(suggestion.name);
    };

    const handleKeyDown = (e) => {
        if (!showDropdown || suggestions.length === 0) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(prev => Math.min(prev + 1, suggestions.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(prev => Math.max(prev - 1, -1));
        } else if (e.key === 'Enter' && selectedIndex >= 0) {
            e.preventDefault();
            handleSuggestionClick(suggestions[selectedIndex]);
        } else if (e.key === 'Escape') {
            setShowDropdown(false);
        }
    };

    const getScoreColor = (score) => {
        if (score >= 7) return 'bg-success-500';
        if (score >= 5) return 'bg-warning-500';
        return 'bg-danger-500';
    };

    const isLarge = size === 'large';

    return (
        <form onSubmit={handleSubmit} className="w-full relative">
            <div className="relative group">
                {/* Search Icon */}
                <div className={`absolute inset-y-0 left-0 flex items-center ${isLarge ? 'pl-5' : 'pl-4'}`}>
                    <svg
                        className={`${isLarge ? 'w-6 h-6' : 'w-5 h-5'} text-gray-400 group-focus-within:text-primary-500 transition-colors`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        />
                    </svg>
                </div>

                {/* Input */}
                <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => {
                        setQuery(e.target.value);
                        setShowDropdown(true);
                        setSelectedIndex(-1);
                    }}
                    onFocus={() => setShowDropdown(true)}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                    className={`w-full bg-white border border-gray-200 text-gray-900 rounded-2xl transition-all duration-200 outline-none
                        ${isLarge
                            ? 'px-6 py-5 pl-14 pr-36 text-lg'
                            : 'px-4 py-4 pl-12 pr-28 text-base'
                        }
                        focus:ring-4 focus:ring-primary-100 focus:border-primary-500
                        hover:border-gray-300
                        shadow-sm hover:shadow-md focus:shadow-lg
                        placeholder:text-gray-400
                    `}
                    disabled={isLoading}
                    aria-label="Search municipalities"
                    aria-autocomplete="list"
                    aria-controls="search-suggestions"
                    aria-expanded={showDropdown}
                />

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={isLoading || !query.trim()}
                    className={`absolute right-2 top-1/2 -translate-y-1/2 bg-primary-600 text-white font-bold rounded-xl
                        hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed 
                        transition-all duration-200 shadow-lg shadow-primary-600/25
                        active:scale-[0.98] 
                        ${isLarge ? 'px-8 py-3.5 text-base' : 'px-6 py-2.5 text-sm'}
                    `}
                >
                    {isLoading ? (
                        <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            <span>Searching</span>
                        </div>
                    ) : (
                        <div className="flex items-center space-x-2">
                            <span>Search</span>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                            </svg>
                        </div>
                    )}
                </button>

                {/* Suggestions Dropdown */}
                {showDropdown && suggestions.length > 0 && (
                    <div
                        ref={dropdownRef}
                        id="search-suggestions"
                        className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden z-50 animate-slide-down"
                        role="listbox"
                    >
                        {suggestions.map((suggestion, index) => (
                            <button
                                key={suggestion.id}
                                type="button"
                                onClick={() => handleSuggestionClick(suggestion)}
                                className={`w-full px-5 py-4 flex items-center justify-between text-left transition-colors
                                    ${index === selectedIndex ? 'bg-primary-50' : 'hover:bg-gray-50'}
                                    ${index !== suggestions.length - 1 ? 'border-b border-gray-50' : ''}
                                `}
                                role="option"
                                aria-selected={index === selectedIndex}
                            >
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center text-gray-500">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                        </svg>
                                    </div>
                                    <div>
                                        <div className="font-bold text-gray-900">{suggestion.name}</div>
                                        <div className="text-sm text-gray-500">
                                            {suggestion.province}, {suggestion.region}
                                        </div>
                                    </div>
                                </div>
                                {suggestion.score && (
                                    <div className="flex items-center space-x-2">
                                        <div className={`w-2 h-2 rounded-full ${getScoreColor(suggestion.score)}`} />
                                        <span className="text-sm font-bold text-gray-600">
                                            {suggestion.score.toFixed(1)}
                                        </span>
                                    </div>
                                )}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* Keyboard hint */}
            {showDropdown && suggestions.length > 0 && (
                <div className="absolute -bottom-6 left-0 text-xs text-gray-400">
                    <span className="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] font-mono">↑↓</span>
                    <span className="ml-1">to navigate</span>
                    <span className="ml-3 px-1.5 py-0.5 bg-gray-100 rounded text-[10px] font-mono">Enter</span>
                    <span className="ml-1">to select</span>
                </div>
            )}
        </form>
    );
};

export default SearchBar;
