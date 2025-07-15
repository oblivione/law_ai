import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { 
  DocumentTextIcon, 
  EyeIcon, 
  ChartBarIcon,
  TagIcon,
  CalendarIcon,
  ScaleIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

const DocumentPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<'content' | 'metadata' | 'analysis'>('content');

  // Mock document data
  const document = {
    id: Number(id),
    title: "Property Rights in Digital Assets: A Comprehensive Analysis",
    originalFilename: "property_law_digital_assets.pdf",
    documentType: "court_decision",
    jurisdiction: "federal",
    datePublished: "2023-11-15",
    source: "U.S. District Court, Southern District of New York",
    processingStatus: "completed",
    fileSize: 2456789,
    pageCount: 45,
    summary: "This comprehensive legal document examines the evolving landscape of property rights as they apply to digital assets, including cryptocurrencies, NFTs, and other blockchain-based instruments. The analysis covers federal and state law perspectives, recent court decisions, and emerging regulatory frameworks that impact digital asset ownership and transfer rights.",
    legalConcepts: ["Property Law", "Digital Assets", "Cryptocurrency", "Blockchain", "NFTs", "Intellectual Property"],
    citations: [
      "17 U.S.C. § 106",
      "Carpenter v. United States, 484 U.S. 19 (1987)",
      "Reves v. Ernst & Young, 507 U.S. 170 (1993)",
      "SEC v. W.J. Howey Co., 328 U.S. 293 (1946)"
    ],
    keyPoints: [
      "Digital assets require new legal frameworks for property classification",
      "Traditional property law concepts may not fully apply to blockchain assets",
      "Regulatory uncertainty creates challenges for legal practitioners",
      "Courts are developing new precedents for digital asset disputes"
    ],
    chunks: [
      {
        id: 1,
        text: "The emergence of digital assets has fundamentally challenged traditional concepts of property law. Unlike physical assets, digital assets exist in a decentralized network where ownership is determined by cryptographic keys rather than traditional legal instruments.",
        pageNumber: 1,
        sectionTitle: "Introduction to Digital Property Rights"
      },
      {
        id: 2,
        text: "Federal courts have begun to grapple with questions of jurisdiction and applicable law when digital assets are involved in legal disputes. The borderless nature of blockchain technology creates complex jurisdictional issues.",
        pageNumber: 15,
        sectionTitle: "Jurisdictional Challenges"
      },
      {
        id: 3,
        text: "The Securities and Exchange Commission has taken an increasingly active role in regulating digital assets, particularly those that may be classified as securities under the Howey test.",
        pageNumber: 28,
        sectionTitle: "Regulatory Framework"
      }
    ]
  };

  const tabs = [
    { id: 'content', label: 'Document Content', icon: DocumentTextIcon },
    { id: 'metadata', label: 'Metadata', icon: TagIcon },
    { id: 'analysis', label: 'AI Analysis', icon: ChartBarIcon }
  ];

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-8">
      {/* Document Header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-justice-900 mb-2">{document.title}</h1>
            <div className="flex flex-wrap gap-4 text-sm text-justice-600 mb-4">
              <div className="flex items-center space-x-1">
                <DocumentTextIcon className="h-4 w-4" />
                <span>{document.documentType.replace('_', ' ').toUpperCase()}</span>
              </div>
              <div className="flex items-center space-x-1">
                <ScaleIcon className="h-4 w-4" />
                <span>{document.jurisdiction.toUpperCase()}</span>
              </div>
              <div className="flex items-center space-x-1">
                <CalendarIcon className="h-4 w-4" />
                <span>{new Date(document.datePublished).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center space-x-1">
                <EyeIcon className="h-4 w-4" />
                <span>{document.pageCount} pages</span>
              </div>
            </div>
            <p className="text-justice-700 leading-relaxed">{document.summary}</p>
          </div>
          
          <div className="ml-6 flex space-x-2">
            <button className="btn-secondary">
              <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
              Search in Document
            </button>
            <button className="btn-primary">
              <EyeIcon className="h-4 w-4 mr-2" />
              View PDF
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-justice-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors duration-200 ${
                activeTab === tab.id
                  ? 'border-legal-500 text-legal-600'
                  : 'border-transparent text-justice-500 hover:text-justice-700 hover:border-justice-300'
              }`}
            >
              <tab.icon className="h-5 w-5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'content' && (
          <div className="space-y-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-justice-900 mb-4">Document Chunks</h3>
              <p className="text-sm text-justice-600 mb-6">
                The document has been intelligently chunked for semantic search and analysis.
              </p>
              
              <div className="space-y-4">
                {document.chunks.map((chunk) => (
                  <div key={chunk.id} className="border border-justice-200 rounded-lg p-4 hover:border-legal-300 transition-colors duration-200">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-medium text-justice-900">{chunk.sectionTitle}</h4>
                        <p className="text-sm text-justice-600">Page {chunk.pageNumber} • Chunk {chunk.id}</p>
                      </div>
                      <button className="text-sm text-legal-600 hover:text-legal-700 font-medium">
                        View in Context
                      </button>
                    </div>
                    <p className="text-justice-700 leading-relaxed">{chunk.text}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* PDF Viewer Placeholder */}
            <div className="card">
              <h3 className="text-lg font-semibold text-justice-900 mb-4">PDF Viewer</h3>
              <div className="bg-justice-100 rounded-lg h-96 flex items-center justify-center">
                <div className="text-center">
                  <DocumentTextIcon className="h-16 w-16 text-justice-400 mx-auto mb-4" />
                  <p className="text-justice-600">PDF viewer would be embedded here</p>
                  <button className="btn-primary mt-4">
                    Load PDF Viewer
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'metadata' && (
          <div className="grid md:grid-cols-2 gap-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-justice-900 mb-4">Document Information</h3>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm font-medium text-justice-600">Original Filename</dt>
                  <dd className="text-sm text-justice-900">{document.originalFilename}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-justice-600">File Size</dt>
                  <dd className="text-sm text-justice-900">{formatFileSize(document.fileSize)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-justice-600">Source</dt>
                  <dd className="text-sm text-justice-900">{document.source}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-justice-600">Processing Status</dt>
                  <dd className="text-sm">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {document.processingStatus}
                    </span>
                  </dd>
                </div>
              </dl>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-justice-900 mb-4">Legal Concepts</h3>
              <div className="flex flex-wrap gap-2">
                {document.legalConcepts.map((concept) => (
                  <span
                    key={concept}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-legal-100 text-legal-800"
                  >
                    {concept}
                  </span>
                ))}
              </div>
            </div>

            <div className="card md:col-span-2">
              <h3 className="text-lg font-semibold text-justice-900 mb-4">Legal Citations</h3>
              <div className="grid md:grid-cols-2 gap-4">
                {document.citations.map((citation, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-legal-500 rounded-full flex-shrink-0" />
                    <span className="legal-citation text-sm">{citation}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-justice-900 mb-4">AI-Generated Key Points</h3>
              <ul className="space-y-3">
                {document.keyPoints.map((point, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-6 h-6 bg-legal-100 rounded-full flex items-center justify-center mt-0.5">
                      <span className="text-xs font-medium text-legal-700">{index + 1}</span>
                    </div>
                    <span className="text-justice-700">{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-justice-900 mb-4">Document Analytics</h3>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-legal-600">87%</div>
                  <div className="text-sm text-justice-600">Readability Score</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-legal-600">23</div>
                  <div className="text-sm text-justice-600">Legal Citations</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-legal-600">High</div>
                  <div className="text-sm text-justice-600">Legal Complexity</div>
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-justice-900 mb-4">Similar Documents</h3>
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center justify-between p-3 border border-justice-200 rounded-lg hover:border-legal-300 transition-colors duration-200">
                    <div>
                      <h4 className="font-medium text-justice-900">Related Document {i}</h4>
                      <p className="text-sm text-justice-600">Court Decision • Federal • Similarity: 92%</p>
                    </div>
                    <button className="text-sm text-legal-600 hover:text-legal-700 font-medium">
                      View Document
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentPage; 