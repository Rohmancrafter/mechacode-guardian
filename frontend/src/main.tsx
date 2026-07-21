import './i18n/index';   // Initialise i18n before rendering
import React from 'react';
import ReactDOM from 'react-dom/client';
import DiagnosisPage from './pages/DiagnosisPage';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <DiagnosisPage />
  </React.StrictMode>,
);
