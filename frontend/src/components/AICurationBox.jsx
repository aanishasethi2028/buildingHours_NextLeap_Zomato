import React from 'react';
import { Sparkles } from 'lucide-react';

export default function AICurationBox({ summary }) {
  if (!summary) return null;

  return (
    <div style={{
      backgroundColor: '#F8FAFC',
      border: '1px solid #E2E8F0',
      borderRadius: 'var(--rounded-md)',
      padding: 'var(--spacing-lg)',
      display: 'flex',
      gap: 'var(--spacing-md)',
      alignItems: 'flex-start',
      marginBottom: 'var(--spacing-xl)'
    }}>
      <div style={{
        width: '40px',
        height: '40px',
        backgroundColor: 'var(--white)',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        flexShrink: 0
      }}>
        <Sparkles size={20} color="var(--primary)" />
      </div>
      <div>
        <div style={{
          fontWeight: '700',
          fontSize: '16px',
          color: 'var(--on-surface)',
          marginBottom: '4px'
        }}>
          AI Curation Complete
        </div>
        <div style={{
          fontSize: '14px',
          color: 'var(--text-muted)',
          fontStyle: 'italic',
          lineHeight: '1.5'
        }}>
          "{summary}"
        </div>
      </div>
    </div>
  );
}
