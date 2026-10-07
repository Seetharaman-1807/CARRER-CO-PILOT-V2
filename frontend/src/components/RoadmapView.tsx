import React, { useState, useEffect } from "react";
import { 
  Map, 
  CheckCircle, 
  Clock, 
  RotateCw, 
  Calendar, 
  Target, 
  Award,
  Sparkles,
  Zap
} from "lucide-react";
import { api } from "../services/api";

interface RoadmapViewProps {
  onDataUpdated: () => void;
}

export const RoadmapView: React.FC<RoadmapViewProps> = ({ onDataUpdated }) => {
  const [roadmap, setRoadmap] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [completingTaskId, setCompletingTaskId] = useState<number | null>(null);

  useEffect(() => {
    loadRoadmap();
  }, []);

  const loadRoadmap = async () => {
    try {
      const rm = await api.getRoadmap();
      setRoadmap(rm);
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const rm = await api.generateRoadmap();
      setRoadmap(rm);
      onDataUpdated();
    } catch (err: any) {
      alert(err.message || "Failed to generate roadmap");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCompleteTask = async (taskId: number) => {
    setCompletingTaskId(taskId);
    try {
      await api.completeRoadmapTask(taskId);
      await loadRoadmap();
      onDataUpdated();
    } catch (err: any) {
      alert(err.message || "Failed to mark task complete");
    } finally {
      setCompletingTaskId(null);
    }
  };

  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: "28px 24px", display: "flex", flexDirection: "column", gap: 28 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffffff" }}>
            Personalized Adaptive Career Roadmap
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Continuous learning milestones dynamically prioritized by your candidate skill gaps and available preparation time.
          </p>
        </div>

        <button 
          className="btn btn-primary" 
          disabled={isGenerating}
          onClick={handleGenerate}
          style={{ display: "flex", alignItems: "center", gap: 8 }}
        >
          <RotateCw size={16} className={isGenerating ? "spin" : ""} />
          {roadmap ? "Adapt & Re-Generate Roadmap" : "Generate Adaptive Roadmap"}
        </button>
      </div>

      {!roadmap ? (
        <div className="glass-panel" style={{ padding: 60, textAlign: "center" }}>
          <Map size={48} color="#818cf8" style={{ margin: "0 auto 16px", display: "block" }} />
          <h3 style={{ fontSize: "1.3rem", fontWeight: 700, color: "#ffffff", marginBottom: 8 }}>
            No Active Roadmap Generated
          </h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", maxWidth: 500, margin: "0 auto 24px" }}>
            Click generate to synthesize an individualized roadmap targeting your identified skill gaps and interview timeline.
          </p>
          <button className="btn btn-primary" onClick={handleGenerate}>
            Generate Roadmap Now
          </button>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1.8fr 1.2fr", gap: 28 }}>
          {/* Left Column: Actionable Tasks with Feedback Loop */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
                <Target size={18} color="#38bdf8" />
                Actionable Milestones ({roadmap.tasks?.length || 0})
              </h3>
              <div style={{ fontSize: "0.75rem", color: "var(--accent-emerald)", display: "flex", alignItems: "center", gap: 6 }}>
                <Zap size={14} /> Closed Feedback: Completion Updates Skill Profile
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {(roadmap.tasks || []).map((t: any) => {
                const isCompleted = t.status === "completed";
                return (
                  <div key={t.id} className="glass-panel" style={{
                    padding: "20px 22px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: 16,
                    border: isCompleted ? "1px solid rgba(16, 185, 129, 0.3)" : "1px solid var(--border-subtle)",
                    background: isCompleted ? "rgba(16, 185, 129, 0.05)" : "var(--bg-card)"
                  }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                        <span style={{ fontWeight: 700, fontSize: "1rem", color: isCompleted ? "#a7f3d0" : "#ffffff", textDecoration: isCompleted ? "line-through" : "none" }}>
                          {t.title}
                        </span>
                        <span className={`badge ${t.priority === "High" ? "badge-high" : "badge-medium"}`}>
                          {t.priority}
                        </span>
                        <span className="badge badge-info" style={{ fontSize: "0.7rem" }}>
                          {t.skill_name}
                        </span>
                      </div>

                      <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: 12, lineHeight: 1.5 }}>
                        {t.description}
                      </p>

                      <div style={{ display: "flex", alignItems: "center", gap: 16, fontSize: "0.75rem", color: "var(--text-muted)" }}>
                        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                          <Clock size={13} /> {t.estimated_minutes} mins effort
                        </span>
                        <span>•</span>
                        <span>Criteria: {t.completion_criteria}</span>
                      </div>
                    </div>

                    <div>
                      {isCompleted ? (
                        <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--accent-emerald)", fontSize: "0.85rem", fontWeight: 700 }}>
                          <CheckCircle size={18} /> Completed
                        </div>
                      ) : (
                        <button
                          className="btn btn-secondary"
                          disabled={completingTaskId === t.id}
                          onClick={() => handleCompleteTask(t.id)}
                          style={{ padding: "8px 14px", fontSize: "0.8rem", whiteSpace: "nowrap" }}
                        >
                          {completingTaskId === t.id ? "Updating State..." : "Mark Complete ✓"}
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Weekly Curriculum Overview */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div className="glass-panel" style={{ padding: 24 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
                <Calendar size={18} color="#a855f7" />
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff" }}>
                  4-Week Adaptive Curriculum
                </h3>
              </div>

              <div style={{ padding: "12px 14px", background: "rgba(99, 102, 241, 0.1)", borderRadius: 10, fontSize: "0.85rem", color: "#c7d2fe", marginBottom: 20 }}>
                <strong>Strategic Goal:</strong> {roadmap.goal}
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                {(roadmap.weekly_plan || []).map((weekItem: any, idx: number) => (
                  <div key={idx} style={{
                    padding: "14px 16px",
                    borderRadius: "var(--radius-md)",
                    background: "rgba(15, 23, 42, 0.6)",
                    border: "1px solid var(--border-subtle)"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                      <span style={{ fontWeight: 700, fontSize: "0.9rem", color: "#38bdf8" }}>
                        WEEK {weekItem.week}
                      </span>
                    </div>

                    <div style={{ fontWeight: 600, fontSize: "0.85rem", color: "#ffffff", marginBottom: 6 }}>
                      {weekItem.focus}
                    </div>

                    <ul style={{ fontSize: "0.8rem", color: "var(--text-muted)", paddingLeft: 16 }}>
                      {weekItem.goals.map((g: string, i: number) => (
                        <li key={i}>{g}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
