import { useEffect, useState } from "react";
import { Download, FileDown, FileText, Loader2, RefreshCw, Search, ShieldCheck } from "lucide-react";
import { Link } from "wouter";
import { useAuth } from "@/_core/hooks/useAuth";
import { getStaffApplications, getStaffApplicationsExportUrl, getStaffDocumentsExportUrl, updateStaffApplicationStatus, updateStaffPaymentStatus, type StaffApplication, type StaffApplicationsResponse } from "@/lib/api";

const money = (amount: number, currency: string) => `${amount.toLocaleString()} ${currency}`;

export default function StaffApplications() {
  const { user, loading: authLoading } = useAuth();
  const [data, setData] = useState<StaffApplicationsResponse | null>(null);
  const [selected, setSelected] = useState<StaffApplication | null>(null);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [paymentStatus, setPaymentStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [working, setWorking] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const result = await getStaffApplications({ q, status, payment_status: paymentStatus });
      setData(result);
      setSelected((current) => current ? result.applications.find((item) => item.id === current.id) || current : result.applications[0] || null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "The staff application workspace is unavailable.");
    } finally { setLoading(false); }
  }

  useEffect(() => { if (user?.role === "admin") void load(); }, [user?.role, status, paymentStatus]);

  async function changeApplicationStatus(nextStatus: string) {
    if (!selected) return;
    setWorking(true);
    try {
      const updated = await updateStaffApplicationStatus(selected.id, nextStatus);
      setSelected(updated);
      setData((current) => current ? { ...current, applications: current.applications.map((item) => item.id === updated.id ? updated : item) } : current);
    } catch { setError("We could not update this application status. Please try again."); } finally { setWorking(false); }
  }

  async function changePaymentStatus(nextStatus: string) {
    if (!selected?.payment) return;
    setWorking(true);
    try {
      const updated = await updateStaffPaymentStatus(selected.payment.id, nextStatus);
      setSelected(updated);
      setData((current) => current ? { ...current, applications: current.applications.map((item) => item.id === updated.id ? updated : item) } : current);
    } catch { setError("We could not update this payment status. Please try again."); } finally { setWorking(false); }
  }

  if (authLoading) return <main className="route-state"><div className="container"><Loader2 className="spin" /><span className="eyebrow">Checking access</span><h1>Preparing your<br /><em>admin workspace.</em></h1></div></main>;
  if (!user) return <main className="route-state"><div className="container"><span className="eyebrow">Staff access</span><h1>Sign in to review<br /><em>applications.</em></h1><p>Application and payment records are available only to authenticated staff.</p><Link href="/" className="button button-dark">Back home</Link></div></main>;
  if (user.role !== "admin") return <main className="route-state"><div className="container"><span className="eyebrow">Private workspace</span><h1>This view is for<br /><em>staff only.</em></h1><p>Your account does not have permission to review applicant records.</p><Link href="/" className="button button-dark">Back home</Link></div></main>;

  return <main className="staff-applications-page"><div className="container">
    <Link href="/" className="back-link">← Back home</Link>
    <div className="staff-heading"><div><span className="eyebrow">Staff workspace</span><h1>Review every<br /><em>next step.</em></h1><p>Manage submissions, payment readiness, and applicant documents from one protected view.</p></div><div className="staff-security-card"><ShieldCheck size={20} /><div><strong>Staff-only access</strong><span>Records are protected by the authenticated staff session.</span></div></div></div>
    {data && <div className="staff-summary-grid"><div><span>Applications</span><strong>{data.summary.applications}</strong></div><div><span>Payment records</span><strong>{data.summary.payments}</strong></div><div><span>Pending payments</span><strong>{data.summary.pending_payments}</strong></div><div><span>Unread alerts</span><strong>{data.summary.unread_notifications}</strong></div></div>}
    <div className="staff-toolbar"><div className="staff-search"><Search size={16} /><input value={q} onChange={(event) => setQ(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void load(); }} placeholder="Search applicant, email, or opportunity" /></div><select value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All application statuses</option>{data?.statuses.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select><select value={paymentStatus} onChange={(event) => setPaymentStatus(event.target.value)}><option value="">All payment statuses</option>{data?.payment_statuses.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select><button className="button button-outline compact" onClick={() => void load()}><RefreshCw size={15} /> Refresh</button><a className="button button-primary compact" href={getStaffApplicationsExportUrl()} download><Download size={15} /> Download CSV</a><a className="button button-outline compact" href={getStaffDocumentsExportUrl()} download><FileDown size={15} /> Download all documents</a></div>
    {error && <div className="inline-error" role="alert"><span>{error}</span><button className="button button-outline compact" onClick={() => void load()}>Retry</button></div>}
    {loading ? <div className="notification-empty"><Loader2 className="spin" /><p>Loading application records…</p></div> : <div className="staff-review-layout"><section className="staff-application-list" aria-label="Application submissions">{data?.applications.length ? data.applications.map((application) => <button key={application.id} className={selected?.id === application.id ? "staff-application-row active" : "staff-application-row"} onClick={() => setSelected(application)}><span className="staff-row-status">{application.status_label}</span><strong>{application.full_name}</strong><span>{application.opportunity_title}</span><small>{application.email} · {new Date(application.created_at).toLocaleDateString()}</small></button>) : <div className="notification-empty"><FileText size={28} /><h2>No applications found.</h2><p>Try clearing the filters or wait for a new submission.</p></div>}</section><section className="staff-application-detail">{selected ? <ApplicationDetail application={selected} working={working} onApplicationStatus={changeApplicationStatus} onPaymentStatus={changePaymentStatus} /> : <div className="notification-empty"><FileText size={28} /><h2>Select an application.</h2><p>Choose a submission to review its details.</p></div>}</section></div>}
  </div></main>;
}

function ApplicationDetail({ application, working, onApplicationStatus, onPaymentStatus }: { application: StaffApplication; working: boolean; onApplicationStatus: (status: string) => void; onPaymentStatus: (status: string) => void }) {
  return <article className="staff-detail-card"><div className="staff-detail-top"><div><span className="eyebrow">Application #{application.id}</span><h2>{application.full_name}</h2><p>{application.opportunity_title} · submitted {new Date(application.created_at).toLocaleString()}</p></div><span className={`status-pill ${application.status}`}>{application.status_label}</span></div><div className="staff-detail-grid"><div><span>Email</span><strong>{application.email}</strong></div><div><span>Phone</span><strong>{application.phone || "Not provided"}</strong></div><div><span>Nationality</span><strong>{application.nationality || "Not provided"}</strong></div><div><span>Education</span><strong>{application.education_level || "Not provided"}</strong></div><div><span>Location</span><strong>{application.current_location || "Not provided"}</strong></div><div><span>Contact consent</span><strong>{application.consent_to_contact ? "Granted" : "Not granted"}</strong></div></div><div className="staff-detail-section"><span className="eyebrow">Statement</span><p className="staff-statement">{application.statement || "No statement provided."}</p></div><div className="staff-control-grid"><label>Application status<select value={application.status} disabled={working} onChange={(event) => onApplicationStatus(event.target.value)}><option value="payment_required">Payment required</option><option value="received">Received</option><option value="reviewing">Reviewing</option><option value="needs_info">Needs information</option><option value="approved">Approved</option><option value="rejected">Not approved</option></select></label>{application.payment && <label>Payment status<select value={application.payment.status} disabled={working} onChange={(event) => onPaymentStatus(event.target.value)}><option value="pending">Pending</option><option value="integration_pending">Integration pending</option><option value="paid">Paid</option><option value="failed">Failed</option></select></label>}</div>{application.payment && <div className="staff-payment-card"><div><span>Payment</span><strong>{money(application.payment.amount, application.payment.currency)}</strong><small>{application.payment.provider_label || "Provider not selected"} · {application.payment.status_label}</small></div><span className="status-pill">{application.payment.status_label}</span></div>}<div className="staff-detail-section"><div className="staff-section-heading"><span className="eyebrow">Documents</span><small>{application.documents.length} uploaded</small></div>{application.documents.length ? <div className="staff-documents">{application.documents.map((document) => <a className="staff-document-link" key={document.download_url} href={document.download_url} target="_blank" rel="noreferrer"><FileDown size={16} /><span>{document.name}<small>{document.category} · {(document.size / 1024).toFixed(0)} KB</small></span></a>)}</div> : <p className="form-help">No documents were uploaded with this application.</p>}</div></article>;
}
