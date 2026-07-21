// i18n initialisation — react-i18next (ARCHITECTURE.md §1.1)
//
// Supported languages:
//   id — Bahasa Indonesia (default per PRD §FR-08.1)
//   en — English
//
// Translation keys are kept flat for MVP simplicity.
// Dynamic LLM output language follows the server response (not overridden here).

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import id from './locales/id.json';
import en from './locales/en.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      id: { translation: id },
      en: { translation: en },
    },
    lng: 'id',          // Default: Bahasa Indonesia (PRD §FR-08.1)
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already escapes by default
    },
  });

export default i18n;
