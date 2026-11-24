import axios from "axios";

export const BRAND = "TalentIQ";
export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000/api" });

api.interceptors.request.use((c) => {
  const t = localStorage.getItem("tiq_token");
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});
api.interceptors.response.use((r) => r, (e) => {
  const s = e.response?.status;
  if ((s === 401 || s === 422) && localStorage.getItem("tiq_token") && !location.pathname.startsWith("/login")) {
    localStorage.clear(); location.href = "/login";
  }
  return Promise.reject(e);
});
export const err = (e) => e.response?.data?.error || e.message || "Something went wrong";
export const fmt = (d) => (d ? new Date(d).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "");
