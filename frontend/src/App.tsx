import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Components
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import DocumentPage from './pages/DocumentPage';
import AnalysisPage from './pages/AnalysisPage';
import UploadPage from './pages/UploadPage';

// Styles
import './index.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

// Derive basename from PUBLIC_URL for GitHub Pages deployments
const derivedBasename = (process.env.PUBLIC_URL || '')
  .replace(/^(https?:\/\/[^/]+)?/, '') || '/';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router basename={derivedBasename}>
        <div className="App">
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/document/:id" element={<DocumentPage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="/upload" element={<UploadPage />} />
            </Routes>
          </Layout>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1e293b',
                color: '#f1f5f9',
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App; 