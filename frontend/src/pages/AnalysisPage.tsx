import React, { useState } from 'react';
import { 
  ChartBarIcon, 
  SparklesIcon, 
  DocumentTextIcon,
  LightBulbIcon,
  ExclamationTriangleIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline';

interface AnalysisResult {
  query: string;
  analysis: string;
  keyPoints: string[];
  citations: string[];
  precedents: string[];
  counterarguments: string[];
  confidenceScore: number;
  sources: number[];
}

const AnalysisPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [analysisType, setAnalysisType] = useState<'general' | 'case_law' | 'statute' | 'precedent'>('general');
  const [includeCitations, setIncludeCitations] = useState(true);
  const [includeCounterarguments, setIncludeCounterarguments] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsAnalyzing(true);
    
    // Simulate API call
    setTimeout(() => {
      const mockResult: AnalysisResult = {
        query,
        analysis: `Based on the comprehensive analysis of relevant legal documents and precedents, the issue of ${query.toLowerCase()} involves several key legal considerations that must be carefully examined.

The primary legal framework governing this matter is established through a combination of statutory provisions, case law precedents, and regulatory guidelines. The analysis reveals that courts have consistently held that the fundamental principles of due process and equitable treatment must be maintained throughout any legal proceedings.

Key statutory provisions include relevant sections of federal and state codes that establish the foundational legal requirements. These provisions work in conjunction with established precedential decisions that have shaped the current interpretation and application of the law.

The judicial interpretation has evolved over time, with courts increasingly recognizing the need for balanced approaches that consider both traditional legal principles and contemporary societal needs. This evolution reflects the dynamic nature of legal interpretation and the importance of adapting legal frameworks to current circumstances.`,
        
        keyPoints: [
          'Due process requirements must be strictly observed',
          'Statutory compliance is mandatory across all jurisdictions',
          'Precedential decisions provide guidance for interpretation',
          'Equitable remedies may be available in appropriate circumstances',
          'Constitutional considerations may override statutory provisions'
        ],
        
        citations: [
          '42 U.S.C. § 1983',
          'Miranda v. Arizona, 384 U.S. 436 (1966)',
          'Brown v. Board of Education, 347 U.S. 483 (1954)',
          '14th Amendment to the U.S. Constitution',
          'Federal Rules of Civil Procedure Rule 12(b)(6)'
        ],
        
        precedents: [
          'Smith v. Jones (2023) - Established modern interpretation standards',
          'United States v. Williams (2022) - Clarified procedural requirements',
          'Johnson v. State (2021) - Defined scope of constitutional protections',
          'Davis v. County (2020) - Set precedent for equitable remedies'
        ],
        
        counterarguments: [
          'Alternative interpretations suggest narrower application scope',
          'Some jurisdictions have adopted more restrictive approaches',
          'Recent legislative changes may limit traditional remedies',
          'Constitutional challenges to current framework are pending'
        ],
        
        confidenceScore: 0.87,
        sources: [1, 3, 7, 12, 15, 23, 28]
      };
      
      setResult(mockResult);
      setIsAnalyzing(false);
    }, 3000);
  };

  const analysisTypes = [
    { value: 'general', label: 'General Analysis', description: 'Comprehensive legal analysis' },
    { value: 'case_law', label: 'Case Law Focus', description: 'Focus on judicial precedents' },
    { value: 'statute', label: 'Statutory Analysis', description: 'Focus on legislative provisions' },
    { value: 'precedent', label: 'Precedent Review', description: 'Focus on precedential value' }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-justice-900">Legal Analysis</h1>
        <p className="text-lg text-justice-600">
          AI-powered comprehensive legal analysis with citations, precedents, and reasoning
        </p>
      </div>

      {/* Analysis Form */}
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleAnalysis} className="card space-y-6">
          <div>
            <label className="block text-sm font-medium text-justice-700 mb-2">
              Legal Query
            </label>
            <textarea
              className="input-field h-32"
              placeholder="Enter your legal question or issue for comprehensive AI analysis (e.g., 'What are the requirements for establishing a breach of contract claim?')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
            />
          </div>

          {/* Analysis Type Selection */}
          <div>
            <label className="block text-sm font-medium text-justice-700 mb-3">
              Analysis Type
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysisTypes.map((type) => (
                <label
                  key={type.value}
                  className={`flex items-start p-4 border rounded-lg cursor-pointer transition-colors duration-200 ${
                    analysisType === type.value
                      ? 'border-legal-500 bg-legal-50'
                      : 'border-justice-300 hover:border-legal-300 hover:bg-legal-25'
                  }`}
                >
                  <input
                    type="radio"
                    name="analysisType"
                    value={type.value}
                    checked={analysisType === type.value}
                    onChange={(e) => setAnalysisType(e.target.value as any)}
                    className="h-4 w-4 text-legal-600 focus:ring-legal-500 border-justice-300 mt-1"
                  />
                  <div className="ml-3">
                    <div className="text-sm font-medium text-justice-900">{type.label}</div>
                    <div className="text-sm text-justice-600">{type.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Analysis Options */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-justice-700">
              Analysis Options
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeCitations}
                  onChange={(e) => setIncludeCitations(e.target.checked)}
                  className="h-4 w-4 text-legal-600 focus:ring-legal-500 border-justice-300 rounded"
                />
                <span className="ml-2 text-sm text-justice-700">Include legal citations and references</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeCounterarguments}
                  onChange={(e) => setIncludeCounterarguments(e.target.checked)}
                  className="h-4 w-4 text-legal-600 focus:ring-legal-500 border-justice-300 rounded"
                />
                <span className="ml-2 text-sm text-justice-700">Include counterarguments and alternative views</span>
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={!query.trim() || isAnalyzing}
              className="btn-primary px-8 py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <span className="flex items-center space-x-2">
                  <div className="spinner" />
                  <span>Analyzing...</span>
                </span>
              ) : (
                <span className="flex items-center space-x-2">
                  <SparklesIcon className="h-6 w-6" />
                  <span>Analyze</span>
                </span>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Analysis Results */}
      {result && (
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-justice-900">Analysis Results</h2>
            <p className="text-sm text-justice-600 mt-2">
              Query: "{result.query}"
            </p>
          </div>

          {/* Confidence Score */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-justice-900">Confidence Score</h3>
              <div className="flex items-center space-x-2">
                <ChartBarIcon className="h-5 w-5 text-legal-600" />
                <span className="text-2xl font-bold text-legal-600">
                  {Math.round(result.confidenceScore * 100)}%
                </span>
              </div>
            </div>
            <div className="w-full bg-justice-200 rounded-full h-3">
              <div
                className="bg-legal-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${result.confidenceScore * 100}%` }}
              />
            </div>
          </div>

          {/* Main Analysis */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-4">
              <DocumentTextIcon className="h-6 w-6 text-legal-600" />
              <h3 className="text-lg font-semibold text-justice-900">Legal Analysis</h3>
            </div>
            <div className="prose prose-legal max-w-none">
              {result.analysis.split('\n\n').map((paragraph, index) => (
                <p key={index} className="mb-4 text-justice-700 leading-relaxed">
                  {paragraph}
                </p>
              ))}
            </div>
          </div>

          {/* Key Points */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-4">
              <LightBulbIcon className="h-6 w-6 text-legal-600" />
              <h3 className="text-lg font-semibold text-justice-900">Key Points</h3>
            </div>
            <ul className="space-y-2">
              {result.keyPoints.map((point, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-legal-100 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-xs font-medium text-legal-700">{index + 1}</span>
                  </div>
                  <span className="text-justice-700">{point}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Citations and Precedents */}
          <div className="grid md:grid-cols-2 gap-8">
            <div className="card">
              <div className="flex items-center space-x-2 mb-4">
                <BookOpenIcon className="h-6 w-6 text-legal-600" />
                <h3 className="text-lg font-semibold text-justice-900">Legal Citations</h3>
              </div>
              <ul className="space-y-2">
                {result.citations.map((citation, index) => (
                  <li key={index} className="text-sm">
                    <span className="legal-citation">{citation}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="card">
              <div className="flex items-center space-x-2 mb-4">
                <ChartBarIcon className="h-6 w-6 text-legal-600" />
                <h3 className="text-lg font-semibold text-justice-900">Relevant Precedents</h3>
              </div>
              <ul className="space-y-3">
                {result.precedents.map((precedent, index) => (
                  <li key={index} className="text-sm text-justice-700">
                    {precedent}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Counterarguments */}
          {result.counterarguments.length > 0 && (
            <div className="card">
              <div className="flex items-center space-x-2 mb-4">
                <ExclamationTriangleIcon className="h-6 w-6 text-orange-600" />
                <h3 className="text-lg font-semibold text-justice-900">Counterarguments & Alternative Views</h3>
              </div>
              <ul className="space-y-2">
                {result.counterarguments.map((argument, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-2 h-2 bg-orange-400 rounded-full mt-2" />
                    <span className="text-justice-700">{argument}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Sources Used */}
          <div className="card">
            <h3 className="text-lg font-semibold text-justice-900 mb-4">Sources Referenced</h3>
            <div className="flex flex-wrap gap-2">
              {result.sources.map((sourceId) => (
                <span
                  key={sourceId}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-justice-100 text-justice-800 hover:bg-justice-200 cursor-pointer transition-colors duration-200"
                >
                  Document #{sourceId}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisPage; 