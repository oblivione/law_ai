import React from 'react';
import { Link } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  DocumentTextIcon, 
  ChartBarIcon, 
  ArrowUpTrayIcon,
  ScaleIcon,
  LightBulbIcon,
  BookOpenIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

const HomePage: React.FC = () => {
  const features = [
    {
      name: 'AI-Powered Search',
      description: 'Semantic search across legal documents with intelligent ranking and relevance scoring.',
      icon: MagnifyingGlassIcon,
      href: '/search',
      color: 'text-legal-600'
    },
    {
      name: 'Legal Analysis',
      description: 'Comprehensive AI analysis with citations, precedents, and legal reasoning.',
      icon: ChartBarIcon,
      href: '/analysis',
      color: 'text-justice-600'
    },
    {
      name: 'Document Upload',
      description: 'Upload and process legal documents with automatic text extraction and chunking.',
      icon: ArrowUpTrayIcon,
      href: '/upload',
      color: 'text-legal-700'
    }
  ];

  const stats = [
    { name: 'Legal Documents', value: '10,000+', icon: DocumentTextIcon },
    { name: 'AI Models', value: '3', icon: SparklesIcon },
    { name: 'Search Accuracy', value: '95%', icon: LightBulbIcon },
    { name: 'Processing Speed', value: '<1s', icon: BookOpenIcon },
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-8">
        <div className="flex justify-center">
          <ScaleIcon className="h-16 w-16 text-legal-600" />
        </div>
        
        <div className="space-y-4">
          <h1 className="text-4xl font-bold text-justice-900 sm:text-5xl lg:text-6xl">
            AI-Powered Legal
            <span className="text-gradient block">Document Search</span>
          </h1>
          
          <p className="text-xl text-justice-600 max-w-3xl mx-auto leading-relaxed">
            Revolutionize your legal research with advanced semantic search, 
            intelligent document analysis, and AI-driven legal reasoning.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/search"
            className="btn-primary inline-flex items-center space-x-2 text-lg px-8 py-3"
          >
            <MagnifyingGlassIcon className="h-6 w-6" />
            <span>Start Searching</span>
          </Link>
          
          <Link
            to="/upload"
            className="btn-secondary inline-flex items-center space-x-2 text-lg px-8 py-3"
          >
            <ArrowUpTrayIcon className="h-6 w-6" />
            <span>Upload Documents</span>
          </Link>
        </div>
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="text-center">
            <div className="flex justify-center mb-2">
              <stat.icon className="h-8 w-8 text-legal-600" />
            </div>
            <div className="text-2xl font-bold text-justice-900">{stat.value}</div>
            <div className="text-sm text-justice-600">{stat.name}</div>
          </div>
        ))}
      </div>

      {/* Features Section */}
      <div className="space-y-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-justice-900">
            Powerful Features for Legal Professionals
          </h2>
          <p className="mt-4 text-lg text-justice-600">
            Everything you need for comprehensive legal document research and analysis.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          {features.map((feature) => (
            <Link
              key={feature.name}
              to={feature.href}
              className="card-hover group"
            >
              <div className="flex items-center space-x-3 mb-4">
                <feature.icon className={`h-8 w-8 ${feature.color} group-hover:scale-110 transition-transform duration-200`} />
                <h3 className="text-xl font-semibold text-justice-900">{feature.name}</h3>
              </div>
              <p className="text-justice-700">{feature.description}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* How it Works Section */}
      <div className="space-y-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-justice-900">How It Works</h2>
          <p className="mt-4 text-lg text-justice-600">
            Simple, powerful, and intelligent legal document processing.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="rounded-full bg-legal-100 p-4">
                <ArrowUpTrayIcon className="h-8 w-8 text-legal-600" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-justice-900">1. Upload</h3>
            <p className="text-justice-700">
              Upload your legal documents in PDF, DOCX, or TXT format. 
              Our system automatically processes and extracts text.
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="rounded-full bg-legal-100 p-4">
                <SparklesIcon className="h-8 w-8 text-legal-600" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-justice-900">2. Process</h3>
            <p className="text-justice-700">
              AI analyzes documents, extracts legal entities, creates embeddings, 
              and identifies key concepts and citations.
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="rounded-full bg-legal-100 p-4">
                <MagnifyingGlassIcon className="h-8 w-8 text-legal-600" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-justice-900">3. Search & Analyze</h3>
            <p className="text-justice-700">
              Perform semantic searches, get AI-powered legal analysis, 
              and discover relevant precedents and citations.
            </p>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-legal-600 to-legal-800 rounded-2xl p-8 text-center text-white">
        <h2 className="text-3xl font-bold mb-4">
          Ready to Transform Your Legal Research?
        </h2>
        <p className="text-lg mb-6 opacity-90">
          Join thousands of legal professionals using AI-powered document analysis.
        </p>
        <Link
          to="/search"
          className="inline-flex items-center space-x-2 bg-white text-legal-700 font-semibold px-6 py-3 rounded-lg hover:bg-legal-50 transition-colors duration-200"
        >
          <MagnifyingGlassIcon className="h-5 w-5" />
          <span>Get Started Now</span>
        </Link>
      </div>
    </div>
  );
};

export default HomePage; 