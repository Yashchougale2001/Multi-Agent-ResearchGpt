// Query input component
import React, { useState } from "react";
import { Search, Sparkles } from "lucide-react";

const QueryInput = ({ onSubmit, isLoading }) => {
  const [query, setQuery] = useState("");

  const exampleQueries = [
    "What are the latest developments in quantum computing?",
    "Compare different machine learning frameworks for NLP",
    "Analyze the impact of AI on healthcare industry",
    "What are the best practices for RAG implementation?",
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query);
    }
  };

  const handleExampleClick = (example) => {
    setQuery(example);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <Sparkles className="w-12 h-12 text-primary animate-pulse" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Multi-Agent Research Assistant
        </h1>
        <p className="text-lg text-gray-600">
          Powered by LangGraph, ChromaDB, and Advanced AI Agents
        </p>
      </div>

      <form onSubmit={handleSubmit} className="mb-6">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your research question or topic..."
            className="w-full px-6 py-4 pr-16 text-lg border-2 border-gray-300 rounded-2xl focus:outline-none focus:border-primary resize-none transition-colors"
            rows="4"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className={`absolute bottom-4 right-4 p-3 rounded-xl transition-all ${
              query.trim() && !isLoading
                ? "bg-primary text-white hover:bg-blue-600 shadow-lg hover:shadow-xl"
                : "bg-gray-300 text-gray-500 cursor-not-allowed"
            }`}
          >
            <Search className="w-6 h-6" />
          </button>
        </div>
      </form>

      {/* Example Queries */}
      <div className="space-y-3">
        <p className="text-sm text-gray-600 font-medium">Try an example:</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              disabled={isLoading}
              className="text-left p-4 bg-gray-50 hover:bg-gray-100 rounded-xl border border-gray-200 transition-colors text-sm text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QueryInput;
