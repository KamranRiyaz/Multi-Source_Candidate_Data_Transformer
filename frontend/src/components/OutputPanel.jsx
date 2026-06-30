export function OutputPanel({ error, result }) {
  return (
    <div className="w-1/2 flex flex-col bg-gray-900 text-gray-100 overflow-hidden">
      <div className="flex items-center px-6 py-3 border-b border-gray-800 bg-gray-950">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">
          Output JSON
        </h2>
      </div>
      <div className="flex-1 p-6 overflow-auto">
        {error ? (
          <div className="p-4 bg-red-900/50 border border-red-500/50 rounded-md text-red-200 text-sm font-mono whitespace-pre-wrap">
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
                Click "Run Pipeline" to transform the inputs.
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
