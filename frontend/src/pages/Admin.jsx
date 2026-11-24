import { useEffect, useRef, useState } from "react";
import { api, err, fmt } from "../api";
import { Badge, Empty, Head, Modal, Ring, Skills, useLoad, useToast } from "../ui";
import { CandidateView } from "./Shared";

export function Dashboard() {
  const [s] = useLoad(() => api.get("/admin/stats"));
  if (!s) return <div className="page"><Empty>Loading dashboard...</Empty></div>;
  const cards = [["Candidates", s.candidates], ["Resumes processed", s.resumes], ["Active jobs", s.active_jobs], ["Applications", s.applications], ["Shortlisted", s.shortlisted], ["Interviews scheduled", s.scheduled_interviews], ["Selected", s.selected]];
  const max = Math.max(1, ...Object.values(s.by_status));
  return (
    <div className="page"><Head title="Dashboard" sub="Where your hiring stands today." />
      <div className="grid g4">{cards.map(([l, v]) => <div className="card stat" key={l}><b>{v}</b><span>{l}</span></div>)}</div>
      <div className="card"><h3>Application pipeline</h3>
        {Object.entries(s.by_status).map(([k, v]) => <div className="bar" key={k}><span>{k}</span><i><u style={{ width: (v / max) * 100 + "%" }} /></i><b>{v}</b></div>)}</div>
    </div>
  );
}

function JobForm({ job, onDone }) {
  const toast = useToast();
  const [f, setF] = useState(() => ({ title: "", description: "", required_skills: "", preferred_skills: "", min_experience: 0, max_experience: 5, education: "", location: "", employment_type: "Full-time", deadline: "", status: "Open",
    ...(job || {}), ...(job ? { required_skills: job.required_skills.join(", "), preferred_skills: job.preferred_skills.join(", ") } : {}) }));
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const save = async () => { try { job ? await api.put(`/jobs/${job.id}`, f) : await api.post("/jobs", f); toast("Job saved"); onDone(); } catch (e) { toast(err(e), "bad"); } };
  const inp = (k, l, t = "text") => <label className="field">{l}<input className="input" type={t} value={f[k] ?? ""} onChange={set(k)} /></label>;
  return (
    <div className="form">
      {inp("title", "Job title")}
      <label className="field">Description<textarea className="input" rows="3" value={f.description} onChange={set("description")} /></label>
      <div className="grid g2">{inp("required_skills", "Required skills (comma separated)")}{inp("preferred_skills", "Preferred skills (comma separated)")}
        {inp("min_experience", "Minimum experience (years)", "number")}{inp("max_experience", "Maximum experience (years)", "number")}
        {inp("education", "Education requirement")}{inp("location", "Location")}
        <label className="field">Employment type<select className="input" value={f.employment_type} onChange={set("employment_type")}>{["Full-time", "Part-time", "Contract", "Internship"].map((x) => <option key={x}>{x}</option>)}</select></label>
        {inp("deadline", "Application deadline", "date")}
        <label className="field">Status<select className="input" value={f.status} onChange={set("status")}><option>Open</option><option>Closed</option></select></label></div>
      <div><button className="btn" onClick={save}>Save job</button></div>
    </div>
  );
}

export function Jobs() {
  const toast = useToast();
  const [jobs, reload] = useLoad(() => api.get("/jobs"));
  const [m, setM] = useState(null);
  const del = async (j) => { if (!confirm(`Delete "${j.title}" and its applications?`)) return; try { await api.delete(`/jobs/${j.id}`); toast("Job deleted"); reload(); } catch (e) { toast(err(e), "bad"); } };
  return (
    <div className="page"><Head title="Jobs" sub="Create and manage open roles."><button className="btn" onClick={() => setM({})}>Create job</button></Head>
      {jobs && !jobs.length && <Empty>No jobs yet. Create your first role to start matching candidates.</Empty>}
      <div className="grid g2">{(jobs || []).map((j) => (
        <div className="card" key={j.id}><div className="row between"><h3>{j.title}</h3><Badge s={j.status} /></div>
          <p className="muted">{j.location} · {j.employment_type} · {j.min_experience}-{j.max_experience} yrs · {j.education || "Any education"}</p>
          <p>{j.description}</p><Skills list={j.required_skills} on={j.required_skills} />
          <div className="row"><button className="btn sec sm" onClick={() => setM({ job: j })}>Edit</button><button className="btn bad sm" onClick={() => del(j)}>Delete</button></div></div>))}</div>
      {m && <Modal wide title={m.job ? "Edit job" : "Create job"} onClose={() => setM(null)}><JobForm job={m.job} onDone={() => { setM(null); reload(); }} /></Modal>}
    </div>
  );
}

export function Candidates() {
  const toast = useToast(), file = useRef();
  const [q, setQ] = useState(""), [skill, setSkill] = useState(""), [view, setView] = useState(null), [res, setRes] = useState(null), [busy, setBusy] = useState(false);
  const [list, reload] = useLoad(() => api.get("/admin/candidates", { params: { q, skill } }), [q, skill]);
  const [resumes, reloadR] = useLoad(() => api.get("/admin/resumes"));
  const upload = async (files) => {
    if (!files.length) return; setBusy(true);
    const fd = new FormData(); [...files].forEach((f) => fd.append("files", f));
    try { const { data } = await api.post("/resumes/bulk-upload", fd); setRes(data); toast(`${data.filter((r) => r.status === "Completed").length} of ${data.length} resumes processed`); reload(); reloadR(); }
    catch (e) { toast(err(e), "bad"); } setBusy(false); file.current.value = "";
  };
  return (
    <div className="page"><Head title="Candidates" sub="Upload resumes in bulk and search your talent pool." />
      <div className="card drop" onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); upload(e.dataTransfer.files); }}>
        <div><b>{busy ? "Processing resumes one by one..." : "Drop resumes here"}</b><p>Select several PDF or DOCX files. A bad file never stops the rest, and duplicates are detected by email.</p></div>
        <button className="btn" disabled={busy} onClick={() => file.current.click()}>Choose resumes</button>
        <input ref={file} type="file" multiple accept=".pdf,.docx" hidden onChange={(e) => upload(e.target.files)} />
      </div>
      {res && <div className="card"><h3>Upload results</h3><div className="tbl"><table><tbody>{res.map((r) => (
        <tr key={r.id}><td>{r.filename}</td><td><Badge s={r.duplicate ? "Duplicate" : r.status} /></td><td>{r.candidate_name || ""}</td><td className="muted">{r.error}</td></tr>))}</tbody></table></div></div>}
      <div className="row"><input className="input" placeholder="Search by name, email or location" value={q} onChange={(e) => setQ(e.target.value)} />
        <input className="input" placeholder="Filter by skill" value={skill} onChange={(e) => setSkill(e.target.value)} /></div>
      {list && !list.length && <Empty>No candidates found. Upload resumes to build your pool.</Empty>}
      <div className="tbl"><table><thead><tr><th>Name</th><th>Contact</th><th>Exp.</th><th>Skills</th><th /></tr></thead><tbody>{(list || []).map((c) => (
        <tr key={c.id}><td><b>{c.name || "Unnamed"}</b></td><td>{c.email}<br /><span className="muted">{c.phone}</span></td><td>{c.experience_years} yrs</td>
          <td><Skills list={c.skills.slice(0, 6)} /></td><td><button className="btn sec sm" onClick={() => setView(c.id)}>View</button></td></tr>))}</tbody></table></div>
      <h3>Resume processing log</h3>
      <div className="tbl"><table><tbody>{(resumes || []).slice(0, 12).map((r) => (
        <tr key={r.id}><td>{r.filename}</td><td><Badge s={r.status} /></td><td className="muted">{r.error}</td><td className="muted">{fmt(r.created_at)}</td></tr>))}</tbody></table></div>
      {view && <CandidateView id={view} admin onClose={() => { setView(null); reload(); }} />}
    </div>
  );
}

export function Matching() {
  const toast = useToast();
  const [jobs] = useLoad(() => api.get("/jobs"));
  const [data, setData] = useState(null), [busy, setBusy] = useState(false), [sel, setSel] = useState([]), [view, setView] = useState(null), [jid, setJid] = useState("");
  const run = async (id) => {
    setJid(id); setSel([]); if (!id) return setData(null); setBusy(true);
    try { setData((await api.get(`/matching/${id}`)).data); } catch (e) { toast(err(e), "bad"); } setBusy(false);
  };
  const shortlist = async () => { try { const { data: d } = await api.post("/shortlists", { job_id: +jid, candidate_ids: sel }); toast(`${d.added} candidate(s) shortlisted`); setSel([]); run(jid); } catch (e) { toast(err(e), "bad"); } };
  const tog = (id) => setSel(sel.includes(id) ? sel.filter((x) => x !== id) : [...sel, id]);
  return (
    <div className="page"><Head title="AI matching" sub="Ranked by required skills, experience, education, preferred skills and semantic similarity.">
      {sel.length > 0 && <button className="btn" onClick={shortlist}>Shortlist {sel.length} selected</button>}</Head>
      <label className="field">Choose a job<select className="input" value={jid} onChange={(e) => run(e.target.value)}><option value="">Select a job...</option>{(jobs || []).map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}</select></label>
      {busy && <Empty>Scoring candidates...</Empty>}
      {data && !data.results.length && <Empty>No candidates to match yet. Upload resumes first.</Empty>}
      <div className="list">{(data?.results || []).map((r) => (
        <div className="card mc" key={r.candidate_id}>
          <input type="checkbox" checked={sel.includes(r.candidate_id)} onChange={() => tog(r.candidate_id)} aria-label={`Select ${r.name}`} disabled={r.shortlisted} />
          <Ring v={r.score} size={72} />
          <div className="grow"><div className="row between"><h3>{r.name || "Unnamed"}</h3><div className="row">{r.shortlisted && <Badge s="Shortlisted" />}<span className="muted">{r.recommendation}</span></div></div>
            <Skills list={[...r.matched_skills, ...r.missing_skills]} on={r.matched_skills} miss={r.missing_skills} />
            <p className="muted">{r.explanation}</p>
            <div className="mini">{Object.entries(r.breakdown).map(([k, v]) => <span key={k}>{k.replace("_", " ")} <i><u style={{ width: v + "%" }} /></i> {v}</span>)}</div></div>
          <button className="btn sec sm" onClick={() => setView(r.candidate_id)}>Profile</button>
        </div>))}</div>
      {view && <CandidateView id={view} admin onClose={() => setView(null)} />}
    </div>
  );
}

export function Search() {
  const toast = useToast();
  const [q, setQ] = useState(""), [out, setOut] = useState(null), [view, setView] = useState(null), [busy, setBusy] = useState(false);
  const go = async () => { setBusy(true); try { setOut((await api.post("/search", { query: q, limit: 10 })).data); } catch (e) { toast(err(e), "bad"); } setBusy(false); };
  return (
    <div className="page"><Head title="Semantic search" sub="Describe who you need in plain language. Results are ranked by meaning, not just keywords." />
      <div className="row"><input className="input" placeholder="Find candidates with Python development experience and knowledge of machine learning" value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && q.trim() && go()} />
        <button className="btn" onClick={go} disabled={busy || !q.trim()}>{busy ? "Searching..." : "Search"}</button></div>
      {out && !out.length && <Empty>No candidates matched. Try different wording or upload more resumes.</Empty>}
      <div className="list">{(out || []).map((c) => (
        <div className="card mc" key={c.id}><Ring v={c.similarity} size={64} />
          <div className="grow"><h3>{c.name || "Unnamed"}</h3><p className="muted">{c.experience_years} yrs · {c.email}</p><Skills list={c.skills.slice(0, 8)} /></div>
          <button className="btn sec sm" onClick={() => setView(c.id)}>Profile</button></div>))}</div>
      {view && <CandidateView id={view} admin onClose={() => setView(null)} />}
    </div>
  );
}

export function Shortlists() {
  const toast = useToast();
  const [jobs] = useLoad(() => api.get("/jobs"));
  const [jid, setJid] = useState(""), [rows, setRows] = useState(null), [view, setView] = useState(null);
  const load = async (id = jid) => { if (!id) return setRows(null); try { setRows((await api.get("/shortlists", { params: { job_id: id } })).data); } catch (e) { toast(err(e), "bad"); } };
  useEffect(() => { load(); }, [jid]);
  const status = async (r, s, msg) => { try { await api.put(`/applications/${r.application_id}`, { status: s }); toast(msg); load(); } catch (e) { toast(err(e), "bad"); } };
  const remove = async (r) => { await api.delete("/shortlists", { params: { job_id: jid, candidate_id: r.candidate.id } }); load(); };
  const exp = async () => {
    const { data } = await api.get("/shortlists/export", { params: { job_id: jid }, responseType: "blob" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(data); a.download = `shortlist_${jid}.csv`; a.click();
  };
  return (
    <div className="page"><Head title="Shortlists" sub="Job-specific shortlists. Approve candidates to notify them about interviews.">{rows?.length > 0 && <button className="btn sec" onClick={exp}>Export CSV</button>}</Head>
      <label className="field">Job<select className="input" value={jid} onChange={(e) => setJid(e.target.value)}><option value="">Select a job...</option>{(jobs || []).map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}</select></label>
      {rows && !rows.length && <Empty>No one is shortlisted for this job. Use AI matching to pick candidates.</Empty>}
      <div className="list">{(rows || []).map((r) => (
        <div className="card row between wrap" key={r.application_id}>
          <div className="row">{r.match_score != null && <Ring v={r.match_score} size={56} />}<div><h3>{r.candidate.name}</h3><p className="muted">{r.candidate.email} · {r.candidate.experience_years} yrs</p></div></div>
          <div className="row"><Badge s={r.status} />
            <button className="btn sec sm" onClick={() => setView(r.candidate.id)}>Profile</button>
            {r.status === "Shortlisted" && <button className="btn sm" onClick={() => status(r, "Approved", "Candidate approved and notified")}>Approve for interview</button>}
            {["Approved", "Interview Scheduled"].includes(r.status) && <button className="btn sm" onClick={() => status(r, "Selected", "Candidate marked as selected")}>Select</button>}
            {r.status !== "Rejected" && <button className="btn bad sm" onClick={() => status(r, "Rejected", "Candidate rejected")}>Reject</button>}
            <button className="btn sec sm" onClick={() => remove(r)}>Remove</button></div>
        </div>))}</div>
      {view && <CandidateView id={view} admin onClose={() => setView(null)} />}
    </div>
  );
}
