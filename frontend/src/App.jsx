import { useState } from "react";
import { Header } from "./components/Header";
import { InputPanel } from "./components/InputPanel";
import { OutputPanel } from "./components/OutputPanel";

const DEFAULT_CONFIG = {
  fields: [
    { path: "full_name", type: "string", required: true },
    {
      path: "primary_email",
      from: "emails[0]",
      type: "string",
      required: true,
    },
    { path: "phone", from: "phones[0]", type: "string", normalize: "E164" },
    {
      path: "skills",
      from: "skills",
      type: "string[]",
      normalize: "canonical",
    },
  ],
  include_confidence: true,
  on_missing: "null",
};

const SAMPLE_CSV = `name,email,phone,current_company,title
Jane Doe,jane.doe@example.com,555-019-2834,Acme Corp,Senior Engineer`;

const SAMPLE_ATS = `{
  "name": "Jane H. Doe",
  "email": "jane@doe.com",
  "location": "San Francisco, CA",
  "skills": ["react", "node", "aws"]
}`;

const SAMPLE_NOTES = `Candidate: Jane Doe
She is currently at Acme Corp as a Staff Engineer.
Phone: (555) 019-2834
Email: jane@doe.com
Skills: React, Python, AWS`;

export default function App() {
  const [activeTab, setActiveTab] = useState("csv");
  const [csvData, setCsvData] = useState(SAMPLE_CSV);
  const [atsData, setAtsData] = useState(SAMPLE_ATS);
  const [notesData, setNotesData] = useState(SAMPLE_NOTES);
  const [folderFiles, setFolderFiles] = useState(null); // { csv_list: [], ats_json_list: [], github_list: [], notes_list: [], files: [] }
  const [configData, setConfigData] = useState(
    JSON.stringify(DEFAULT_CONFIG, null, 2),
  );

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTransform = async () => {
    setLoading(true);
    setError(null);
    try {
      let sources = {};
      
      if (activeTab === "folder" && folderFiles) {
        sources = {
          csv_list: folderFiles.csv_list,
          ats_json_list: folderFiles.ats_json_list,
          github_list: folderFiles.github_list,
          notes_list: folderFiles.notes_list
        };
      } else {
        sources = {
          csv: csvData,
          ats_json: atsData,
          notes: notesData,
        };
      }
      
      const payload = {
        sources,
        config: JSON.parse(configData),
      };

      const res = await fetch("http://localhost:8000/api/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`Server Error: ${res.statusText}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(
        err.message +
          ".\nMake sure you are running the FastAPI backend locally using 'uvicorn app.main:app --reload'",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <Header onTransform={handleTransform} loading={loading} />

      <main className="flex-1 flex overflow-hidden">
        <InputPanel
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          csvData={csvData}
          setCsvData={setCsvData}
          atsData={atsData}
          setAtsData={setAtsData}
          notesData={notesData}
          setNotesData={setNotesData}
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
