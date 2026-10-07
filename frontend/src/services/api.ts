const API_BASE_URL = "http://localhost:8000/api/v1";

export function getStoredToken(): string | null {
  return localStorage.getItem("career_copilot_token");
}

export function setStoredToken(token: string): void {
  localStorage.setItem("career_copilot_token", token);
}

export function removeStoredToken(): void {
  localStorage.removeItem("career_copilot_token");
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken();
  const headers: HeadersInit = {
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  // If body is not FormData, default content-type to application/json
  if (options.body && !(options.body instanceof FormData)) {
    (headers as Record<string, string>)["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || JSON.stringify(errorJson);
    } catch {
      errorDetail = response.statusText;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Auth
  register: (data: any) => request<any>("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data: any) => request<any>("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  getMe: () => request<any>("/auth/me"),

  // Dashboard
  getDashboard: () => request<any>("/dashboard"),

  // Resumes
  uploadResume: (formData: FormData) => request<any>("/resumes", { method: "POST", body: formData }),
  getResumes: () => request<any>("/resumes"),
  getResumeVersions: (id: number) => request<any>(`/resumes/${id}/versions`),
  compareResumes: (id: number, v1?: number, v2?: number) => {
    const params = new URLSearchParams();
    if (v1) params.append("v1", v1.toString());
    if (v2) params.append("v2", v2.toString());
    return request<any>(`/resumes/${id}/compare?${params.toString()}`);
  },

  // Jobs
  getTargetRoles: () => request<any>("/target-roles"),
  createTargetRole: (data: any) => request<any>("/target-roles", { method: "POST", body: JSON.stringify(data) }),
  getJobDescriptions: () => request<any>("/job-descriptions"),
  createJobDescription: (data: any) => request<any>("/job-descriptions", { method: "POST", body: JSON.stringify(data) }),

  // Analyses
  computeAts: (data: { resume_version_id: number; job_description_id: number }) =>
    request<any>("/analyses/ats", { method: "POST", body: JSON.stringify(data) }),
  computeSkillGaps: (job_description_id?: number) => {
    const url = job_description_id ? `/analyses/skill-gap?job_description_id=${job_description_id}` : "/analyses/skill-gap";
    return request<any>(url, { method: "POST" });
  },
  computeReadiness: (target_role_id?: number) => {
    const url = target_role_id ? `/analyses/readiness?target_role_id=${target_role_id}` : "/analyses/readiness";
    return request<any>(url, { method: "POST" });
  },

  // Skills
  getTaxonomy: () => request<any>("/skills/taxonomy"),
  getSkillProfile: () => request<any>("/skills/profile"),

  // Roadmap
  getRoadmap: () => request<any>("/roadmap"),
  generateRoadmap: (data: any = {}) => request<any>("/roadmap/generate", { method: "POST", body: JSON.stringify(data) }),
  completeRoadmapTask: (id: number) => request<any>(`/roadmap/tasks/${id}/complete`, { method: "POST" }),

  // DSA
  getDSAProblems: () => request<any>("/dsa/problems"),
  getDSAProblem: (slug: string) => request<any>(`/dsa/problems/${slug}`),
  submitDSAAttempt: (data: { problem_id: number; code: string; hints_used?: number }) =>
    request<any>("/dsa/attempts", { method: "POST", body: JSON.stringify(data) }),

  // Interviews
  startInterview: (data: { type: string; difficulty?: string; target_role_id?: number }) =>
    request<any>("/interviews", { method: "POST", body: JSON.stringify(data) }),
  getInterviewSession: (id: number) => request<any>(`/interviews/${id}`),
  submitInterviewResponse: (id: number, data: { question_id: string; response: string }) =>
    request<any>(`/interviews/${id}/responses`, { method: "POST", body: JSON.stringify(data) }),
  completeInterview: (id: number) => request<any>(`/interviews/${id}/complete`, { method: "POST" }),
};
