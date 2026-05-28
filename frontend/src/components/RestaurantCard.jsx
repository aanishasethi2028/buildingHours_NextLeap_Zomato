import React from 'react';

const getCuisineImage = (cuisine_str) => {
  const c = (cuisine_str || '').toLowerCase();
  if (c.includes("italian") || c.includes("pizza")) return "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=800&auto=format&fit=crop";
  if (c.includes("north indian") || c.includes("mughlai")) return "https://images.unsplash.com/photo-1585937421612-70a008356fbe?q=80&w=800&auto=format&fit=crop";
  if (c.includes("south indian")) return "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?q=80&w=800&auto=format&fit=crop";
  if (c.includes("kebab") || c.includes("frontier")) return "https://images.unsplash.com/photo-1603360946369-dc9bb6258143?q=80&w=800&auto=format&fit=crop";
  return "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800&auto=format&fit=crop";
};

export default function RestaurantCard({ item }) {
  const rest = item.restaurant || {};
  const rating = rest.rating ? rest.rating.toFixed(1) : "N/A";
  const imgUrl = getCuisineImage(rest.cuisine);

  return (
    <div className="rounded-card shadow-hover" style={{
      backgroundColor: 'var(--surface-container-lowest)',
      border: '1px solid var(--border-subtle)',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => { e.currentTarget.querySelector('img').style.transform = 'scale(1.05)' }}
    onMouseLeave={(e) => { e.currentTarget.querySelector('img').style.transform = 'scale(1)' }}
    >
      <div style={{ position: 'relative', height: '200px', overflow: 'hidden' }}>
        <img src={imgUrl} alt={rest.name} style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.4s ease' }} />
        <div style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          color: 'var(--on-surface)',
          fontSize: '12px',
          fontWeight: '700',
          padding: '4px 8px',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          {rating} <span style={{ color: 'var(--rating-gold)' }}>★</span>
        </div>
      </div>
      <div style={{ padding: 'var(--spacing-md)', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
        <h3 style={{ fontSize: '18px', fontWeight: '700', margin: '0 0 4px 0' }}>{rest.name}</h3>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '0 0 16px 0' }}>{rest.cuisine}</p>
        
        <div style={{
          backgroundColor: '#F9FAFB',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--rounded)',
          padding: '12px',
          fontSize: '12px',
          color: '#4B5563',
          fontStyle: 'italic',
          lineHeight: '1.5',
          marginTop: 'auto',
          position: 'relative'
        }}>
          <span style={{
            position: 'absolute',
            top: '-10px',
            left: '10px',
            backgroundColor: 'var(--white)',
            borderRadius: '50%',
            padding: '2px',
            fontSize: '12px'
          }}>✨</span>
          {item.explanation}
        </div>
      </div>
    </div>
  );
}
