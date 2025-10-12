import type { PropsWithChildren } from 'react';
import { createContext, useContext, useMemo } from 'react';

import { createApiClient } from './apiClient';

const ApiContext = createContext<ReturnType<typeof createApiClient> | null>(null);

export const ApiContextProvider = ({ children }: PropsWithChildren) => {
  const client = useMemo(() => createApiClient(), []);

  return <ApiContext.Provider value={client}>{children}</ApiContext.Provider>;
};

export const useApiContext = () => {
  const ctx = useContext(ApiContext);

  if (!ctx) {
    throw new Error('ApiContext가 초기화되지 않았습니다.');
  }

  return ctx;
};
