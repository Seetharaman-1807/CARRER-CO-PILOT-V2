import React, { useState, useEffect } from "react";
import { 
  Target, 
  Plus, 
  CheckCircle2, 
  HelpCircle, 
  AlertCircle, 
  ArrowRight,
  Sparkles,
  Layers
} from "lucide-react";
import { api } from "../services/api";

interface JobsAndGapsViewProps {
  onDataUpdated: () => void;
  onNavigate: (tab: string) => void;
}

export const JobsAndGapsView: React.FC<JobsAndGapsViewProps> = ({
  onDataUpdated,
  onNavigate,
}) => {
  const [targetRoles, setTargetRoles] = useState<any[]>([]);
  const [jobDescriptions, setJobDescriptions] = useState<any[]>([]);
  const [selectedJdId, setSelectedJdId] = useState<number | null>(null);
  const [skillGapData, setSkillGapData] = useState<any>(null);
  const [isLoadingGaps, setIsLoadingGaps] = useState(false);

  // New JD input state
  const [showAddJd, setShowAddJd] = useState(false);
  const [jdTitle, setJdTitle] = useState("Backend Engineer");
  const [jdCompany, setJdCompany] = useState("Stripe");
  const [jdContent, setJdContent] = useState(
`Senior Backend Engineer
We are seeking an engineer to build high-scale financial infrastructure.
Required Qualifications:
- 3+ years experience with Python and FastAPI
- Production experience with PostgreSQL, Database Indexing, and Redis
- Strong foundation in Data Structures & Algorithms
- Experience with Docker, Kubernetes, and CI/CD
- Practical understanding of System Design and distributed architecture`
  );

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const roles = await api.getTargetRoles();
      setTargetRoles(roles);

      const jds = await api.getJobDescriptions();
      setJobDescriptions(jds);
      if (jds.length > 0) {
        setSelectedJdId(jds[0].id);
        fetchGaps(jds[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchGaps = async (jdId?: number) => {
    setIsLoadingGaps(true);
    try {
      const res = await api.computeSkillGaps(jdId);
      setSkillGapData(res);
      onDataUpdated();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoadingGaps(false);
    }
  };

  const handleCreateJd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jdContent.trim()) return;

    try {
      const newJd = await api.createJobDescription({
        title: jdTitle,
        company: jdCompany,
        content: jdContent,
      });
      setShowAddJd(false);
      await loadData();
      setSelectedJdId(newJd.id);
      fetchGaps(newJd.id);
    } catch (err: any) {
      alert(err.message || "Failed to create Job Description");
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "exact":
        return <span className="badge badge-exact">Exact Match</span>;
      case "related":
        return <span className="badge badge-related">Transferable</span>;
      case "partial":
        return <span className="badge badge-medium">Partial Evidence</span>;
      case "missing":
        return <span className="badge badge-missing">Missing Gap</span>;
      default:
        return <span className="badge badge-info">{status}</span>;
    }
  };

  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: "28px 24px", display: "flex", flexDirection: "column", gap: 28 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffffff" }}>
            Target Roles & Semantic Skill Gap Engine
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Classifies candidate capabilities against target job requirements as Exact, Transferable, Partial, or Missing.
          </p>
        </div>

        <button 
          className="btn btn-primary" 
          onClick={() => setShowAddJd(!showAddJd)}
          style={{ display: "flex", alignItems: "center", gap: 8 }}
        >
          <Plus size={16} /> Add Job Description
        </button>
      </div>

      {/* Modal/Accordion for adding JD */}
      {showAddJd && (
        <div className="glass-panel-glow" style={{ padding: 24, border: "1px solid var(--accent-primary)" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", marginBottom: 12 }}>
            Add New Job Description
          </h3>
          <form onSubmit={handleCreateJd} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: 4 }}>Role Title</label>
                <input
                  className="input-field"
                  value={jdTitle}
                  onChange={(e) => setJdTitle(e.target.value)}
                  placeholder="e.g. Backend Developer"
                />
              </div>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: 4 }}>Company (Optional)</label>
                <input
                  className="input-field"
                  value={jdCompany}
                  onChange={(e) => setJdCompany(e.target.value)}
                  placeholder="e.g. Stripe, Google, Acme Corp"
                />
              </div>
            </div>

            <div>
              <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: 4 }}>Job Description Content</label>
              <textarea
                className="input-field"
                rows={6}
                value={jdContent}
                onChange={(e) => setJdContent(e.target.value)}
              />
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
              <button type="button" className="btn btn-secondary" onClick={() => setShowAddJd(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Parse Requirements & Save</button>
            </div>
          </form>
        </div>
      )}

      {/* Main Analysis Display */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 28 }}>
        {/* Left Column: Target JDs & Summary */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div className="glass-panel" style={{ padding: 22 }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#ffffff", marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
              <Target size={16} color="#38bdf8" />
              Target Job Descriptions
            </h3>

            {jobDescriptions.length === 0 ? (
              <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                No job descriptions saved yet. Click "Add Job Description" to parse requirements.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {jobDescriptions.map((jd) => (
                  <button
                    key={jd.id}
                    onClick={() => {
                      setSelectedJdId(jd.id);
                      fetchGaps(jd.id);
                    }}
                    style={{
                      padding: "12px 14px",
                      borderRadius: 10,
                      background: selectedJdId === jd.id ? "rgba(99, 102, 241, 0.2)" : "rgba(15, 23, 42, 0.5)",
                      border: selectedJdId === jd.id ? "1px solid var(--accent-primary)" : "1px solid var(--border-subtle)",
                      color: "#ffffff",
                      textAlign: "left",
                      cursor: "pointer",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>{jd.title}</div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{jd.company || "General"}</div>
                    </div>
                    {selectedJdId === jd.id && <CheckCircle2 size={16} color="var(--accent-primary)" />}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Alignment Stats summary */}
          {skillGapData && (
            <div className="glass-panel" style={{ padding: 22 }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#ffffff", marginBottom: 14 }}>
                Requirement Alignment Summary
              </h3>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div style={{ padding: 12, background: "rgba(16, 185, 129, 0.1)", borderRadius: 8, textAlign: "center" }}>
                  <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--accent-emerald)" }}>
                    {skillGapData.summary?.exact_matches || 0}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Exact Matches</div>
                </div>

                <div style={{ padding: 12, background: "rgba(168, 85, 247, 0.1)", borderRadius: 8, textAlign: "center" }}>
                  <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--accent-purple)" }}>
                    {skillGapData.summary?.related_matches || 0}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Transferable</div>
                </div>

                <div style={{ padding: 12, background: "rgba(245, 158, 11, 0.1)", borderRadius: 8, textAlign: "center" }}>
                  <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--accent-amber)" }}>
                    {skillGapData.summary?.weak_matches || 0}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Partial / Weak</div>
                </div>

                <div style={{ padding: 12, background: "rgba(244, 63, 94, 0.1)", borderRadius: 8, textAlign: "center" }}>
                  <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--accent-rose)" }}>
                    {skillGapData.summary?.missing_skills || 0}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Missing Gaps</div>
                </div>
              </div>

              <div style={{ marginTop: 18 }}>
                <button
                  className="btn btn-primary"
                  onClick={() => onNavigate("roadmap")}
                  style={{ width: "100%", fontSize: "0.85rem" }}
                >
                  Generate Roadmap for Gaps <ArrowRight size={14} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Semantic Gaps Breakdown */}
        <div className="glass-panel" style={{ padding: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
              <Layers size={18} color="#818cf8" />
              Role Requirements & Gap Prioritization Matrix
            </h3>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
              {skillGapData?.gaps?.length || 0} requirements evaluated
            </span>
          </div>

          {isLoadingGaps ? (
            <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
              Evaluating requirements...
            </div>
          ) : !skillGapData || skillGapData.gaps.length === 0 ? (
            <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
              Select a Job Description to compute candidate skill gaps.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {skillGapData.gaps.map((item: any, idx: number) => (
                <div key={idx} style={{
                  padding: "16px 18px",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(15, 23, 42, 0.6)",
                  border: "1px solid var(--border-subtle)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 8
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <span style={{ fontWeight: 700, fontSize: "0.95rem", color: "#ffffff" }}>
                        {item.canonical_skill || item.skill}
                      </span>
                      {getStatusBadge(item.status)}
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                        Score: <strong>{item.candidate_score.toFixed(0)}/100</strong>
                      </span>
                      <span className={`badge ${item.priority === "High" ? "badge-high" : item.priority === "Medium" ? "badge-medium" : "badge-low"}`}>
                        {item.priority}
                      </span>
                    </div>
                  </div>

                  <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                    {item.reason}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
