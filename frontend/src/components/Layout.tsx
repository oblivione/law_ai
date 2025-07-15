import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  DocumentTextIcon, 
  ChartBarIcon, 
  ArrowUpTrayIcon,
  ScaleIcon
} from '@heroicons/react/24/outline';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Search', href: '/search', icon: MagnifyingGlassIcon },
    { name: 'Analysis', href: '/analysis', icon: ChartBarIcon },
    { name: 'Upload', href: '/upload', icon: ArrowUpTrayIcon },
  ];

  return (
    <div className="min-h-screen bg-justice-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-justice-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3">
              <ScaleIcon className="h-8 w-8 text-legal-600" />
              <div>
                <h1 className="text-xl font-bold text-justice-900">LegalSearch</h1>
                <p className="text-xs text-justice-600">AI-Powered Legal Research</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="flex space-x-8">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                      isActive
                        ? 'bg-legal-100 text-legal-700'
                        : 'text-justice-600 hover:text-justice-900 hover:bg-justice-100'
                    }`}
                  >
                    <item.icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-justice-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <ScaleIcon className="h-6 w-6 text-legal-600" />
              <span className="text-sm text-justice-600">
                © 2024 LegalSearch. AI-powered legal document analysis.
              </span>
            </div>
            <div className="flex space-x-6">
              <a href="#" className="text-sm text-justice-600 hover:text-justice-900">
                Privacy Policy
              </a>
              <a href="#" className="text-sm text-justice-600 hover:text-justice-900">
                Terms of Service
              </a>
              <a href="#" className="text-sm text-justice-600 hover:text-justice-900">
                Support
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout; 