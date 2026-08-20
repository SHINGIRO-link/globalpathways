import { useEffect, useState } from "react";
import { Link } from "wouter";
import { ArrowRight, Bell, FileText, Loader2, RefreshCw, ShieldCheck, Users } from "lucide-react";
import { useAuth } from "@/_core/hooks/useAuth";
import AccountControls from "@/components/AccountControls";
import { getAdminAccounts, type AdminAccount, updateAdminAccountRole } from "@/lib/api";

export default function AdminDashboard() {
  const { user, loading } = useAuth();
  const [accounts, setAccounts] = useState<AdminAccount[]>([]);
  const [accountsLoading, setAccountsLoading] = useState(false);
  const [accountsError, setAccountsError] = useState("");
  const [savingId, setSavingId] = useState<number | null>(null);

  useEffect(() => {
    if (!user || user.role !== "admin") return;
    let active = true;
    setAccountsLoading(true);
    setAccountsError("");
    getAdminAccounts()
      .then((payload) => active && setAccounts(payload.accounts))
      .catch((error) => active && setAccountsError(error instanceof Error ? error.message : "We could not load account management."))
      .finally(() => active && setAccountsLoading(false));
    return () => { active = false; };
  }, [user]);

  async function changeRole(account: AdminAccount, role: AdminAccount["role"]) {
    setSavingId(account.id);
    setAccountsError("");
    try {
      const updated = await updateAdminAccountRole(account.id, role);
      setAccounts((current) => current.map((item) => item.id === updated.id ? updated : item));
    } catch (error) {
      setAccountsError(error instanceof Error ? error.message : "The account role could not be updated.");
    } finally {
      setSavingId(null);
    }
  }

  if (loading) return <main className="route-state"><div className="container"><Loader2 className="spin" /><span className="eyebrow">Checking administrator access</span><h1>Preparing your<br /><em>admin dashboard.</em></h1></div></main>;
  if (!user) return <main className="route-state"><div className="container"><span className="eyebrow">Administrator access</span><h1>Sign in to open<br /><em>this dashboard.</em></h1><p>This workspace is reserved for authorized administrators.</p><Link href="/dashboard" className="button button-dark">Return to account access</Link></div></main>;
  if (user.role !== "admin") return <main className="route-state"><div className="container"><span className="eyebrow">Access not authorized</span><h1>This is not your<br /><em>dashboard.</em></h1><p>Your account is recognized as {user.role === "staff" ? "staff" : "an applicant"}. The system keeps each dashboard separate.</p><Link href={user.role === "staff" ? "/staff" : "/dashboard/end-user"} className="button button-dark">Open my dashboard <ArrowRight size={17} /></Link></div></main>;

  return <main className="dashboard-page"><div className="container dashboard-wrap"><AccountControls /><div className="dashboard-heading"><div><span className="eyebrow">Administrator dashboard</span><h1>Lead with<br /><em>clarity.</em></h1><p>{user.email || user.name}</p></div><div className="secure-label"><ShieldCheck size={15} /> Admin credentials verified</div></div><section className="dashboard-stats"><div><span>Account type</span><strong>Admin</strong></div><div><span>Review access</span><strong>Full</strong></div><div><span>Workspace</span><strong>Protected</strong></div></section><section className="dashboard-section"><div className="section-heading"><div><span className="eyebrow">Management tools</span><h2>Run the platform with confidence.</h2></div></div><div className="saved-grid"><Link href="/staff/applications" className="saved-card saved-card-link"><FileText size={22} /><span className="detail-category">Submissions & payments</span><h3>Review applications</h3><p>Search submissions, update statuses, monitor payments, and download applicant documents.</p><span className="text-button dark-button">Open staff review <ArrowRight size={15} /></span></Link><Link href="/staff/notifications" className="saved-card saved-card-link"><Bell size={22} /><span className="detail-category">Team operations</span><h3>Notification center</h3><p>Review internal alerts and manage unread staff notifications.</p><span className="text-button dark-button">Open notifications <ArrowRight size={15} /></span></Link></div></section><section className="dashboard-section admin-accounts-section"><div className="section-heading"><div><span className="eyebrow">Identity and access</span><h2>Manage account roles.</h2><p>Use least-privilege roles and never demote your own administrator account.</p></div><Users size={24} /></div>{accountsError && <div className="dashboard-error" role="alert">{accountsError}</div>}{accountsLoading ? <div className="dashboard-empty"><Loader2 className="spin" /> Loading accounts…</div> : accounts.length === 0 ? <div className="dashboard-empty">No local accounts have been created yet.</div> : <div className="account-table-wrap"><table className="account-table"><caption className="sr-only">Global Pathways local accounts and roles</caption><thead><tr><th scope="col">Account</th><th scope="col">Role</th><th scope="col">Created</th><th scope="col"><span className="sr-only">Actions</span></th></tr></thead><tbody>{accounts.map((account) => <tr key={account.id}><td><strong>{account.name}</strong><span>{account.email}</span></td><td><span className={`role-badge role-${account.role}`}>{account.role}</span></td><td>{new Date(account.created_at).toLocaleDateString()}</td><td><label className="sr-only" htmlFor={`role-${account.id}`}>Change role for {account.email}</label><select id={`role-${account.id}`} value={account.role} disabled={savingId === account.id} onChange={(event) => changeRole(account, event.target.value as AdminAccount["role"])}><option value="user">Applicant</option><option value="staff">Staff</option><option value="admin">Admin</option></select>{savingId === account.id && <Loader2 className="inline-spin" aria-label="Saving role" />}</td></tr>)}</tbody></table></div>}<button type="button" className="button button-light" onClick={() => { setAccountsLoading(true); getAdminAccounts().then((payload) => setAccounts(payload.accounts)).catch((error) => setAccountsError(error instanceof Error ? error.message : "We could not refresh accounts.")).finally(() => setAccountsLoading(false)); }}><RefreshCw size={16} /> Refresh accounts</button></section></div></main>;
}
