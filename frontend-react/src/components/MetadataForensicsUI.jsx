"use client";
import React, { useState, useRef } from 'react';
import { Upload, Download, Trash, FileText, AlertCircle, FileImage, FileAudio, FileBarChart, Loader2 } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function MetadataForensicsUI() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [error, setError] = useState('');
  const [metadata, setMetadata] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile) => {
    setError('');
    setMetadata(null);
    setFile(selectedFile);
  };

  const clearFile = () => {
    setFile(null);
    setMetadata(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const extractMetadata = async () => {
    if (!file) return;

    setIsExtracting(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/api/extract`, {
        method: 'POST',
        body: formData,
      });

      // If /api/extract fails, fallback to /api/analyze
      let responseObj = response;
      if (response.status === 404) {
        responseObj = await fetch(`${API_BASE_URL}/api/analyze`, {
          method: 'POST',
          body: formData,
        });
      }

      if (!responseObj.ok) {
        throw new Error(`Server returned ${responseObj.status}: ${responseObj.statusText}`);
      }

      const data = await responseObj.json();
      
      // Map response correctly whether it has { success: true, metadata: {...} } or is flat
      const actualMetadata = data.metadata ? data.metadata : data;
      setMetadata(actualMetadata);
    } catch (err) {
      console.error('Extraction error:', err);
      setError('Failed to extract metadata. Please ensure the backend is running and the file is valid.');
    } finally {
      setIsExtracting(false);
    }
  };

  const downloadJSON = () => {
    if (!metadata) return;
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(metadata, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `metadata_${file?.name || 'export'}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const downloadHTMLReport = () => {
    if (!metadata || !file) return;

    const sectionsHTML = Object.entries(metadata)
      .filter(([key, val]) => typeof val === 'object' && val !== null && !Array.isArray(val))
      .map(([section, data]) => {
        if (Object.keys(data).length === 0) return '';
        
        const rows = Object.entries(data).map(([k, v]) => `
          <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; font-weight: 600; width: 30%; color: #374151;">${k}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; color: #111827; word-break: break-all;">${v}</td>
          </tr>
        `).join('');

        return `
          <div style="margin-bottom: 30px;">
            <h3 style="color: #2563eb; font-size: 1.25rem; border-bottom: 2px solid #bfdbfe; padding-bottom: 8px; margin-bottom: 15px; text-transform: uppercase;">
              ${section} Data
            </h3>
            <table style="width: 100%; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden;">
              <tbody>
                ${rows}
              </tbody>
            </table>
          </div>
        `;
      }).join('');

    const htmlContent = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Metadata Forensics Report - ${file.name}</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f3f4f6; color: #1f2937; line-height: 1.6; padding: 40px 20px; }
          .container { max-width: 800px; margin: 0 auto; }
          .header { text-align: center; margin-bottom: 40px; }
          .title { color: #1e3a8a; font-size: 2rem; font-weight: bold; margin-bottom: 10px; }
          .subtitle { color: #4b5563; font-size: 1.1rem; }
          .file-info { background: #eff6ff; border: 1px solid #bfdbfe; padding: 20px; border-radius: 8px; margin-bottom: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
          .info-item label { display: block; font-size: 0.875rem; color: #6b7280; font-weight: 600; text-transform: uppercase; }
          .info-item span { font-size: 1.125rem; color: #1e40af; font-weight: 500; word-break: break-all; }
          .footer { margin-top: 50px; text-align: center; color: #9ca3af; font-size: 0.875rem; border-top: 1px solid #e5e7eb; padding-top: 20px; }
          @media print {
            body { background-color: white; padding: 0; }
            .container { max-width: 100%; }
            .file-info { background: #f8fafc; border: 1px solid #e2e8f0; }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1 class="title">Metadata Forensics Report</h1>
            <p class="subtitle">Generated on ${new Date().toLocaleString()}</p>
          </div>
          
          <div class="file-info">
            <div class="info-item">
              <label>Filename</label>
              <span>${metadata.filename || file.name}</span>
            </div>
            <div class="info-item">
              <label>File Type</label>
              <span>${metadata.file_type || file.type || 'Unknown'}</span>
            </div>
            <div class="info-item">
              <label>File Size</label>
              <span>${metadata.file_size ? (metadata.file_size / 1024).toFixed(2) + ' KB' : (file.size / 1024).toFixed(2) + ' KB'}</span>
            </div>
          </div>
          
          ${sectionsHTML}
          
          <div class="footer">
            Generated by Metadata Extraction Tool
          </div>
        </div>
      </body>
      </html>
    `;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", url);
    downloadAnchorNode.setAttribute("download", `metadata_report_${file.name}.html`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
    URL.revokeObjectURL(url);
  };

  const renderFileIcon = () => {
    if (!file) return <Upload className="w-12 h-12 text-blue-500 mb-4" />;
    
    if (file.type.startsWith('image/')) return <FileImage className="w-12 h-12 text-blue-500 mb-4" />;
    if (file.type.startsWith('audio/')) return <FileAudio className="w-12 h-12 text-blue-500 mb-4" />;
    if (file.type === 'application/pdf') return <FileText className="w-12 h-12 text-blue-500 mb-4" />;
    
    return <FileText className="w-12 h-12 text-blue-500 mb-4" />;
  };

  const renderMetadataSection = (title, data) => {
    if (!data || Object.keys(data).length === 0) return null;
    
    return (
      <div className="mb-6 bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm" key={title}>
        <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 uppercase tracking-wider">{title}</h3>
        </div>
        <div className="divide-y divide-gray-100">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="flex flex-col sm:flex-row px-4 py-3 hover:bg-gray-50 transition-colors">
              <div className="sm:w-1/3 font-medium text-gray-600 mb-1 sm:mb-0 break-words pr-4">{key}</div>
              <div className="sm:w-2/3 text-gray-900 break-all">{String(value)}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Metadata Forensics</h1>
          <p className="mt-3 text-lg text-gray-500 max-w-2xl mx-auto">
            Extract and analyze hidden metadata from images, audio files, and documents securely.
          </p>
        </div>

        {/* Upload Section */}
        {!metadata && (
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
            <div className="p-8">
              <div 
                className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center transition-all duration-200 ${
                  isDragging 
                    ? 'border-blue-500 bg-blue-50' 
                    : file ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => !file && fileInputRef.current.click()}
                style={{ cursor: file ? 'default' : 'pointer' }}
              >
                <input 
                  type="file" 
                  ref={fileInputRef}
                  onChange={handleFileInput}
                  className="hidden"
                />
                
                {renderFileIcon()}
                
                {file ? (
                  <div className="text-center">
                    <p className="text-lg font-semibold text-gray-800">{file.name}</p>
                    <p className="text-sm text-gray-500 mt-1">{(file.size / 1024).toFixed(2)} KB • {file.type || 'Unknown type'}</p>
                    
                    <div className="flex space-x-4 mt-6 justify-center">
                      <button 
                        onClick={(e) => { e.stopPropagation(); clearFile(); }}
                        className="px-4 py-2 text-sm font-medium text-red-600 bg-red-100 hover:bg-red-200 rounded-lg flex items-center transition-colors"
                        disabled={isExtracting}
                      >
                        <Trash className="w-4 h-4 mr-2" />
                        Remove
                      </button>
                      <button 
                        onClick={(e) => { e.stopPropagation(); extractMetadata(); }}
                        disabled={isExtracting}
                        className="px-6 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center shadow-md transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                      >
                        {isExtracting ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Extracting...
                          </>
                        ) : (
                          <>
                            <FileBarChart className="w-4 h-4 mr-2" />
                            Extract Metadata
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="text-lg font-medium text-gray-700">Drag & drop your file here</p>
                    <p className="text-sm text-gray-500 mt-2">or click to browse from your device</p>
                    <div className="mt-6 flex flex-wrap justify-center gap-2">
                      <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">.jpg / .png</span>
                      <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">.pdf</span>
                      <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">.docx / .xlsx</span>
                      <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">.mp3</span>
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg flex items-start">
                  <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Results Section */}
        {metadata && (
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header Banner */}
            <div className="bg-blue-600 p-6 sm:px-8 text-white flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div className="flex items-center gap-4">
                <div className="bg-blue-500/50 p-3 rounded-xl">
                  {renderFileIcon()}
                </div>
                <div>
                  <h2 className="text-xl font-bold">{metadata.filename || file?.name}</h2>
                  <p className="text-blue-100 text-sm mt-1">
                    {metadata.file_type || file?.type || 'Unknown'} • 
                    {metadata.file_size ? (metadata.file_size / 1024).toFixed(2) + ' KB' : (file?.size / 1024).toFixed(2) + ' KB'}
                  </p>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-3 w-full sm:w-auto">
                <button 
                  onClick={downloadJSON}
                  className="flex-1 sm:flex-none px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white text-sm font-medium rounded-lg flex items-center justify-center transition-colors border border-blue-500"
                >
                  <Download className="w-4 h-4 mr-2" />
                  JSON
                </button>
                <button 
                  onClick={downloadHTMLReport}
                  className="flex-1 sm:flex-none px-4 py-2 bg-white text-blue-700 hover:bg-blue-50 text-sm font-medium rounded-lg flex items-center justify-center transition-colors shadow-sm"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  HTML Report
                </button>
              </div>
            </div>

            {/* Metadata Content */}
            <div className="p-6 sm:p-8 bg-gray-50">
              
              {/* Dynamic Sections based on returned JSON keys that are objects */}
              {Object.entries(metadata).map(([key, value]) => {
                // Skip primitive top-level metadata like filename, file_size
                if (typeof value !== 'object' || value === null || Array.isArray(value)) return null;
                
                // Capitalize key for title
                const title = key === 'exif' ? 'EXIF Data' 
                            : key === 'id3' ? 'ID3 Tags' 
                            : key === 'document' ? 'Document Info'
                            : key;
                            
                return renderMetadataSection(title, value);
              })}
              
              {/* Fallback if no structured metadata found */}
              {Object.keys(metadata).filter(k => typeof metadata[k] === 'object' && metadata[k] !== null && !Array.isArray(metadata[k])).length === 0 && (
                <div className="text-center py-12">
                  <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900">No structured metadata found</h3>
                  <p className="text-gray-500 mt-2">The extraction process completed, but no recognizable EXIF, ID3, or document properties were detected in this file.</p>
                </div>
              )}

              <div className="mt-8 flex justify-center border-t border-gray-200 pt-8">
                <button 
                  onClick={clearFile}
                  className="px-6 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-medium rounded-lg transition-colors shadow-sm"
                >
                  Analyze Another File
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
