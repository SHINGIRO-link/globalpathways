import { useEffect, useState } from "react";
import { Link } from "wouter";
import { Bell, CheckCheck, ChevronLeft, Inbox, Loader2, MoreHorizontal, SlidersHorizontal, Trash2 } from "lucide-react";
import { useAuth } from "@/_core/hooks/useAuth";
import { archiveStaffNotification, getStaffNotifications, markAllStaffNotificationsRead, markStaffNotificationRead, type StaffNotification } from "@/lib/api";
import AccountControls from "@/components/AccountControls";

const FILTERS = [
  { value: "all", label: "All alerts" },
  { value: "unread", label: "Unread" },
  { value: "application_submitted", label: "Applications" },
  { value: "application_status", label: "Status changes" },
  { value: "payment_status", label: "Payments" },
] as const;

export default function StaffNotifications() {
  const { user, loading: authLoading } = useAuth();
  const [filter, setFilter] = useState<(typeof FILTERS)[number]["value"]>("all");
  const [notifications, setNotifications] = useState<StaffNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [workingId, setWorkingId] = useState<number | null>(null);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const result = filter === "unread" ? await getStaffNotifications({ read: "unread" }) : await getStaffNotifications({ event_type: filter === "all" ? undefined : filter });
      setNotifications(result.notifications);
      setUnreadCount(result.unread_count);
    } catch {
      setError("The notification center is not available yet. Check the Django API connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (user?.role === "staff" || user?.role === "admin") void load(); }, [filter, user?.role]);

  if (authLoading) return <main className="route-state"><div className="container"><Loader2 className="spin" /><span className="eyebrow">Checking access</span><h1>Preparing your<br /><em>staff space.</em></h1></div></main>;
  if (!user) return <main className="route-state"><div className="container"><span className="eyebrow">Staff access</span><h1>Sign in to view<br /><em>team alerts.</em></h1><p>Staff notifications are available to authenticated team members only.</p><Link href="/" className="button button-dark">Back home</Link></div></main>;
  if (user.role !== "staff" && user.role !== "admin") return <main className="route-state"><div className="container"><span className="eyebrow">Private workspace</span><h1>This view is for<br /><em>staff only.</em></h1><p>Your applicant account does not have staff notification permissions.</p><Link href="/dashboard/end-user" className="button button-dark">Open my dashboard</Link></div></main>;

  async function markRead(notification: StaffNotification) {
    setWorkingId(notification.id);
    try {
      await markStaffNotificationRead(notification.id, !notification.is_read);
      setNotifications((items) => items.map((item) => item.id === notification.id ? { ...item, is_read: !item.is_read } : item));
      setUnreadCount((count) => Math.max(0, count + (notification.is_read ? 1 : -1)));
    } catch { setError("We could not update this alert. Please try again."); } finally { setWorkingId(null); }
  }

  async function archive(notification: StaffNotification) {
    setWorkingId(notification.id);
    try { await archiveStaffNotification(notification.id); setNotifications((items) => items.filter((item) => item.id !== notification.id)); if (!notification.is_read) setUnreadCount((count) => Math.max(0, count - 1)); }
    catch { setError("We could not archive this alert. Please try again."); } finally { setWorkingId(null); }
  }

  async function markAllRead() {
    try { await markAllStaffNotificationsRead(); setNotifications((items) => items.map((item) => ({ ...item, is_read: true }))); setUnreadCount(0); }
    catch { setError("We could not mark all alerts as read. Please try again."); }
  }

  return <main className="staff-notifications-page"><div className="container"><AccountControls />
    <Link href="/" className="back-link"><ChevronLeft size={16} /> Back home</Link>
    <div className="staff-heading"><div><span className="eyebrow">Staff workspace</span><h1>Stay close to<br /><em>every next step.</em></h1><p>Review application, status, and payment activity from one calm operational view.</p></div><div className="unread-card"><Bell size={18} /><strong>{unreadCount}</strong><span>unread alerts</span></div><Link href="/staff/applications" className="button button-primary compact">Review applications</Link></div>
    <div className="notification-toolbar"><div className="filter-label"><SlidersHorizontal size={15} /> Filter alerts</div><div className="notification-filters">{FILTERS.map((item) => <button key={item.value} className={filter === item.value ? "filter-chip active" : "filter-chip"} onClick={() => setFilter(item.value)}>{item.label}</button>)}</div><button className="button button-outline compact" onClick={markAllRead} disabled={!unreadCount}><CheckCheck size={15} /> Mark all read</button></div>
    {error && <div className="inline-error" role="alert"><span>{error}</span><button className="button button-outline compact" onClick={() => void load()}>Retry loading</button></div>}
    {loading ? <div className="notification-empty"><Loader2 className="spin" /><p>Loading staff alerts…</p></div> : notifications.length === 0 ? <div className="notification-empty"><Inbox size={28} /><h2>Nothing needs your attention.</h2><p>New application and payment activity will appear here.</p></div> : <div className="notification-list">{notifications.map((notification) => <article key={notification.id} className={notification.is_read ? "notification-item read" : "notification-item unread"}><div className="notification-icon"><Bell size={17} /></div><div className="notification-copy"><div className="notification-meta"><span>{notification.event_type_label}</span><time>{new Date(notification.created_at).toLocaleString()}</time></div><h2>{notification.title}</h2><p>{notification.message}</p>{notification.application_name && <small>Applicant: {notification.application_name}</small>}</div><div className="notification-actions"><button title={notification.is_read ? "Mark unread" : "Mark read"} aria-label={notification.is_read ? `Mark ${notification.title} unread` : `Mark ${notification.title} read`} onClick={() => markRead(notification)} disabled={workingId === notification.id}>{workingId === notification.id ? <Loader2 className="spin" size={15} /> : <CheckCheck size={15} />}</button><button title="Archive alert" aria-label={`Archive ${notification.title}`} onClick={() => archive(notification)} disabled={workingId === notification.id}><Trash2 size={15} /></button><MoreHorizontal size={17} className="muted-icon" aria-hidden="true" /></div></article>)}</div>}
  </div></main>;
}
