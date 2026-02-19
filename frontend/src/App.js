import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import PropertyDetailsPage from './pages/PropertyDetailsPage';
import AboutPage from './pages/AboutPage';

function App() {
    return (
        <Router>
            <div className="flex flex-col min-h-screen bg-dark-900 text-white antialiased">
                {/* Global Aurora Background */}
                <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
                    <div className="absolute inset-0 bg-hero-dark opacity-30" />
                    <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-primary-500/10 rounded-full blur-[150px] animate-blob-slow" />
                    <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[120px] animate-blob-slower animation-delay-2000" />
                    <div className="absolute top-1/2 left-1/3 w-[400px] h-[400px] bg-cyan-500/5 rounded-full blur-[100px] animate-blob animation-delay-4000" />
                    <div className="absolute inset-0 noise-overlay opacity-50" />
                </div>

                {/* Content */}
                <div className="relative z-10 flex flex-col min-h-screen">
                    <Header />
                    <main className="flex-grow">
                        <Routes>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/search" element={<SearchPage />} />
                            <Route path="/property/:municipalityId" element={<PropertyDetailsPage />} />
                            <Route path="/about" element={<AboutPage />} />
                        </Routes>
                    </main>
                    <Footer />
                </div>
            </div>
        </Router>
    );
}


