import { useState, useEffect } from "react";
import { fetchHealth } from "../api";
import type { HealthStatus } from "../types";

const POLL_INTERVAL_MS = 30_000;

interface UseHealthReturn {
  health: HealthStatus | null;
  isOnline: boolean;
}

export function useHealth(): UseHealthReturn {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isOnline, setIsOnline] = useState<boolean>(false);

  useEffect(() => {
    let cancelled = false;

    async function check(): Promise<void> {
      try {
        const data = await fetchHealth();
        if (!cancelled) {
          setHealth(data as HealthStatus);
          setIsOnline(true);
        }
      } catch {
        if (!cancelled) {
          setHealth(null);
          setIsOnline(false);
        }
      }
    }

    void check();

    const interval = setInterval(() => {
      void check();
    }, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return { health, isOnline };
}
