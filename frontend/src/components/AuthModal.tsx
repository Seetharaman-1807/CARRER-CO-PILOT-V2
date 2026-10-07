import React, { useState } from "react";
import { Zap, Lock, Mail, User, ShieldCheck } from "lucide-react";
import { api, setStoredToken } from "../services/api";

interface AuthModalProps {
  onSuccess: (user: any) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ onSuccess }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("candidate@copilot.ai");
  const [password, setPassword] = useState("SecurePassword123!");
  const [fullName, setFullName] = useState("Alex Mercer");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      let res;
      if (isRegister) {
        res = await api.register({ email, password, full_name: fullName });
      } else {
        res = await api.login({ email, password });
      }
      setStoredToken(res.access_token);
      onSuccess(res.user);
    } catch (err: any) {
      // If login failed because user not registered yet, try registering automatically for demo convenience
      if (!isRegister && (err.message.includes("Incorrect") || err.message.includes("not found"))) {
        try {
          const regRes = await api.register({ email, password, full_name: fullName });
          setStoredToken(regRes.access_token);
          onSuccess(regRes.user);
          return;
        } catch (regErr: any) {
          setError(regErr.message || "Authentication failed");
        }
      } else {
        setError(err.message || "Authentication failed");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: "rgba(0, 0, 0, 0.8)",
      backdropFilter: "blur(12px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
      padding: 20
    }}>
      <div className="glass-panel-glow" style={{ maxWidth: 440, width: "100%", padding: 36, border: "1px solid var(--border-glow)" }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 14,
            background: "linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 14px",
            boxShadow: "0 8px 24px rgba(99, 102, 241, 0.4)"
          }}>
            <Zap size={26} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 800, color: "#ffffff", letterSpacing: "-0.02em" }}>
            Career Copilot V2
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginTop: 4 }}>
            Adaptive AI-Based Career Readiness Platform
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {isRegister && (
            <div>
              <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: 4 }}>
                Full Name
              </label>
              <input
                className="input-field"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Candidate Name"
                required
              />
            </div>
          )}

          <div>
            <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: 4 }}>
              Email Address
            </label>
            <input
              type="email"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              required
            />
          </div>

          <div>
            <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: 4 }}>
              Password
            </label>
            <input
              type="password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div style={{ color: "var(--accent-rose)", fontSize: "0.8rem" }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="btn btn-primary"
            style={{ width: "100%", padding: "12px 0", marginTop: 6 }}
          >
            {isLoading ? "Authenticating..." : isRegister ? "Create Account & Enter" : "Sign In to Copilot"}
          </button>
        </form>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 20, paddingTop: 16, borderTop: "1px solid var(--border-subtle)", fontSize: "0.8rem" }}>
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            style={{ background: "none", border: "none", color: "#818cf8", cursor: "pointer", fontWeight: 600 }}
          >
            {isRegister ? "Already have an account? Sign in" : "New user? Create account"}
          </button>

          <span style={{ color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 4 }}>
            <ShieldCheck size={14} color="var(--accent-emerald)" /> Isolated Tenant
          </span>
        </div>
      </div>
    </div>
  );
};
