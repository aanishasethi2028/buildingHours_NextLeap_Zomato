import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export default function SearchCard({ onSearch, loading }) {
  const [locations, setLocations] = useState(["Indiranagar", "Mumbai", "Delhi", "Bangalore"]);
  const [location, setLocation] = useState("Indiranagar");
  const [cuisine, setCuisine] = useState("Italian");
  const [rating, setRating] = useState(4.2);
  const [prefs, setPrefs] = useState("");
  const [budget, setBudget] = useState("medium");
  const [customCuisine, setCustomCuisine] = useState("");
  const [showCustomCuisineInput, setShowCustomCuisineInput] = useState(false);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/locations`)
      .then(res => {
        if (res.data.locations && res.data.locations.length > 0) {
          setLocations(res.data.locations);
          // Find Indiranagar or select first
          const target = res.data.locations.find(loc => loc.toLowerCase().includes("indiranagar"));
          if (target) {
            setLocation(target);
          } else {
            setLocation(res.data.locations[0]);
          }
        }
      })
      .catch(err => console.error(err));
  }, []);

  const handleSearch = () => {
    const finalCuisine = showCustomCuisineInput && customCuisine ? customCuisine : cuisine;
    onSearch({ location, cuisine: finalCuisine, min_rating: rating, additional_preferences: prefs, budget });
  };

  const handleCuisineClick = (c) => {
    setCuisine(c);
    setShowCustomCuisineInput(false);
  };

  // Cuisine pills data matching screen1.png
  const cuisinePills = ["North Indian", "South Indian", "Biryani", "Street Food", "Italian"];

  return (
    <div className="bg-surface shadow-ambient" style={{
      maxWidth: '920px',
      margin: '40px auto var(--spacing-xxl) auto',
      padding: '48px',
      borderRadius: '28px',
      position: 'relative',
      overflow: 'hidden',
      border: '1px solid rgba(226, 55, 68, 0.05)',
      backgroundColor: '#ffffff'
    }}>
      {/* Top Left Sparkle Icon */}
      <div style={{
        position: 'absolute',
        top: '40px',
        left: '40px',
        width: '42px',
        height: '42px',
        borderRadius: '50%',
        backgroundColor: '#FFEBEF',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C12 2 12.5 7.5 18 12C12.5 12.5 12 18 12 18C12 18 11.5 12.5 6 12C11.5 11.5 12 2 12 2Z" fill="#b7122a"/>
          <path d="M7 6C7 6 7.15 7.85 9 9C7.15 9.15 7 11 7 11C7 11 6.85 9.15 5 9C6.85 8.85 7 6 7 6Z" fill="#b7122a" opacity="0.6"/>
        </svg>
      </div>

      {/* Top Right Serving Dome Cloche SVG Illustration */}
      <div style={{
        position: 'absolute',
        top: '20px',
        right: '24px',
        pointerEvents: 'none',
        display: 'block'
      }}>
        <svg width="180" height="150" viewBox="0 0 180 150" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M40 90C40 60 70 40 100 45C130 50 150 70 145 95C140 120 110 125 90 125C70 125 40 120 40 90Z" fill="#FFF5F5" opacity="0.6" filter="blur(10px)"/>
          <circle cx="125" cy="22" r="4" fill="#818CF8" />
          <path d="M142.5 35.5L144.1 38.8L147.7 39.3L145.1 41.8L145.7 45.4L142.5 43.7L139.3 45.4L139.9 41.8L137.3 39.3L140.9 38.8L142.5 35.5Z" fill="#FBBF24" />
          <path d="M101.5 28C99.5 25.5 96.5 25.5 94.5 27.5C92.5 29.5 92.5 32.5 94.5 34.5L101.5 41.5L108.5 34.5C110.5 32.5 110.5 29.5 108.5 27.5C106.5 25.5 103.5 25.5 101.5 28Z" fill="#EF4444" />
          <path d="M148 57C148 50 155 46 155 46C155 46 156 53 151 57C149.5 58.2 148 57.5 148 57Z" fill="#34D399" />
          <circle cx="114" cy="74" r="2" fill="#A7F3D0" />
          <circle cx="91" cy="58" r="3" fill="#C7D2FE" />
          
          <ellipse cx="100" cy="115" rx="50" ry="6" fill="#E2E8F0" opacity="0.8"/>
          
          <path d="M46 110C46 109 48 107 55 107H145C152 107 154 109 154 110C154 111.5 148 114 100 114C52 114 46 111.5 46 110Z" fill="#CBD5E1"/>
          <path d="M50 108.5C50 108 52 107 58 107H142C148 107 150 108 150 108.5C150 109.5 144 111.5 100 111.5C56 111.5 50 109.5 50 108.5Z" fill="#E2E8F0"/>
          
          <path d="M53 105C53 70 74 61 100 61C126 61 147 70 147 105H53Z" fill="url(#cloche-grad)"/>
          
          <circle cx="100" cy="56" r="5" fill="#CBD5E1"/>
          <circle cx="100" cy="56" r="3" fill="#E2E8F0"/>
          <path d="M98 59.5H102V61.5H98V59.5Z" fill="#94A3B8"/>
          <path d="M60 95C60 78 71 70 85 66.5" stroke="#FFFFFF" strokeWidth="2.5" strokeLinecap="round" opacity="0.4"/>
          
          <defs>
            <linearGradient id="cloche-grad" x1="100" y1="61" x2="100" y2="105" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#F8FAFC"/>
              <stop offset="70%" stopColor="#E2E8F0"/>
              <stop offset="100%" stopColor="#CBD5E1"/>
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Heading Text */}
      <div style={{ marginTop: '36px', marginBottom: '36px' }}>
        <h1 style={{
          fontSize: '44px',
          fontWeight: '800',
          color: '#1a1c1c',
          lineHeight: '1.2',
          letterSpacing: '-1.5px',
          marginBottom: '8px',
          fontFamily: 'var(--font-family)'
        }}>
          Discover your<br />
          <span style={{
            background: 'linear-gradient(90deg, #b7122a 0%, #3b82f6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            next craving
          </span>
        </h1>
        <p style={{
          fontSize: '15px',
          color: 'var(--text-muted)',
          fontWeight: '500'
        }}>
          Let AI curate the perfect dining experience for you.
        </p>
      </div>

      {/* Form Fields Stack */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        {/* ROW 1: LOCATION */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '20px',
          paddingBottom: '24px',
          borderBottom: '1px solid #F1F5F9'
        }}>
          {/* Blue Pin Icon Circle */}
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '50%',
            backgroundColor: '#EFF6FF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
          </div>
          {/* Label + Input Selector */}
          <div style={{ display: 'flex', alignItems: 'center', flexGrow: 1, gap: '32px' }}>
            <div style={{
              fontSize: '14px',
              fontWeight: '700',
              color: '#1a1c1c',
              minWidth: '80px'
            }}>
              Location
            </div>
            <div style={{ flexGrow: 1, position: 'relative' }}>
              <select
                value={location}
                onChange={e => setLocation(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px 24px',
                  borderRadius: '9999px',
                  border: '1px solid #E2E8F0',
                  backgroundColor: '#ffffff',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#1a1c1c',
                  appearance: 'none',
                  cursor: 'pointer',
                  outline: 'none',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.02)'
                }}
              >
                {locations.map(loc => <option key={loc} value={loc}>{loc}</option>)}
              </select>
              <div style={{ position: 'absolute', right: '20px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2.5" strokeLinecap="round">
                  <path d="M6 9l6 6 6-6"/>
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* ROW 2: CUISINE */}
        <div style={{
          display: 'flex',
          gap: '20px',
          paddingBottom: '24px',
          borderBottom: '1px solid #F1F5F9'
        }}>
          {/* Orange Fork & Knife Icon Circle */}
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '50%',
            backgroundColor: '#FFF7ED',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            marginTop: '2px'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#EA580C" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 3v7a6 6 0 0 0 5 5.92m3-.92V3m6 0v4c0 1.66-1.34 3-3 3M12 21v-6m0 0H4h16v6" />
            </svg>
          </div>
          {/* Label + Chips stack */}
          <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
            <div style={{
              fontSize: '14px',
              fontWeight: '700',
              color: '#1a1c1c',
              marginBottom: '12px'
            }}>
              Cuisine
            </div>
            
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '8px' }}>
              {cuisinePills.map(cp => {
                const isSelected = cuisine === cp && !showCustomCuisineInput;
                return (
                  <button
                    key={cp}
                    onClick={() => handleCuisineClick(cp)}
                    style={{
                      padding: '10px 20px',
                      borderRadius: '9999px',
                      border: isSelected ? '1px solid var(--primary)' : '1px solid #E2E8F0',
                      backgroundColor: isSelected ? '#FFF1F2' : '#ffffff',
                      color: isSelected ? 'var(--primary)' : '#64748B',
                      fontSize: '13px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      transition: 'all 0.2s ease',
                      outline: 'none'
                    }}
                  >
                    {cp}
                    {isSelected && (
                      <span style={{
                        width: '16px',
                        height: '16px',
                        borderRadius: '50%',
                        backgroundColor: 'var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#ffffff',
                        fontSize: '10px'
                      }}>
                        ✓
                      </span>
                    )}
                  </button>
                );
              })}
              
              {/* Custom Cuisine Pill Toggle */}
              <button
                onClick={() => setShowCustomCuisineInput(true)}
                style={{
                  padding: '10px 20px',
                  borderRadius: '9999px',
                  border: showCustomCuisineInput ? '1px solid var(--primary)' : '1px solid #E2E8F0',
                  backgroundColor: showCustomCuisineInput ? '#FFF1F2' : '#ffffff',
                  color: showCustomCuisineInput ? 'var(--primary)' : '#64748B',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'all 0.2s ease',
                  outline: 'none'
                }}
              >
                Other...
                {showCustomCuisineInput && (
                  <span style={{
                    width: '16px',
                    height: '16px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ffffff',
                    fontSize: '10px'
                  }}>
                    ✓
                  </span>
                )}
              </button>
            </div>

            {/* Custom Cuisine Input box when toggled */}
            {showCustomCuisineInput && (
              <div style={{ marginTop: '8px', width: '100%' }}>
                <input
                  type="text"
                  placeholder="Type another cuisine (e.g. Japanese, Mexican...)"
                  value={customCuisine}
                  onChange={e => setCustomCuisine(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 18px',
                    borderRadius: '9999px',
                    border: '1px solid var(--primary)',
                    fontSize: '13px',
                    fontWeight: '500',
                    outline: 'none'
                  }}
                  autoFocus
                />
              </div>
            )}
          </div>
        </div>

        {/* ROW 3: BUDGET */}
        <div style={{
          display: 'flex',
          gap: '20px',
          paddingBottom: '24px',
          borderBottom: '1px solid #F1F5F9'
        }}>
          {/* Green Wallet Icon Circle */}
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '50%',
            backgroundColor: '#F0FDF4',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            marginTop: '2px'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16A34A" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="4" width="20" height="16" rx="2" ry="2"/>
              <line x1="12" y1="12" x2="20" y2="12"/>
            </svg>
          </div>
          {/* Label + Budget Chips */}
          <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
            <div style={{
              fontSize: '14px',
              fontWeight: '700',
              color: '#1a1c1c',
              marginBottom: '12px'
            }}>
              Budget
            </div>
            
            <div style={{ display: 'flex', gap: '12px' }}>
              {['low', 'medium', 'high'].map(b => {
                const isSelected = budget === b;
                return (
                  <button
                    key={b}
                    onClick={() => setBudget(b)}
                    style={{
                      flex: 1,
                      padding: '12px',
                      borderRadius: '9999px',
                      border: isSelected ? '1px solid var(--primary)' : '1px solid #E2E8F0',
                      backgroundColor: isSelected ? '#FFF1F2' : '#ffffff',
                      color: isSelected ? 'var(--primary)' : '#64748B',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                      textTransform: 'capitalize',
                      transition: 'all 0.2s ease',
                      outline: 'none'
                    }}
                  >
                    <span style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: isSelected ? 'var(--primary)' : '#CBD5E1',
                      display: 'inline-block'
                    }} />
                    {b}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* ROW 4: PREFERENCES & MIN RATING */}
        <div style={{
          display: 'flex',
          gap: '20px'
        }}>
          {/* Yellow Star Icon Circle */}
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '50%',
            backgroundColor: '#FEF9C3',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            marginTop: '2px'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#CA8A04" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          {/* Label + Controls (Rating & Preferences) */}
          <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
            <div style={{
              fontSize: '14px',
              fontWeight: '700',
              color: '#1a1c1c',
              marginBottom: '12px'
            }}>
              Preferences &amp; Minimum Rating
            </div>
            
            <div style={{
              display: 'flex',
              gap: '16px',
              alignItems: 'center',
              flexWrap: 'wrap'
            }}>
              {/* Rating Control (Box with value and slider) */}
              <div style={{
                borderRadius: '16px',
                border: '1px solid #E2E8F0',
                padding: '12px 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                flex: '1 1 300px',
                backgroundColor: '#ffffff'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="#FFBA00" stroke="#FFBA00">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                  <div>
                    <div style={{ fontSize: '15px', fontWeight: '800', color: '#1a1c1c' }}>
                      {rating.toFixed(1)}+
                    </div>
                    <div style={{ fontSize: '10px', fontWeight: '500', color: '#64748B', whiteSpace: 'nowrap' }}>
                      Minimum Rating
                    </div>
                  </div>
                </div>
                {/* Slider */}
                <input
                  type="range"
                  min="0"
                  max="5"
                  step="0.1"
                  value={rating}
                  onChange={e => setRating(parseFloat(e.target.value))}
                  className="rating-slider"
                  style={{
                    flexGrow: 1,
                    background: `linear-gradient(to right, #b7122a 0%, #b7122a ${(rating / 5) * 100}%, #E2E8F0 ${(rating / 5) * 100}%, #E2E8F0 100%)`
                  }}
                />
              </div>

              {/* Preferences Text Input */}
              <div style={{
                flex: '2 1 350px',
                borderRadius: '9999px',
                border: '1px solid #E2E8F0',
                padding: '12px 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                backgroundColor: '#ffffff'
              }}>
                {/* Search Magnifying Glass Icon */}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                  <circle cx="11" cy="11" r="8"/>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
                {/* Text input */}
                <input
                  type="text"
                  placeholder="e.g., Spicy food, quiet atmosphere, romantic lighting..."
                  value={prefs}
                  onChange={e => setPrefs(e.target.value)}
                  style={{
                    width: '100%',
                    border: 'none',
                    outline: 'none',
                    fontSize: '13px',
                    fontWeight: '500',
                    color: '#1a1c1c',
                    backgroundColor: 'transparent'
                  }}
                />
                {/* Sliders settings icon */}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, cursor: 'pointer' }}>
                  <line x1="4" y1="21" x2="4" y2="14" />
                  <line x1="4" y1="10" x2="4" y2="3" />
                  <line x1="12" y1="21" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12" y2="3" />
                  <line x1="20" y1="21" x2="20" y2="16" />
                  <line x1="20" y1="12" x2="20" y2="3" />
                  <line x1="1" y1="14" x2="7" y2="14" />
                  <line x1="9" y1="8" x2="15" y2="8" />
                  <line x1="17" y1="16" x2="23" y2="16" />
                </svg>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Find My Table Button */}
      <div style={{ marginTop: '40px' }}>
        <button
          onClick={handleSearch}
          disabled={loading}
          style={{
            width: '100%',
            padding: '16px 24px',
            borderRadius: '12px',
            border: 'none',
            background: loading ? '#CBD5E1' : 'linear-gradient(90deg, #E23744 0%, #9D1C7F 100%)',
            color: loading ? '#64748B' : '#ffffff',
            fontSize: '16px',
            fontWeight: '700',
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
            boxShadow: loading ? 'none' : '0 4px 20px rgba(226, 55, 68, 0.2)',
            transition: 'transform 0.2s ease, opacity 0.2s ease',
            outline: 'none',
            opacity: loading ? 0.8 : 1
          }}
          onMouseDown={e => { if(!loading) e.currentTarget.style.transform = 'scale(0.985)'; }}
          onMouseUp={e => { if(!loading) e.currentTarget.style.transform = 'scale(1)'; }}
          onMouseEnter={e => { if(!loading) e.currentTarget.style.opacity = '0.92'; }}
          onMouseLeave={e => {
            if(!loading) {
              e.currentTarget.style.opacity = '1';
              e.currentTarget.style.transform = 'scale(1)';
            }
          }}
        >
          {/* Sparkles icon inside button */}
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C12 2 12.5 7.5 18 12C12.5 12.5 12 18 12 18C12 18 11.5 12.5 6 12C11.5 11.5 12 2 12 2Z" fill={loading ? "#64748B" : "#ffffff"}/>
            <path d="M6 6C6 6 6.1 7.4 7.5 8.5C6.1 8.6 6 10 6 10C6 10 5.9 8.6 4.5 8.5C5.9 8.4 6 6 6 6Z" fill={loading ? "#64748B" : "#ffffff"} opacity="0.7"/>
          </svg>
          {loading ? 'Finding Your Table...' : 'Find My Table'}
        </button>
      </div>

      {/* Shield check note */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px',
        marginTop: '16px'
      }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <path d="M9 11l2 2 4-4" />
        </svg>
        <span style={{ fontSize: '11px', fontWeight: '600', color: '#64748B' }}>
          Personalized recommendations in seconds
        </span>
      </div>

    </div>
  );
}
