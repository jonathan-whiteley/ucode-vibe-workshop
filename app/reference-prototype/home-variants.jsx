// Homebase — three home-screen directions. Depends on homebase-directions.jsx.
const PRIO = { danger: 0, warn: 1, info: 2, ok: 3 };

/* ============ A · The Morning Brief (prioritized action queue) ============ */
const HomeBrief = () => {
  const items = [...DAY.modules].sort((a, b) => PRIO[a.level] - PRIO[b.level]);
  return (
    <div style={{ flex: 1, overflow: 'hidden', background: 'var(--db-oat-light)' }}>
      <div style={{ padding: '28px 32px', maxWidth: 1080, margin: '0 auto' }}>
        {/* hero */}
        <div style={{ background: 'var(--db-navy-800)', borderRadius: 16, padding: '28px 32px', display: 'flex', gap: 32, color: '#fff', position: 'relative', overflow: 'hidden' }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="db-eyebrow" style={{ color: 'var(--db-lava-400)' }}>{DAY.date}</div>
            <h1 style={{ fontSize: 34, fontWeight: 500, color: '#fff', letterSpacing: '-0.02em', margin: '8px 0 0' }}>Good morning, {DAY.manager}.</h1>
            <p style={{ fontSize: 15, lineHeight: 1.55, color: 'var(--db-navy-300)', margin: '12px 0 0', maxWidth: 560 }}>
              You're forecast to do <strong style={{ color: '#fff', fontWeight: 600 }}>{DAY.forecast.v}</strong> today — <strong style={{ color: 'var(--db-green-400)', fontWeight: 600 }}>11% ahead</strong> of last Friday. Five things need a decision before the lunch rush. The walk-in cooler is the one to watch.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 10, alignSelf: 'stretch' }}>
            {[['Sales yest.', DAY.sales.v, DAY.sales.d, true], ['Labor %', DAY.labor.v, 'on target', true], ['Guest score', DAY.guest.v + '★', DAY.guest.d, true]].map(([l, v, d]) => (
              <div key={l} style={{ background: 'var(--db-navy-700)', borderRadius: 12, padding: '14px 16px', minWidth: 116, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <div style={{ fontSize: 11, color: 'var(--db-navy-400)', fontWeight: 500 }}>{l}</div>
                <div style={{ fontSize: 24, fontWeight: 600, color: '#fff', margin: '4px 0 2px', letterSpacing: '-0.01em' }}>{v}</div>
                <div style={{ fontSize: 11.5, color: 'var(--db-green-400)', fontWeight: 500 }}>{d}</div>
              </div>
            ))}
          </div>
        </div>
        {/* queue header */}
        <div style={{ display: 'flex', alignItems: 'center', marginTop: 26, marginBottom: 14 }}>
          <h2 style={{ fontSize: 17, fontWeight: 500, color: 'var(--db-navy-800)', margin: 0 }}>Needs you today</h2>
          <span style={{ marginLeft: 10, fontSize: 12, fontWeight: 500, color: 'var(--db-lava-700)', background: 'var(--db-lava-300)', padding: '2px 9px', borderRadius: 999 }}>5</span>
          <button className="hb-ghost" style={{ marginLeft: 'auto' }}>Mark all reviewed</button>
        </div>
        {/* action cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 11 }}>
          {items.map(m => {
            const lv = LEVEL[m.level];
            return (
              <div key={m.id} className="hb-card" style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '16px 20px' }}>
                <div style={{ width: 44, height: 44, borderRadius: 10, background: lv.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <HBIcon name={m.icon} size={21} color={lv.fg} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="db-eyebrow" style={{ fontSize: 11 }}>{m.name}</span>
                    <span style={{ width: 5, height: 5, borderRadius: 999, background: lv.dot }} />
                  </div>
                  <div style={{ fontSize: 15.5, fontWeight: 500, color: 'var(--db-navy-800)', marginTop: 3 }}>{m.sig}</div>
                  <div style={{ fontSize: 13, color: 'var(--db-gray-text)', marginTop: 2 }}>{m.detail}</div>
                </div>
                <button className="hb-ghost">View</button>
                <button className="hb-primary">{m.cta}<HBIcon name="arrow" size={14} color="#fff" /></button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

/* ============ B · Command Deck (KPIs + module tiles) ============ */
const HomeDeck = () => {
  const kpis = [
    { l: 'Sales yesterday', v: DAY.sales.v, d: DAY.sales.d, up: true, spark: DAY.sales.spark, c: 'var(--db-lava-600)' },
    { l: 'Forecast today', v: DAY.forecast.v, sub: DAY.forecast.sub, spark: DAY.forecast.spark, c: 'var(--db-blue-600)' },
    { l: 'Labor cost', v: DAY.labor.v, d: DAY.labor.d, up: true, spark: DAY.labor.spark, c: 'var(--db-green-600)' },
    { l: 'Guest score', v: DAY.guest.v + '★', d: DAY.guest.d, up: true, spark: DAY.guest.spark, c: 'var(--db-yellow-600)' },
  ];
  return (
    <div style={{ flex: 1, overflow: 'hidden', background: 'var(--db-oat-light)' }}>
      <div style={{ padding: '26px 32px', maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
          <div>
            <div className="db-eyebrow" style={{ color: 'var(--db-lava-700)' }}>{DAY.date}</div>
            <h1 style={{ fontSize: 28, fontWeight: 500, color: 'var(--db-navy-800)', letterSpacing: '-0.02em', margin: '6px 0 0' }}>Good morning, {DAY.manager}</h1>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9, fontSize: 13, color: 'var(--db-gray-text)' }}>
            <span style={{ width: 7, height: 7, borderRadius: 999, background: 'var(--db-green-600)' }} />
            All systems nominal · <span style={{ fontFamily: 'var(--font-mono)' }}>612 guests yest.</span>
          </div>
        </div>
        {/* KPI row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 13, marginTop: 20 }}>
          {kpis.map(k => (
            <div key={k.l} className="hb-card" style={{ padding: '16px 18px' }}>
              <div style={{ fontSize: 11.5, color: 'var(--db-gray-text)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{k.l}</div>
              <div style={{ fontSize: 30, fontWeight: 600, color: 'var(--db-navy-800)', letterSpacing: '-0.02em', margin: '6px 0 4px' }}>{k.v}</div>
              <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
                {k.d ? <Delta up={k.up}>{k.d}</Delta> : <span style={{ fontSize: 12, color: 'var(--db-gray-text)' }}>{k.sub}</span>}
                <Spark pts={k.spark} color={k.c} w={84} h={28} />
              </div>
            </div>
          ))}
        </div>
        {/* module tiles */}
        <div style={{ display: 'flex', alignItems: 'center', marginTop: 26, marginBottom: 14 }}>
          <h2 style={{ fontSize: 17, fontWeight: 500, color: 'var(--db-navy-800)', margin: 0 }}>Operations</h2>
          <span style={{ marginLeft: 'auto', fontSize: 13, color: 'var(--db-gray-text)' }}>5 items need attention</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 13 }}>
          {DAY.modules.map(m => {
            const lv = LEVEL[m.level];
            return (
              <div key={m.id} className="hb-card" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
                  <div style={{ width: 38, height: 38, borderRadius: 9, background: lv.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <HBIcon name={m.icon} size={19} color={lv.fg} />
                  </div>
                  <span style={{ fontSize: 15, fontWeight: 500, color: 'var(--db-navy-800)' }}>{m.name}</span>
                  <span style={{ marginLeft: 'auto', fontSize: 12, fontWeight: 600, color: lv.fg, background: lv.bg, minWidth: 22, height: 22, borderRadius: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 7px' }}>{m.count > 99 ? '184' : m.count}</span>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--db-navy-800)' }}>{m.sig}</div>
                  <div style={{ fontSize: 12.5, color: 'var(--db-gray-text)', marginTop: 3 }}>{m.detail}</div>
                </div>
                <button className="hb-primary" style={{ justifyContent: 'center', width: '100%' }}>{m.cta}</button>
              </div>
            );
          })}
          {/* Genie tile */}
          <div className="hb-card" style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 12, background: 'var(--db-navy-800)', border: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
              <div style={{ width: 38, height: 38, borderRadius: 9, background: 'var(--db-lava-600)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <HBIcon name="spark" size={19} color="#fff" />
              </div>
              <span style={{ fontSize: 15, fontWeight: 500, color: '#fff' }}>Ask Homebase</span>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14, color: 'var(--db-navy-300)', lineHeight: 1.5 }}>“Why is labor down vs last week?” · “What should I prep extra of today?”</div>
            </div>
            <button className="hb-primary" style={{ justifyContent: 'center', width: '100%' }}>Ask a question</button>
          </div>
        </div>
      </div>
    </div>
  );
};

/* ============ C · Genie-first (bold, AI briefing led) ============ */
const HomeGenie = () => (
  <div style={{ flex: 1, overflow: 'hidden', background: 'var(--db-oat-light)' }}>
    <div style={{ padding: '26px 32px', maxWidth: 1080, margin: '0 auto' }}>
      {/* AI hero */}
      <div style={{ background: 'var(--db-navy-900)', borderRadius: 18, padding: '32px 36px', position: 'relative', overflow: 'hidden' }}>
        <svg viewBox="0 0 24 24" width="320" height="320" fill="none" stroke="var(--db-navy-700)" strokeWidth="0.5" style={{ position: 'absolute', right: -40, top: -60, opacity: 0.6 }}>
          <path d={HB_PATHS.spark} />
        </svg>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, position: 'relative' }}>
          <div style={{ width: 30, height: 30, borderRadius: 8, background: 'var(--db-lava-600)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <HBIcon name="spark" size={17} color="#fff" />
          </div>
          <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--db-lava-400)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>Homebase AI · your daily brief</span>
        </div>
        <p style={{ fontSize: 23, lineHeight: 1.5, color: '#fff', fontWeight: 400, margin: '20px 0 0', maxWidth: 720, letterSpacing: '-0.01em', position: 'relative' }}>
          Morning, {DAY.manager}. Yesterday closed at <strong style={{ fontWeight: 600 }}>{DAY.sales.v}</strong>, up <span style={{ color: 'var(--db-green-400)', fontWeight: 600 }}>6.2%</span>. Today's forecast is <strong style={{ fontWeight: 600 }}>{DAY.forecast.v}</strong>. The biggest thing to handle: <span style={{ color: 'var(--db-lava-400)', fontWeight: 600 }}>walk-in cooler #2 is trending +4°F</span> — book service before the weekend rush. Three timecards and two reorders are also waiting.
        </p>
        <div style={{ display: 'flex', gap: 10, marginTop: 24, flexWrap: 'wrap', position: 'relative' }}>
          {['Schedule cooler service', 'Approve 3 timecards', 'Release 2 reorders', 'Send win-back to 184 members'].map((s, i) => (
            <button key={s} className="hb-chip-action">{i === 0 && <span style={{ width: 6, height: 6, borderRadius: 999, background: 'var(--db-lava-500)' }} />}{s}</button>
          ))}
        </div>
        <div style={{ marginTop: 22, background: 'var(--db-navy-800)', border: '1px solid var(--db-navy-700)', borderRadius: 12, padding: '6px 6px 6px 16px', display: 'flex', alignItems: 'center', gap: 10, position: 'relative', maxWidth: 720 }}>
          <HBIcon name="spark" size={16} color="var(--db-navy-400)" />
          <span style={{ flex: 1, fontSize: 14, color: 'var(--db-navy-400)' }}>Ask anything about your store…</span>
          <button className="hb-primary"><HBIcon name="arrow" size={15} color="#fff" /></button>
        </div>
      </div>
      {/* module rail */}
      <div style={{ display: 'flex', alignItems: 'center', marginTop: 24, marginBottom: 13 }}>
        <h2 style={{ fontSize: 16, fontWeight: 500, color: 'var(--db-navy-800)', margin: 0 }}>Jump into a module</h2>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 12 }}>
        {DAY.modules.map(m => {
          const lv = LEVEL[m.level];
          return (
            <div key={m.id} className="hb-card" style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ width: 36, height: 36, borderRadius: 9, background: lv.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <HBIcon name={m.icon} size={18} color={lv.fg} />
                </div>
                <span style={{ width: 8, height: 8, borderRadius: 999, background: lv.dot }} />
              </div>
              <div>
                <div style={{ fontSize: 13.5, fontWeight: 500, color: 'var(--db-navy-800)' }}>{m.name}</div>
                <div style={{ fontSize: 12, color: 'var(--db-gray-text)', marginTop: 3, lineHeight: 1.4 }}>{m.sig}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  </div>
);

Object.assign(window, { HomeBrief, HomeDeck, HomeGenie });
