import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { DashboardView } from "./components/DashboardView";
import { ResumeView } from "./components/ResumeView";
import { JobsAndGapsView } from "./components/JobsAndGapsView";
import { RoadmapView } from "./components/RoadmapView";
import { DSAView } from "./components/DSAView";
import { InterviewView } from "./components/InterviewView";
import { SkillsView } from "./components/SkillsView";
import { AuthModal } from "./components/AuthModal";
import { api, getStoredToken, removeStoredToken } from "./services/api";

export function App() {
  const [user, setUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [targetRole, setTargetRole] = useState<string>("Backend Developer");
  const [isInitializing, setIsInitializing] = useState<boolean>(true);

  useEffect(() => {
    initApp();
  }, []);

  const initApp = async () => {
    setIsInitializing(true);
    const token = getStoredToken();
    if (token) {
      try {
        const u = await api.getMe();
        setUser(u);
        await refreshDashboard();
      } catch {
        removeStoredToken();
        setUser(null);
      }
    }
    setIsInitializing(false);
  };

  const refreshDashboard = async () => {
    try {
      const data = await api.getDashboard();
      setDashboardData(data);
      if (data.target_role) {
        setTargetRole(data.target_role);
      }
    } catch (e) {
      console.error("Dashboard refresh error:", e);
    }
  };

  const handleLogout = () => {
    removeStoredToken();
    setUser(null);
    setDashboardData(null);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onLogout={handleLogout}
        targetRole={targetRole}
      />

      <main style={{ flex: 1, paddingBottom: 60 }}>
        {activeTab === "dashboard" && (
          <DashboardView
            data={dashboardData}
            onNavigate={setActiveTab}
            onRefresh={refreshDashboard}
          />
        )}
        {activeTab === "resume" && (
          <ResumeView onDataUpdated={refreshDashboard} />
        )}
        {activeTab === "gaps" && (
          <JobsAndGapsView
            onDataUpdated={refreshDashboard}
            onNavigate={setActiveTab}
          />
        )}
        {activeTab === "roadmap" && (
          <RoadmapView onDataUpdated={refreshDashboard} />
        )}
        {activeTab === "dsa" && (
          <DSAView onDataUpdated={refreshDashboard} />
        )}
        {activeTab === "interview" && (
          <InterviewView onDataUpdated={refreshDashboard} />
        )}
        {activeTab === "skills" && (
          <SkillsView onDataUpdated={refreshDashboard} />
        )}
      </main>

      {!user && !isInitializing && (
        <AuthModal
          onSuccess={(loggedInUser) => {
            setUser(loggedInUser);
            refreshDashboard();
          }}
        />
      )}
    </div>
  );
}

export default App;
