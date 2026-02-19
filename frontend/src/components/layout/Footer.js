import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
    const [email, setEmail] = useState('');
    const [subscribed, setSubscribed] = useState(false);

    const handleNewsletterSubmit = (e) => {
        e.preventDefault();
        if (email) {
            setSubscribed(true);
            setEmail('');
            setTimeout(() => setSubscribed(false), 3000);
        }
    };

    const currentYear = new Date().getFullYear();

    const footerLinks = {
        platform: [
            { label: 'Discover Towns', path: '/search' },
            { label: 'How It Works', path: '/about' },
            { label: 'Data Sources', path: '/about#data' },
            { label: 'API Access', path: '#', disabled: true },
        ],
        resources: [
            { label: 'Investment Guides', path: '#', disabled: true },
            { label: 'Market Reports', path: '#', disabled: true },
            { label: 'Blog', path: '#', disabled: true },
            { label: 'Support', path: '#', disabled: true },
        ],
        legal: [
            { label: 'Privacy Policy', path: '#' },
            { label: 'Terms of Service', path: '#' },
            { label: 'Cookie Policy', path: '#' },
            { label: 'GDPR', path: '#' },
        ],
    };

    const dataSources = [
        { name: 'OMI', desc: 'Agenzia delle Entrate' },
        { name: 'ISTAT', desc: 'National Statistics' },
        { name: 'ISPRA', desc: 'Environmental Data' },
        { name: 'INGV', desc: 'Seismic Monitoring' },
        { name: 'ARPA', desc: 'Air Quality' },
        { name: 'OSM', desc: 'Infrastructure' },
    ];

    return (
        <footer className="bg-dark-900 border-t border-white/5 relative overflow-hidden">
            {/* Background Decoration */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl" />
            </div>

            <div className="relative">
                {/* Newsletter Section */}
                <div className="border-b border-white/5">
                    <div className="container mx-auto px-4 py-12 lg:py-16">
                        <div className="max-w-4xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-8">
                            <div className="text-center lg:text-left">
                                <h3 className="text-2xl lg:text-3xl font-black text-white tracking-tight mb-2">Stay ahead of the market</h3>
                                <p className="text-white/50 text-sm lg:text-base">Get weekly insights on Italian real estate trends and opportunities.</p>
                            </div>
                            <form onSubmit={handleNewsletterSubmit} className="flex w-full max-w-md">
                                <div className="relative flex-1">
                                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Enter your email" className="w-full px-5 py-4 bg-white/5 border border-white/10 rounded-l-xl text-white placeholder-white/40 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all" disabled={subscribed} />
                                </div>
                                <button type="submit" disabled={subscribed} className={`px-6 py-4 font-bold rounded-r-xl transition-all duration-300 ${subscribed ? 'bg-success-500 text-white' : 'bg-primary-600 text-white hover:bg-primary-500'}`}>
                                    {subscribed ? (
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                                    ) : 'Subscribe'}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>

                {/* Main Footer Content */}
                <div className="container mx-auto px-4 py-12 lg:py-16">
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 lg:gap-12">
                        {/* Brand Column */}
                        <div className="col-span-2">
                            <Link to="/" className="flex items-center space-x-3 mb-6">
                                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center">
                                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
                                </div>
                                <div>
                                    <h2 className="text-lg font-black text-white">SafeSquare</h2>
                                    <p className="text-xs text-white/40 font-medium">Italian Real Estate Intel</p>
                                </div>
                            </Link>
                            <p className="text-white/40 text-sm leading-relaxed mb-6 max-w-xs">The first intelligence platform combining market value, demographics, and risk data for definitive investment insights across 7,900+ Italian municipalities.</p>
                            {/* Social Links */}
                            <div className="flex space-x-3">
                                {['twitter', 'linkedin', 'github'].map((social) => (
                                    <a key={social} href="#" className="w-9 h-9 bg-white/5 border border-white/10 rounded-lg flex items-center justify-center text-white/40 hover:bg-primary-500/20 hover:border-primary-500/30 hover:text-primary-400 transition-all duration-200">
                                        {social === 'twitter' && (
                                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>
                                        )}
                                        {social === 'linkedin' && (
                                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" /></svg>
                                        )}
                                        {social === 'github' && (
                                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" /></svg>
                                        )}
                                    </a>
                                ))}
                            </div>
                        </div>

                        {/* Platform Links */}
                        <div>
                            <h4 className="text-xs font-bold text-white/50 uppercase tracking-widest mb-4">Platform</h4>
                            <ul className="space-y-3">
                                {footerLinks.platform.map((link) => (
                                    <li key={link.label}>
                                        <Link to={link.path} className={`text-sm transition-colors ${link.disabled ? 'text-white/30 cursor-not-allowed' : 'text-white/60 hover:text-white'}`}>
                                            {link.label}
                                            {link.disabled && <span className="ml-2 text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-white/30">Soon</span>}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Resources Links */}
                        <div>
                            <h4 className="text-xs font-bold text-white/50 uppercase tracking-widest mb-4">Resources</h4>
                            <ul className="space-y-3">
                                {footerLinks.resources.map((link) => (
                                    <li key={link.label}>
                                        <Link to={link.path} className={`text-sm transition-colors ${link.disabled ? 'text-white/30 cursor-not-allowed' : 'text-white/60 hover:text-white'}`}>
                                            {link.label}
                                            {link.disabled && <span className="ml-2 text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-white/30">Soon</span>}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Data Sources */}
                        <div className="col-span-2 md:col-span-4 lg:col-span-2">
                            <h4 className="text-xs font-bold text-white/50 uppercase tracking-widest mb-4">Data Partners</h4>
                            <div className="grid grid-cols-3 gap-3">
                                {dataSources.map((source) => (
                                    <div key={source.name} className="bg-white/5 border border-white/5 rounded-xl px-3 py-2 text-center hover:bg-white/10 hover:border-white/10 transition-colors">
                                        <div className="text-sm font-bold text-white">{source.name}</div>
                                        <div className="text-[10px] text-white/40">{source.desc}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="border-t border-white/5">
                    <div className="container mx-auto px-4 py-6">
                        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                            <p className="text-sm text-white/40">© {currentYear} SafeSquare. All rights reserved.</p>
                            <div className="flex items-center space-x-6">
                                {footerLinks.legal.map((link) => (
                                    <Link key={link.label} to={link.path} className="text-xs text-white/40 hover:text-white/60 transition-colors">{link.label}</Link>
                                ))}
                            </div>
                            <p className="text-xs text-white/30">Made with ♥ for Italian Real Estate</p>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;