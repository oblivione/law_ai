import React, { useState } from 'react';
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'semantic' | 'keyword' | 'hybrid'>('hybrid');
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement search functionality
    console.log('Searching for:', query, 'Type:', searchType);
  };

  return (
    <div className="space-y-8">
      {/* Search Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-justice-900">Legal Document Search</h1>
        <p className="text-lg text-justice-600">
          Search through thousands of legal documents using AI-powered semantic search
        </p>
      </div>

      {/* Search Form */}
      <div className="card max-w-4xl mx-auto">
        <form onSubmit={handleSearch} className="space-y-6">
          {/* Main Search Input */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-justice-400" />
            </div>
            <input
              type="text"
              className="input-field pl-10 text-lg h-14"
              placeholder="Enter your legal query (e.g., 'contract breach remedies')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          {/* Search Options */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
            {/* Search Type */}
            <div className="flex space-x-4">
              <label className="text-sm font-medium text-justice-700">Search Type:</label>
              <div className="flex space-x-4">
                {[
                  { value: 'semantic', label: 'Semantic' },
                  { value: 'keyword', label: 'Keyword' },
                  { value: 'hybrid', label: 'Hybrid' }
                ].map((type) => (
                  <label key={type.value} className="flex items-center">
                    <input
                      type="radio"
                      name="searchType"
                      value={type.value}
                      checked={searchType === type.value}
                      onChange={(e) => setSearchType(e.target.value as any)}
                      className="h-4 w-4 text-legal-600 focus:ring-legal-500 border-justice-300"
                    />
                    <span className="ml-2 text-sm text-justice-700">{type.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Filters Toggle */}
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="btn-ghost flex items-center space-x-2"
            >
              <AdjustmentsHorizontalIcon className="h-5 w-5" />
              <span>Filters</span>
            </button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="border-t border-justice-200 pt-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-justice-700 mb-2">
                    Document Type
                  </label>
                  <select className="input-field">
                    <option value="">All Types</option>
                    <option value="court_decision">Court Decision</option>
                    <option value="statute">Statute</option>
                    <option value="regulation">Regulation</option>
                    <option value="contract">Contract</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-justice-700 mb-2">
                    Jurisdiction
                  </label>
                  <select className="input-field">
                    <option value="">All Jurisdictions</option>
                    <option value="federal">Federal</option>
                    <option value="state">State</option>
                    <option value="california">California</option>
                    <option value="new_york">New York</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-justice-700 mb-2">
                    Date Range
                  </label>
                  <select className="input-field">
                    <option value="">All Dates</option>
                    <option value="last_year">Last Year</option>
                    <option value="last_5_years">Last 5 Years</option>
                    <option value="last_10_years">Last 10 Years</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Search Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              className="btn-primary px-8 py-3 text-lg"
              disabled={!query.trim()}
            >
              Search Documents
            </button>
          </div>
        </form>
      </div>

      {/* Search Results Placeholder */}
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-justice-900">Search Results</h2>
          <p className="text-sm text-justice-600">Search to see results</p>
        </div>

        {/* Example Results */}
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card-hover">
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="document-title">Example Legal Document {i}</h3>
                    <p className="document-meta">
                      Court Decision • Federal • 2023-01-15 • Page 12
                    </p>
                  </div>
                  <div className="text-sm font-medium text-legal-600">
                    Relevance: 95%
                  </div>
                </div>
                
                <p className="search-result-snippet">
                  This is an example search result snippet that would show the relevant 
                  text from the document with <span className="search-highlight">highlighted</span> search terms 
                  and contextual information about the legal content...
                </p>
                
                <div className="flex flex-wrap gap-2">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-legal-100 text-legal-800">
                    Contract Law
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-justice-100 text-justice-800">
                    Breach of Contract
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-legal-100 text-legal-800">
                    Damages
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SearchPage; 