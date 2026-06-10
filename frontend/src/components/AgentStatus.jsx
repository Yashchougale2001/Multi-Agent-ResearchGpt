// Agent status component
import React, { useState, useEffect } from "react";
import {
  Activity,
  Brain,
  Search,
  Database,
  FileText,
  CheckCircle2,
  Loader2,
  Clock,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
} from "lucide-react";

const AgentStatus = ({ status, currentStep, subtasks = [], messages = [] }) => {
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [agentLogs, setAgentLogs] = useState({
    planner: [],
    researcher: [],
    retriever: [],
    summarizer: [],
  });

  useEffect(() => {
    // Update agent logs based on messages
    if (messages && messages.length > 0) {
      const newLogs = { ...agentLogs };
      messages.forEach((msg) => {
        if (msg.agent && newLogs[msg.agent.toLowerCase()]) {
          newLogs[msg.agent.toLowerCase()].push({
            content: msg.content,
            timestamp: new Date().toISOString(),
            role: msg.role,
          });
        }
      });
      setAgentLogs(newLogs);
    }
  }, [messages]);

  const agents = [
    {
      id: "planner",
      name: "Planner Agent",
      icon: Brain,
      color: "blue",
      description: "Analyzing query and creating research plan",
      activeOn: ["planning", "initializing"],
      tasks: [
        "Query decomposition",
        "Task prioritization",
        "Strategy formulation",
      ],
    },
    {
      id: "researcher",
      name: "Research Agent",
      icon: Search,
      color: "purple",
      description: "Gathering information from multiple sources",
      activeOn: ["researching"],
      tasks: [
        "Web search execution",
        "API data collection",
        "Content extraction",
      ],
    },
    {
      id: "retriever",
      name: "Retriever Agent",
      icon: Database,
      color: "green",
      description: "Querying knowledge base with RAG",
      activeOn: ["retrieving"],
      tasks: ["Semantic search", "Document retrieval", "Relevance ranking"],
    },
    {
      id: "summarizer",
      name: "Summarizer Agent",
      icon: FileText,
      color: "orange",
      description: "Generating comprehensive report",
      activeOn: ["summarizing"],
      tasks: [
        "Information synthesis",
        "Report structuring",
        "Quality assurance",
      ],
    },
  ];

  const getAgentStatus = (agent) => {
    if (status === "completed") return "completed";
    if (status === "error" || status === "failed") return "error";
    if (agent.activeOn.includes(currentStep) || agent.activeOn.includes(status))
      return "active";

    // Check if agent should be completed
    const agentIndex = agents.findIndex((a) => a.id === agent.id);
    const currentAgentIndex = agents.findIndex(
      (a) => a.activeOn.includes(currentStep) || a.activeOn.includes(status),
    );

    if (agentIndex < currentAgentIndex) return "completed";
    return "pending";
  };

  const getStatusColor = (agentStatus) => {
    switch (agentStatus) {
      case "active":
        return "border-blue-500 bg-blue-50";
      case "completed":
        return "border-green-500 bg-green-50";
      case "error":
        return "border-red-500 bg-red-50";
      default:
        return "border-gray-300 bg-gray-50";
    }
  };

  const getIconColor = (agent, agentStatus) => {
    if (agentStatus === "active") return `bg-${agent.color}-500 text-white`;
    if (agentStatus === "completed") return "bg-green-500 text-white";
    if (agentStatus === "error") return "bg-red-500 text-white";
    return "bg-gray-300 text-gray-600";
  };

  const toggleAgent = (agentId) => {
    setExpandedAgent(expandedAgent === agentId ? null : agentId);
  };

  const getAgentMetrics = (agentId) => {
    switch (agentId) {
      case "planner":
        return {
          processed: subtasks.length,
          total: subtasks.length,
          metric: "Subtasks Created",
        };
      case "researcher":
        return {
          processed: subtasks.filter((t) => t.status === "completed").length,
          total: subtasks.length,
          metric: "Tasks Completed",
        };
      case "retriever":
        return {
          processed: agentLogs.retriever.length,
          total: 5,
          metric: "Documents Retrieved",
        };
      case "summarizer":
        return {
          processed: agentLogs.summarizer.length,
          total: 1,
          metric: "Reports Generated",
        };
      default:
        return { processed: 0, total: 0, metric: "Tasks" };
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center">
          <Activity className="w-7 h-7 mr-3 text-primary" />
          Agent Activity Monitor
        </h2>
        <p className="text-gray-600">Real-time status of all research agents</p>
      </div>

      {/* Agent Cards */}
      <div className="space-y-4">
        {agents.map((agent, index) => {
          const agentStatus = getAgentStatus(agent);
          const Icon = agent.icon;
          const isExpanded = expandedAgent === agent.id;
          const metrics = getAgentMetrics(agent.id);
          const logs = agentLogs[agent.id] || [];

          return (
            <div
              key={agent.id}
              className={`border-2 rounded-xl transition-all duration-300 ${getStatusColor(agentStatus)}`}
            >
              {/* Agent Header */}
              <div
                className="p-5 cursor-pointer"
                onClick={() => toggleAgent(agent.id)}
              >
                <div className="flex items-center justify-between">
                  {/* Left Side - Icon & Info */}
                  <div className="flex items-center flex-grow">
                    <div
                      className={`w-14 h-14 rounded-xl flex items-center justify-center mr-4 transition-all ${getIconColor(agent, agentStatus)}`}
                    >
                      {agentStatus === "active" ? (
                        <Icon className="w-7 h-7 animate-pulse" />
                      ) : agentStatus === "completed" ? (
                        <CheckCircle2 className="w-7 h-7" />
                      ) : agentStatus === "error" ? (
                        <AlertTriangle className="w-7 h-7" />
                      ) : (
                        <Icon className="w-7 h-7" />
                      )}
                    </div>

                    <div className="flex-grow">
                      <div className="flex items-center mb-1">
                        <h3 className="text-lg font-semibold text-gray-900 mr-3">
                          {agent.name}
                        </h3>
                        <StatusBadge status={agentStatus} />
                      </div>
                      <p className="text-sm text-gray-600">
                        {agent.description}
                      </p>

                      {/* Metrics */}
                      {agentStatus !== "pending" && (
                        <div className="mt-2 flex items-center text-sm">
                          <span className="text-gray-500 mr-2">
                            {metrics.metric}:
                          </span>
                          <span className="font-semibold text-gray-700">
                            {metrics.processed}/{metrics.total}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right Side - Activity Indicator & Expand */}
                  <div className="flex items-center ml-4">
                    {agentStatus === "active" && (
                      <Loader2 className="w-6 h-6 text-blue-500 animate-spin mr-3" />
                    )}
                    {isExpanded ? (
                      <ChevronDown className="w-6 h-6 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                </div>

                {/* Progress Bar for Active Agent */}
                {agentStatus === "active" && (
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-500 animate-pulse"
                        style={{ width: "60%" }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="border-t border-gray-200 p-5 bg-white">
                  {/* Tasks */}
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">
                      Tasks:
                    </h4>
                    <div className="space-y-2">
                      {agent.tasks.map((task, idx) => (
                        <div key={idx} className="flex items-center text-sm">
                          <div
                            className={`w-2 h-2 rounded-full mr-3 ${
                              agentStatus === "completed"
                                ? "bg-green-500"
                                : agentStatus === "active" && idx === 0
                                  ? "bg-blue-500 animate-pulse"
                                  : "bg-gray-300"
                            }`}
                          />
                          <span className="text-gray-600">{task}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Subtasks (for Planner) */}
                  {agent.id === "planner" && subtasks.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-gray-700 mb-3">
                        Generated Subtasks ({subtasks.length}):
                      </h4>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {subtasks.map((subtask, idx) => (
                          <div
                            key={subtask.id}
                            className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                          >
                            <div className="flex items-start">
                              <span className="text-xs font-semibold text-blue-600 mr-2">
                                #{idx + 1}
                              </span>
                              <div className="flex-grow">
                                <p className="text-sm text-gray-700">
                                  {subtask.description}
                                </p>
                                <div className="flex items-center mt-1">
                                  <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded mr-2">
                                    {subtask.type}
                                  </span>
                                  <span
                                    className={`text-xs px-2 py-0.5 rounded ${
                                      subtask.status === "completed"
                                        ? "bg-green-100 text-green-700"
                                        : subtask.status === "in_progress"
                                          ? "bg-yellow-100 text-yellow-700"
                                          : "bg-gray-100 text-gray-700"
                                    }`}
                                  >
                                    {subtask.status}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Activity Logs */}
                  {logs.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                        <Clock className="w-4 h-4 mr-2" />
                        Activity Log:
                      </h4>
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {logs
                          .slice(-5)
                          .reverse()
                          .map((log, idx) => (
                            <div
                              key={idx}
                              className="text-xs text-gray-600 p-2 bg-gray-50 rounded"
                            >
                              <span className="text-gray-400 mr-2">
                                {new Date(log.timestamp).toLocaleTimeString()}
                              </span>
                              {log.content}
                            </div>
                          ))}
                      </div>
                    </div>
                  )}

                  {/* No Activity Message */}
                  {logs.length === 0 && agentStatus === "pending" && (
                    <div className="text-center py-4 text-gray-400 text-sm">
                      <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      Waiting to start...
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Overall System Status */}
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Activity className="w-5 h-5 text-blue-600 mr-2" />
            <span className="font-semibold text-gray-800">System Status:</span>
          </div>
          <div className="flex items-center">
            {status === "completed" ? (
              <>
                <CheckCircle2 className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-green-700 font-semibold">
                  All Agents Completed
                </span>
              </>
            ) : status === "error" || status === "failed" ? (
              <>
                <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                <span className="text-red-700 font-semibold">
                  Error Occurred
                </span>
              </>
            ) : (
              <>
                <Loader2 className="w-5 h-5 text-blue-600 mr-2 animate-spin" />
                <span className="text-blue-700 font-semibold">
                  Processing...
                </span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Status Badge Component
const StatusBadge = ({ status }) => {
  const badges = {
    active: { color: "bg-blue-500", text: "Active", animate: "animate-pulse" },
    completed: { color: "bg-green-500", text: "Completed", animate: "" },
    error: { color: "bg-red-500", text: "Error", animate: "" },
    pending: { color: "bg-gray-400", text: "Pending", animate: "" },
  };

  const badge = badges[status] || badges.pending;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold text-white ${badge.color} ${badge.animate}`}
    >
      {badge.text}
    </span>
  );
};

export default AgentStatus;
