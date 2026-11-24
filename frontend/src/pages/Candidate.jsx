import { useRef, useState } from "react";
import { api, err, fmt } from "../api";
import { Badge, Empty, Head, Ring, useLoad, useToast } from "../ui";
import { ProfileEditor } from "./Shared";

export function CProfile() {
  const toast = useToast(), file = useRef();
  const [c, reload] = useLoad(() => api.get("/candidates/profile"));
  const [busy, setBusy] = useState(false);
  const upload = async (f) => {
    if (!f) return; setBusy(true);
    const fd = new FormData(); fd.append("file", f);
    try { await api.post("/resumes/upload", fd); toast("Resume parsed. Review the details below."); await reload(); }
    catch (e) { toast(err(e), "bad"); } setBusy(false); file.current.value = "";
  };
  const save = async (p) => { try { await api.put("/candidates/profile", p); toast("Profile saved"); reload(); } catch (e) { toast(err(e), "bad"); } };
  if (!c) return <div className="page"><Empty>Loading your profile...</Empty></div>;
  return (
    <div className="page">
      <Head title="My profile" sub="Upload your resume and we fill in the details. Check them before you apply." />
      <div className="card drop" onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); upload(e.dataTransfer.files[0]); }}>
        <div><b>{busy ? "Reading your resume..." : "Drop your resume here"}</b><p>PDF or DOCX. Skills, education and experience are extracted for you to review.</p></div>
        <button className="btn" disabled={busy} onClick={() => file.current.click()}>Choose file</button>
        <input ref={file} type="file" accept=".pdf,.docx" hidden onChange={(e) => upload(e.target.files[0])} />
      </div>
      <div className="card"><ProfileEditor c={c} onSave={save} /></div>
    </div>
  );
}

export function CJobs() {
  const toast = useToast();
  const [jobs] = useLoad(() => api.get("/jobs"));
  const [apps, reload] = useLoad(() => api.get("/applications/mine"));
  const applied = new Set((apps || []).map((a) => a.job_id));
  const apply = async (id) => { try { await api.post("/applications", { job_id: id }); toast("Application sent"); reload(); } catch (e) { toast(err(e), "bad"); } };
  return (
    <div className="page"><Head title="Open jobs" sub="Roles you can apply to right now." />
      {jobs && !jobs.length && <Empty>No open jobs yet. Check back soon.</Empty>}
      <div className="grid g2">{(jobs || []).map((j) => (
        <div className="card" key={j.id}>
          <h3>{j.title}</h3><p className="muted">{j.location} · {j.employment_type} · {j.min_experience}-{j.max_experience} yrs{j.deadline ? " · apply by " + j.deadline : ""}</p>
          <p>{j.description}</p>
          <div className="chips">{j.required_skills.map((s) => <span className="chip" key={s}>{s}</span>)}</div>
          <button className="btn" disabled={applied.has(j.id)} onClick={() => apply(j.id)}>{applied.has(j.id) ? "Applied" : "Apply now"}</button>
        </div>))}</div>
    </div>
  );
}

export function CApps() {
  const [apps] = useLoad(() => api.get("/applications/mine"));
  return (
    <div className="page"><Head title="My applications" sub="Track where each application stands." />
      {apps && !apps.length && <Empty>You have not applied yet. Browse open jobs to get started.</Empty>}
      <div className="list">{(apps || []).map((a) => (
        <div className="card row between" key={a.id}>
          <div><h3>{a.job_title}</h3><p className="muted">Applied {fmt(a.created_at)}</p></div>
          <div className="row">{a.match_score != null && <Ring v={a.match_score} size={52} />}<Badge s={a.status} /></div>
        </div>))}</div>
    </div>
  );
}
