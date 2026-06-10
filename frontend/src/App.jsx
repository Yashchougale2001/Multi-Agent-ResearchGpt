import React, { useState } from "react";
import QueryInput from "./components/QueryInput";
import ProgressMonitor from "./components/ProgressMonitor";
import ResultDisplay from "./components/ResultDisplay";
import AgentStatus from "./components/AgentStatus";
import ErrorBoundary from "./components/ErrorBoundary";
import Notification from "./components/Notification";
import { useResearch } from "./hooks/useResearch";
import { ArrowLeft, AlertCircle, Settings, FileText } from "lucide-react";

function App() {
  const [currentQuery, setCurrentQuery] = useState("");
  const [showAgentStatus, setShowAgentStatus] = useState(true);
  const [notification, setNotification] = useState(null);

  const {
    sessionId,
    status,
    progress,
    currentStep,
    message,
    result,
    error,
    startResearch,
    reset,
  } = useResearch();

  const handleQuerySubmit = (query) => {
    setCurrentQuery(query);
    startResearch(query);
    setNotification({
      type: "info",
      message: "Research started! Our AI agents are working on your query.",
    });
  };

  const handleReset = () => {
    setCurrentQuery("");
    reset();
    setNotification(null);
  };

  const isActive =
    status !== "idle" && status !== "completed" && status !== "error";
  const isCompleted = status === "completed";
  const hasError = status === "error";

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* Notification */}
        {notification && (
          <Notification
            type={notification.type}
            message={notification.message}
            onClose={() => setNotification(null)}
          />
        )}

        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-xl">RA</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Research Assistant
                </h1>
                <p className="text-xs text-gray-500">
                  Multi-Agent AI System • Powered by Groq
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {(isActive || isCompleted) && (
                <>
                  <button
                    onClick={() => setShowAgentStatus(!showAgentStatus)}
                    className={`flex items-center px-3 py-2 rounded-lg transition-colors ${
                      showAgentStatus
                        ? "bg-blue-100 text-blue-700"
                        : "text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Agent Status
                  </button>

                  <button
                    onClick={handleReset}
                    className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    New Research
                  </button>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          {/* Error Display */}
          {hasError && (
            <div className="max-w-4xl mx-auto mb-6">
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start">
                <AlertCircle className="w-6 h-6 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 mb-1">
                    Research Failed
                  </h3>
                  <p className="text-red-700 text-sm">{error}</p>
                  <button
                    onClick={handleReset}
                    className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                  >
                    Try Again
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Query Input (show when idle or error) */}
          {(status === "idle" || hasError) && (
            <QueryInput onSubmit={handleQuerySubmit} isLoading={isActive} />
          )}

          {/* Active Research View */}
          {isActive && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Progress Monitor */}
              <div
                className={showAgentStatus ? "lg:col-span-2" : "lg:col-span-3"}
              >
                <ProgressMonitor
                  status={status}
                  progress={progress}
                  currentStep={currentStep}
                  message={message}
                />
              </div>

              {/* Agent Status (collapsible) */}
              {showAgentStatus && (
                <div className="lg:col-span-1">
                  <div className="sticky top-24">
                    <AgentStatus
                      status={status}
                      currentStep={currentStep}
                      subtasks={[]}
                      messages={[]}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Result Display (show when completed) */}
          {isCompleted && result && (
            <ResultDisplay result={result} query={currentQuery} />
          )}
        </main>

        {/* Footer */}
        <footer className="mt-16 py-8 border-t border-gray-200 bg-white">
          <div className="max-w-7xl mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* About */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">About</h3>
                <p className="text-sm text-gray-600">
                  Multi-Agent Research Assistant using LangGraph, Groq AI, and
                  ChromaDB for intelligent research automation.
                </p>
              </div>

              {/* Tech Stack */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Powered By</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Groq API (Llama 3)</li>
                  <li>• LangGraph & LangChain</li>
                  <li>• ChromaDB (Vector DB)</li>
                  <li>• FastAPI + React</li>
                </ul>
              </div>

              {/* Links */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Resources</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>
                    <a
                      href="https://console.groq.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-primary transition-colors"
                    >
                      Get Groq API Key
                    </a>
                  </li>
                  <li>
                    <a
                      href="/docs"
                      className="hover:text-primary transition-colors"
                    >
                      Documentation
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-primary transition-colors"
                    >
                      GitHub Repository
                    </a>
                  </li>
                </ul>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t border-gray-200 text-center">
              <p className="text-sm text-gray-600">
                Built with ❤️ using LangGraph, Groq, and FastAPI
              </p>
              <p className="mt-2 text-xs text-gray-500">
                © 2024 Multi-Agent Research Assistant. All rights reserved.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;
