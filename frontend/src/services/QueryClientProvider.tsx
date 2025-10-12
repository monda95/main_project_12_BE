import type { PropsWithChildren } from 'react';
import { QueryClient, QueryClientProvider as RQProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      staleTime: 60_000,
      gcTime: 5 * 60_000
    }
  }
});

export const QueryClientProvider = ({ children }: PropsWithChildren) => {
  return <RQProvider client={queryClient}>{children}</RQProvider>;
};
