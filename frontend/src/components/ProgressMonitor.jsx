// Progress monitor component
import React from "react";
import {
  CheckCircle2,
  Loader2,
  AlertCircle,
  Brain,
  Search,
  Database,
  FileText,
} from "lucide-react";

const ProgressMonitor = ({ status, progress, currentStep, message }) => {
  const steps = [
    {
      id: "planning",
      label: "Planning",
      icon: Brain,
      description: "Decomposing query into subtasks",
    },
    {
      id: "researching",
      label: "Researching",
      icon: Search,
      description: "Gathering information",
    },
    {
      id: "retrieving",
      label: "Retrieving",
      icon: Database,
      description: "Querying knowledge base",
    },
    {
      id: "summarizing",
      label: "Summarizing",
      icon: FileText,
      description: "Generating report",
    },
  ];

  const getStepStatus = (stepId) => {
    const stepIndex = steps.findIndex((s) => s.id === stepId);
    const currentIndex = steps.findIndex((s) => s.id === currentStep);

    if (status === "completed") return "completed";
    if (status === "error") return "error";
    if (stepIndex < currentIndex) return "completed";
    if (stepId === currentStep) return "active";
    return "pending";
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            Overall Progress
          </span>
          <span className="text-sm font-medium text-primary">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-primary to-secondary h-full transition-all duration-500 ease-out rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Status Message */}
      <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-xl">
        <div className="flex items-center">
          <Loader2 className="w-5 h-5 text-primary animate-spin mr-3" />
          <span className="text-blue-900 font-medium">{message}</span>
        </div>
      </div>

      {/* Step Progress */}
      <div className="space-y-4">
        {steps.map((step, index) => {
          const stepStatus = getStepStatus(step.id);
          const Icon = step.icon;

          return (
            <div
              key={step.id}
              className={`relative p-5 rounded-xl border-2 transition-all ${
                stepStatus === "active"
                  ? "border-primary bg-blue-50 shadow-lg"
                  : stepStatus === "completed"
                    ? "border-green-300 bg-green-50"
                    : stepStatus === "error"
                      ? "border-red-300 bg-red-50"
                      : "border-gray-200 bg-gray-50"
              }`}
            >
              <div className="flex items-center">
                {/* Step Icon */}
                <div
                  className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center mr-4 ${
                    stepStatus === "active"
                      ? "bg-primary text-white"
                      : stepStatus === "completed"
                        ? "bg-green-500 text-white"
                        : stepStatus === "error"
                          ? "bg-red-500 text-white"
                          : "bg-gray-300 text-gray-600"
                  }`}
                >
                  {stepStatus === "completed" ? (
                    <CheckCircle2 className="w-6 h-6" />
                  ) : stepStatus === "active" ? (
                    <Icon className="w-6 h-6 animate-pulse" />
                  ) : stepStatus === "error" ? (
                    <AlertCircle className="w-6 h-6" />
                  ) : (
                    <Icon className="w-6 h-6" />
                  )}
                </div>

                {/* Step Info */}
                <div className="flex-grow">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {step.label}
                  </h3>
                  <p className="text-sm text-gray-600">{step.description}</p>
                </div>

                {/* Status Indicator */}
                <div className="flex-shrink-0">
                  {stepStatus === "active" && (
                    <Loader2 className="w-6 h-6 text-primary animate-spin" />
                  )}
                  {stepStatus === "completed" && (
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                  )}
                </div>
              </div>

              {/* Connecting Line */}
              {index < steps.length - 1 && (
                <div
                  className={`absolute left-10 top-full w-0.5 h-4 -mb-4 ${
                    getStepStatus(steps[index + 1].id) === "completed" ||
                    getStepStatus(steps[index + 1].id) === "active"
                      ? "bg-primary"
                      : "bg-gray-300"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProgressMonitor;
