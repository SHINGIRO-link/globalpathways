import { Toaster } from "@/components/ui/sonner";
import { lazy, Suspense } from "react";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
const Dashboard = lazy(() => import("@/pages/Dashboard"));
const StaffNotifications = lazy(() => import("@/pages/StaffNotifications"));
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";

function Router() {
  return <Suspense fallback={<main className="route-state"><div className="container"><span className="eyebrow">Loading workspace</span><h1>Preparing your<br /><em>next step.</em></h1><p>Please give us a moment.</p></div></main>}><Switch>
    <Route path="/dashboard" component={Dashboard} />
    <Route path="/staff/notifications" component={StaffNotifications} />
    <Route path="/" component={Home} />
    <Route path="/opportunities" component={Home} />
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
