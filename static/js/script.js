// ── STATE ──────────────────────────────────────────────────────────────────
let currencies = [];
let fromC  = 'USD';
let toC    = 'EUR';
let recent = JSON.parse(localStorage.getItem('cx_recent') || '[]');

// ── BOOT ───────────────────────────────────────────────────────────────────
(async () => {
  await loadCurrencies();
  buildLists();
  await Promise.all([loadTicker(), loadNews(), doConvert(true)]);
  renderRecent();

  // Auto-refresh every 5 seconds
  setInterval(() => doConvert(false), 5000);
  setInterval(loadTicker,   5000);
})();

// ── API HELPER ─────────────────────────────────────────────────────────────
async function api(url) {
  try {
    const res = await fetch(url);
    return res.ok ? res.json() : null;
  } catch {
    return null;
  }
}

// ── LOAD CURRENCIES ────────────────────────────────────────────────────────
async function loadCurrencies() {
  const data = await api('/api/currencies');
  currencies = data || [
    { code: 'USD', name: 'US Dollar', symbol: '$' },
    { code: 'EUR', name: 'Euro',      symbol: '€' },
  ];
}

// ── CONVERT ────────────────────────────────────────────────────────────────
let historyTimer = null;

async function doConvert(saveToHistory = false) {
  const amt  = parseFloat(document.getElementById('amtInput').value) || 0;
  const data = await api(`/api/convert?from=${fromC}&to=${toC}&amount=${amt}`);
  if (!data) return;

  document.getElementById('resVal').textContent  = data.result.toFixed(4);
  document.getElementById('resCur').textContent  = toC;
  document.getElementById('rateInfo').textContent =
    `1 ${fromC} = ${data.rate.toFixed(6)} ${toC}`;

  // Only save to history when user has finished typing
  if (saveToHistory && amt > 0) {
    const entry = `${amt.toLocaleString()} ${fromC} → ${data.result.toFixed(2)} ${toC}`;
    if (!recent.length || recent[0] !== entry) {
      recent.unshift(entry);
      if (recent.length > 10) recent.pop();
      localStorage.setItem('cx_recent', JSON.stringify(recent));
      renderRecent();
    }
  }
}

// Updates result instantly on every keystroke, saves history only after 1s pause
function doConvertDebounced() {
  doConvert(false);
  clearTimeout(historyTimer);
  historyTimer = setTimeout(() => doConvert(true), 1000);
}

// ── TICKER ─────────────────────────────────────────────────────────────────
async function loadTicker() {
  const data = await api('/api/ticker');
  if (!data) return;

  // Duplicate items for seamless infinite scroll
  const items = [...data, ...data];
  document.getElementById('tickerTrack').innerHTML = items.map(t => `
    <div class="t-item">
      <span class="t-pair">${t.pair}</span>
      <span class="t-rate">${t.rate.toFixed(4)}</span>
      <span class="t-chg ${t.change >= 0 ? 'up' : 'dn'}">
        ${t.change >= 0 ? '▲' : '▼'} ${Math.abs(t.change).toFixed(2)}%
      </span>
    </div>
  `).join('');
}

// ── NEWS ───────────────────────────────────────────────────────────────────
async function loadNews() {
  const data = await api('/api/news');
  console.log(data);
  if (!data) return;

  document.getElementById('newsList').innerHTML = data.map(n => `
    <div class="news-card" onclick="window.open('${n.url}','_blank')" style="cursor:pointer">
      <div class="nm">
        <span class="badge ${n.impact === 'High Impact' ? 'high' : 'medium'}">${n.impact}</span>
        <span class="ntime">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          ${n.published_at}
        </span>
      </div>
      <div class="ntitle">${n.title}</div>
      <div class="ndesc">${n.desc}</div>
      <div class="nfooter">
        <div class="ntags">${n.tags.map(t => `<span class="ntag">${t}</span>`).join('')}</div>
        <span class="nsrc">${n.source}</span>
      </div>
    </div>
  `).join('');
}

// ── CURRENCY DROPDOWN LISTS ────────────────────────────────────────────────
function buildLists() {
  renderList('from', '');
  renderList('to', '');
  updateBtnLabels();
}

function renderList(side, query) {
  const selected = side === 'from' ? fromC : toC;
  const q        = query.toLowerCase();
  const filtered = currencies.filter(c =>
    c.code.toLowerCase().includes(q) ||
    c.name.toLowerCase().includes(q)
  );

  document.getElementById(`${side}List`).innerHTML = filtered.length
    ? filtered.map(c => `
        <div class="dd-opt ${c.code === selected ? 'sel' : ''}" onclick="pick('${side}', '${c.code}')">
          <div>
            <div class="oc">${c.code}</div>
            <div class="on">${c.name}</div>
          </div>
          ${c.code === selected ? '<span class="ck">✓</span>' : ''}
        </div>
      `).join('')
    : `<div style="padding:12px 14px; font-size:13px; color:var(--text3)">No results</div>`;
}

function filterDD(side) {
  const query = document.getElementById(`${side}Search`).value;
  renderList(side, query);
}

function toggleDD(side) {
  const ddEl    = document.getElementById(`${side}DD`);
  const otherDD = document.getElementById(side === 'from' ? 'toDD' : 'fromDD');
  otherDD.classList.remove('open');
  ddEl.classList.toggle('open');
  if (ddEl.classList.contains('open')) {
    setTimeout(() => document.getElementById(`${side}Search`).focus(), 60);
  }
}

function closeAllDD() {
  document.getElementById('fromDD').classList.remove('open');
  document.getElementById('toDD').classList.remove('open');
}

// Close dropdowns when clicking outside
document.addEventListener('click', e => {
  if (!e.target.closest('.sel-wrap')) closeAllDD();
});

function pick(side, code) {
  if (side === 'from') fromC = code;
  else                 toC   = code;

  closeAllDD();
  document.getElementById(`${side}Search`).value = '';
  renderList(side, '');
  updateBtnLabels();
  doConvert(true);
}

function updateBtnLabels() {
  const fc = currencies.find(c => c.code === fromC) || { code: fromC, name: '', symbol: '$' };
  const tc = currencies.find(c => c.code === toC)   || { code: toC,   name: '', symbol: '€' };

  document.getElementById('fromCode').textContent  = fromC;
  document.getElementById('fromName').textContent  = fc.name;
  document.getElementById('toCode').textContent    = toC;
  document.getElementById('toName').textContent    = tc.name;
  document.getElementById('symLabel').textContent  = fc.symbol;
  document.getElementById('resCur').textContent    = toC;
}


// ── SWAP ───────────────────────────────────────────────────────────────────
function doSwap() {
  [fromC, toC] = [toC, fromC];
  renderList('from', '');
  renderList('to', '');
  updateBtnLabels();
  doConvert(true);
}

// ── QUICK AMOUNTS ──────────────────────────────────────────────────────────
function setQA(val, btn) {
  document.getElementById('amtInput').value = val;
  document.querySelectorAll('.qa-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  doConvert(true);
}

document.getElementById('amtInput').addEventListener('input', () => {
  document.querySelectorAll('.qa-btn').forEach(b => b.classList.remove('active'));
  doConvertDebounced();
});

// ── RECENT CONVERSIONS ─────────────────────────────────────────────────────
function renderRecent() {
  const el = document.getElementById('recList');
  el.innerHTML = recent.length
    ? recent.map(r => `<div class="rec-item">${r}</div>`).join('')
    : '<div class="rec-empty">No conversions yet</div>';
}

function clearRec() {
  recent = [];
  localStorage.removeItem('cx_recent');
  renderRecent();
}

// ── COPY TO CLIPBOARD ──────────────────────────────────────────────────────
function doCopy() {
  const val = document.getElementById('resVal').textContent;
  const cur = document.getElementById('resCur').textContent;
  navigator.clipboard.writeText(`${val} ${cur}`)
    .then(() => showToast('Copied to clipboard!'));
}

// ── THEME TOGGLE ───────────────────────────────────────────────────────────
let isDark = true;
document.getElementById('themeBtn').addEventListener('click', () => {
  isDark = !isDark;
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  document.getElementById('themeBtn').textContent = isDark ? '☀️' : '🌙';
});

// ── TOAST NOTIFICATION ─────────────────────────────────────────────────────
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}
