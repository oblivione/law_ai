import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  ArrowUpTrayIcon, 
  DocumentTextIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  documentId?: number;
  errorMessage?: string;
}

const UploadPage: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      status: 'uploading',
      progress: 0
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // Simulate file upload and processing
    newFiles.forEach(file => {
      simulateUpload(file.id);
    });
  }, []);

  const simulateUpload = (fileId: string) => {
    // Simulate upload progress
    const uploadInterval = setInterval(() => {
      setUploadedFiles(prev => prev.map(file => {
        if (file.id === fileId && file.status === 'uploading') {
          const newProgress = Math.min(file.progress + Math.random() * 20, 100);
          if (newProgress >= 100) {
            clearInterval(uploadInterval);
            // Start processing simulation
            setTimeout(() => simulateProcessing(fileId), 500);
            return { ...file, progress: 100, status: 'processing' as const };
          }
          return { ...file, progress: newProgress };
        }
        return file;
      }));
    }, 300);
  };

  const simulateProcessing = (fileId: string) => {
    // Simulate processing phases
    const phases = ['Text Extraction', 'AI Analysis', 'Embedding Generation'];
    let currentPhase = 0;

    const processingInterval = setInterval(() => {
      setUploadedFiles(prev => prev.map(file => {
        if (file.id === fileId && file.status === 'processing') {
          const newProgress = Math.min(file.progress + Math.random() * 15, 100);
          
          if (newProgress >= 100) {
            clearInterval(processingInterval);
            return { 
              ...file, 
              progress: 100, 
              status: 'completed' as const,
              documentId: Math.floor(Math.random() * 1000) + 1
            };
          }
          
          return { ...file, progress: newProgress };
        }
        return file;
      }));
    }, 500);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <ClockIcon className="h-5 w-5 text-legal-600 animate-spin" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
    }
  };

  const getStatusText = (file: UploadedFile) => {
    switch (file.status) {
      case 'uploading':
        return `Uploading... ${Math.round(file.progress)}%`;
      case 'processing':
        return `Processing... ${Math.round(file.progress)}%`;
      case 'completed':
        return 'Processing Complete';
      case 'error':
        return file.errorMessage || 'Upload failed';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-justice-900">Upload Legal Documents</h1>
        <p className="text-lg text-justice-600">
          Upload PDF, DOCX, or TXT files for AI-powered analysis and search indexing
        </p>
      </div>

      {/* Upload Area */}
      <div className="max-w-4xl mx-auto">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors duration-200 cursor-pointer ${
            isDragActive
              ? 'border-legal-500 bg-legal-50'
              : 'border-justice-300 hover:border-legal-400 hover:bg-legal-25'
          }`}
        >
          <input {...getInputProps()} />
          <div className="space-y-4">
            <div className="flex justify-center">
              <ArrowUpTrayIcon className="h-12 w-12 text-justice-400" />
            </div>
            
            {isDragActive ? (
              <p className="text-lg text-legal-600 font-medium">
                Drop the files here...
              </p>
            ) : (
              <div className="space-y-2">
                <p className="text-lg text-justice-700 font-medium">
                  Drag & drop files here, or click to select files
                </p>
                <p className="text-sm text-justice-500">
                  Supports PDF, DOCX, and TXT files up to 50MB each
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {uploadedFiles.length > 0 && (
        <div className="max-w-4xl mx-auto space-y-6">
          <h2 className="text-2xl font-bold text-justice-900">Upload Progress</h2>
          
          <div className="space-y-4">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="card">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <DocumentTextIcon className="h-8 w-8 text-justice-400" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="text-sm font-medium text-justice-900 truncate">
                          {file.name}
                        </p>
                        <p className="text-sm text-justice-500">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(file.status)}
                        <span className="text-sm font-medium text-justice-700">
                          {getStatusText(file)}
                        </span>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="w-full bg-justice-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          file.status === 'completed' 
                            ? 'bg-green-500' 
                            : file.status === 'error'
                            ? 'bg-red-500'
                            : 'bg-legal-500'
                        }`}
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                    
                    {/* Document ID for completed files */}
                    {file.status === 'completed' && file.documentId && (
                      <div className="mt-2 flex items-center justify-between">
                        <span className="text-sm text-green-600 font-medium">
                          Document ID: {file.documentId}
                        </span>
                        <button className="text-sm text-legal-600 hover:text-legal-700 font-medium">
                          View Document
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Guidelines */}
      <div className="max-w-4xl mx-auto">
        <div className="card">
          <h3 className="text-lg font-semibold text-justice-900 mb-4">
            Upload Guidelines
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-justice-800 mb-2">Supported File Types</h4>
              <ul className="text-sm text-justice-600 space-y-1">
                <li>• PDF documents (.pdf)</li>
                <li>• Microsoft Word documents (.docx)</li>
                <li>• Plain text files (.txt)</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-justice-800 mb-2">Processing Steps</h4>
              <ul className="text-sm text-justice-600 space-y-1">
                <li>• Text extraction and cleaning</li>
                <li>• Legal entity identification</li>
                <li>• AI-powered content analysis</li>
                <li>• Vector embedding generation</li>
                <li>• Search index creation</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-justice-800 mb-2">File Requirements</h4>
              <ul className="text-sm text-justice-600 space-y-1">
                <li>• Maximum file size: 50MB</li>
                <li>• Text-based content (no images)</li>
                <li>• English language preferred</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-justice-800 mb-2">After Upload</h4>
              <ul className="text-sm text-justice-600 space-y-1">
                <li>• Documents are automatically indexed</li>
                <li>• Available for semantic search</li>
                <li>• AI analysis generates metadata</li>
                <li>• Integration with legal reasoning</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage; 