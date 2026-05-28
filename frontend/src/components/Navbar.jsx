import React from 'react';
import { User } from 'lucide-react';

export default function Navbar() {
  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 'var(--spacing-md) var(--spacing-xxl)',
      backgroundColor: 'rgba(255, 255, 255, 0.85)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-subtle)',
      marginBottom: 'var(--spacing-xl)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: '0 4px 24px -12px rgba(0,0,0,0.05)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{
          fontSize: '36px',
          fontWeight: '800',
          color: '#E23744',
          letterSpacing: '-1.5px',
          fontStyle: 'italic',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}>
          zomato
        </div>
        <div style={{
          fontSize: '16px',
          fontWeight: '700',
          color: '#E23744',
          backgroundColor: '#FFF4F5',
          border: '1px solid #FFE4E6',
          padding: '4px 10px',
          borderRadius: '12px',
          letterSpacing: '0.5px'
        }}>
          AI
        </div>
      </div>
      <div style={{
        display: 'flex',
        gap: 'var(--spacing-lg)',
        alignItems: 'center',
        fontSize: '14px',
        fontWeight: '500',
        color: 'var(--text-muted)'
      }}>
        <span style={{ cursor: 'pointer' }}>Add Restaurant</span>
        <span style={{ cursor: 'pointer' }}>Log in</span>
        <span style={{ cursor: 'pointer' }}>Sign up</span>
        <div style={{
          backgroundColor: '#4B5563',
          color: 'white',
          borderRadius: '50%',
          width: '28px',
          height: '28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <User size={16} />
        </div>
      </div>
    </nav>
  );
}
