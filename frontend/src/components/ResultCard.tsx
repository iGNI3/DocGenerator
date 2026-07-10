import React from 'react';
import { Download } from 'lucide-react';

interface ResultCardProps {
  data: {
    plan: {
      doc_type: string;
      title: string;
      assumptions: string[];
    };
    reflection_notes: string[];
    summary: string;
    document_url: string;
  };
}

const API_BASE = import.meta.env.VITE_API_URL || '';

export const ResultCard: React.FC<ResultCardProps> = ({ data }) => {
  const { plan, reflection_notes, document_url } = data;
  const fullDocumentUrl = document_url.startsWith('http') ? document_url : `${API_BASE}${document_url}`;

  return (
    <div className="result-doc">
      <div className="result-doc-header">
        <div>
          <div className="doc-meta">DOCUMENT TYPE: {plan.doc_type}</div>
          <h2 className="doc-title">{plan.title}</h2>
        </div>
        <a href={fullDocumentUrl} download className="btn-download">
          <Download size={14} />
          DOWNLOAD DOCX
        </a>
      </div>

      <div className="doc-section">
        <div className="doc-section-title">01. EXECUTIVE SUMMARY</div>
        <p style={{fontFamily: 'var(--font-serif)', fontSize: '1.1rem', lineHeight: '1.6'}}>
          {data.summary}
        </p>
      </div>

      {plan.assumptions.length > 0 && (
        <div className="doc-section">
          <div className="doc-section-title">02. SYSTEM ASSUMPTIONS</div>
          <ul className="doc-list">
            {plan.assumptions.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </div>
      )}

      {reflection_notes.length > 0 && (
        <div className="doc-section">
          <div className="doc-section-title" style={{color: '#d9534f'}}>03. REFLECTION WARNINGS (AUTO-CORRECTED)</div>
          <ul className="doc-list" style={{color: '#d9534f'}}>
            {reflection_notes.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
