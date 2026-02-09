import { useState, useEffect, useCallback } from "react";

interface UseFetchState<T> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
}

export function useFetch<T>(
  fetchFn: (signal?: AbortSignal) => Promise<T>,
  dependencies: unknown[] = [],
): UseFetchState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<UseFetchState<T>>({
    data: null,
    isLoading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const result = await fetchFn();
      setState({ data: result, isLoading: false, error: null });
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") return;
      setState({
        data: null,
        isLoading: false,
        error: error instanceof Error ? error : new Error(String(error)),
      });
    }
  }, [fetchFn]);

  useEffect(() => {
    const controller = new AbortController();

    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    fetchFn(controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) {
          setState({ data: result, isLoading: false, error: null });
        }
      })
      .catch((error) => {
        if (controller.signal.aborted) return;
        setState({
          data: null,
          isLoading: false,
          error: error instanceof Error ? error : new Error(String(error)),
        });
      });

    return () => controller.abort();
  }, dependencies);

  return { ...state, refetch };
}
