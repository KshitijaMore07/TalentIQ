import { createContext, useContext, useState } from "react";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => { try { return JSON.parse(localStorage.getItem("tiq_user")); } catch { return null; } });
  const login = (token, u) => { localStorage.setItem("tiq_token", token); localStorage.setItem("tiq_user", JSON.stringify(u)); setUser(u); };
  const logout = () => { localStorage.clear(); setUser(null); };
  return <Ctx.Provider value={{ user, login, logout }}>{children}</Ctx.Provider>;
}
