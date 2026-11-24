import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import { BRAND } from "./api";
import { Login, Register } from "./pages/Auth";
import { CApps, CJobs, CProfile } from "./pages/Candidate";
import { Candidates, Dashboard, Jobs, Matching, Search, Shortlists } from "./pages/Admin";
import { Interviews, Notifications } from "./pages/Shared";

const NAV = {
  candidate: [["", "My profile"], ["jobs", "Open jobs"], ["applications", "Applications"], ["interviews", "Interviews"], ["notifications", "Notifications"]],
  admin: [["", "Dashboard"], ["jobs", "Jobs"], ["candidates", "Candidates"], ["matching", "AI matching"], ["search", "Semantic search"], ["shortlists", "Shortlists"], ["interviews", "Interviews"], ["notifications", "Notifications"]],
  interviewer: [["", "My interviews"], ["notifications", "Notifications"]],
};

function Shell({ role }) {
  const { user, logout } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role) return <Navigate to={"/" + user.role} replace />;
  return (
    <div className="app">
      <aside className="side">
        <div className="brand"><span className="mark" />{BRAND}</div>
        <nav>{NAV[role].map(([p, l]) => <NavLink key={p} end={p === ""} to={`/${role}${p && "/" + p}`}>{l}</NavLink>)}</nav>
        <div className="who"><b>{user.name}</b><span>{user.role}</span><button className="btn sec sm" onClick={logout}>Sign out</button></div>
      </aside>
      <main className="main"><Outlet /></main>
    </div>
  );
}

export default function App() {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/" element={<Navigate to={user ? "/" + user.role : "/login"} replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/candidate" element={<Shell role="candidate" />}>
        <Route index element={<CProfile />} /><Route path="jobs" element={<CJobs />} /><Route path="applications" element={<CApps />} />
        <Route path="interviews" element={<Interviews role="candidate" />} /><Route path="notifications" element={<Notifications />} />
      </Route>
      <Route path="/admin" element={<Shell role="admin" />}>
        <Route index element={<Dashboard />} /><Route path="jobs" element={<Jobs />} /><Route path="candidates" element={<Candidates />} />
        <Route path="matching" element={<Matching />} /><Route path="search" element={<Search />} /><Route path="shortlists" element={<Shortlists />} />
        <Route path="interviews" element={<Interviews role="admin" />} /><Route path="notifications" element={<Notifications />} />
      </Route>
      <Route path="/interviewer" element={<Shell role="interviewer" />}>
        <Route index element={<Interviews role="interviewer" />} /><Route path="notifications" element={<Notifications />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
