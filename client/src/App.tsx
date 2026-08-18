import { Toaster } from "@/components/ui/sonner";
import { lazy, Suspense } from "react";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
const Dashboard = lazy(() => import("@/pages/Dashboard"));
const StaffNotifications = lazy(() => import("@/pages/StaffNotifications"));
const StaffApplications = lazy(() => import("@/pages/StaffApplications"));
const AdminDashboard = lazy(() => import("@/pages/AdminDashboard"));
const RoleRedirect = lazy(() => import("@/pages/RoleRedirect"));
const AuthPage = lazy(() => import("@/pages/AuthPage"));
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";

function Router() {
  return <Suspense fallback={<main className="route-state"><div className="container"><span className="eyebrow">Loading workspace</span><h1>Preparing your<br /><em>next step.</em></h1><p>Please give us a moment.</p></div></main>}><Switch>
    <Route path="/sign-in" component={AuthPage} />
    <Route path="/create-account" component={AuthPage} />
    <Route path="/forgot-password" component={AuthPage} />
    <Route path="/reset-password" component={AuthPage} />
    <Route path="/dashboard" component={RoleRedirect} />
    <Route path="/dashboard/end-user" component={Dashboard} />
    <Route path="/staff" component={StaffApplications} />
    <Route path="/staff/notifications" component={StaffNotifications} />
    <Route path="/staff/applications" component={StaffApplications} />
    <Route path="/admin" component={AdminDashboard} />
    <Route path="/" component={Home} />
    <Route path="/opportunities" component={Home} />
    <Route path="/how-it-works" component={Home} />
    <Route path="/why-us" component={Home} />
    <Route path="/guest/claim" component={Home} />
    <Route path="/guest/status" component={Home} />
    <Route path="/applicant-responsibility" component={Home} />
    <Route path="/policies" component={Home} />
    <Route path="/opportunities/:slug" component={Home} />
    <Route path="/apply/:slug" component={Home} />
    <Route path="/404" component={NotFound} />
    <Route component={NotFound} />
  </Switch></Suspense>;
}

function App() {
  return <ErrorBoundary><ThemeProvider defaultTheme="light"><TooltipProvider><Toaster /><Router /></TooltipProvider></ThemeProvider></ErrorBoundary>;
}

export default App;
