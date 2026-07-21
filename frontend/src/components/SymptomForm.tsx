import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { DiagnoseRequest } from '../api/client';

interface SymptomFormProps {
  onSubmit: (request: DiagnoseRequest) => void;
  isLoading: boolean;
}

/**
 * SymptomForm — Equipment and symptom input (FR-01).
 *
 * Collects:
 *  - equipment_type (required)
 *  - manufacturer, model, alarm_code (optional)
 *  - symptom_text (required, min 5 chars)
 *  - language toggle (FR-08)
 */
const SymptomForm: React.FC<SymptomFormProps> = ({ onSubmit, isLoading }) => {
  const { t, i18n } = useTranslation();

  const [equipmentType, setEquipmentType] = useState('');
  const [manufacturer, setManufacturer] = useState('');
  const [model, setModel] = useState('');
  const [alarmCode, setAlarmCode] = useState('');
  const [symptomText, setSymptomText] = useState('');
  const [language, setLanguage] = useState<'id' | 'en'>('id');

  const handleLanguageToggle = () => {
    const next = language === 'id' ? 'en' : 'id';
    setLanguage(next);
    void i18n.changeLanguage(next);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!equipmentType.trim() || symptomText.trim().length < 5) return;

    onSubmit({
      equipment_type: equipmentType.trim(),
      manufacturer: manufacturer.trim() || undefined,
      model: model.trim() || undefined,
      alarm_code: alarmCode.trim() || undefined,
      symptom_text: symptomText.trim(),
      language,
    });
  };

  return (
    <form onSubmit={handleSubmit} aria-label={t('symptom.form.title')}>
      <h2 style={{ marginBottom: '1rem' }}>{t('symptom.form.title')}</h2>

      {/* Language toggle */}
      <div style={{ marginBottom: '1rem', textAlign: 'right' }}>
        <button type="button" onClick={handleLanguageToggle} style={{ cursor: 'pointer' }}>
          {t('nav.language')}: {language.toUpperCase()}
        </button>
      </div>

      {/* Equipment type */}
      <div style={{ marginBottom: '0.75rem' }}>
        <label htmlFor="equipment_type" style={{ display: 'block', marginBottom: '0.25rem' }}>
          {t('symptom.form.equipment_type')} *
        </label>
        <input
          id="equipment_type"
          type="text"
          value={equipmentType}
          onChange={e => setEquipmentType(e.target.value)}
          placeholder={t('symptom.form.equipment_type.placeholder')}
          required
          style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
        />
      </div>

      {/* Manufacturer */}
      <div style={{ marginBottom: '0.75rem' }}>
        <label htmlFor="manufacturer" style={{ display: 'block', marginBottom: '0.25rem' }}>
          {t('symptom.form.manufacturer')}
        </label>
        <input
          id="manufacturer"
          type="text"
          value={manufacturer}
          onChange={e => setManufacturer(e.target.value)}
          style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
        />
      </div>

      {/* Model */}
      <div style={{ marginBottom: '0.75rem' }}>
        <label htmlFor="model" style={{ display: 'block', marginBottom: '0.25rem' }}>
          {t('symptom.form.model')}
        </label>
        <input
          id="model"
          type="text"
          value={model}
          onChange={e => setModel(e.target.value)}
          style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
        />
      </div>

      {/* Alarm code */}
      <div style={{ marginBottom: '0.75rem' }}>
        <label htmlFor="alarm_code" style={{ display: 'block', marginBottom: '0.25rem' }}>
          {t('symptom.form.alarm_code')}
        </label>
        <input
          id="alarm_code"
          type="text"
          value={alarmCode}
          onChange={e => setAlarmCode(e.target.value)}
          style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
        />
      </div>

      {/* Symptom description */}
      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="symptom_text" style={{ display: 'block', marginBottom: '0.25rem' }}>
          {t('symptom.form.symptom_text')} *
        </label>
        <textarea
          id="symptom_text"
          value={symptomText}
          onChange={e => setSymptomText(e.target.value)}
          placeholder={t('symptom.form.symptom_text.placeholder')}
          required
          minLength={5}
          rows={4}
          style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box', resize: 'vertical' }}
        />
      </div>

      <button
        type="submit"
        disabled={isLoading || !equipmentType.trim() || symptomText.trim().length < 5}
        style={{ padding: '0.625rem 1.5rem', cursor: 'pointer' }}
      >
        {isLoading ? t('symptom.form.submitting') : t('symptom.form.submit')}
      </button>
    </form>
  );
};

export default SymptomForm;
