import i18n, { type i18n as I18nInstance } from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  ko: {
    translation: {
      common: {
        loading: '로딩 중',
        retry: '다시 시도',
        empty: '표시할 데이터가 없습니다.',
        no_access: '권한이 없습니다.',
        error: '문제가 발생했습니다.'
      },
      home: {
        title: '음식·영양 AI 비서',
        search_placeholder: '예) 닭가슴살 샐러드 칼로리',
        submit: '질문하기',
        suggestions: '추천 질문',
        history: '최근 검색어',
        popular: '인기 검색어'
      }
    }
  }
};

export const initI18n = (): I18nInstance => {
  if (!i18n.isInitialized) {
    i18n.use(initReactI18next).init({
      resources,
      lng: import.meta.env.VITE_I18N_LOCALE || 'ko',
      fallbackLng: 'ko',
      defaultNS: 'translation',
      interpolation: {
        escapeValue: false
      }
    });
  }

  return i18n;
};
