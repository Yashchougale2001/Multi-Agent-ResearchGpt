// Result display component
import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  FileText,
  Download,
  Copy,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  TrendingUp,
} from "lucide-react";

const ResultDisplay = ({ result, query }) => {
  const [copied, setCopied] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);
  const [showSubtasks, setShowSubtasks] = useState(false);

  if (!result) return null;

  const { final_report, metadata, subtasks } = result;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(final_report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([final_report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `research-report-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full max-w-5xl mx-auto p-6">
      {/* Success Banner */}
      <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex items-center">
        <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
        <div>
          <h3 className="font-semibold text-green-900">Research Complete!</h3>
          <p className="text-sm text-green-700">
            Your comprehensive report is ready
          </p>
        </div>
      </div>

      {/* Query Display */}
      <div className="mb-6 p-5 bg-blue-50 border border-blue-200 rounded-xl">
        <h4 className="text-sm font-medium text-blue-900 mb-2">
          Research Query:
        </h4>
        <p className="text-blue-800">{query}</p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={handleCopy}
          className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          {copied ? (
            <>
              <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
              <span className="text-green-600">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 mr-2" />
              <span>Copy Report</span>
            </>
          )}
        </button>

        <button
          onClick={handleDownload}
          className="flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Download className="w-4 h-4 mr-2" />
          <span>Download PDF</span>
        </button>
      </div>

      {/* Metadata Summary */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-white rounded-xl border border-gray-200">
          <div className="text-2xl font-bold text-primary">
            {metadata.total_subtasks}
          </div>
          <div className="text-sm text-gray-600">Subtasks</div>
        </div>
        <div className="p-4 bg-white rounded-xl border border-gray-200">
          <div className="text-2xl font-bold text-green-600">
            {metadata.total_research_results}
          </div>
          <div className="text-sm text-gray-600">Research Results</div>
        </div>
        <div className="p-4 bg-white rounded-xl border border-gray-200">
          <div className="text-2xl font-bold text-purple-600">
            {metadata.total_documents_retrieved}
          </div>
          <div className="text-sm text-gray-600">Documents</div>
        </div>
        <div className="p-4 bg-white rounded-xl border border-gray-200">
          <div className="text-2xl font-bold text-orange-600">
            {(metadata.avg_document_relevance * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-600">Avg Relevance</div>
        </div>
      </div>

      {/* Subtasks Accordion */}
      {subtasks && subtasks.length > 0 && (
        <div className="mb-6">
          <button
            onClick={() => setShowSubtasks(!showSubtasks)}
            className="w-full flex items-center justify-between p-4 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center">
              <TrendingUp className="w-5 h-5 text-primary mr-3" />
              <span className="font-semibold text-gray-900">
                Research Plan ({subtasks.length} subtasks)
              </span>
            </div>
            {showSubtasks ? <ChevronUp /> : <ChevronDown />}
          </button>

          {showSubtasks && (
            <div className="mt-3 p-5 bg-gray-50 rounded-xl border border-gray-200">
              <div className="space-y-3">
                {subtasks.map((task, index) => (
                  <div
                    key={task.id}
                    className="p-4 bg-white rounded-lg border border-gray-200"
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-semibold mr-3">
                        {index + 1}
                      </div>
                      <div className="flex-grow">
                        <div className="flex items-center mb-1">
                          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded mr-2">
                            {task.type}
                          </span>
                          <span className="text-xs text-gray-500">
                            Priority: {task.priority}
                          </span>
                        </div>
                        <p className="text-gray-800">{task.description}</p>
                      </div>
                      <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 ml-3" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Main Report */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="p-5 bg-gradient-to-r from-primary to-secondary text-white flex items-center">
          <FileText className="w-6 h-6 mr-3" />
          <h2 className="text-xl font-bold">Research Report</h2>
        </div>

        <div className="p-8 prose prose-lg max-w-none">
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className="text-3xl font-bold text-gray-900 mb-4 pb-2 border-b-2 border-primary">
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-2xl font-bold text-gray-800 mt-8 mb-3">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-2">
                  {children}
                </h3>
              ),
              p: ({ children }) => (
                <p className="text-gray-700 leading-relaxed mb-4">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="list-disc list-inside space-y-2 mb-4 text-gray-700">
                  {children}
                </ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-inside space-y-2 mb-4 text-gray-700">
                  {children}
                </ol>
              ),
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:text-blue-700 underline inline-flex items-center"
                >
                  {children}
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              ),
              code: ({ children }) => (
                <code className="px-2 py-1 bg-gray-100 text-red-600 rounded text-sm">
                  {children}
                </code>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-primary pl-4 italic text-gray-600 my-4">
                  {children}
                </blockquote>
              ),
            }}
          >
            {final_report}
          </ReactMarkdown>
        </div>
      </div>

      {/* Metadata Details */}
      <div className="mt-6">
        <button
          onClick={() => setShowMetadata(!showMetadata)}
          className="w-full flex items-center justify-between p-4 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
        >
          <span className="font-semibold text-gray-900">Research Metadata</span>
          {showMetadata ? <ChevronUp /> : <ChevronDown />}
        </button>

        {showMetadata && (
          <div className="mt-3 p-5 bg-gray-50 rounded-xl border border-gray-200">
            <pre className="text-sm text-gray-700 overflow-x-auto">
              {JSON.stringify(metadata, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultDisplay;
