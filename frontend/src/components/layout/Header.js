import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const Header = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    useEffect(() => {
        setIsMobileMenuOpen(false);
    }, [location]);

    const isActive = (path) => location.pathname === path;

    const handleQuickSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
            setSearchQuery('');
        }
    };

    const navLinks = [
        { path: '/', label: 'Home' },
        { path: '/search', label: 'Discover' },
        { path: '/about', label: 'About' },
    ];

    return (
        <>
            <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? 'glass shadow-lg' : 'bg-transparent'}`}>
                <div className="container mx-auto px-4">
                    <div className="flex items-center justify-between h-16 lg:h-20">
                        {/* Logo */}
                        <Link to="/" className="flex items-center space-x-3 group">
                            <div className="relative">
                                <div className="w-10 h-10 lg:w-12 lg:h-12 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-glow transition-all duration-300 group-hover:scale-105">
                                    <svg className="w-5 h-5 lg:w-6 lg:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                    </svg>
                                </div>
                                <div className="absolute -top-1 -right-1 w-3 h-3 bg-success-500 rounded-full border-2 border-dark-900 animate-pulse" />
                            </div>
                            <div className="hidden md:block">
                                <h1 className="text-lg lg:text-xl font-black text-white tracking-tight leading-none">SafeSquare</h1>
                                <p className="text-[10px] lg:text-xs text-white/50 font-semibold tracking-wider uppercase">Italian Real Estate Intel</p>
                            </div>
                        </Link>

                        {/* Desktop Navigation */}
                        <nav className="hidden lg:flex items-center space-x-1">
                            {navLinks.map((link) => (
                                <Link key={link.path} to={link.path} className={`relative px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${isActive(link.path) ? 'text-primary-400' : 'text-white/60 hover:text-white hover:bg-white/5'}`}>
                                    {link.label}
                                    {isActive(link.path) && <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary-400 rounded-full" />}
                                </Link>
                            ))}
                        </nav>

                        {/* Desktop Search & CTA */}
                        <div className="hidden lg:flex items-center space-x-4">
                            <form onSubmit={handleQuickSearch} className="relative">
                                <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Quick search..." className="w-48 xl:w-56 px-4 py-2 pl-10 text-sm bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/40 focus:bg-white/10 focus:border-white/20 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200 outline-none" />
                                <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                            </form>
                            <Link to="/search" className="btn btn-primary btn-sm">
                                <span>Start Exploring</span>
                                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
                            </Link>
                        </div>

                        {/* Mobile Menu Button */}
                        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="lg:hidden p-2 rounded-xl text-white/60 hover:bg-white/10 transition-colors" aria-label="Toggle menu">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                {isMobileMenuOpen ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /> : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Mobile Menu */}
                <div className={`lg:hidden fixed inset-x-0 top-16 glass border-t border-white/10 transition-all duration-300 ${isMobileMenuOpen ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'}`}>
                    <div className="container mx-auto px-4 py-6 space-y-4">
                        <form onSubmit={handleQuickSearch} className="relative">
                            <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search municipalities..." className="w-full px-4 py-3 pl-12 text-base bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/40 focus:bg-white/10 focus:border-white/20 outline-none" />
                            <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                        </form>
                        <nav className="space-y-1">
                            {navLinks.map((link) => (
                                <Link key={link.path} to={link.path} className={`flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 ${isActive(link.path) ? 'bg-primary-500/20 text-primary-400' : 'text-white/60 hover:bg-white/5 hover:text-white'}`}>
                                    <span className="font-semibold">{link.label}</span>
                                    <svg className="w-4 h-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                                </Link>
                            ))}
                        </nav>
                        <Link to="/search" className="btn btn-primary w-full justify-center">Start Exploring</Link>
                    </div>
                </div>
            </header>

            {/* Spacer for fixed header */}
            <div className="h-16 lg:h-20" />
        </>
    );
};

export default Header;