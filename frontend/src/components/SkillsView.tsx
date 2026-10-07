import React, { useState, useEffect } from "react";
import { 
  Award, 
  TrendingUp, 
  ShieldCheck, 
  Layers, 
  History, 
  ChevronRight,
  Database,
  Search
} from "lucide-react";
import { api } from "../services/api";

interface SkillsViewProps {
  onDataUpdated: () => void;
}

export const SkillsView: React.FC<SkillsViewProps> = ({ onDataUpdated }) => {
  const [skills, setSkills] = useState<any[]>([]);
  const [taxonomy, setTaxonomy] = useState<any>({});
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState<"profile" | "taxonomy">("profile");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const p = await api.getSkillProfile();
      setSkills(p);

      const tax = await api.getTaxonomy();
      setTaxonomy(tax);
    } catch (e) {
      console.error(e);
    }
  };

  const filteredSkills = skills.filter(s => 
    s.canonical_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getTrendColor = (trend: string) => {
    if (trend === "Improving") return "var(--accent-emerald)";
    if (trend === "Regressing") return "var(--accent-rose)";
    return "#94a3b8";
  };

  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: "28px 24px", display: "flex", flexDirection: "column", gap: 28 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffffff" }}>
            Candidate Skill Profile & Taxonomy Matrix
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Persistent, explainable candidate state aggregating evidence from resumes, DSA challenges, and interviews.
          </p>
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button
            className="btn"
            onClick={() => setActiveTab("profile")}
            style={{
              background: activeTab === "profile" ? "var(--accent-primary)" : "rgba(255, 255, 255, 0.06)",
              color: "#ffffff"
            }}
          >
            Demonstrated Profile ({skills.length})
          </button>
          <button
            className="btn"
            onClick={() => setActiveTab("taxonomy")}
            style={{
              background: activeTab === "taxonomy" ? "var(--accent-primary)" : "rgba(255, 255, 255, 0.06)",
              color: "#ffffff"
            }}
          >
            Canonical Taxonomy Tree
          </button>
        </div>
      </div>

      {activeTab === "profile" ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {/* Search bar */}
          <div style={{ maxWidth: 400 }}>
            <input
              className="input-field"
              placeholder="Search demonstrated skills..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {filteredSkills.length === 0 ? (
            <div className="glass-panel" style={{ padding: 60, textAlign: "center", color: "var(--text-muted)" }}>
              No candidate skills registered yet. Upload a resume, solve a DSA problem, or complete an interview to establish verified evidence.
            </div>
          ) : (
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
              gap: 20
            }}>
              {filteredSkills.map((sk) => (
                <div key={sk.id} className="glass-panel" style={{ padding: 22, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                      <span style={{ fontWeight: 800, fontSize: "1.1rem", color: "#ffffff" }}>
                        {sk.canonical_name}
                      </span>
                      <div style={{ display: "flex", gap: 6 }}>
                        <span className={`badge ${sk.confidence === "High" ? "badge-low" : sk.confidence === "Medium" ? "badge-medium" : "badge-info"}`}>
                          {sk.confidence} Conf.
                        </span>
                        <span className="badge" style={{ color: getTrendColor(sk.trend), background: "rgba(255, 255, 255, 0.05)" }}>
                          {sk.trend}
                        </span>
                      </div>
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 6 }}>
                      <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Demonstrated Score</span>
                      <span style={{ fontSize: "1.4rem", fontWeight: 800, color: sk.score >= 70 ? "var(--accent-emerald)" : "var(--accent-amber)" }}>
                        {sk.score.toFixed(0)} / 100
                      </span>
                    </div>

                    <div className="progress-bar-bg" style={{ marginBottom: 16 }}>
                      <div className="progress-bar-fill" style={{ width: `${sk.score}%`, background: sk.score >= 70 ? "var(--accent-emerald)" : "var(--accent-amber)" }} />
                    </div>
                  </div>

                  {/* Evidence sources */}
                  <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: 12 }}>
                    <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", marginBottom: 6, display: "flex", alignItems: "center", gap: 4 }}>
                      <History size={12} /> RECENT EVIDENCE ITEMS ({sk.evidence_items?.length || 0}):
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      {(sk.evidence_items || []).slice(0, 2).map((ev: any) => (
                        <div key={ev.id} style={{ fontSize: "0.75rem", color: "var(--text-secondary)", background: "rgba(15, 23, 42, 0.4)", padding: "6px 8px", borderRadius: 6 }}>
                          <strong style={{ color: "#38bdf8", textTransform: "capitalize" }}>[{ev.source_type}]</strong> {ev.notes || `Score: ${ev.score}`}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* Taxonomy Tree */
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 20
        }}>
          {Object.entries(taxonomy).map(([canName, info]: [string, any]) => (
            <div key={canName} className="glass-panel" style={{ padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <span style={{ fontWeight: 700, fontSize: "1rem", color: "#ffffff" }}>
                  {canName}
                </span>
                <span className="badge badge-info" style={{ fontSize: "0.7rem" }}>
                  {info.category}
                </span>
              </div>

              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 8 }}>
                Aliases: {info.aliases?.join(", ") || "None"}
              </div>

              {info.related?.length > 0 && (
                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
                  <strong>Related/Transferable:</strong> {info.related.join(", ")}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
