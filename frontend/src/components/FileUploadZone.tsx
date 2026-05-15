import React, { useState } from 'react';
import { Upload, FileText, X, Loader2, CheckCircle2 } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import api from '../services/api';

interface FileUploadZoneProps {
  activityId?: number;
  riskId?: number;
  docType?: string;
  contextName: string;
  onSuccess: () => void;
  onClose: () => void;
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({ 
  activityId, 
  riskId, 
  docType, 
  contextName, 
  onSuccess, 
  onClose 
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: acceptedFiles => setFiles(prev => [...prev, ...acceptedFiles])
  });

  const removeFile = (name: string) => {
    setFiles(files.filter(f => f.name !== name));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        const url = activityId 
          ? `tasks/${activityId}/upload/?doc_type=${docType}`
          : `risks/${riskId}/proof/`;
          
        await api.post(url, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }
      onSuccess();
    } catch (err: any) {
      console.error('Upload failed', err);
      const detail = err?.response?.data?.detail;
      alert(detail ? `Upload failed: ${detail}` : 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] bg-background flex flex-col animate-in fade-in duration-200">
      {/* Top Bar */}
      <div className="flex items-center justify-between px-8 py-4 border-b border-slate-200 dark:border-white/5 bg-sidebar">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-accent-primary/10 rounded-xl flex items-center justify-center border border-accent-primary/20">
            <Upload className="w-5 h-5 text-accent-primary" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white uppercase tracking-tight">Upload Documents</h2>
            <p className="text-slate-500 font-bold text-[9px] uppercase tracking-widest mt-0.5">Secure Document Portal • {contextName}</p>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="w-10 h-10 rounded-full bg-slate-100 dark:bg-white/5 hover:bg-rose-500/20 text-slate-400 hover:text-rose-500 transition-all border border-slate-200 dark:border-white/10 flex items-center justify-center"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 flex flex-col lg:flex-row gap-6 p-8 max-w-6xl mx-auto w-full overflow-hidden">
        {/* Left Side: Selection */}
        <div className="lg:w-1/2 flex flex-col gap-6">
          <div className="p-6 bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/5 rounded-2xl shadow-sm">
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2">Project Activity</p>
            <p className="text-slate-900 dark:text-white font-bold text-lg leading-tight uppercase tracking-tight">{contextName}</p>
            {docType && (
              <span className="inline-block mt-3 px-2 py-1 bg-accent-primary/10 text-accent-primary text-[8px] font-semibold uppercase rounded border border-accent-primary/20 tracking-widest">
                {docType}
              </span>
            )}
          </div>

          <div 
            {...getRootProps()} 
            className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all cursor-pointer group flex-1 flex flex-col items-center justify-center bg-slate-50/50 dark:bg-black/20 ${
              isDragActive ? 'border-accent-primary bg-accent-primary/5' : 'border-slate-200 dark:border-white/10 hover:border-accent-primary/30 hover:bg-slate-100 dark:hover:bg-white/[0.02]'
            }`}
          >
            <input {...getInputProps()} />
            <div className="w-16 h-16 bg-white dark:bg-white/5 rounded-2xl flex items-center justify-center mb-4 group-hover:bg-accent-primary/10 transition-colors shadow-sm">
              <Upload className={`w-8 h-8 ${isDragActive ? 'text-accent-primary animate-bounce' : 'text-slate-400 dark:text-slate-600 group-hover:text-accent-primary'}`} />
            </div>
            <p className="text-slate-700 dark:text-slate-200 font-bold text-lg uppercase tracking-tight">Select Files</p>
            <p className="text-slate-500 text-[10px] mt-2 uppercase font-medium tracking-widest opacity-60">Drag and drop or click to browse</p>
          </div>
        </div>

        {/* Right Side: List & Action */}
        <div className="lg:w-1/2 flex flex-col overflow-hidden">
          <div className="flex-1 bg-slate-50 dark:bg-white/[0.02] rounded-3xl border border-slate-200 dark:border-white/5 flex flex-col overflow-hidden shadow-xl">
            <div className="px-8 py-5 border-b border-slate-200 dark:border-white/5 flex justify-between items-center bg-white dark:bg-white/5">
              <h4 className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-widest flex items-center gap-3">
                <FileText className="w-4 h-4 text-lime-500" /> Queued Documents ({files.length})
              </h4>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-3 custom-scrollbar">
              {files.map((f, i) => (
                <div key={i} className="flex items-center gap-4 p-4 bg-white dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/5 hover:border-slate-300 dark:hover:border-white/10 transition-all shadow-sm">
                  <FileText className="w-5 h-5 text-lime-500 dark:text-lime-400 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-slate-700 dark:text-slate-200 truncate uppercase tracking-tight">{f.name}</p>
                    <p className="text-[9px] text-slate-500 font-mono mt-0.5">{(f.size/1024/1024).toFixed(2)} MB</p>
                  </div>
                  <button onClick={() => removeFile(f.name)} className="p-2 hover:bg-rose-500/20 text-slate-400 hover:text-rose-500 rounded-lg transition-all">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
              {files.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center opacity-20 py-20">
                  <FileText className="w-12 h-12 text-slate-400 dark:text-slate-500 mb-4" />
                  <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest">No files selected</p>
                </div>
              )}
            </div>

            <div className="p-6 bg-white dark:bg-white/5 border-t border-slate-200 dark:border-white/5 mt-auto">
              <button
                disabled={files.length === 0 || uploading}
                onClick={handleUpload}
                className="w-full bg-accent-primary hover:bg-accent-secondary disabled:opacity-20 text-white font-semibold py-4 rounded-xl transition-all shadow-xl shadow-accent-primary/20 uppercase tracking-[0.2em] text-xs active:scale-95 flex items-center justify-center gap-3"
              >
                {uploading ? (
                  <>
                    <Loader2 className="animate-spin w-4 h-4" />
                    <span>Uploading...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Upload</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
