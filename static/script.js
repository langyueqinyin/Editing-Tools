(function(){
'use strict';

const I18N = {
  en: {
    title: "Bulk Timecode Calculator",
    subtitle: "Batch diff/sum · Supports 23.976/24/25/29.97/30/50/59.94/60 and Drop‑Frame for 29.97/59.94. Paste from Excel, auto colonize 8‑digit inputs, one‑click copy results.",
    fpsLabel: "Frame rate (FPS):",
    customFpsOption: "Custom…",
    customFpsLabel: "Custom FPS:",
    dfLabel: "Drop‑Frame (DF)",
    opLabel: "Operation:",
    opDiff: "Difference (B − A)",
    opSum: "Sum (A + B)",
    outModeLabel: "Output:",
    outTC: "Timecode (HH:MM:SS:FF/;FF)",
    outFrames: "Total frames",
    outBoth: "Both",
    calc: "Calculate",
    hint: "Tip: Typing 8 digits like 01000000 auto‑colonizes to 01:00:00:00. Paste area accepts one column (A or B) or two columns (A+B).",
    colA: "A Start timecode",
    colB: "B End/Addend",
    colRes: "Result",
    paste: "Paste",
    pastePair: "Paste two columns",
    copyTC: "Copy timecode",
    copyFrames: "Copy frames",
    addRows: "+ Add 10 rows",
    clearRows: "Clear",
    legendSummary: "About 23.976 and Drop‑Frame (click to open)",
    legendHTML: `<p>23.976 is actually <code>24000/1001</code> fps. Timecode still counts 24 frames per “TC second”, so one TC second is ~1.001 real seconds. Industry convention: <b>23.976 uses NDF (no DF)</b>. <b>DF applies only to 29.97 (drop 2f/min, not every 10th) and 59.94 (drop 4f/min, not every 10th).</b></p>
      <ul>
        <li>DF only skips frame numbers to align wall‑clock, it does not drop picture frames.</li>
        <li>DF timecode is written with semicolon: <code>HH:MM:SS;FF</code>.</li>
      </ul>`,
    pasteTitle: "Bulk Paste",
    cancel: "Cancel",
    import: "Import",
    footer: "Made with Flask + vanilla JS. Single‑file front‑end, easy to drop into suites/machines.",
    aPlaceholder: "A  Start (e.g. 01:00:00:00 or 01000000)",
    bPlaceholder: "B  End/Addend",
    pastePlaceholder: "You can paste from Excel. One or two columns separated by TAB/comma/space.",
    pasteSample: `Example (two columns): <code>01:00:00:00<TAB>01:00:10:00</code>`
  },
  zh: {
    title: "时间码批量计算器",
    subtitle: "批量计算差值/加值 · 支持 23.976/24/25/29.97/30/50/59.94/60，且仅 29.97/59.94 提供丢帧（DF）。支持从 Excel 粘贴、8 位数字自动补冒号、结果一键复制。",
    fpsLabel: "帧率（FPS）：",
    customFpsOption: "自定义…",
    customFpsLabel: "自定义 FPS：",
    dfLabel: "丢帧（DF）",
    opLabel: "运算：",
    opDiff: "差值（B − A）",
    opSum: "加值（A + B）",
    outModeLabel: "输出显示：",
    outTC: "时间码（HH:MM:SS:FF/;FF）",
    outFrames: "总帧数",
    outBoth: "两者都显示",
    calc: "计算",
    hint: "小贴士：输入 8 位数字（如 01000000）会自动变成 01:00:00:00。粘贴区支持单列（A 或 B）或两列（A+B）。",
    colA: "A 起始时间码",
    colB: "B 结束/加数",
    colRes: "结果",
    paste: "批量粘贴",
    pastePair: "粘贴两列",
    copyTC: "复制时间码",
    copyFrames: "复制帧数",
    addRows: "+ 添加 10 行",
    clearRows: "清空表格",
    legendSummary: "关于 23.976 与丢帧（点开查看）",
    legendHTML: `<p>23.976 实际为 <code>24000/1001</code> fps。时间码每秒仍计 24 帧，因此“时间码里的 1 秒”略长于真实 1 秒（约 1.001 秒）。行业通行做法是：<b>23.976 不使用丢帧（DF）</b>，<b>DF 仅用于 29.97（丢 2 帧/分，逢十不丢）与 59.94（丢 4 帧/分，逢十不丢）。</b></p>
      <ul>
        <li>DF 只是跳过某些“帧号”，并不丢画面帧。</li>
        <li>DF 时间码常用分号书写：<code>HH:MM:SS;FF</code>。</li>
      </ul>`,
    pasteTitle: "批量粘贴",
    cancel: "取消",
    import: "导入",
    footer: "Made with Flask + 原生 JS。前端为单文件，便于在片场/机房临时投放。",
    aPlaceholder: "A  起始（如 01:00:00:00 或 01000000）",
    bPlaceholder: "B  结束/加数",
    pastePlaceholder: "可直接从 Excel/表格粘贴（支持一列或两列，用制表符/逗号/空格分隔）",
    pasteSample: `示例（两列）：<code>01:00:00:00<TAB>01:00:10:00</code>`
  }
};

function applyI18n(lang){
  const dict = I18N[lang] || I18N.en;
  document.documentElement.setAttribute('lang', lang);
  document.documentElement.setAttribute('data-lang', lang);
  document.title = dict.title + " · Flask";
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    const key = el.getAttribute('data-i18n');
    if (!dict[key]) return;
    el.textContent = dict[key];
  });
  const legend = document.getElementById('legendHTML');
  if (legend) legend.innerHTML = dict.legendHTML;
  document.querySelectorAll('#grid .row .a').forEach(el=> el.placeholder = dict.aPlaceholder);
  document.querySelectorAll('#grid .row .b').forEach(el=> el.placeholder = dict.bPlaceholder);
  const pasteBox = document.getElementById('pasteBox');
  if (pasteBox) pasteBox.placeholder = dict.pastePlaceholder;
  const sample = document.getElementById('pasteSample');
  if (sample) sample.innerHTML = dict.pasteSample;
  const customFps = document.getElementById('customFps');
  if (customFps) customFps.placeholder = (lang === 'zh') ? "例如 47.952" : "e.g. 47.952";
}
function getLang(){ return localStorage.getItem('tc_lang') || 'en'; }
function setLang(lang){ localStorage.setItem('tc_lang', lang); applyI18n(lang); }
function toggleLang(){ setLang(getLang()==='en' ? 'zh' : 'en'); }

const FPS_PROFILES = {
  "23.976": { exact: 24000/1001, timebase: 24, allowDF: false },
  "24":     { exact: 24,          timebase: 24, allowDF: false },
  "25":     { exact: 25,          timebase: 25, allowDF: false },
  "29.97":  { exact: 30000/1001,  timebase: 30, allowDF: true  },
  "30":     { exact: 30,          timebase: 30, allowDF: false },
  "50":     { exact: 50,          timebase: 50, allowDF: false },
  "59.94":  { exact: 60000/1001,  timebase: 60, allowDF: true  },
  "60":     { exact: 60,          timebase: 60, allowDF: false },
};

function getFpsProfile() {
  const sel = document.getElementById('fpsPreset');
  if (!sel) return { exact: 30000/1001, timebase: 30, allowDF: true };
  const preset = sel.value;
  if (preset === 'custom') {
    const inp = document.getElementById('customFps');
    const v = parseFloat((inp && inp.value) ? inp.value : '0');
    const rounded = Math.round(v || 0);
    const allowDF = Math.abs(v - 29.97) < 0.001 || Math.abs(v - 59.94) < 0.001;
    return { exact: v || 0, timebase: rounded || 30, allowDF };
  }
  return FPS_PROFILES[preset];
}
function setDropFrameAvailability() {
  const df = document.getElementById('dropFrame');
  if (!df) return;
  const { allowDF } = getFpsProfile();
  df.disabled = !allowDF;
  if (!allowDF) df.checked = false;
}

function autoColonize(s) {
  const neg = s.startsWith('-');
  const digits = s.replace(/[^0-9]/g, '');
  if (digits.length === 8) {
    const out = `${digits.slice(0,2)}:${digits.slice(2,4)}:${digits.slice(4,6)}:${digits.slice(6,8)}`;
    return neg ? '-' + out : out;
  }
  return s;
}
function parseTCToParts(tc) {
  let s = tc.trim();
  if (s === '') return null;
  const neg = s.startsWith('-');
  if (neg) s = s.slice(1);
  if (/^\d{8}$/.test(s)) s = autoColonize(s);
  s = s.replace(/;/g, ':');
  const m = s.match(/^(\d{1,2}):([0-5]?\d):([0-5]?\d):(\d{1,2})$/);
  if (!m) return null;
  const [_, HH, MM, SS, FF] = m;
  return { neg, h: +HH, m: +MM, s: +SS, f: +FF };
}
function fmtTC(h,m,s,f, useSemicolon=false, timebase=30) {
  const HH = String(h).padStart(2,'0');
  const MM = String(m).padStart(2,'0');
  const SS = String(s).padStart(2,'0');
  if (f >= timebase) f = timebase-1;
  const FF = String(f).padStart(2,'0');
  const sep = useSemicolon ? ';' : ':';
  return `${HH}:${MM}:${SS}${sep}${FF}`;
}
function ndfToFrames(parts, timebase) {
  const {h,m,s,f} = parts;
  return ((h*3600 + m*60 + s) * timebase) + f;
}
function framesToNDF(frames, timebase) {
  const sign = frames < 0 ? -1 : 1;
  let fr = Math.abs(frames);
  const hourFrames = timebase * 3600;
  const minuteFrames = timebase * 60;
  const h = Math.floor(fr / hourFrames); fr -= h * hourFrames;
  const min = Math.floor(fr / minuteFrames); fr -= min * minuteFrames;
  const sec = Math.floor(fr / timebase); fr -= sec * timebase;
  return {sign, h, m:min, s:sec, f:fr};
}
function dropFramesCount(fpsExact) { return Math.round(fpsExact * 0.066666); }
function dfToFrames(parts, fpsExact) {
  const timebase = Math.round(fpsExact);
  const drop = dropFramesCount(fpsExact);
  const hourFrames = timebase * 3600;
  const minuteFrames = timebase * 60;
  const totalMinutes = 60*parts.h + parts.m;
  const base = (hourFrames*parts.h) + (minuteFrames*parts.m) + (timebase*parts.s) + parts.f;
  return base - (drop * (totalMinutes - Math.floor(totalMinutes / 10)));
}
function framesToDF(frames, fpsExact) {
  const sign = frames < 0 ? -1 : 1;
  let fr = Math.abs(frames);
  const timebase = Math.round(fpsExact);
  const drop = dropFramesCount(fpsExact);
  const framesPerHour = timebase * 3600;
  const framesPer24Hours = framesPerHour * 24;
  const framesPer10Minutes = timebase * 60 * 10;
  const framesPerMinute = (timebase * 60) - drop;
  fr = fr % framesPer24Hours;
  const d = Math.floor(fr / framesPer10Minutes);
  let m = fr % framesPer10Minutes;
  if (m >= drop) {
    fr = fr + (drop * 9 * d) + drop * Math.floor((m - drop) / framesPerMinute);
  } else {
    fr = fr + (drop * 9 * d);
  }
  const tb = timebase;
  const f = fr % tb;
  const s = Math.floor(fr / tb) % 60;
  const min = Math.floor(Math.floor(fr / tb) / 60) % 60;
  const h = Math.floor(Math.floor(Math.floor(fr / tb) / 60) / 60);
  return {sign, h, m:min, s, f};
}

const grid = document.getElementById('grid');
function makeRow(i){
  const row = document.createElement('div');
  row.className = 'row';
  row.innerHTML = `
    <input class="tc-input a" placeholder="${I18N.en.aPlaceholder}" />
    <input class="tc-input b" placeholder="${I18N.en.bPlaceholder}" />
    <div class="res-cell">
      <div class="res-tc" data-i="${i}" title="Timecode result"></div>
      <div class="res-frames" data-i="${i}" title="Total frames"></div>
    </div>
  `;
  row.querySelector('.a').addEventListener('input', e => {
    const v = e.target.value;
    const withColon = autoColonize(v);
    if (withColon !== v) e.target.value = withColon;
  });
  row.querySelector('.b').addEventListener('input', e => {
    const v = e.target.value;
    const withColon = autoColonize(v);
    if (withColon !== v) e.target.value = withColon;
  });
  grid.appendChild(row);
}
function addRows(n=10){ for (let i=0;i<n;i++) makeRow(grid.children.length); }
addRows(20);

const addRowsBtn = document.getElementById('addRows');
if (addRowsBtn) addRowsBtn.onclick = ()=> addRows(10);
const clearRowsBtn = document.getElementById('clearRows');
if (clearRowsBtn) clearRowsBtn.onclick = ()=> { grid.innerHTML=''; addRows(20); applyI18n(getLang()); };

function calculate() {
  try {
    const prof = getFpsProfile();
    const exact = prof.exact;
    const timebase = prof.timebase;
    const useDF = !!(document.getElementById('dropFrame') && document.getElementById('dropFrame').checked);
    const opSel = document.getElementById('op');
    const outSel = document.getElementById('outMode');
    const op = opSel ? opSel.value : 'diff';
    const outMode = outSel ? outSel.value : 'both';
    [...grid.children].forEach((row) => {
      const aIn = row.querySelector('.a'); const bIn = row.querySelector('.b');
      const resTC = row.querySelector('.res-tc'); const resFrames = row.querySelector('.res-frames');
      const aParts = aIn.value.trim() ? parseTCToParts(aIn.value) : null;
      const bParts = bIn.value.trim() ? parseTCToParts(bIn.value) : null;
      aIn.classList.remove('bad'); bIn.classList.remove('bad');
      resTC.textContent = ''; resFrames.textContent = '';
      if (!aParts && !bParts) return;
      const toFrames = (parts)=> useDF ? dfToFrames(parts, exact) : ndfToFrames(parts, timebase);
      const fromFrames = (frames)=> useDF ? framesToDF(frames, exact) : framesToNDF(frames, timebase);
      const checkFrameRange = (p)=> p && p.f < timebase;
      let ok = true;
      if (aParts && !checkFrameRange(aParts)) { aIn.classList.add('bad'); ok = false; }
      if (bParts && !checkFrameRange(bParts)) { bIn.classList.add('bad'); ok = false; }
      if (!ok) return;
      const aF = aParts ? toFrames(aParts) * (aParts.neg?-1:1) : 0;
      const bF = bParts ? toFrames(bParts) * (bParts.neg?-1:1) : 0;
      let rF = (op === 'diff') ? (bF - aF) : (aF + bF);
      const rTCparts = fromFrames(rF);
      const semicolon = !!useDF;
      const tcText = (rTCparts.sign<0?'-':'') + fmtTC(rTCparts.h, rTCparts.m, rTCparts.s, rTCparts.f, semicolon, timebase);
      const framesText = (rTCparts.sign<0?'-':'') + Math.abs(rF).toString();
      if (outMode === 'tc') { resTC.textContent = tcText; resFrames.textContent = ''; }
      else if (outMode === 'frames') { resTC.textContent = framesText; resFrames.textContent = ''; }
      else { resTC.textContent = tcText; resFrames.textContent = framesText; }
    });
  } catch (err) {
    console.error('Calculate error:', err);
    alert('JS error: ' + (err?.message || err));
  }
}
document.getElementById('calcBtn')?.addEventListener('click', calculate);
document.getElementById('fpsPreset')?.addEventListener('change', () => {
  const wrap = document.getElementById('customFpsWrap');
  if (wrap) wrap.classList.toggle('hidden', document.getElementById('fpsPreset').value !== 'custom');
  setDropFrameAvailability();
});
document.getElementById('customFps')?.addEventListener('input', setDropFrameAvailability);
setDropFrameAvailability();
let pasteMode = 'A';
const pasteModal = document.getElementById('pasteModal');
const pasteBox = document.getElementById('pasteBox');
const pasteTitle = document.getElementById('pasteTitle');
document.querySelectorAll('[data-paste]').forEach(btn => {
  btn.addEventListener('click', ()=>{
    pasteMode = btn.dataset.paste;
    const lang = getLang();
    if (pasteTitle) {
      pasteTitle.textContent = pasteMode === 'PAIR'
        ? (lang==='zh' ? '批量粘贴（两列：A + B）' : 'Bulk Paste (two columns: A + B)')
        : (lang==='zh' ? `批量粘贴到列 ${pasteMode}` : `Bulk Paste to column ${pasteMode}`);
    }
    if (pasteBox) pasteBox.value = '';
    pasteModal?.showModal();
  });
});
document.getElementById('pasteConfirm')?.addEventListener('click', (e)=>{
  e.preventDefault();
  const text = (pasteBox?.value || '').trim();
  if (!text) { pasteModal?.close(); return; }
  const lines = text.split(/\r?\n/).map(l=>l.trim()).filter(Boolean);
  if (pasteMode === 'PAIR') {
    let r = 0;
    for (const line of lines) {
      const cols = line.split(/[\t, ]+/).filter(Boolean);
      const a = cols[0] ?? ''; const b = cols[1] ?? '';
      if (grid.children[r] == null) addRows(10);
      grid.children[r].querySelector('.a').value = autoColonize(a);
      grid.children[r].querySelector('.b').value = autoColonize(b);
      r++;
    }
  } else {
    let r = 0;
    for (const line of lines) {
      if (grid.children[r] == null) addRows(10);
      grid.children[r].querySelector(pasteMode==='A'?'.a':'.b').value = autoColonize(line);
      r++;
    }
  }
  pasteModal?.close();
  calculate();
});
function copyColumn(which){
  const vals = [...grid.children].map(row => {
    if (which==='tc') return row.querySelector('.res-tc').textContent.trim();
    return row.querySelector('.res-frames').textContent.trim();
  }).filter(Boolean);
  if (!vals.length) return;
  const text = vals.join('\n');
  navigator.clipboard.writeText(text).catch(()=>{
    const ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
  });
}
document.getElementById('copyTC')?.addEventListener('click', ()=>copyColumn('tc'));
document.getElementById('copyFrames')?.addEventListener('click', ()=>copyColumn('frames'));
document.addEventListener('keydown', (e)=>{
  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) calculate();
});
document.getElementById('langToggle')?.addEventListener('click', toggleLang);
applyI18n(getLang());
})();