import React, { useState, useEffect } from "react";
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  Layers, 
  GitCompare, 
  ChevronRight, 
  AlertTriangle,
  Award,
  Sparkles,
  BarChart3
} from "lucide-react";
import { api } from "../services/api";

interface ResumeViewProps {
  onDataUpdated: () => void;
}

export const ResumeView: React.FC<ResumeViewProps> = ({ onDataUpdated }) => {
  const [resumes, setResumes] = useState<any[]>([]);
  const [currentResume, setCurrentResume] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<any>(null);
  const [jobDescriptions, setJobDescriptions] = useState<any[]>([]);
  const [selectedJdId, setSelectedJdId] = useState<number | null>(null);

  // Upload state
  const [rawText, setRawText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  // ATS scoring state
  const [isScoringAts, setIsScoringAts] = useState(false);
  const [atsResult, setAtsResult] = useState<any>(null);

  // Compare state
  const [isComparing, setIsComparing] = useState(false);
  const [compareResult, setCompareResult] = useState<any>(null);

  useEffect(() => {
    loadResumesAndJds();
  }, []);

  const loadResumesAndJds = async () => {
    try {
      const resList = await api.getResumes();
      setResumes(resList);
      if (resList.length > 0) {
        const rootResume = resList[0];
        setCurrentResume(rootResume);
        const vList = await api.getResumeVersions(rootResume.id);
        setVersions(vList);
        if (vList.length > 0) {
          setSelectedVersion(vList[0]);
        }
      }

      const jdList = await api.getJobDescriptions();
      setJobDescriptions(jdList);
      if (jdList.length > 0) {
        setSelectedJdId(jdList[0].id);
      }
    } catch (e: any) {
      console.error(e);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file && !rawText.trim()) {
      setUploadError("Please provide a resume document file or paste text content.");
      return;
    }

    setIsUploading(true);
    setUploadError("");

    try {
      const formData = new FormData();
      if (file) {
        formData.append("file", file);
      } else {
        formData.append("raw_text", rawText);
      }
      formData.append("title", "Candidate Technical Resume");

      const newVer = await api.uploadResume(formData);
      setRawText("");
      setFile(null);
      await loadResumesAndJds();
      setSelectedVersion(newVer);
      onDataUpdated();
    } catch (err: any) {
      setUploadError(err.message || "Failed to process resume.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleComputeAts = async () => {
    if (!selectedVersion || !selectedJdId) return;
    setIsScoringAts(true);
    try {
      const res = await api.computeAts({
        resume_version_id: selectedVersion.id,
        job_description_id: selectedJdId,
      });
      setAtsResult(res);
      onDataUpdated();
    } catch (err: any) {
      alert(err.message || "Failed to compute ATS score");
    } finally {
      setIsScoringAts(false);
    }
  };

  const handleCompareVersions = async () => {
    if (!currentResume || versions.length < 2) return;
    setIsComparing(true);
    try {
      const comp = await api.compareResumes(currentResume.id);
      setCompareResult(comp);
    } catch (err: any) {
      alert(err.message || "Comparison failed");
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: "28px 24px", display: "flex", flexDirection: "column", gap: 28 }}>
      {/* Top Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffffff" }}>
            Resume Intelligence & ATS Screening
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Extracts verifiable technical skills with exact source quotes and computes deterministic ATS alignment.
          </p>
        </div>

        {versions.length >= 2 && (
          <button 
            className="btn btn-secondary" 
            onClick={handleCompareVersions}
            style={{ display: "flex", alignItems: "center", gap: 8 }}
          >
            <GitCompare size={16} /> Compare V1 vs V2 Diffs
          </button>
        )}
      </div>

      {/* Version Comparison Modal/Card if active */}
      {compareResult && (
        <div className="glass-panel-glow" style={{ padding: 24, border: "1px solid var(--accent-primary)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
              <GitCompare size={18} color="#818cf8" />
              Resume Evolution Comparison: V{compareResult.v1_version} → V{compareResult.v2_version}
            </h3>
            <button 
              onClick={() => setCompareResult(null)}
              style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "0.85rem" }}
            >
              ✕ Close Diff
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1.5fr", gap: 20 }}>
            <div style={{ padding: 16, background: "rgba(15, 23, 42, 0.6)", borderRadius: 12 }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Estimated ATS Improvement</div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "var(--accent-emerald)" }}>
                +{compareResult.ats_score_delta}%
              </div>
            </div>

            <div style={{ padding: 16, background: "rgba(15, 23, 42, 0.6)", borderRadius: 12 }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 6 }}>Newly Added Skills</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {compareResult.skills_added.map((s: string, idx: number) => (
                  <span key={idx} className="badge badge-low">{s}</span>
                ))}
              </div>
            </div>

            <div style={{ padding: 16, background: "rgba(15, 23, 42, 0.6)", borderRadius: 12 }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 6 }}>Verified Improvements</div>
              <ul style={{ fontSize: "0.85rem", color: "var(--text-secondary)", paddingLeft: 16 }}>
                {compareResult.improvements.map((imp: string, idx: number) => (
                  <li key={idx}>{imp}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Upload & Intelligence View */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.4fr", gap: 28 }}>
        {/* Left Column: Upload New Version & ATS Trigger */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          {/* Upload Form */}
          <div className="glass-panel" style={{ padding: 24 }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", marginBottom: 6, display: "flex", alignItems: "center", gap: 8 }}>
              <Upload size={18} color="#38bdf8" />
              Upload Resume (PDF, DOCX, Text)
            </h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 16 }}>
              Creates a new version and automatically updates candidate skill evidence.
            </p>

            <form onSubmit={handleUpload} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}
                />
              </div>

              <div style={{ textAlign: "center", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                — OR PASTE TEXT BELOW —
              </div>

              <textarea
                className="input-field"
                placeholder="Paste complete resume content here (sections, skills, work history)..."
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                rows={6}
              />

              {uploadError && (
                <div style={{ color: "var(--accent-rose)", fontSize: "0.8rem", display: "flex", alignItems: "center", gap: 6 }}>
                  <AlertTriangle size={14} /> {uploadError}
                </div>
              )}

              <button
                type="submit"
                disabled={isUploading}
                className="btn btn-primary"
                style={{ width: "100%" }}
              >
                {isUploading ? "Extracting Intelligence..." : "Ingest & Extract Evidence"}
              </button>
            </form>
          </div>

          {/* Deterministic ATS Scorer Trigger */}
          <div className="glass-panel" style={{ padding: 24 }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", marginBottom: 6, display: "flex", alignItems: "center", gap: 8 }}>
              <BarChart3 size={18} color="#a855f7" />
              Deterministic ATS Screening
            </h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 14 }}>
              Evaluates current resume version against a target Job Description using 7 mathematical weights.
            </p>

            {jobDescriptions.length === 0 ? (
              <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                Please add at least one Job Description in the 'Role & Gaps' tab first.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div>
                  <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: 6 }}>
                    Select Target Job Description:
                  </label>
                  <select
                    className="input-field"
                    value={selectedJdId || ""}
                    onChange={(e) => setSelectedJdId(Number(e.target.value))}
                  >
                    {jobDescriptions.map((jd) => (
                      <option key={jd.id} value={jd.id}>
                        {jd.title} {jd.company ? `(${jd.company})` : ""}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  className="btn btn-secondary"
                  disabled={isScoringAts || !selectedVersion}
                  onClick={handleComputeAts}
                  style={{ width: "100%" }}
                >
                  {isScoringAts ? "Calculating 7 Factors..." : "Run Deterministic ATS Check"}
                </button>
              </div>
            )}

            {/* ATS Score Results display */}
            {atsResult && (
              <div style={{ marginTop: 20, paddingTop: 16, borderTop: "1px solid var(--border-subtle)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <span style={{ fontWeight: 700, color: "#ffffff", fontSize: "1rem" }}>Overall ATS Score</span>
                  <span style={{ fontSize: "1.6rem", fontWeight: 800, color: atsResult.overall_score >= 70 ? "var(--accent-emerald)" : "var(--accent-amber)" }}>
                    {atsResult.overall_score}/100
                  </span>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {Object.entries(atsResult.component_scores).map(([compKey, val]: [string, any]) => (
                    <div key={compKey} style={{ fontSize: "0.8rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-secondary)", marginBottom: 2 }}>
                        <span>{compKey.replace("_", " ").toUpperCase()}</span>
                        <strong>{val} pts</strong>
                      </div>
                      <div className="progress-bar-bg">
                        <div className="progress-bar-fill" style={{ width: `${(val / 25) * 100}%`, background: "var(--accent-primary)" }} />
                      </div>
                    </div>
                  ))}
                </div>

                {atsResult.feedback?.recommendations && (
                  <div style={{ marginTop: 14 }}>
                    <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", marginBottom: 6 }}>RECOMMENDATIONS:</div>
                    <ul style={{ fontSize: "0.8rem", color: "var(--text-secondary)", paddingLeft: 16 }}>
                      {atsResult.feedback.recommendations.map((rec: string, i: number) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Parsed Intelligence & Evidence */}
        <div className="glass-panel" style={{ padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>
          {/* Version Selector Tabs */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-subtle)", paddingBottom: 14 }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: 8 }}>
              <Layers size={18} color="var(--accent-emerald)" />
              Extracted Evidence Model
            </h3>

            {versions.length > 0 && (
              <div style={{ display: "flex", gap: 6 }}>
                {versions.map((ver) => (
                  <button
                    key={ver.id}
                    onClick={() => setSelectedVersion(ver)}
                    className="btn"
                    style={{
                      padding: "4px 10px",
                      fontSize: "0.75rem",
                      background: selectedVersion?.id === ver.id ? "var(--accent-primary)" : "rgba(255,255,255,0.06)",
                      color: "#ffffff"
                    }}
                  >
                    V{ver.version_number}
                  </button>
                ))}
              </div>
            )}
          </div>

          {!selectedVersion ? (
            <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
              No resume uploaded yet. Upload a resume to view extracted skills and evidence quotes.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              {/* Candidate Info */}
              <div style={{ display: "flex", gap: 20, fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                <div><strong>Candidate:</strong> {selectedVersion.parsed_content?.contact?.name || "Extracted Candidate"}</div>
                {selectedVersion.parsed_content?.contact?.email && (
                  <div><strong>Email:</strong> {selectedVersion.parsed_content.contact.email}</div>
                )}
              </div>

              {/* Skills with Verified Evidence */}
              <div>
                <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", marginBottom: 10, display: "flex", alignItems: "center", gap: 6 }}>
                  <Award size={16} color="#38bdf8" />
                  Verified Skills & Evidence Quotes ({selectedVersion.parsed_content?.skills?.length || 0})
                </h4>

                <div style={{ display: "flex", flexDirection: "column", gap: 10, maxHeight: 340, overflowY: "auto", paddingRight: 6 }}>
                  {(selectedVersion.parsed_content?.skills || []).map((s: any, idx: number) => (
                    <div key={idx} style={{
                      padding: "10px 14px",
                      borderRadius: "var(--radius-md)",
                      background: "rgba(15, 23, 42, 0.6)",
                      border: "1px solid var(--border-subtle)"
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                        <span style={{ fontWeight: 700, fontSize: "0.9rem", color: "#ffffff" }}>
                          {s.canonical || s.skill}
                        </span>
                        <div style={{ display: "flex", gap: 6 }}>
                          <span className="badge badge-info" style={{ fontSize: "0.65rem" }}>
                            {s.source_section}
                          </span>
                          <span className="badge badge-low" style={{ fontSize: "0.65rem" }}>
                            {(s.confidence * 100).toFixed(0)}% Conf.
                          </span>
                        </div>
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontStyle: "italic", lineHeight: 1.4 }}>
                        "{s.evidence}"
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quantifiable Achievements */}
              {selectedVersion.parsed_content?.achievements?.length > 0 && (
                <div>
                  <h4 style={{ fontSize: "0.9rem", fontWeight: 700, color: "#ffffff", marginBottom: 8, display: "flex", alignItems: "center", gap: 6 }}>
                    <Sparkles size={16} color="var(--accent-amber)" />
                    Measurable Quantitative Achievements
                  </h4>
                  <ul style={{ fontSize: "0.8rem", color: "var(--text-secondary)", paddingLeft: 18 }}>
                    {selectedVersion.parsed_content.achievements.map((ach: string, i: number) => (
                      <li key={i} style={{ marginBottom: 4 }}>{ach}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Projects */}
              <div>
                <h4 style={{ fontSize: "0.9rem", fontWeight: 700, color: "#ffffff", marginBottom: 8 }}>
                  Projects Recorded ({selectedVersion.parsed_content?.projects?.length || 0})
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {(selectedVersion.parsed_content?.projects || []).map((proj: string, i: number) => (
                    <div key={i} style={{ padding: 10, background: "rgba(15, 23, 42, 0.4)", borderRadius: 8, fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                      {proj}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
