import { useState, useEffect, useCallback } from "react";

/**
 * useFetch Hook
 * 
 * Generic hook for fetching data from the API with loading and error states.
 */

interface UseFetchState<T> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
}

export function useFetch<T>(
  fetchFn: () => Promise<T>,
  dependencies: unknown[] = []
): UseFetchState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<UseFetchState<T>>({
    data: null,
    isLoading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState({ data: null, isLoading: true, error: null });
    try {
      const result = await fetchFn();
      setState({ data: result, isLoading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        isLoading: false,
        error: error instanceof Error ? error : new Error(String(error)),
      });
    }
  }, [fetchFn]);

  useEffect(() => {
    refetch();
  }, dependencies);

  return { ...state, refetch };
}
