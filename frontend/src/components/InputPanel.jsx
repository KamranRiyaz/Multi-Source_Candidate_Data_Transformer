import { FileJson, FileText, Settings, FolderUp, Folder } from "lucide-react";
import { useRef } from "react";

export function InputPanel({
  activeTab,
  setActiveTab,
  csvData,
  setCsvData,
  atsData,
  setAtsData,
  notesData,
  setNotesData,
  configData,
  setConfigData,
  folderFiles,
  setFolderFiles,
}) {
  const fileInputRef = useRef(null);

  const handleDirectoryUpload = async (e) => {
    const files = Array.from(e.target.files);
    const newFolderFiles = {
      csv_list: [],
      ats_json_list: [],
      github_list: [],
      notes_list: [],
      filenames: [],
    };

    for (const file of files) {
      if (file.name.includes("config")) continue; // Skip configs if any

      const text = await file.text();
      newFolderFiles.filenames.push(file.webkitRelativePath || file.name);

      if (file.name.endsWith(".csv")) {
        newFolderFiles.csv_list.push(text);
      } else if (file.name.endsWith(".txt")) {
        newFolderFiles.notes_list.push(text);
      } else if (file.name.endsWith(".json")) {
        try {
          const data = JSON.parse(text);
          if (data.login || data.repos_url) {
            newFolderFiles.github_list.push(text);
          } else {
            newFolderFiles.ats_json_list.push(text);
          }
        } catch (err) {
          // invalid json
        }
      }
    }
    
    setFolderFiles(newFolderFiles);
  };

  return (
    <div className="w-1/2 flex flex-col border-r border-gray-200 bg-white">
      <div className="flex border-b border-gray-200 overflow-x-auto">
        <button
          onClick={() => setActiveTab("csv")}
          className={`flex whitespace-nowrap items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 ${activeTab === "csv" ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
        >
          <FileText className="w-4 h-4" /> Recruiter CSV
        </button>
        <button
          onClick={() => setActiveTab("ats")}
          className={`flex whitespace-nowrap items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 ${activeTab === "ats" ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
        >
          <FileJson className="w-4 h-4" /> ATS JSON
        </button>
        <button
          onClick={() => setActiveTab("notes")}
          className={`flex whitespace-nowrap items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 ${activeTab === "notes" ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
        >
          <FileText className="w-4 h-4" /> Recruiter Notes
        </button>
        <button
          onClick={() => setActiveTab("folder")}
          className={`flex whitespace-nowrap items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 ${activeTab === "folder" ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
        >
          <Folder className="w-4 h-4" /> Directory Batch
        </button>
        <button
          onClick={() => setActiveTab("config")}
          className={`flex whitespace-nowrap items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 ${activeTab === "config" ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
        >
          <Settings className="w-4 h-4" /> Config
        </button>
      </div>

      <div className="flex-1 p-4 bg-gray-50 overflow-auto">
        {activeTab === "csv" && (
          <textarea
            value={csvData}
            onChange={(e) => setCsvData(e.target.value)}
            className="w-full h-full p-4 font-mono text-sm border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="Enter CSV data here..."
          />
        )}
        {activeTab === "ats" && (
          <textarea
            value={atsData}
            onChange={(e) => setAtsData(e.target.value)}
            className="w-full h-full p-4 font-mono text-sm border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="Enter ATS JSON here..."
          />
        )}
        {activeTab === "notes" && (
          <textarea
            value={notesData}
            onChange={(e) => setNotesData(e.target.value)}
            className="w-full h-full p-4 font-mono text-sm border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="Enter unstructured recruiter notes here..."
          />
        )}
        {activeTab === "folder" && (
          <div className="w-full h-full p-4 font-mono text-sm border border-gray-300 rounded-md shadow-sm bg-white flex flex-col items-center justify-center space-y-4">
            <FolderUp className="w-12 h-12 text-gray-400" />
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">Upload a directory of candidates</h3>
              <p className="mt-1 text-gray-500">Process multiple CSVs, JSONs, and text notes at once.</p>
            </div>
            
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleDirectoryUpload}
              className="hidden"
              webkitdirectory="true"
              directory="true"
              multiple
            />
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Select Folder
            </button>
            
            {folderFiles && (
              <div className="mt-6 w-full text-left max-w-md bg-gray-50 p-4 rounded-md border border-gray-200">
                <p className="font-semibold text-gray-700 mb-2">Selected Files ({folderFiles.filenames.length}):</p>
                <ul className="text-xs text-gray-600 max-h-32 overflow-y-auto list-disc pl-5">
                  {folderFiles.filenames.map((name, i) => (
                    <li key={i}>{name}</li>
                  ))}
                </ul>
                <div className="mt-3 text-xs text-gray-500 font-semibold grid grid-cols-2 gap-2">
                  <div>CSVs: {folderFiles.csv_list.length}</div>
                  <div>ATS JSONs: {folderFiles.ats_json_list.length}</div>
                  <div>GitHub JSONs: {folderFiles.github_list.length}</div>
                  <div>Notes: {folderFiles.notes_list.length}</div>
                </div>
              </div>
            )}
          </div>
        )}
        {activeTab === "config" && (
          <textarea
            value={configData}
            onChange={(e) => setConfigData(e.target.value)}
            className="w-full h-full p-4 font-mono text-sm border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="Enter JSON Projection Config..."
          />
        )}
      </div>
    </div>
  );
}
