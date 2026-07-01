import React, { useState, useRef } from "react";
import { Settings, FileJson, FolderUp, Folder, FilePlus } from "lucide-react";

const DEFAULT_CONFIG = `{
  "fields": [
    { "path": "full_name", "type": "string", "required": true },
    { "path": "primary_email", "from": "emails[0]", "type": "string", "required": true },
    { "path": "phone", "from": "phones[0]", "type": "string", "normalize": "E164" },
    { "path": "skills", "from": "skills[*].name", "type": "string[]", "normalize": "canonical" }
  ],
  "include_confidence": true,
  "include_provenance": true,
  "on_missing": "null"
}`;

function Header({ onTransform, loading }) {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="bg-blue-600 p-2 rounded-lg">
          <Settings className="w-5 h-5 text-white" />
        </div>
        <h1 className="text-xl font-semibold text-gray-900">
          Data Transformer
        </h1>
      </div>
      <button
        onClick={onTransform}
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
      >
        {loading ? "Processing..." : "Run Pipeline"}
      </button>
    </header>
  );
}

function InputPanel({
  activeTab,
  setActiveTab,
  configData,
  setConfigData,
  folderFiles,
  setFolderFiles,
}) {
  const folderInputRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    const newFolderFiles = {
      csv_list: [],
      ats_json_list: [],
      github_list: [],
      notes_list: [],
      filenames: [],
    };

    for (const file of files) {
      if (file.name.includes("config")) continue; // Skip if they accidentally highlight config.json

      const text = await file.text();
      newFolderFiles.filenames.push(file.webkitRelativePath || file.name);

      if (file.name.endsWith(".csv")) {
        newFolderFiles.csv_list.push(text);
      } else if (file.name.endsWith(".txt")) {
        newFolderFiles.notes_list.push(text);
      } else if (file.name.endsWith(".json")) {
        try {
          const data = JSON.parse(text);
          // Distinguish GitHub API JSON from standard ATS JSON structurally
          if (data.login || data.repos_url) {
            newFolderFiles.github_list.push(text);
          } else {
            newFolderFiles.ats_json_list.push(text);
          }
        } catch (err) {
          console.error(`Failed to parse ${file.name}`);
        }
      }
    }
    setFolderFiles(newFolderFiles);
  };

  return (
    <div className="w-1/2 flex flex-col bg-white border-r border-gray-200">
      <div className="flex items-center px-4 py-2 border-b border-gray-200 bg-gray-50 space-x-2">
        <button
          onClick={() => setActiveTab("files")}
          className={`px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-2 ${
            activeTab === "files" ? "bg-white shadow-sm text-blue-600" : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <Folder className="w-4 h-4" />
          Batch Upload
        </button>
        <button
          onClick={() => setActiveTab("config")}
          className={`px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-2 ${
            activeTab === "config" ? "bg-white shadow-sm text-blue-600" : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <FileJson className="w-4 h-4" />
          Runtime Config
        </button>
      </div>
      
      <div className="flex-1 overflow-auto p-4 bg-gray-50">
        {activeTab === "files" && (
          <div className="h-full flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg bg-white p-8">
            <FolderUp className="w-12 h-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">Select Candidate Data</h3>
            <p className="text-sm text-gray-500 mb-6 text-center">
              Upload individual files or a folder containing ATS (.json), GitHub (.json), CSVs, and Notes (.txt).
            </p>
            
            {/* Hidden Inputs */}
            <input
              type="file"
              ref={folderInputRef}
              onChange={handleFileUpload}
              webkitdirectory=""
              directory=""
              className="hidden"
            />
            <input
              type="file"
              multiple
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
            />

            {/* Upload Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors flex items-center gap-2 shadow-sm"
              >
                <FilePlus className="w-4 h-4" />
                Select Files
              </button>
              <button
                onClick={() => folderInputRef.current?.click()}
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2 shadow-sm"
              >
                <Folder className="w-4 h-4" />
                Select Folder
              </button>
            </div>
            
            {folderFiles && folderFiles.filenames.length > 0 && (
              <div className="mt-8 w-full text-left max-w-md bg-gray-50 p-4 rounded-md border border-gray-200">
                <p className="font-semibold text-gray-700 mb-2">Selected Files ({folderFiles.filenames.length}):</p>
                <div className="mt-2 text-xs text-gray-600 font-medium grid grid-cols-2 gap-2 mb-3">
                  <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded">CSVs: {folderFiles.csv_list.length}</div>
                  <div className="bg-green-100 text-green-800 px-2 py-1 rounded">ATS JSONs: {folderFiles.ats_json_list.length}</div>
                  <div className="bg-purple-100 text-purple-800 px-2 py-1 rounded">GitHub JSONs: {folderFiles.github_list.length}</div>
                  <div className="bg-orange-100 text-orange-800 px-2 py-1 rounded">Notes: {folderFiles.notes_list.length}</div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {activeTab === "config" && (
          <textarea
            value={configData}
            onChange={(e) => setConfigData(e.target.value)}
            className="w-full h-full p-4 font-mono text-sm border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 outline-none"
            spellCheck="false"
          />
        )}
      </div>
    </div>
  );
}

function OutputPanel({ error, result }) {
  return (
    <div className="w-1/2 flex flex-col bg-gray-900 text-gray-100 overflow-hidden">
      <div className="flex items-center px-6 py-3 border-b border-gray-800 bg-gray-950">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">
          Output JSON
        </h2>
      </div>
      <div className="flex-1 p-6 overflow-auto">
        {error ? (
          <div className="p-4 bg-red-900/50 border border-red-500/50 rounded-md text-red-200 text-sm font-mono whitespace-pre-wrap shadow-inner">
            {error}
          </div>
        ) : result ? (
          <pre className="font-mono text-sm whitespace-pre-wrap">
            {JSON.stringify(result, null, 2)}
          </pre>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500 text-sm text-center">
            <div className="max-w-md">
              <p className="mb-2">
                Upload your files/directory and click "Run Pipeline" to transform the inputs.
              </p>
              <p className="text-xs text-gray-600">
                The FastAPI backend processes the rules, normalizes the data,
                merges sources, and applies the dynamic configuration.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState("files");
  const [configData, setConfigData] = useState(DEFAULT_CONFIG);
  const [folderFiles, setFolderFiles] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTransform = async () => {
    if (!folderFiles || folderFiles.filenames.length === 0) {
      setError("Please select candidate files or a folder first.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let parsedConfig;
      try {
        parsedConfig = JSON.parse(configData);
      } catch (err) {
        throw new Error("Invalid Config JSON format. Please check for syntax errors.");
      }

      const payload = {
        sources: {
          csv_list: folderFiles.csv_list,
          ats_json_list: folderFiles.ats_json_list,
          github_list: folderFiles.github_list,
          notes_list: folderFiles.notes_list,
        },
        config: parsedConfig,
      };

      // Ensure FastAPI backend is running on 8000 via Uvicorn
      const response = await fetch("http://localhost:8000/api/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let errorMsg = `Server error: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMsg = errorData.detail || errorMsg;
        } catch (e) {
          // If the backend didn't send JSON, just use the status text
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-full flex flex-col bg-gray-50 font-sans">
      <Header onTransform={handleTransform} loading={loading} />
      <main className="flex-1 flex overflow-hidden">
        <InputPanel
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          configData={configData}
          setConfigData={setConfigData}
          folderFiles={folderFiles}
          setFolderFiles={setFolderFiles}
        />
        <OutputPanel error={error} result={result} />
      </main>
    </div>
  );
}