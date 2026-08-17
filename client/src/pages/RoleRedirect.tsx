import { useEffect } from "react";
import { Link, useLocation } from "wouter";
import { Loader2, ShieldCheck } from "lucide-react";
import { useAuth } from "@/_core/hooks/useAuth";
import { startLogin } from "@/const";
import { dashboardPath } from "@/lib/roles";
import { claimGuestApplication } from "@/lib/api";

export { dashboardPath } from "@/lib/roles";

export default function RoleRedirect() {
  const { user, loading } = useAuth();
  const [, setLocation] = useLocation();

  useEffect(() => {
    if (!loading && user) {
      void (async () => {
        let claimToken = "";
        try { claimToken = sessionStorage.getItem("globalpathways-guest-claim-token") || ""; } catch {}
        if (claimToken) {
          try { await claimGuestApplication(claimToken); } catch { /* Keep the account usable even if the optional claim expires. */ }
          try { sessionStorage.removeItem("globalpathways-guest-claim-token"); } catch {}
        }
        setLocation(dashboardPath(user.role));
      })();
    }
  }, [loading, user, setLocation]);

  if (loading) return <main className="route-state"><div className="container"><Loader2 className="spin" /><span className="eyebrow">Checking account</span><h1>Opening your<br /><em>workspace.</em></h1><p>We are checking your account type and preparing the correct dashboard.</p></div></main>;
  if (!user) return <main className="route-state"><div className="container"><span className="eyebrow">Secure account access</span><h1>Sign in to open<br /><em>your workspace.</em></h1><p>After sign-in, Global Pathways automatically sends applicants, staff, and administrators to the correct dashboard.</p><button className="button button-dark" onClick={() => startLogin()}>Sign in to continue</button></div></main>;
  return <main className="route-state"><div className="container"><ShieldCheck /><span className="eyebrow">Account verified</span><h1>Opening your<br /><em>dashboard.</em></h1><p>Your account role is being applied automatically.</p></div></main>;
}

export function RoleHomeLink() {
  const { user } = useAuth();
  return <Link href={dashboardPath(user?.role)} className="button button-dark">Open my dashboard</Link>;
}
