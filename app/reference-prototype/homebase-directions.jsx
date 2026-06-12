// Homebase — home-screen direction explorations
// Shared shell, icons, sparkline + 3 home variants. Attaches to window.
const { useState } = React;

/* ---------------- Icons (lucide-ish, on-brand line weight) ---------------- */
const HB_PATHS = {
  today:    'M3 10.5 12 3l9 7.5M5 9v11a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9',
  sales:    'M3 3v18h18M7 14l3-3 3 3 5-6',
  labor:    'M16 18v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M9.5 8.5a3 3 0 1 0 0-.01M18 7v5M21 9.5h-6',
  inventory:'M3 7 12 3l9 4-9 4-9-4ZM3 7v8l9 4 9-4V7M12 11v8',
  equipment:'M14.5 6.5a3.5 3.5 0 0 0-4.6 4.6l-6 6a2 2 0 1 0 2.8 2.8l6-6a3.5 3.5 0 0 0 4.6-4.6l-2.2 2.2-2-2 2.2-2.2Z',
  members:  'M19 14c1.5-1.5 2-3 2-5a5 5 0 0 0-9-3 5 5 0 0 0-9 3c0 2 .5 3.5 2 5l7 7 7-7Z',
  feedback: 'M21 12a8 8 0 0 1-11.5 7.2L3 21l1.8-6.5A8 8 0 1 1 21 12Z',
  reports:  'M3 3v18h18M8 17V9M13 17V5M18 17v-6',
  settings: 'M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM19.4 13a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-2.9 1.2V21a2 2 0 1 1-4 0v-.1A1.7 1.7 0 0 0 7 19.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.7 1.7 0 0 0 3 13H3a2 2 0 1 1 0-4h.1A1.7 1.7 0 0 0 4.7 7L4.6 7a2 2 0 1 1 2.8-2.8l.1.1A1.7 1.7 0 0 0 10 4.7V4a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 2.9 1.2l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9v.2A1.7 1.7 0 0 0 21 11.9h.1a2 2 0 1 1 0 4H21a1.7 1.7 0 0 0-1.6 1.1Z',
  spark:    'M12 3l1.8 5.6L19 10l-5.2 1.4L12 17l-1.8-5.6L5 10l5.2-1.4L12 3Z',
  bell:     'M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9ZM10 21a2 2 0 0 0 4 0',
  search:   'M21 21l-4.5-4.5M3 11a8 8 0 1 0 16 0 8 8 0 0 0-16 0Z',
  arrow:    'M5 12h14M13 6l6 6-6 6',
  chev:     'M9 6l6 6-6 6',
  chevd:    'M6 9l6 6 6-6',
  check:    'M5 13l4 4 10-10',
  clock:    'M12 7v5l3 2M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z',
  alert:    'M12 9v4M12 17h.01M10.3 4 2.6 17a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 4a2 2 0 0 0-3.4 0Z',
  truck:    'M3 6h11v9H3zM14 9h4l3 3v3h-7M6.5 18.5a1.5 1.5 0 1 0 0-.01M17.5 18.5a1.5 1.5 0 1 0 0-.01',
  star:     'M12 3l2.7 6.2 6.7.6-5 4.5 1.5 6.6L12 17.9 6.1 21.4l1.5-6.6-5-4.5 6.7-.6Z',
  thermo:   'M14 14.8V5a2 2 0 1 0-4 0v9.8a4 4 0 1 0 4 0Z',
  arrowup:  'M12 19V5M6 11l6-6 6 6',
  arrowdn:  'M12 5v14M6 13l6 6 6-6',
  flame:    'M12 3c3 4 6 6 6 10a6 6 0 0 1-12 0c0-1.6.6-2.8 1.5-4 .4 1 1 1.7 2 2-.3-3 1-5.4 2.5-8Z',
  plus:     'M12 5v14M5 12h14',
};
const HBIcon = ({ name, size = 18, color = 'currentColor', stroke = 1.6 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
       strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
    <path d={HB_PATHS[name] || HB_PATHS.today} />
  </svg>
);

/* ---------------- Sparkline ---------------- */
const Spark = ({ pts, w = 96, h = 30, color = 'var(--db-lava-600)', fill = true, sw = 2 }) => {
  const max = Math.max(...pts), min = Math.min(...pts);
  const rng = max - min || 1;
  const step = w / (pts.length - 1);
  const xy = pts.map((p, i) => [i * step, h - ((p - min) / rng) * (h - 4) - 2]);
  const line = xy.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  const area = `${line} L${w} ${h} L0 ${h} Z`;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: 'block', overflow: 'visible' }}>
      {fill && <path d={area} fill={color} opacity="0.1" />}
      <path d={line} fill="none" stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={xy[xy.length - 1][0]} cy={xy[xy.length - 1][1]} r="2.6" fill={color} />
    </svg>
  );
};

/* ---------------- Shared day data ---------------- */
const DAY = {
  manager: 'Maya', store: 'Lakehouse Market', num: '#0417', hood: 'Fillmore · San Francisco',
  date: 'Friday, May 30',
  sales: { v: '$14,820', d: '+6.2%', up: true, spark: [9,11,10,13,12,14,13,15,14,16,15,17] },
  forecast: { v: '$16,400', sub: 'today · 91% conf.', spark: [12,13,12,14,15,14,16,15,17,16,18,17] },
  labor: { v: '24.8%', d: 'target 26%', up: false, spark: [27,26,27,25,26,25,24,25,24,25,24,25] },
  guest: { v: '4.3', d: 'NPS 41', up: true, spark: [4.0,4.1,4.0,4.2,4.1,4.3,4.2,4.4,4.3,4.2,4.3,4.3] },
  traffic: { v: '612', d: '+38 vs LW', up: true },
  modules: [
    { id: 'labor', icon: 'labor', name: 'Labor', sig: '3 timecards flagged', detail: '$1,240 OT this week · 2 missed breaks', cta: 'Approve', count: 3, level: 'warn' },
    { id: 'inventory', icon: 'inventory', name: 'Reorders', sig: '2 POs ready to release', detail: '6 items below par · $3,180 total', cta: 'Release', count: 2, level: 'info' },
    { id: 'equipment', icon: 'equipment', name: 'Equipment', sig: 'Walk-in cooler #2 trending warm', detail: '+4°F over 36h · service recommended', cta: 'Schedule', count: 1, level: 'danger' },
    { id: 'members', icon: 'members', name: 'Members', sig: '184 members lapsing', detail: 'Win-back offer ready to send', cta: 'Review', count: 184, level: 'info' },
    { id: 'feedback', icon: 'feedback', name: 'Guest feedback', sig: '2 reviews need a reply', detail: '9 new today · 4.3★ avg', cta: 'Respond', count: 2, level: 'warn' },
  ],
};
const LEVEL = {
  danger: { fg: 'var(--db-lava-700)', bg: 'var(--db-lava-300)', dot: 'var(--db-lava-600)' },
  warn:   { fg: 'var(--db-yellow-800)', bg: 'var(--db-yellow-300)', dot: 'var(--db-yellow-600)' },
  info:   { fg: 'var(--db-blue-700)', bg: 'var(--db-blue-300)', dot: 'var(--db-blue-600)' },
  ok:     { fg: 'var(--db-green-800)', bg: 'var(--db-green-300)', dot: 'var(--db-green-600)' },
};

/* ---------------- Shell (sidebar + topbar) ---------------- */
const NAV = [
  { id: 'today', label: 'Today', icon: 'today' },
  { id: 'sales', label: 'Sales', icon: 'sales' },
  { id: 'labor', label: 'Labor', icon: 'labor' },
  { id: 'inventory', label: 'Inventory', icon: 'inventory' },
  { id: 'equipment', label: 'Equipment', icon: 'equipment' },
  { id: 'members', label: 'Members', icon: 'members' },
  { id: 'feedback', label: 'Guest feedback', icon: 'feedback' },
  { id: 'reports', label: 'Reports', icon: 'reports' },
];

const HBLogo = ({ size = 26 }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
    <div style={{ width: size, height: size, borderRadius: 7, background: 'var(--db-lava-600)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 0 0 1px rgba(255,255,255,0.08)' }}>
      <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 10.5 12 3l9 7.5M5 9v11a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9" />
      </svg>
    </div>
    <span style={{ fontSize: 16, fontWeight: 700, color: '#fff', letterSpacing: '-0.01em' }}>Homebase</span>
  </div>
);

const Sidebar = ({ active }) => (
  <aside style={{ width: 232, background: 'var(--db-navy-900)', display: 'flex', flexDirection: 'column', flexShrink: 0, height: '100%' }}>
    <div style={{ padding: '18px 18px 14px', borderBottom: '1px solid var(--db-navy-700)' }}>
      <HBLogo />
    </div>
    <div style={{ padding: '12px 14px 8px' }}>
      <div style={{ background: 'var(--db-navy-700)', borderRadius: 8, padding: '8px 11px', display: 'flex', alignItems: 'center', gap: 9 }}>
        <HBIcon name="search" size={15} color="var(--db-navy-400)" />
        <span style={{ fontSize: 12.5, color: 'var(--db-navy-400)' }}>Search store…</span>
        <span style={{ marginLeft: 'auto', fontSize: 10.5, color: 'var(--db-navy-500)', fontFamily: 'var(--font-mono)' }}>⌘K</span>
      </div>
    </div>
    <nav style={{ padding: '4px 12px', flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
      {NAV.map(it => {
        const on = active === it.id;
        return (
          <div key={it.id} style={{
            display: 'flex', alignItems: 'center', gap: 11, padding: '8px 11px', borderRadius: 7,
            background: on ? 'var(--db-navy-700)' : 'transparent',
            color: on ? '#fff' : 'var(--db-navy-300)', fontSize: 13.5, fontWeight: on ? 500 : 400,
            position: 'relative', cursor: 'pointer',
          }}>
            {on && <span style={{ position: 'absolute', left: -12, top: 8, bottom: 8, width: 3, borderRadius: 3, background: 'var(--db-lava-600)' }} />}
            <HBIcon name={it.icon} size={17} color={on ? 'var(--db-lava-500)' : 'var(--db-navy-400)'} />
            {it.label}
          </div>
        );
      })}
    </nav>
    <div style={{ padding: '10px 14px', borderTop: '1px solid var(--db-navy-700)', display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, opacity: 0.7 }}>
        <img src="assets/databricks-symbol-color.svg" style={{ height: 15 }} alt="" />
        <span style={{ fontSize: 10.5, color: 'var(--db-navy-400)' }}>Powered by Databricks</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: 30, height: 30, borderRadius: 999, background: 'var(--db-lava-600)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700, color: '#fff' }}>MO</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 12.5, fontWeight: 500, color: '#fff' }}>Maya Okonkwo</div>
          <div style={{ fontSize: 10.5, color: 'var(--db-navy-400)' }}>Store manager</div>
        </div>
        <HBIcon name="settings" size={15} color="var(--db-navy-400)" />
      </div>
    </div>
  </aside>
);

const TopBar = ({ title }) => (
  <header style={{ height: 56, padding: '0 28px', background: '#fff', borderBottom: '1px solid var(--db-gray-lines)', display: 'flex', alignItems: 'center', gap: 14, flexShrink: 0 }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 9, fontSize: 13.5 }}>
      <span style={{ color: 'var(--db-gray-text)' }}>{DAY.store}</span>
      <span style={{ color: 'var(--db-navy-300)' }}>/</span>
      <span style={{ fontWeight: 500, color: 'var(--db-navy-800)' }}>{DAY.num} · {DAY.hood.split(' · ')[0]}</span>
      <HBIcon name="chevd" size={14} color="var(--db-navy-400)" />
    </div>
    <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 14 }}>
      <span style={{ fontSize: 12.5, color: 'var(--db-gray-text)', fontFamily: 'var(--font-mono)' }}>{DAY.date} · 7:42 AM</span>
      <span style={{ position: 'relative', display: 'flex' }}>
        <HBIcon name="bell" size={19} color="var(--db-gray-text)" />
        <span style={{ position: 'absolute', top: -2, right: -2, width: 7, height: 7, borderRadius: 999, background: 'var(--db-lava-600)', border: '1.5px solid #fff' }} />
      </span>
    </div>
  </header>
);

/* small shared bits */
const Chip = ({ children, color = 'var(--db-navy-300)', bg = 'rgba(255,255,255,0.1)' }) => (
  <span style={{ fontSize: 11.5, fontWeight: 500, padding: '4px 10px', borderRadius: 999, color, background: bg }}>{children}</span>
);
const Delta = ({ up, children, size = 12 }) => (
  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, fontSize: size, fontWeight: 500, color: up ? 'var(--db-green-700)' : 'var(--db-lava-700)' }}>
    <HBIcon name={up ? 'arrowup' : 'arrowdn'} size={size} stroke={2} /> {children}
  </span>
);

Object.assign(window, { HBIcon, Spark, DAY, LEVEL, NAV, HBLogo, Sidebar, TopBar, Chip, Delta });
