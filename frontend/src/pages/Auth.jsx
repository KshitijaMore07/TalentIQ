import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, err, BRAND } from "../api";
import { useAuth } from "../auth";

function Hero() {
  return (
    <aside className="hero">
      <div className="brand light"><span className="mark" />{BRAND}</div>
      <h1>Know who fits before the first call.</h1>
      <p>Upload resumes, match them to a role in seconds and see exactly why each candidate ranks where they do.</p>
      <div className="sample">
        <div className="sh"><span>Python Backend Developer</span><b>86</b></div>
        <div className="chips"><span className="chip on">Python</span><span className="chip on">Flask</span><span className="chip on">SQL</span><span className="chip miss">Docker</span></div>
        <small>Matches 3 of 3 required skills. Missing preferred skill: Docker.</small>
      </div>
    </aside>
  );
}

function Form({ mode }) {
  const nav = useNavigate(), { login } = useAuth();
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [e, setE] = useState(""); const [busy, setBusy] = useState(false);
  const set = (k) => (ev) => setF({ ...f, [k]: ev.target.value });
  const submit = async (ev) => {
    ev.preventDefault(); setE(""); setBusy(true);
    try { const { data } = await api.post("/auth/" + mode, f); login(data.token, data.user); nav("/" + data.user.role); }
    catch (x) { setE(err(x)); } setBusy(false);
  };
  const reg = mode === "register";
  return (
    <div className="auth">
      <Hero />
      <section className="panel">
        <form onSubmit={submit} className="form">
          <h2>{reg ? "Create your candidate account" : "Sign in to " + BRAND}</h2>
          {reg && <label className="field">Full name<input className="input" value={f.name} onChange={set("name")} required /></label>}
          <label className="field">Email<input className="input" type="email" value={f.email} onChange={set("email")} required /></label>
          <label className="field">Password<input className="input" type="password" value={f.password} onChange={set("password")} required minLength={6} /></label>
          {e && <div className="error" role="alert">{e}</div>}
          <button className="btn" disabled={busy}>{busy ? "Please wait..." : reg ? "Create account" : "Sign in"}</button>
          <p className="alt">{reg ? <>Already registered? <Link to="/login">Sign in</Link></> : <>New candidate? <Link to="/register">Create an account</Link></>}</p>
          {!reg && <div className="demo"><span>Demo accounts</span>
            <button type="button" className="btn sec sm" onClick={() => setF({ ...f, email: "admin@talentiq.com", password: "Admin@123" })}>Recruiter</button>
            <button type="button" className="btn sec sm" onClick={() => setF({ ...f, email: "interviewer@talentiq.com", password: "Interview@123" })}>Interviewer</button></div>}
        </form>
      </section>
    </div>
  );
}
export const Login = () => <Form mode="login" />;
export const Register = () => <Form mode="register" />;
