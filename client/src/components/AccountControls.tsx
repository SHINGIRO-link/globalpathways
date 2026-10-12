import { useState } from "react";
import { Home, LogOut, ShieldCheck, UserRound } from "lucide-react";
import { Link, useLocation } from "wouter";
import { useAuth } from "@/_core/hooks/useAuth";
import { roleLabel } from "@/lib/roles";


export default function AccountControls() {
  const { user, logout } = useAuth();
  const [, setLocation] = useLocation();
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  if (!user) return null;
  const label = roleLabel(user.role);
  async function handleLogout() {
    setWorking(true);
    setError("");
    try {
      await logout();
      setLocation("/");
    } catch {
      setError("We could not sign you out. Please try again.");
    } finally {
      setWorking(false);
    }
  }
  return <aside className="account-controls" aria-label="Account controls"><Link href="/" className="account-home-link" aria-label="Go to Global Pathways homepage"><Home size={16} /><span>Homepage</span></Link><div className="account-profile"><span className="account-avatar" aria-hidden="true">{user.name?.slice(0, 1).toUpperCase() || <UserRound size={16} />}</span><div><strong>{user.name || "Signed-in account"}</strong><span>{user.email || "Email not available"}</span><span className={`role-badge role-${user.role}`}><ShieldCheck size={12} /> {label} account</span></div></div><button type="button" className="account-sign-out" onClick={() => void handleLogout()} disabled={working} aria-label="Sign out of Global Pathways"><LogOut size={15} /> {working ? "Signing out…" : "Sign out"}</button>{error && <p className="account-error" role="alert">{error}</p>}</aside>;
}
