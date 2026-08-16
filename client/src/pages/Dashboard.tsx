import { useEffect, useMemo, useState } from "react";
import { Link } from "wouter";
import { ArrowRight, Bookmark, Check, Clock3, CreditCard, Loader2, LockKeyhole, LogIn, RefreshCw, ShieldCheck } from "lucide-react";
import { startLogin } from "@/const";
import { useAuth } from "@/_core/hooks/useAuth";
import { getApplicationStatus, getDashboard, preparePayment, removeSavedOpportunity, type DashboardData } from "@/lib/api";

const statusSteps = ["payment_required", "received", "reviewing", "needs_info", "approved", "rejected"];

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function StatusTimeline({ email, applicationId, currentStatus }: { email: string; applicationId: number; currentStatus: string }) {
  const [events, setEvents] = useState<Array<{ id: number; status: string; status_label: string; note: string; created_at: string }>>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { getApplicationStatus(email, applicationId).then(result => setEvents(result.events)).catch(() => setEvents([])).finally(() => setLoading(false)); }, [email, applicationId]);
  const activeIndex = Math.max(statusSteps.indexOf(currentStatus), 0);
  return <div className="status-timeline">{loading ? <span className="timeline-loading"><Loader2 size={15} className="spin" /> Updating status…</span> : <>{statusSteps.map((step, index) => { const event = events.find(item => item.status === step); return <div className={index <= activeIndex ? "timeline-step active" : "timeline-step"} key={step}><span className="timeline-dot">{index <= activeIndex ? <Check size={12} /> : <span />}</span><div><strong>{event?.status_label || step.replace("_", " ")}</strong>{event && <small>{formatDate(event.created_at)}{event.note ? ` · ${event.note}` : ""}</small>}</div></div>; })}</>}</div>;
}

function PaymentReady({ email, applicationId, currentProvider }: { email: string; applicationId: number; currentProvider?: string }) {
  const [provider, setProvider] = useState<"momo" | "airtel">((currentProvider as "momo" | "airtel") || "momo");
  const [message, setMessage] = useState("");
  const [pending, setPending] = useState(false);
  async function chooseProvider() { setPending(true); setMessage(""); try { const result = await preparePayment(email, applicationId, provider); setMessage(result.message); } catch { setMessage("We could not save your provider choice yet. Please try again later."); } finally { setPending(false); } }
  return <div className="payment-ready"><div className="payment-ready-icon"><CreditCard size={19} /></div><div><span className="eyebrow">Next step · service fee</span><h4>Payment will be enabled here</h4><p>Your application is recorded. The 2,000 RWF service fee will be payable after MoMo or Airtel integration is connected.</p><div className="provider-row"><button className={provider === "momo" ? "provider active" : "provider"} onClick={() => setProvider("momo")}>MoMo</button><button className={provider === "airtel" ? "provider active" : "provider"} onClick={() => setProvider("airtel")}>Airtel Money</button><button className="button button-dark compact" onClick={chooseProvider} disabled={pending}>{pending ? "Saving…" : "Choose provider"}</button></div>{message && <small className="payment-note">{message}</small>}</div></div>;
}

export default function Dashboard() {
  const { user, loading: authLoading } = useAuth();
  const email = useMemo(() => user?.email || "", [user?.email]);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  async function loadDashboard() { if (!email) return; setLoading(true); setError(""); try { setDashboard(await getDashboard(email)); } catch { setError("We could not load your dashboard yet. Make sure the Django API is connected and try again."); } finally { setLoading(false); } }
  useEffect(() => { if (user?.email) loadDashboard(); }, [user?.email]);

  if (authLoading) return <main className="dashboard-page"><div className="dashboard-state"><Loader2 size={22} className="spin" /><p>Preparing your dashboard…</p></div></main>;
  if (!user) return <main className="dashboard-page"><div className="dashboard-access"><div className="dashboard-access-icon"><LockKeyhole size={22} /></div><span className="eyebrow">Your private workspace</span><h1>Keep every<br /><em>next step close.</em></h1><p>Sign in to track submitted applications and saved opportunities. Your dashboard is private to your signed-in account.</p><button className="button button-dark" onClick={() => startLogin()}><LogIn size={17} /> Sign in to continue</button></div></main>;

  return <main className="dashboard-page"><div className="container dashboard-wrap"><div className="dashboard-heading"><div><span className="eyebrow">Your Global Pathways workspace</span><h1>Keep moving<br /><em>with clarity.</em></h1><p>{email}</p></div><button className="button button-outline" onClick={loadDashboard} disabled={loading}><RefreshCw size={16} /> Refresh</button></div>{loading && <div className="dashboard-banner"><Loader2 size={15} className="spin" /> Refreshing your application status…</div>}{error && <div className="dashboard-error"><ShieldCheck size={17} /><span>{error}</span></div>}{dashboard && <><section className="dashboard-stats"><div><span>Applications</span><strong>{dashboard.applications.length}</strong></div><div><span>Saved routes</span><strong>{dashboard.saved_opportunities.length}</strong></div><div><span>Next action</span><strong>{dashboard.applications.some(item => item.status === "payment_required") ? "Payment" : "Review"}</strong></div></section><section className="dashboard-section"><div className="section-heading"><div><span className="eyebrow">Application tracker</span><h2>See where things stand.</h2></div><span className="secure-label"><ShieldCheck size={15} /> Private to you</span></div>{dashboard.applications.length === 0 ? <div className="dashboard-empty"><Clock3 size={22} /><h3>No submitted applications yet.</h3><p>When you submit an application, its status and next action will appear here.</p><Link href="/opportunities" className="button button-dark">Explore opportunities <ArrowRight size={16} /></Link></div> : <div className="application-list">{dashboard.applications.map(application => <article className="dashboard-application" key={application.id}><div className="application-topline"><div><span className="detail-category">Application · {application.opportunity_title}</span><h3>{application.status_label}</h3><p>Submitted {formatDate(application.created_at)}</p></div><span className={`status-pill ${application.status === "approved" ? "open" : "coming"}`}>{application.status_label}</span></div><StatusTimeline email={email} applicationId={application.id} currentStatus={application.status} />{application.status === "payment_required" && <PaymentReady email={email} applicationId={application.id} />}</article>)}</div>}</section><section className="dashboard-section"><div className="section-heading"><div><span className="eyebrow">Saved for later</span><h2>Your considered routes.</h2></div><Bookmark size={21} /></div>{dashboard.saved_opportunities.length === 0 ? <div className="dashboard-empty"><Bookmark size={22} /><h3>Your shortlist is waiting.</h3><p>Save an opportunity when you want to return with a clearer plan.</p><Link href="/opportunities" className="button button-outline">Browse the library <ArrowRight size={16} /></Link></div> : <div className="saved-grid">{dashboard.saved_opportunities.map(saved => <div className="saved-card" key={saved.id}><Link href={`/opportunities/${saved.opportunity_detail.slug}`} className="saved-card-link"><span className="detail-category">{saved.opportunity_detail.category_label} · {saved.opportunity_detail.country}</span><h3>{saved.opportunity_detail.title}</h3><p>{saved.opportunity_detail.summary}</p><span className="text-button dark-button">View route <ArrowRight size={15} /></span></Link><button className="unsave-button" onClick={async () => { await removeSavedOpportunity(email, saved.opportunity); setDashboard(current => current ? { ...current, saved_opportunities: current.saved_opportunities.filter(item => item.id !== saved.id) } : current); }}>Remove from saved</button></div>)}</div>}</section></>}</div></main>;
}
