import { FormEvent, useMemo, useState } from "react";
import { ArrowRight, CheckCircle2, LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { Link, useLocation } from "wouter";
import { confirmPasswordReset, loginAccount, notifyAuthChanged, registerAccount, requestPasswordReset } from "@/lib/auth";

function AuthShell({ eyebrow, title, description, children }: { eyebrow: string; title: string; description: string; children: React.ReactNode }) {
  return <main className="route-state auth-page"><div className="container auth-wrap"><Link href="/" className="brand auth-brand"><span className="brand-mark"><ShieldCheck size={18} /></span><span>Global<span>Pathways</span></span></Link><section className="auth-card"><div className="auth-intro"><div className="dashboard-access-icon"><LockKeyhole size={22} /></div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{children}</section><p className="auth-note">Your account protects dashboard access. Guest applications remain available without registration.</p></div></main>;
}

function Field({ label, type = "text", value, onChange, placeholder, autoComplete }: { label: string; type?: string; value: string; onChange: (value: string) => void; placeholder: string; autoComplete?: string }) {
  return <label className="auth-field"><span>{label}</span><input type={type} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} autoComplete={autoComplete} required /></label>;
}

export default function AuthPage() {
  const [location, setLocation] = useLocation();
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [working, setWorking] = useState(false);
  const params = useMemo(() => new URLSearchParams(window.location.search), [location]);
  const resetMode = location.startsWith("/reset-password");
  const registerMode = location === "/create-account";
  const forgotMode = location === "/forgot-password";

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    setWorking(true);
    try {
      if (resetMode) {
        if (password !== confirmation) throw new Error("The passwords do not match.");
        await confirmPasswordReset(params.get("uid") || "", params.get("token") || "", password);
        notifyAuthChanged();
        setLocation("/dashboard");
      } else if (forgotMode) {
        const response = await requestPasswordReset(email);
        setMessage(response.detail);
      } else if (registerMode) {
        await registerAccount(name, email, password);
        notifyAuthChanged();
        setLocation("/dashboard");
      } else {
        await loginAccount(email, password);
        notifyAuthChanged();
        setLocation("/dashboard");
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "We could not complete that request.");
    } finally {
      setWorking(false);
    }
  }

  if (resetMode) return <AuthShell eyebrow="Create a new password" title="Return with confidence." description="Choose a new password for your Global Pathways account."><form className="auth-form" onSubmit={submit}><Field label="New password" type="password" value={password} onChange={setPassword} placeholder="At least 8 characters" autoComplete="new-password" /><Field label="Confirm password" type="password" value={confirmation} onChange={setConfirmation} placeholder="Repeat your password" autoComplete="new-password" />{error && <div className="auth-error" role="alert">{error}</div>}<button className="button button-dark auth-submit" disabled={working}>{working ? "Saving…" : "Set new password"}<ArrowRight size={17} /></button></form><p className="auth-switch"><Link href="/sign-in">Return to sign in</Link></p></AuthShell>;

  if (forgotMode) return <AuthShell eyebrow="Password recovery" title="A clear way back in." description="Enter your account email and we will send a secure password-reset link if the account exists."><form className="auth-form" onSubmit={submit}><Field label="Email address" type="email" value={email} onChange={setEmail} placeholder="you@example.com" autoComplete="email" />{message && <div className="auth-success" role="status"><CheckCircle2 size={17} />{message}</div>}{error && <div className="auth-error" role="alert">{error}</div>}<button className="button button-dark auth-submit" disabled={working}>{working ? "Sending…" : "Send reset link"}<Mail size={17} /></button></form><p className="auth-switch"><Link href="/sign-in">Return to sign in</Link></p></AuthShell>;

  return <AuthShell eyebrow={registerMode ? "Create your account" : "Global Pathways account"} title={registerMode ? "Keep your next step close." : "Welcome back."} description={registerMode ? "Create a secure account to track applications, save routes, and return to your plans." : "Sign in to continue to your private application workspace."}><form className="auth-form" onSubmit={submit}>{registerMode && <Field label="Full name" value={name} onChange={setName} placeholder="Your full name" autoComplete="name" />}<Field label="Email address" type="email" value={email} onChange={setEmail} placeholder="you@example.com" autoComplete="email" /><Field label="Password" type="password" value={password} onChange={setPassword} placeholder="At least 8 characters" autoComplete={registerMode ? "new-password" : "current-password"} />{error && <div className="auth-error" role="alert">{error}</div>}<button className="button button-dark auth-submit" disabled={working}>{working ? "Please wait…" : registerMode ? "Create account" : "Sign in"}<ArrowRight size={17} /></button></form><div className="auth-links">{!registerMode && <Link href="/forgot-password">Forgot password?</Link>}<span>{registerMode ? "Already have an account?" : "New to Global Pathways?"} <Link href={registerMode ? "/sign-in" : "/create-account"}>{registerMode ? "Sign in" : "Create account"}</Link></span></div></AuthShell>;
}
