import React, { useState } from "react";
import { 
  MessageSquare, 
  Send, 
  Award, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  RotateCcw,
  Zap
} from "lucide-react";
import { api } from "../services/api";

interface InterviewViewProps {
  onDataUpdated: () => void;
}

export const InterviewView: React.FC<InterviewViewProps> = ({ onDataUpdated }) => {
  const [session, setSession] = useState<any>(null);
  const [interviewType, setInterviewType] = useState("technical");
  const [difficulty, setDifficulty] = useState("Medium");
  const [isStarting, setIsStarting] = useState(false);

  // Response state
  const [userResponse, setUserResponse] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastEvaluation, setLastEvaluation] = useState<any>(null);

  const handleStartSession = async () => {
    setIsStarting(true);
    setLastEvaluation(null);
    try {
      const sess = await api.startInterview({
        type: interviewType,
        difficulty,
      });
      setSession(sess);
      onDataUpdated();
    } catch (err: any) {
      alert(err.message || "Failed to start interview session");
    } finally {
      setIsStarting(false);
    }
  };

  const handleSubmitResponse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!session || !userResponse.trim()) return;

    const currentQuestion = session.questions[session.current_question_idx];
    if (!currentQuestion) return;

    setIsSubmitting(true);
    try {
      const respItem = await api.submitInterviewResponse(session.id, {
        question_id: currentQuestion.id,
        response: userResponse,
      });
      setLastEvaluation(respItem.evaluation);
      setUserResponse("");

      // Refresh session state to get updated questions index
      const updatedSess = await api.getInterviewSession(session.id);
      setSession(updatedSess);
      onDataUpdated();
    } catch (err: any) {
      alert(err.message || "Failed to submit response");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCompleteInterview = async () => {
    if (!session) return;
    try {
      const finished = await api.completeInterview(session.id);
      setSession(finished);
      onDataUpdated();
    } catch (err: any) {
      alert(err.message || "Failed to complete interview");
    }
  };

  const currentQ = session?.questions?.[session.current_question_idx];
  const isCompleted = session?.status === "completed";

  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: "28px 24px", display: "flex", flexDirection: "column", gap: 28 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffffff" }}>
            Adaptive Mock Interview Studio
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Multi-turn technical and behavioral simulation with rubric-graded accuracy, clarity, and depth.
          </p>
        </div>

        {session && !isCompleted && (
          <button 
            className="btn btn-secondary" 
            onClick={handleCompleteInterview}
          >
            Finish & Generate Final Report
          </button>
        )}
      </div>

      {!session ? (
        /* Setup Studio */
        <div className="glass-panel" style={{ padding: 48, maxWidth: 640, margin: "0 auto", textAlign: "center" }}>
          <MessageSquare size={48} color="#818cf8" style={{ margin: "0 auto 16px", display: "block" }} />
          <h3 style={{ fontSize: "1.3rem", fontWeight: 700, color: "#ffffff", marginBottom: 8 }}>
            Start Adaptive Interview Round
          </h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: 28 }}>
            Simulate realistic questions tailored to your target role, with responses analyzed for conceptual accuracy and depth.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 20, textAlign: "left" }}>
            <div>
              <label style={{ fontSize: "0.85rem", color: "var(--text-secondary)", display: "block", marginBottom: 8 }}>
                Interview Mode:
              </label>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <button
                  type="button"
                  onClick={() => setInterviewType("technical")}
                  className="btn"
                  style={{
                    background: interviewType === "technical" ? "rgba(99, 102, 241, 0.25)" : "rgba(15, 23, 42, 0.6)",
                    border: interviewType === "technical" ? "1px solid var(--accent-primary)" : "1px solid var(--border-subtle)",
                    color: "#ffffff"
                  }}
                >
                  Technical & Architecture
                </button>
                <button
                  type="button"
                  onClick={() => setInterviewType("behavioral")}
                  className="btn"
                  style={{
                    background: interviewType === "behavioral" ? "rgba(99, 102, 241, 0.25)" : "rgba(15, 23, 42, 0.6)",
                    border: interviewType === "behavioral" ? "1px solid var(--accent-primary)" : "1px solid var(--border-subtle)",
                    color: "#ffffff"
                  }}
                >
                  Behavioral & Leadership
                </button>
              </div>
            </div>

            <div>
              <label style={{ fontSize: "0.85rem", color: "var(--text-secondary)", display: "block", marginBottom: 8 }}>
                Target Difficulty:
              </label>
              <select
                className="input-field"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="Easy">Standard / Associate</option>
                <option value="Medium">Mid-Level / Senior</option>
                <option value="Hard">Staff / Principal</option>
              </select>
            </div>

            <button
              className="btn btn-primary"
              disabled={isStarting}
              onClick={handleStartSession}
              style={{ marginTop: 12, padding: "12px 24px" }}
            >
              {isStarting ? "Initializing AI Studio..." : "Launch Interview Session"}
            </button>
          </div>
        </div>
      ) : isCompleted ? (
        /* Final Report Screen */
        <div className="glass-panel-glow" style={{ padding: 36 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div>
              <span className="badge badge-low" style={{ marginBottom: 6 }}>Round Completed</span>
              <h3 style={{ fontSize: "1.4rem", fontWeight: 800, color: "#ffffff" }}>
                Interview Performance Evaluation
              </h3>
            </div>
            <button className="btn btn-secondary" onClick={() => setSession(null)}>
              Start New Session <RotateCcw size={14} />
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 24 }}>
            <div style={{ padding: 18, background: "rgba(15, 23, 42, 0.6)", borderRadius: 12, textAlign: "center" }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Technical Accuracy</div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "var(--accent-emerald)" }}>
                {session.final_evaluation?.technical_accuracy || "—"}/10
              </div>
            </div>
            <div style={{ padding: 18, background: "rgba(15, 23, 42, 0.6)", borderRadius: 12, textAlign: "center" }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Clarity & Structure</div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#38bdf8" }}>
                {session.final_evaluation?.clarity || "—"}/10
              </div>
            </div>
            <div style={{ padding: 18, background: "rgba(15, 23, 42, 0.6)", borderRadius: 12, textAlign: "center" }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Overall Composite</div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "var(--accent-primary)" }}>
                {session.final_evaluation?.overall || "—"}/10
              </div>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <div style={{ padding: 18, background: "rgba(15, 23, 42, 0.6)", borderRadius: 12 }}>
              <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--accent-emerald)", marginBottom: 10, display: "flex", alignItems: "center", gap: 6 }}>
                <CheckCircle2 size={16} /> Demonstrated Strengths
              </h4>
              <ul style={{ fontSize: "0.85rem", color: "var(--text-secondary)", paddingLeft: 18 }}>
                {(session.final_evaluation?.strengths || []).map((s: string, i: number) => (
                  <li key={i} style={{ marginBottom: 6 }}>{s}</li>
                ))}
              </ul>
            </div>

            <div style={{ padding: 18, background: "rgba(15, 23, 42, 0.6)", borderRadius: 12 }}>
              <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--accent-amber)", marginBottom: 10, display: "flex", alignItems: "center", gap: 6 }}>
                <AlertCircle size={16} /> Targeted Refinements
              </h4>
              <ul style={{ fontSize: "0.85rem", color: "var(--text-secondary)", paddingLeft: 18 }}>
                {(session.final_evaluation?.improvements || []).map((imp: string, i: number) => (
                  <li key={i} style={{ marginBottom: 6 }}>{imp}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ) : (
        /* Active Multi-Turn Interview Screen */
        <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1.2fr", gap: 24 }}>
          {/* Question & Response Column */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {/* Live Question Card */}
            <div className="glass-panel-glow" style={{ padding: 24 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                <span className="badge badge-info">
                  Question {(session.current_question_idx || 0) + 1} of {session.questions?.length || 1}
                </span>
                <span className="badge badge-low">
                  Focus: {currentQ?.focus_skill || "Architecture"}
                </span>
              </div>

              <h3 style={{ fontSize: "1.2rem", fontWeight: 700, color: "#ffffff", lineHeight: 1.5 }}>
                {currentQ?.question}
              </h3>
            </div>

            {/* Answer Input */}
            <form onSubmit={handleSubmitResponse} className="glass-panel" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
              <label style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Your Answer (Explain architectural choices, edge cases, and trade-offs):
              </label>

              <textarea
                className="input-field"
                rows={7}
                placeholder="Type your structured explanation here..."
                value={userResponse}
                onChange={(e) => setUserResponse(e.target.value)}
              />

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ fontSize: "0.75rem", color: "var(--accent-emerald)", display: "flex", alignItems: "center", gap: 6 }}>
                  <Zap size={14} /> Submitting automatically produces candidate skill evidence
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting || !userResponse.trim()}
                  className="btn btn-primary"
                  style={{ padding: "10px 20px" }}
                >
                  <Send size={15} />
                  {isSubmitting ? "Evaluating Rubric..." : "Submit Response"}
                </button>
              </div>
            </form>
          </div>

          {/* Feedback & Rubric Column */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#ffffff", marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
                <Award size={18} color="#38bdf8" />
                Latest Rubric Evaluation
              </h3>

              {!lastEvaluation ? (
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", padding: 20, textAlign: "center" }}>
                  Submit an answer to receive live evaluation on technical accuracy, clarity, and conceptual depth.
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>Overall Answer Rating</span>
                    <span style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--accent-emerald)" }}>
                      {lastEvaluation.overall}/10
                    </span>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, fontSize: "0.8rem" }}>
                    <div style={{ padding: 8, background: "rgba(15, 23, 42, 0.5)", borderRadius: 6 }}>
                      Accuracy: <strong>{lastEvaluation.technical_accuracy}/10</strong>
                    </div>
                    <div style={{ padding: 8, background: "rgba(15, 23, 42, 0.5)", borderRadius: 6 }}>
                      Clarity: <strong>{lastEvaluation.clarity}/10</strong>
                    </div>
                  </div>

                  {lastEvaluation.matched_concepts?.length > 0 && (
                    <div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 4 }}>Covered Concepts:</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                        {lastEvaluation.matched_concepts.map((c: string, idx: number) => (
                          <span key={idx} className="badge badge-low" style={{ fontSize: "0.65rem" }}>{c}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {lastEvaluation.improvements?.length > 0 && (
                    <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                      <strong>Suggested Improvement:</strong> {lastEvaluation.improvements[0]}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
