import { createContext, useCallback, useContext, useEffect, useState } from "react";

const T = createContext(() => {});
export const useToast = () => useContext(T);

export function ToastHost({ children }) {
  const [t, setT] = useState(null);
  const show = useCallback((m, k = "ok") => { setT({ m, k }); setTimeout(() => setT(null), 3400); }, []);
  return <T.Provider value={show}>{children}{t && <div className={"toast " + t.k} role="status">{t.m}</div>}</T.Provider>;
}

export function useLoad(fn, deps = []) {
  const [d, setD] = useState(null);
  const [l, setL] = useState(true);
  const run = useCallback(() => { setL(true); return fn().then((r) => setD(r.data)).catch(() => setD(null)).finally(() => setL(false)); }, deps);
  useEffect(() => { run(); }, [run]);
  return [d, run, l];
}

export const Badge = ({ s }) => <span className={"badge " + String(s || "").toLowerCase().replace(/\s+/g, "-")}>{s}</span>;
export const Empty = ({ children }) => <div className="empty">{children}</div>;
export const Head = ({ title, sub, children }) => <div className="head"><div><h2>{title}</h2>{sub && <p>{sub}</p>}</div><div className="row">{children}</div></div>;
export const Skills = ({ list = [], on = [], miss = [] }) => (
  <div className="chips">{list.map((s) => <span key={s} className={"chip" + (on.includes(s) ? " on" : "") + (miss.includes(s) ? " miss" : "")}>{s}</span>)}</div>
);

export function Ring({ v = 0, size = 64 }) {
  const r = size / 2 - 6, c = 2 * Math.PI * r, col = v >= 75 ? "#0E8F86" : v >= 50 ? "#D99A00" : "#D4532F";
  return (
    <svg width={size} height={size} className="ring" role="img" aria-label={`Score ${Math.round(v)} out of 100`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E1E9E7" strokeWidth="6" />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={col} strokeWidth="6" strokeLinecap="round"
        strokeDasharray={c} strokeDashoffset={c * (1 - Math.min(v, 100) / 100)} transform={`rotate(-90 ${size / 2} ${size / 2})`} />
      <text x="50%" y="52%" textAnchor="middle" dominantBaseline="middle" fontSize={size / 3.1} fontWeight="700" fill="#12232B">{Math.round(v)}</text>
    </svg>
  );
}

export function Modal({ title, onClose, children, wide }) {
  useEffect(() => { const k = (e) => e.key === "Escape" && onClose(); window.addEventListener("keydown", k); return () => window.removeEventListener("keydown", k); }, [onClose]);
  return (
    <div className="overlay" onClick={onClose}>
      <div className={"modal" + (wide ? " wide" : "")} role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <div className="mh"><h3>{title}</h3><button className="x" onClick={onClose} aria-label="Close">×</button></div>
        {children}
      </div>
    </div>
  );
}
