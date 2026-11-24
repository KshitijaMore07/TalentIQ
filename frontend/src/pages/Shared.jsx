import { useEffect, useState } from "react";
import { api, err, fmt } from "../api";
import { Badge, Empty, Head, Modal, Skills, useLoad, useToast } from "../ui";

const EDU = ["degree", "institution"], EXP = ["title", "company", "duration", "description"], PRJ = ["name", "description"];
const toLines = (a, k) => (a || []).map((o) => k.map((x) => o[x] || "").join(" | ")).join("\n");
const fromLines = (t, k) => t.split("\n").map((l) => l.trim()).filter(Boolean).map((l) => { const p = l.split("|").map((x) => x.trim()); return Object.fromEntries(k.map((x, i) => [x, p[i] || ""])); });

export function ProfileEditor({ c, onSave }) {
  const init = () => ({ name: c.name || "", email: c.email || "", phone: c.phone || "", location: c.location || "", summary: c.summary || "", experience_years: c.experience_years || 0,
    skills: (c.skills || []).join(", "), edu: toLines(c.education, EDU), exp: toLines(c.experience, EXP), prj: toLines(c.projects, PRJ) });
  const [f, setF] = useState(init);
  useEffect(() => setF(init()), [c]);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const save = () => onSave({ name: f.name, phone: f.phone, location: f.location, summary: f.summary, experience_years: Number(f.experience_years) || 0, skills: f.skills,
    education: fromLines(f.edu, EDU), experience: fromLines(f.exp, EXP), projects: fromLines(f.prj, PRJ) });
  return (
    <div className="form">
      <div className="grid g2">
        <label className="field">Full name<input className="input" value={f.name} onChange={set("name")} readOnly={!!c.name} /></label>
        <label className="field">Email<input className="input" value={f.email} readOnly /></label>
        <label className="field">Phone<input className="input" value={f.phone} onChange={set("phone")} /></label>
        <label className="field">Location<input className="input" value={f.location} onChange={set("location")} /></label>
        <label className="field">Years of experience<input className="input" type="number" min="0" step="0.5" value={f.experience_years} onChange={set("experience_years")} /></label>
        <label className="field">Skills (comma separated)<input className="input" value={f.skills} onChange={set("skills")} /></label>
      </div>
      <label className="field">Summary<textarea className="input" rows="2" value={f.summary} onChange={set("summary")} /></label>
      <label className="field">Education (one per line: degree | institution)<textarea className="input" rows="2" value={f.edu} onChange={set("edu")} /></label>
      <label className="field">Experience (one per line: title | company | duration | description)<textarea className="input" rows="3" value={f.exp} onChange={set("exp")} /></label>
      <label className="field">Projects (one per line: name | description)<textarea className="input" rows="2" value={f.prj} onChange={set("prj")} /></label>
      <div><button className="btn" onClick={save}>Save changes</button></div>
    </div>
  );
}

export function CandidateView({ id, admin, onClose }) {
  const toast = useToast();
  const [c, reload] = useLoad(() => api.get(`/candidates/${id}`), [id]);
  const [edit, setEdit] = useState(false), [note, setNote] = useState("");
  const save = async (p) => { try { await api.put(`/admin/candidates/${id}`, p); toast("Candidate updated"); setEdit(false); reload(); } catch (e) { toast(err(e), "bad"); } };
  const addNote = async () => { try { await api.post(`/admin/candidates/${id}/notes`, { note }); setNote(""); reload(); } catch (e) { toast(err(e), "bad"); } };
  return (
    <Modal wide title={c ? c.name || "Candidate" : "Candidate"} onClose={onClose}>
      {!c ? <Empty>Loading...</Empty> : edit ? <ProfileEditor c={c} onSave={save} /> : (
        <div className="detail">
          <p className="muted">{[c.email, c.phone, c.location].filter(Boolean).join(" · ")} · {c.experience_years} yrs experience</p>
          {c.summary && <p>{c.summary}</p>}
          <h4>Skills</h4><Skills list={c.skills} />
          <h4>Education</h4>{c.education.length ? c.education.map((e, i) => <p key={i}>{e.degree}{e.institution && " - " + e.institution}</p>) : <p className="muted">Not found in resume</p>}
          <h4>Experience</h4>{c.experience.length ? c.experience.map((e, i) => <p key={i}><b>{e.title}</b> {e.company && "at " + e.company} <span className="muted">{e.duration}</span><br />{e.description}</p>) : <p className="muted">Not found in resume</p>}
          <h4>Projects</h4>{c.projects.length ? c.projects.map((p, i) => <p key={i}><b>{p.name}</b> {p.description}</p>) : <p className="muted">Not found in resume</p>}
          {admin && <>
            <h4>Internal notes</h4>
            {(c.notes || []).map((n) => <p key={n.id} className="note">{n.note}<br /><span className="muted">{n.author} · {fmt(n.created_at)}</span></p>)}
            <div className="row"><input className="input" placeholder="Add a note for your team" value={note} onChange={(e) => setNote(e.target.value)} /><button className="btn sm" onClick={addNote} disabled={!note.trim()}>Add note</button></div>
            <div><button className="btn sec" onClick={() => setEdit(true)}>Correct extracted details</button></div></>}
        </div>)}
    </Modal>
  );
}

function Schedule({ onDone }) {
  const toast = useToast();
  const [cands] = useLoad(() => api.get("/admin/candidates")), [jobs] = useLoad(() => api.get("/jobs")), [ivs] = useLoad(() => api.get("/admin/interviewers"));
  const [f, setF] = useState({ candidate_id: "", job_id: "", interviewer_id: "", scheduled_at: "", duration_minutes: 45 });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const go = async () => {
    try { await api.post("/interviews", { ...f, candidate_id: +f.candidate_id, job_id: +f.job_id, interviewer_id: +f.interviewer_id }); toast("Interview scheduled. Invitations sent."); onDone(); }
    catch (e) { toast(err(e), "bad"); }
  };
  const sel = (k, list, label) => <label className="field">{label}<select className="input" value={f[k]} onChange={set(k)}><option value="">Choose...</option>{(list || []).map((x) => <option key={x.id} value={x.id}>{x.name || x.title}</option>)}</select></label>;
  return (
    <div className="form">
      {sel("candidate_id", cands, "Candidate")}{sel("job_id", jobs, "Job")}{sel("interviewer_id", ivs, "Interviewer")}
      <div className="grid g2">
        <label className="field">Date and time<input className="input" type="datetime-local" value={f.scheduled_at} onChange={set("scheduled_at")} /></label>
        <label className="field">Duration (minutes)<input className="input" type="number" min="15" step="15" value={f.duration_minutes} onChange={set("duration_minutes")} /></label>
      </div>
      <div><button className="btn" onClick={go} disabled={!f.candidate_id || !f.job_id || !f.interviewer_id || !f.scheduled_at}>Schedule and send invitations</button></div>
    </div>
  );
}

function Feedback({ iv, onDone }) {
  const toast = useToast();
  const [f, setF] = useState({ technical: 7, communication: 7, problem_solving: 7, remarks: "", recommendation: "Hire", ...(iv.feedback || {}) });
  const go = async () => { try { await api.post(`/interviews/${iv.id}/feedback`, f); toast("Feedback submitted"); onDone(); } catch (e) { toast(err(e), "bad"); } };
  const rng = (k, l) => <label className="field">{l}: <b>{f[k]}/10</b><input type="range" min="1" max="10" value={f[k]} onChange={(e) => setF({ ...f, [k]: +e.target.value })} /></label>;
  return (
    <div className="form">
      {rng("technical", "Technical skills")}{rng("communication", "Communication")}{rng("problem_solving", "Problem solving")}
      <label className="field">Remarks<textarea className="input" rows="3" value={f.remarks || ""} onChange={(e) => setF({ ...f, remarks: e.target.value })} /></label>
      <label className="field">Final recommendation<select className="input" value={f.recommendation} onChange={(e) => setF({ ...f, recommendation: e.target.value })}>{["Strong hire", "Hire", "Maybe", "No hire"].map((x) => <option key={x}>{x}</option>)}</select></label>
      <div><button className="btn" onClick={go}>Submit feedback</button></div>
    </div>
  );
}

export function Interviews({ role }) {
  const toast = useToast();
  const [list, reload] = useLoad(() => api.get("/interviews"));
  const [m, setM] = useState(null), [when, setWhen] = useState("");
  const done = () => { setM(null); reload(); };
  const update = async (iv, p, msg) => { try { await api.put(`/interviews/${iv.id}`, p); toast(msg); done(); } catch (e) { toast(err(e), "bad"); } };
  return (
    <div className="page">
      <Head title={role === "interviewer" ? "My interviews" : "Interviews"} sub={role === "candidate" ? "Your scheduled interviews." : role === "admin" ? "Schedule, move or cancel interviews." : "Review candidates and submit feedback."}>
        {role === "admin" && <button className="btn" onClick={() => setM({ t: "new" })}>Schedule interview</button>}
      </Head>
      {list && !list.length && <Empty>{role === "admin" ? "No interviews yet. Schedule one for a shortlisted candidate." : "Nothing scheduled yet."}</Empty>}
      <div className="list">{(list || []).map((i) => (
        <div className="card row between wrap" key={i.id}>
          <div><h3>{role === "candidate" ? i.job_title : i.candidate_name}</h3>
            <p className="muted">{role !== "candidate" && i.job_title + " · "}{fmt(i.scheduled_at)} · {i.duration_minutes} min{role !== "interviewer" && " · with " + i.interviewer_name}</p>
            {i.feedback && role !== "candidate" && <p className="muted">Feedback: {i.feedback.recommendation} (tech {i.feedback.technical}, comm {i.feedback.communication}, problem solving {i.feedback.problem_solving}){i.feedback.remarks && " - " + i.feedback.remarks}</p>}</div>
          <div className="row"><Badge s={i.status} />
            {role !== "candidate" && <button className="btn sec sm" onClick={() => setM({ t: "cand", i })}>Profile</button>}
            {role === "interviewer" && i.status !== "Cancelled" && <button className="btn sm" onClick={() => setM({ t: "fb", i })}>{i.feedback ? "Edit feedback" : "Give feedback"}</button>}
            {role === "admin" && i.status !== "Cancelled" && <>
              <button className="btn sec sm" onClick={() => { setWhen((i.scheduled_at || "").slice(0, 16)); setM({ t: "move", i }); }}>Reschedule</button>
              <button className="btn bad sm" onClick={() => update(i, { status: "Cancelled" }, "Interview cancelled")}>Cancel</button></>}
          </div>
        </div>))}</div>
      {m?.t === "new" && <Modal title="Schedule interview" onClose={() => setM(null)}><Schedule onDone={done} /></Modal>}
      {m?.t === "fb" && <Modal title={`Feedback: ${m.i.candidate_name}`} onClose={() => setM(null)}><Feedback iv={m.i} onDone={done} /></Modal>}
      {m?.t === "cand" && <CandidateView id={m.i.candidate_id} admin={role === "admin"} onClose={() => setM(null)} />}
      {m?.t === "move" && <Modal title="Reschedule interview" onClose={() => setM(null)}><div className="form">
        <label className="field">New date and time<input className="input" type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} /></label>
        <div><button className="btn" onClick={() => update(m.i, { scheduled_at: when }, "Interview rescheduled")}>Save new time</button></div></div></Modal>}
    </div>
  );
}

export function Notifications() {
  const [n] = useLoad(() => api.get("/notifications"));
  return (
    <div className="page"><Head title="Notifications" sub="Updates about applications and interviews." />
      {n && !n.length && <Empty>You are all caught up.</Empty>}
      <div className="list">{(n || []).map((x) => <div className="card" key={x.id}><p>{x.message}</p><p className="muted">{fmt(x.created_at)}</p></div>)}</div>
    </div>
  );
}
