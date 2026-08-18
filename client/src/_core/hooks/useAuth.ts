import { useCallback, useEffect, useState } from "react";
import { getCurrentUser, logoutAccount, notifyAuthChanged, type LocalUser } from "@/lib/auth";

export type UseAuthOptions = {
  redirectOnUnauthenticated?: boolean;
  redirectPath?: string;
};

export function useAuth(_options?: UseAuthOptions) {
  const [user, setUser] = useState<LocalUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setUser(await getCurrentUser());
      setError(null);
    } catch (caught) {
      setUser(null);
      setError(caught instanceof Error ? caught : new Error("Authentication is unavailable."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const listener = () => void refresh();
    window.addEventListener("globalpathways-auth-changed", listener);
    return () => window.removeEventListener("globalpathways-auth-changed", listener);
  }, [refresh]);

  const logout = useCallback(async () => {
    await logoutAccount();
    setUser(null);
    notifyAuthChanged();
  }, []);

  return {
    user,
    loading,
    error,
    isAuthenticated: Boolean(user),
    refresh,
    logout,
  };
}
