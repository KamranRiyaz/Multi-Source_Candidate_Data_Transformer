import { Settings } from "lucide-react";

export function Header({ onTransform, loading }) {
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
