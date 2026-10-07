import React from "react";
import { 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  TrendingUp, 
  FileCheck, 
  Sparkles,
  Target,
  ShieldCheck,
  Calendar
} from "lucide-react";

interface DashboardViewProps {
  data: any;
  onNavigate: (tab: string) => void;
  onRefresh: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  data,
  onNavigate,
}) => {
  if (!data) {
    return (
      <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
        Loading executive dashboard state...
      </div>
    );
  }

  const {
    career_readiness = 0,
    confidence = "Insufficient evidence",
    target_role = "Backend Developer",
    next_best_action,
    readiness_breakdown = {},
    top_skill_gaps = [],
    todays_plan = [],
    progress_trend = [],
    recent_activity = [],
    resume_status = {},
    upcoming_interview
  } = data;

  const getScoreColor = (score: number) => {
    if (score >= 75) return "var(--accent-emerald)";
    if (score >= 50) return "var(--accent-amber)";
    return "var(--accent-rose)";
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 28, maxWidth: 1400, margin: "0 auto", padding: "28px 24px" }}>
      {/* ABOVE THE FOLD: Hero Cockpit */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1.2fr 2fr",
        gap: 24,
      }}>
        {/* Readiness Gauge Card */}
        <div className="glass-panel-glow" style={{ padding: "32px 28px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <span className="badge badge-info" style={{ marginBottom: 8 }}>
                  Candidate Readiness
                </span>
                <h2 style={{ fontSize: "1.4rem", fontWeight: 700, color: "#ffffff" }}>
                  {target_role}
                </h2>
              </div>
              <span className={`badge ${confidence === "High" ? "badge-low" : confidence === "Medium" ? "badge-medium" : "badge-high"}`}>
                {confidence} Confidence
              </span>
            </div>
            
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: 24 }}>
              Evidence-based composite readiness across resumes, verified code attempts, and simulated interview evaluations.
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <div style={{
              width: 110,
              height: 110,
              borderRadius: "50%",
              background: `radial-gradient(closest-side, var(--bg-secondary) 75%, transparent 80% 100%), conic-gradient(${getScoreColor(career_readiness)} ${career_readiness}%, rgba(255, 255, 255, 0.08) 0)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 24px rgba(99, 102, 241, 0.2)"
            }}>
              <div style={{ textAlign: "center" }}>
                <span style={{ fontSize: "1.8rem", fontWeight: 800, color: "#ffffff", lineHeight: 1 }}>
                  {career_readiness.toFixed(0)}
                </span>
                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "block" }}>
                  / 100
                </span>
              </div>
            </div>

            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                <span style={{ color: "var(--text-secondary)" }}>Preparedness Tier</span>
                <strong style={{ color: getScoreColor(career_readiness) }}>
                  {career_readiness >= 75 ? "Interview Ready" : career_readiness >= 50 ? "Targeted Practice" : "Foundational Gap"}
                </strong>
              </div>
              <div className="progress-bar-bg">
                <div 
                  className="progress-bar-fill" 
                  style={{ width: `${career_readiness}%`, background: getScoreColor(career_readiness) }}
                />
              </div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Target threshold for {target_role}: 80/100
              </span>
            </div>
          </div>
        </div>

        {/* PRIMARY CTA: Next Best Action Card */}
        <div className="glass-panel" style={{
          padding: "32px 28px",
          background: "linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          border: "1px solid rgba(99, 102, 241, 0.3)"
        }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
              <div style={{
                padding: "6px 12px",
                background: "rgba(99, 102, 241, 0.2)",
                borderRadius: 8,
                color: "#c7d2fe",
                fontSize: "0.75rem",
                fontWeight: 700,
                display: "inline-flex",
                alignItems: "center",
                gap: 6
              }}>
                <Sparkles size={14} color="#a5b4fc" />
                RECOMMENDED ACTION
              </div>
              <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                Continuous Feedback Engine
              </span>
            </div>

            <h3 style={{ fontSize: "1.35rem", fontWeight: 700, color: "#ffffff", marginBottom: 12 }}>
              {next_best_action?.title || "Complete Next Step"}
            </h3>

            <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 20 }}>
              {next_best_action?.description || "Upload your resume or practice targeted challenges to begin continuous calibration."}
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 8 }}>
              <ShieldCheck size={16} color="var(--accent-emerald)" />
              Measurable candidate improvement upon completion
            </div>

            <button
              className="btn btn-primary"
              onClick={() => {
                const route = next_best_action?.action_route?.replace("/", "") || "resume";
                onNavigate(route);
              }}
              style={{ padding: "12px 24px", fontSize: "0.95rem" }}
            >
              {next_best_action?.button_text || "Take Action Now"}
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* 6-DIMENSION READINESS BREAKDOWN */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
            <TrendingUp size={20} color="#818cf8" />
            Career Readiness Component Model
          </h3>
          <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
            PRD Formula: Transparent weights, explicit evidence
          </span>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 16
        }}>
          {Object.entries(readiness_breakdown).map(([key, comp]: [string, any]) => {
            const isInsufficient = comp.confidence === "Insufficient evidence";
            return (
              <div key={key} className="glass-panel" style={{ padding: "20px 18px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                    <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)" }}>
                      {comp.name}
                    </span>
                    <span className={`badge ${isInsufficient ? "badge-high" : "badge-low"}`} style={{ fontSize: "0.65rem", padding: "2px 6px" }}>
                      {comp.confidence}
                    </span>
                  </div>

                  <div style={{ fontSize: "1.6rem", fontWeight: 800, color: isInsufficient ? "var(--text-muted)" : getScoreColor(comp.score), marginBottom: 8 }}>
                    {isInsufficient ? "—" : `${comp.score.toFixed(0)}%`}
                  </div>

                  <div className="progress-bar-bg" style={{ marginBottom: 12 }}>
                    <div 
                      className="progress-bar-fill" 
                      style={{ 
                        width: isInsufficient ? "0%" : `${comp.score}%`, 
                        background: getScoreColor(comp.score) 
                      }} 
                    />
                  </div>
                </div>

                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", lineHeight: 1.4 }}>
                  {comp.evidence}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* LOWER SECTION: Top Gaps & Today's Plan */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1.8fr", gap: 24 }}>
        {/* Top Skill Gaps */}
        <div className="glass-panel" style={{ padding: "24px 22px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
              <AlertCircle size={18} color="var(--accent-rose)" />
              Highest-Impact Skill Gaps
            </h3>
            <button 
              onClick={() => onNavigate("gaps")}
              style={{ background: "none", border: "none", color: "#818cf8", fontSize: "0.8rem", cursor: "pointer", fontWeight: 600 }}
            >
              View All Gaps →
            </button>
          </div>

          {top_skill_gaps.length === 0 ? (
            <div style={{ padding: 24, textAlign: "center", color: "var(--text-muted)", fontSize: "0.85rem" }}>
              Upload your target Job Description to identify specific missing or weak skills.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {top_skill_gaps.slice(0, 3).map((gap: any, idx: number) => (
                <div key={idx} style={{
                  padding: "14px 16px",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(15, 23, 42, 0.6)",
                  border: "1px solid var(--border-subtle)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 6
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontWeight: 700, fontSize: "0.95rem", color: "#ffffff" }}>
                      {gap.canonical_skill || gap.skill}
                    </span>
                    <span className={`badge ${gap.priority === "High" ? "badge-high" : "badge-medium"}`}>
                      {gap.priority} Priority
                    </span>
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                    {gap.reason}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* What should I do today? Plan */}
        <div className="glass-panel" style={{ padding: "24px 22px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
            <div>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
                <CheckCircle2 size={18} color="var(--accent-emerald)" />
                What Should I Do Today?
              </h3>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                3–5 high-value adaptive actions grounded in your current state
              </div>
            </div>
            <button 
              onClick={() => onNavigate("roadmap")}
              className="btn btn-secondary" 
              style={{ padding: "6px 12px", fontSize: "0.8rem" }}
            >
              Open Roadmap
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {todays_plan.map((item: any, idx: number) => (
              <div key={idx} style={{
                padding: "12px 16px",
                borderRadius: "var(--radius-md)",
                background: "rgba(15, 23, 42, 0.5)",
                border: "1px solid var(--border-subtle)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 14
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <div style={{
                    width: 28,
                    height: 28,
                    borderRadius: "50%",
                    background: "rgba(99, 102, 241, 0.15)",
                    color: "#a5b4fc",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: 700,
                    fontSize: "0.8rem"
                  }}>
                    {idx + 1}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: "0.85rem", color: "#ffffff" }}>
                      {item.task}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                      {item.reason}
                    </div>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 4 }}>
                    <Clock size={12} /> {item.estimated_time}
                  </span>
                  <span className={`badge ${item.priority === "High" ? "badge-high" : "badge-medium"}`}>
                    {item.priority}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* RECENT ACTIVITY & RESUME STATUS */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* Resume status widget */}
        <div className="glass-panel" style={{ padding: "20px 22px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
              <FileCheck size={16} color="#38bdf8" />
              Active Resume Snapshot
            </h4>
            <button 
              onClick={() => onNavigate("resume")}
              style={{ background: "none", border: "none", color: "#38bdf8", fontSize: "0.75rem", cursor: "pointer", fontWeight: 600 }}
            >
              Manage Versions →
            </button>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontWeight: 600, color: "var(--text-primary)", fontSize: "0.9rem" }}>
                {resume_status.has_resume ? `Resume V${resume_status.version_number}` : "No Resume Uploaded"}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                {resume_status.file_name} • {resume_status.skills_extracted_count} skills extracted
              </div>
            </div>

            {resume_status.ats_score !== null && resume_status.ats_score !== undefined ? (
              <div style={{ textAlign: "right" }}>
                <span style={{ fontSize: "1.4rem", fontWeight: 800, color: getScoreColor(resume_status.ats_score) }}>
                  {resume_status.ats_score}
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "block" }}>
                  ATS Score
                </span>
              </div>
            ) : (
              <span className="badge badge-medium">ATS Unscored</span>
            )}
          </div>
        </div>

        {/* Upcoming interview widget */}
        <div className="glass-panel" style={{ padding: "20px 22px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
              <Calendar size={16} color="#a855f7" />
              Interview Target
            </h4>
            <button 
              onClick={() => onNavigate("interview")}
              style={{ background: "none", border: "none", color: "#a855f7", fontSize: "0.75rem", cursor: "pointer", fontWeight: 600 }}
            >
              Mock Practice Studio →
            </button>
          </div>

          <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            {upcoming_interview ? (
              <div>
                Target Interview Date: <strong>{new Date(upcoming_interview.date).toLocaleDateString()}</strong>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 4 }}>
                  {upcoming_interview.days_remaining} days remaining for targeted role preparation.
                </div>
              </div>
            ) : (
              <div>
                Configure your target interview timeline in your candidate profile to calculate learning velocity.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
