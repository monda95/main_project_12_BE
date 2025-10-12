import type { PropsWithChildren } from 'react';
import { I18nextProvider } from 'react-i18next';

import { ApiContextProvider } from '../services/ApiContext';
import { QueryClientProvider } from '../services/QueryClientProvider';
import { initI18n } from '../i18n';

const i18n = initI18n();

export const AppProviders = ({ children }: PropsWithChildren) => {
  return (
    <I18nextProvider i18n={i18n}>
      <QueryClientProvider>
        <ApiContextProvider>{children}</ApiContextProvider>
      </QueryClientProvider>
    </I18nextProvider>
  );
};
