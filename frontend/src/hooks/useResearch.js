// Research hook
import { useState, useEffect, useCallback } from "react";
import { researchAPI } from "../services/api";
import websocketService from "../services/websocket";

export const useResearch = () => {
  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState("idle"); // idle, planning, researching, retrieving, summarizing, completed, error
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!sessionId) return;

    // Connect to WebSocket
    websocketService.connect(sessionId);

    // Add message listener
    const listenerId = "research-hook";
    websocketService.addListener(listenerId, handleWebSocketMessage);

    return () => {
      websocketService.removeListener(listenerId);
      websocketService.disconnect();
    };
  }, [sessionId]);

  const handleWebSocketMessage = useCallback((data) => {
    console.log("WebSocket message:", data);

    switch (data.type) {
      case "status":
        setStatus(data.step);
        setMessage(data.message);
        break;

      case "progress":
        setCurrentStep(data.step);
        setProgress(data.progress);
        setMessage(data.message);
        setStatus(data.step);
        break;

      case "completed":
        setStatus("completed");
        setProgress(100);
        setResult(data.data);
        setMessage("Research completed successfully!");
        break;

      case "error":
        setStatus("error");
        setError(data.message);
        setMessage(`Error: ${data.message}`);
        break;

      default:
        console.warn("Unknown WebSocket message type:", data.type);
    }
  }, []);

  const startResearch = async (query) => {
    try {
      setStatus("initializing");
      setProgress(0);
      setError(null);
      setResult(null);
      setMessage("Starting research...");

      const response = await researchAPI.startResearch(query);
      setSessionId(response.session_id);
      setMessage("Research initiated. Connecting...");
    } catch (err) {
      setStatus("error");
      setError(err.message || "Failed to start research");
      setMessage("Failed to start research");
    }
  };

  const reset = () => {
    setSessionId(null);
    setStatus("idle");
    setProgress(0);
    setCurrentStep("");
    setMessage("");
    setResult(null);
    setError(null);
  };

  return {
    sessionId,
    status,
    progress,
    currentStep,
    message,
    result,
    error,
    startResearch,
    reset,
  };
};
