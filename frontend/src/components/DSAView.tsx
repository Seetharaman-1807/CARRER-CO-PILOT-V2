import React, { useState, useEffect } from "react";
import { 
  Code2, 
  Play, 
  Lightbulb, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  ShieldCheck,
  ChevronRight,
  Sparkles
} from "lucide-react";
import { api } from "../services/api";

interface DSAViewProps {
  onDataUpdated: () => void;
}

export const DSAView: React.FC<DSAViewProps> = ({ onDataUpdated }) => {
  const [problems, setProblems] = useState<any[]>([]);
  const [selectedProblem, setSelectedProblem] = useState<any>(null);
  const [code, setCode] = useState("");
  const [hintsRevealed, setHintsRevealed] = useState(0);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);

  useEffect(() => {
    loadProblems();
  }, []);

  const loadProblems = async () => {
    try {
      const pList = await api.getDSAProblems();
      setProblems(pList);
      if (pList.length > 0) {
        selectProblem(pList[0].slug);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const selectProblem = async (slug: string) => {
    try {
      const full = await api.getDSAProblem(slug);
      setSelectedProblem(full);
      setCode(full.starter_code);
      setHintsRevealed(0);
      setExecutionResult(null);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRunCode = async () => {
    if (!selectedProblem || !code.trim()) return;
    setIsExecuting(true);
    setExecutionResult(null);

    try {
      const res = await api.submitDSAAttempt({
        problem_id: selectedProblem.id,
        code,
        hints_used: hintsRevealed,
      });
      setExecutionResult(res.execution_result);
      onDataUpdated();
    } catch (err: any) {
      alert(err.message || "Failed to execute code");
    } finally {
      setIsExecuting(false);
    }
  };

  const revealNextHint = () => {
    if (selectedProblem && hintsRevealed < selectedProblem.hints.length) {
      setHintsRevealed(hintsRevealed + 1);
    }
  };

  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: "28px 24px", display: "flex", flexDirection: "column", gap: 28 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffffff" }}>
            Adaptive DSA Practice & Sandbox Verification
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Real code execution against automated test suites. Verified passes directly elevate candidate DSA readiness.
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.8rem", color: "var(--accent-emerald)" }}>
          <ShieldCheck size={16} /> AST Sandboxed Execution Active
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 2.2fr", gap: 24 }}>
        {/* Left Column: Problem Bank */}
        <div className="glass-panel" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
          <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
            <Code2 size={16} color="#38bdf8" />
            Curated Problem Library
          </h3>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {problems.map((p) => {
              const isSelected = selectedProblem?.id === p.id;
              return (
                <button
                  key={p.id}
                  onClick={() => selectProblem(p.slug)}
                  style={{
                    padding: "12px 14px",
                    borderRadius: 10,
                    background: isSelected ? "rgba(99, 102, 241, 0.2)" : "rgba(15, 23, 42, 0.5)",
                    border: isSelected ? "1px solid var(--accent-primary)" : "1px solid var(--border-subtle)",
                    color: "#ffffff",
                    textAlign: "left",
                    cursor: "pointer",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center"
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: "0.85rem" }}>{p.title}</div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 2 }}>
                      {p.topic}
                    </div>
                  </div>

                  <span className={`badge ${p.difficulty === "Easy" ? "badge-low" : p.difficulty === "Medium" ? "badge-medium" : "badge-high"}`} style={{ fontSize: "0.65rem" }}>
                    {p.difficulty}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Column: Problem Description, Interactive Editor, and Execution console */}
        {selectedProblem && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {/* Problem Header & Description */}
            <div className="glass-panel" style={{ padding: 24 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                    <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#ffffff" }}>
                      {selectedProblem.title}
                    </h3>
                    <span className={`badge ${selectedProblem.difficulty === "Easy" ? "badge-low" : "badge-medium"}`}>
                      {selectedProblem.difficulty}
                    </span>
                    <span className="badge badge-info">
                      Topic: {selectedProblem.topic}
                    </span>
                  </div>
                </div>

                {selectedProblem.hints && selectedProblem.hints.length > 0 && (
                  <button
                    className="btn btn-secondary"
                    onClick={revealNextHint}
                    disabled={hintsRevealed >= selectedProblem.hints.length}
                    style={{ padding: "6px 12px", fontSize: "0.75rem" }}
                  >
                    <Lightbulb size={14} color="#f59e0b" />
                    {hintsRevealed >= selectedProblem.hints.length ? "All Hints Revealed" : `Need Hint? (${hintsRevealed}/${selectedProblem.hints.length})`}
                  </button>
                )}
              </div>

              <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
                {selectedProblem.description}
              </p>

              {/* Revealed Hints */}
              {hintsRevealed > 0 && (
                <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 8 }}>
                  {selectedProblem.hints.slice(0, hintsRevealed).map((h: string, idx: number) => (
                    <div key={idx} style={{ padding: "10px 14px", background: "rgba(245, 158, 11, 0.1)", borderRadius: 8, fontSize: "0.8rem", color: "#fde68a" }}>
                      <strong>Hint {idx + 1}:</strong> {h}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Python Code Editor */}
            <div className="glass-panel" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "#94a3b8", display: "flex", alignItems: "center", gap: 6 }}>
                  <Code2 size={16} color="#818cf8" /> Python 3.11 Solution Editor
                </span>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                  AST verified • 5.0s execution timeout
                </span>
              </div>

              <textarea
                style={{
                  width: "100%",
                  minHeight: 220,
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.9rem",
                  background: "#080c14",
                  color: "#38bdf8",
                  padding: 16,
                  borderRadius: 10,
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  outline: "none",
                  resize: "vertical",
                  lineHeight: 1.6
                }}
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  className="btn btn-primary"
                  disabled={isExecuting}
                  onClick={handleRunCode}
                  style={{ padding: "10px 24px", fontSize: "0.9rem" }}
                >
                  <Play size={16} />
                  {isExecuting ? "Executing Test Harness..." : "Run & Submit Code"}
                </button>
              </div>
            </div>

            {/* Execution Console Results */}
            {executionResult && (
              <div className="glass-panel-glow" style={{ padding: 22 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    {executionResult.passed ? (
                      <CheckCircle2 size={22} color="var(--accent-emerald)" />
                    ) : (
                      <XCircle size={22} color="var(--accent-rose)" />
                    )}
                    <span style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff" }}>
                      {executionResult.passed ? "All Test Cases Passed! ✓" : "Solution Failed Test Cases"}
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 14, fontSize: "0.8rem", color: "var(--text-muted)" }}>
                    <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <Clock size={14} /> {executionResult.runtime_ms} ms
                    </span>
                    <span>
                      Passed {executionResult.passed_count} / {executionResult.total}
                    </span>
                  </div>
                </div>

                {executionResult.error && (
                  <div style={{ padding: 12, background: "rgba(244, 63, 94, 0.15)", borderRadius: 8, color: "#fda4af", fontSize: "0.85rem", marginBottom: 14 }}>
                    {executionResult.error}
                  </div>
                )}

                {/* Test case breakdown */}
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {(executionResult.test_results || []).map((tr: any) => (
                    <div key={tr.test_index} style={{
                      padding: "10px 14px",
                      borderRadius: 8,
                      background: "rgba(15, 23, 42, 0.6)",
                      border: "1px solid var(--border-subtle)",
                      fontSize: "0.8rem",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}>
                      <div>
                        <span style={{ fontWeight: 600, color: "#ffffff" }}>Test #{tr.test_index}: </span>
                        <span style={{ color: "var(--text-muted)" }}>Input: {JSON.stringify(tr.input)} → Expected: {JSON.stringify(tr.expected)}</span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ color: tr.passed ? "var(--accent-emerald)" : "var(--accent-rose)", fontWeight: 600 }}>
                          Actual: {JSON.stringify(tr.actual)}
                        </span>
                        {tr.passed ? <CheckCircle2 size={16} color="var(--accent-emerald)" /> : <XCircle size={16} color="var(--accent-rose)" />}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
