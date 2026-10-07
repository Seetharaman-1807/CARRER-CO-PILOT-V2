import React from "react";
import { 
  Compass, 
  FileText, 
  Target, 
  Map, 
  Code2, 
  MessageSquare, 
  Award, 
  LogOut, 
  User as UserIcon,
  Zap
} from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: any;
  onLogout: () => void;
  targetRole: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  user,
  onLogout,
  targetRole,
}) => {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: Compass },
    { id: "resume", label: "Resume & ATS", icon: FileText },
    { id: "gaps", label: "Role & Gaps", icon: Target },
    { id: "roadmap", label: "Roadmap", icon: Map },
    { id: "dsa", label: "DSA Practice", icon: Code2 },
    { id: "interview", label: "Mock Interview", icon: MessageSquare },
    { id: "skills", label: "Skill Profile", icon: Award },
  ];

  return (
    <header style={{
      borderBottom: "1px solid var(--border-subtle)",
      background: "rgba(11, 15, 25, 0.8)",
      backdropFilter: "blur(16px)",
      position: "sticky",
      top: 0,
      zIndex: 100,
      padding: "0 24px"
    }}>
      <div style={{
        maxWidth: 1400,
        margin: "0 auto",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: 72
      }}>
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{
            width: 40,
            height: 40,
            borderRadius: 12,
            background: "linear-gradient(135deg, #6366f1 0%, #38bdf8 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 4px 16px rgba(99, 102, 241, 0.35)"
          }}>
            <Zap size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: "1.2rem", fontWeight: 800, letterSpacing: "-0.02em", color: "#ffffff" }}>
                CAREER COPILOT
              </span>
              <span style={{
                background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                padding: "2px 7px",
                borderRadius: 6,
                fontSize: "0.7rem",
                fontWeight: 700,
                color: "#ffffff"
              }}>
                V2 ADAPTIVE
              </span>
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
              Target: <span style={{ color: "#38bdf8", fontWeight: 600 }}>{targetRole}</span>
            </div>
          </div>
        </div>

        {/* Navigation items */}
        <nav style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "9px 14px",
                  borderRadius: 10,
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  color: isActive ? "#ffffff" : "var(--text-secondary)",
                  background: isActive ? "rgba(99, 102, 241, 0.15)" : "transparent",
                  border: isActive ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid transparent",
                  cursor: "pointer",
                  transition: "all 0.15s ease"
                }}
              >
                <Icon size={16} color={isActive ? "#818cf8" : "#94a3b8"} />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* User state */}
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {user ? (
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)" }}>
                  {user.full_name || user.email}
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--accent-emerald)" }}>
                  ● Authenticated
                </div>
              </div>
              <button
                onClick={onLogout}
                title="Sign out"
                style={{
                  padding: "8px",
                  borderRadius: 8,
                  background: "rgba(255, 255, 255, 0.05)",
                  border: "1px solid var(--border-subtle)",
                  color: "var(--text-muted)",
                  cursor: "pointer"
                }}
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div style={{ display: "flex", gap: 8 }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 6 }}>
                <UserIcon size={14} /> Guest Session
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
