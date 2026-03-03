from pathlib import Path
import pandas as pd
import json

APP_DIR = Path(__file__).resolve().parent

def load_data():
    pos_df = pd.read_csv(APP_DIR / 'data' / 'archetype_positions.csv', encoding='utf-8-sig')
    mat_df = pd.read_csv(APP_DIR / 'data' / 'works_matrix.csv',     encoding='utf-8-sig')

    # 兼容列
    for col in ('masc','parent','x2','y2'):
        if col not in pos_df.columns:
            pos_df[col] = pos_df['x'] if col=='x2' else (pos_df['y'] if col=='y2' else (0.5 if col=='masc' else ''))

    pos_df['archetype'] = pos_df['archetype'].astype(str).str.strip()
    mat_df.columns = [c.strip() for c in mat_df.columns]

    positions = pos_df.to_dict(orient='records')

    archetypes = list(pos_df['archetype'])
    works = []
    for _, row in mat_df.iterrows():
        work_name = str(row[mat_df.columns[0]]).strip()
        roles = {}
        for a in archetypes:
            if a in mat_df.columns:
                val = row[a]
                if pd.notna(val) and str(val).strip():
                    roles[a] = str(val).strip()
        works.append({'name': work_name, 'roles': roles})

    # NEW: 读注记CSV（不存在也不报错）
    notes_path = APP_DIR / 'data' / 'archetype_notes.csv'
    notes = {}
    if notes_path.exists():
        notes_df = pd.read_csv(notes_path, encoding='utf-8-sig')
        if 'archetype' in notes_df.columns and 'note' in notes_df.columns:
            notes = {str(r['archetype']).strip(): str(r['note']).strip()
                     for _, r in notes_df.iterrows() if pd.notna(r['archetype'])}

    return positions, works, notes

TPL = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>人物原型坐标图 · Archetypes × Works</title>
<style>
  :root{
    --bg:#f7fafc; --ink:#0f172a; --muted:#475569; --accent:#2563eb;
    --grid:#e5e7eb; --card:#ffffff; --border:#e5e7eb;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,"Noto Sans","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink)}
  header{padding:14px 20px;border-bottom:1px solid var(--border);position:sticky;top:0;background:rgba(255,255,255,.85);backdrop-filter:blur(8px);z-index:2}
  h1{font-size:18px;margin:0}
  .wrap{
    display:grid;
    grid-template-columns: minmax(520px,1fr) 360px 340px; /* ← 三列 */
    gap:16px; padding:16px; max-width:1400px; margin:0 auto;
  }
    /* 小屏自动一列堆叠 */
  @media (max-width: 1100px){
    .wrap{ grid-template-columns: 1fr; }
  }
  .panel{background:var(--card);border:1px solid var(--border);border-radius:16px}
  #plot{padding:12px}
  #list{padding:12px;max-height:78vh;overflow:auto}

  /* 自适应 SVG */
  #svg{width:100%;height:auto;aspect-ratio:3/2;display:block}

  .plotbar{display:flex;align-items:center;gap:8px;padding:8px 12px 0 12px}
  .plotbar label{font-size:12px;color:#475569}
  .select{padding:6px 10px;border:1px solid var(--border);border-radius:10px;background:#fff;color:#0f172a}

  .axisLabel{fill:var(--muted); font-size:12px}
  .tick text{fill:#64748b;font-size:10px}
  .tick line{stroke:var(--grid)}
  .domain{stroke:#cbd5e1}

  .node{ transition: opacity .12s ease; transform:none; }
  .node:hover{ opacity:1; stroke-width:2.2; }
  .node.selected{stroke:var(--accent) !important; stroke-width:2.8 !important}

  .nodeLabel{fill:#334155; font-size:11px; opacity:.9; pointer-events:none}
  .nodeLabel tspan.role{ fill:#475569; font-size:10px; opacity:.95 }
  .highlight{opacity:1 !important}
  .pulse{stroke:var(--accent); stroke-width:2; fill:transparent; opacity:.9; animation:pulse 1.2s ease-out infinite; pointer-events:none}
  @keyframes pulse {0%{r:0; opacity:.9} 80%{r:22; opacity:0} 100%{opacity:0}}

  .work{padding:10px 12px;border-radius:10px;cursor:pointer;display:flex;justify-content:space-between;gap:10px;align-items:center;border:1px solid transparent}
  .work:hover{background:#f8fafc;border-color:#e5e7eb}
  .work.active{background:#eef2ff;border-color:#c7d2fe}
  .badge{background:#eef2ff;border:1px solid #e0e7ff;color:#3730a3;border-radius:999px;padding:2px 8px;font-size:11px}
  .muted{color:var(--muted)}
  .toolbar{display:flex;gap:10px;align-items:center;padding:0 12px 12px}
  input[type="search"]{width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--border);background:#fff;color:#0f172a;outline:none}
  #legend{padding:12px;border-top:1px dashed var(--border)}
  #legend h3{font-size:12px;margin:0 0 8px;color:#0f172a}
  #legend .line{font-size:12px;color:#1f2937;margin:2px 0}
  #archRoles{padding:12px;border-top:1px dashed var(--border)}
  #archRoles h3{font-size:12px;margin:0 0 8px;color:#0f172a}
  #archRoles .line{font-size:12px;color:#1f2937;margin:2px 0}
  .axesNote{font-size:12px;color:#64748b;padding:0 12px 12px}
  #archNote{padding:12px;border-top:1px dashed var(--border)}
  #insights .insHead{ padding:12px 12px 0; font-size:12px; color:#475569; }
  #insights .insGrid{ display:grid; gap:12px; padding:12px; }
  #archRoles, #archNote{ border-top:1px dashed var(--border); padding-top:12px; }

  /* 你之前的样式可继续用： */
  #archRoles h3, #archNote h3{ font-size:12px; margin:0 0 8px; color:#0f172a; }
  #archRoles .line{ font-size:12px; color:#1f2937; margin:2px 0; }
  #archNote .text{ white-space:pre-wrap; color:#111827; font-size:12.5px; line-height:1.6; }

  /* === 字体调优补丁：左侧更大、更易读；右侧列表略小更紧凑 === */

  /* 左列：图表下方两块（坐标说明 & 角色映射/legend） */
  #plot .axesNote{
    font-size: 13.5px;
    line-height: 1.6;
  }
  #legend h3{
    font-size: 14px;
  }
  #legend .line{
    font-size: 13.5px;
    line-height: 1.7;
    letter-spacing: .1px;
  }

  /* 中列：原型洞见（全作品角色 + 原型注记） */
  #insights .insHead{
    font-size: 12.5px;
  }
  #archRoles h3, #archNote h3{
    font-size: 13.5px;
  }
  #archRoles .line{
    font-size: 13.5px;
    line-height: 1.65;
  }
  #archNote .text{
    font-size: 14px;
    line-height: 1.7;
    letter-spacing: .1px;
  }

  /* 右列：作品列表更紧凑一些 */
  #works .toolbar input[type="search"]{
    font-size: 13px;
    padding: 9px 12px;
  }
  #works .badge{
    font-size: 11px;
   padding: 2px 8px;
  }
  #works .work{
    padding: 8px 10px;             /* 更紧凑 */
  }
  #works .work > div{               /* 作品名 */
    font-size: 13px;
  }
  #works .work .muted{              /* “X 角色” 这个灰字 */
    font-size: 12px;
  }

  /* 如果你想让左侧图上“点旁边的标签”也稍大（可选） */
  .nodeLabel{
    font-size: 12px;                /* 原来是 11px */
  }
  .nodeLabel tspan.role{
    font-size: 11px;                /* 第二行人物名 */
  }
  /* 非交互层不接管鼠标，避免抢 hover */
  .nodeLabel,.pulse{ pointer-events:none; }
  #plot .tick line, #plot .domain{ pointer-events:none; } /* 网格/轴线 */
  .links line{ pointer-events:none; } /* 如果你给连线层起名不是 .links，忽略这条 */

  
  /* 三列：左=作品（可折叠），中=图表，右=洞见 */
:root{ --listw: 280px; --insw: 360px; }
.wrap{
  display:grid;
  grid-template-columns: var(--listw) 1fr var(--insw);
  gap:16px; padding:16px; max-width:1500px; margin:0 auto;
  transition: grid-template-columns .25s ease;
}
@media (max-width: 1100px){ .wrap{ grid-template-columns: 1fr; } }

/* 顶部按钮样式 */
header{ display:flex; align-items:center; gap:12px; }
#toggleList{
  border:1px solid var(--border); background:#fff; color:#0f172a;
  padding:6px 10px; border-radius:10px; cursor:pointer; font-size:12px;
}
#toggleList[aria-pressed="true"]{ background:#eef2ff; border-color:#c7d2fe; }

/* 折叠时：左列宽度=0，隐藏内容，图表+洞见变宽 */
body.list-collapsed{ --listw: 0px; }
body.list-collapsed #works{ opacity:0; padding:0; border-width:0; overflow:hidden; }
#works{ transition: opacity .2s ease, padding .2s ease, border-width .2s ease; }

/* 左边/中间的文字更大一点，右侧列表略紧凑 */
#legend h3, #archRoles h3, #archNote h3{ font-size: 14px; }
#legend .line, #archRoles .line{ font-size: 13.5px; line-height: 1.65; }
#archNote .text{ font-size: 14px; line-height: 1.7; }

#works .toolbar input[type="search"]{ font-size:13px; padding:9px 12px; }
#works .work{ padding:8px 10px; }
#works .work > div{ font-size:13px; }
#works .work .muted{ font-size:12px; }

/* 图上标签稍放大一点（可按需再调） */
.nodeLabel{ font-size:12.5px; }
.nodeLabel tspan.role{ font-size:11.5px; }

/* 防抖：非交互层不抢鼠标（确保保留） */
.nodeLabel,.pulse{ pointer-events:none; }

/* 顶部提示条 */
.notice{
  padding:10px 16px;
  background:#f1f5ff;              /* 淡蓝 */
  border:1px solid #dbe3ff;
  color:#0f172a;
  font-size:13px;
  line-height:1.6;
  border-radius:12px;
  max-width:1500px;
  margin:12px auto 0;
}
.notice strong{ color:#1d4ed8; }

</style>
</head>
<body>
<header>
  <button id="toggleList" aria-pressed="false" title="收起/展开作品列表">⟨ 作品</button>
  <h1>人物原型坐标图 · Archetypes × Works</h1>
</header>

<div class="notice">
  💡 小提示：左上角的<strong>「⟨ 作品」按钮</strong>可收起/展开左侧作品列表；
  点击<strong>图表中的任意原型点</strong>可在右侧查看「全作品角色」与「原型注记」；
  图表上方的<strong>「坐标系」下拉</strong>可在「主动/结构」与「轻/重 × 清/浊」之间切换。
</div>


<div class="wrap">
  <aside class="panel" id="works">
    <div class="toolbar">
      <input id="q" type="search" placeholder="搜索作品…">
      <span class="badge" id="count"></span>
    </div>
    <div id="list"></div>
  </aside>
  
  <section class="panel" id="plot">
    <div class="plotbar">
      <label for="axesSel">坐标系：</label>
      <select id="axesSel" class="select">
        <option value="base">主动/结构</option>
        <option value="tone">轻/重 × 清/浊</option>
      </select>
    </div>
    <svg id="svg"></svg>
    <div class="axesNote" id="axesNote">当前：横轴=主动程度（左=被动，右=主动） · 纵轴=对结构/体系的态度（下=反结构，上=亲结构）</div>
    <div id="legend"></div>
  </section>
  
  <section class="panel" id="insights">
  <div class="insHead">原型洞见</div>
  <div class="insGrid">
    <div id="archRoles"></div>
    <div id="archNote"></div>
  </div>
</section>


  </div>


<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script>
const POSITIONS = {{ positions | safe }};
const WORKS = {{ works | safe }};
const NOTES     = {{ notes | safe }};   // NEW

// 折叠按钮逻辑 + 记忆上次状态
const btn = document.getElementById('toggleList');
const LS_KEY = 'listCollapsed';
const saved = localStorage.getItem(LS_KEY) === '1';
if (saved) { document.body.classList.add('list-collapsed'); btn.setAttribute('aria-pressed','true'); btn.textContent = '⟩ 作品'; }

btn.addEventListener('click', () => {
  const collapsed = document.body.classList.toggle('list-collapsed');
  btn.setAttribute('aria-pressed', collapsed ? 'true' : 'false');
  btn.textContent = collapsed ? '⟩ 作品' : '⟨ 作品';
  localStorage.setItem(LS_KEY, collapsed ? '1' : '0');

  // 触发一次重排（可选）
  window.dispatchEvent(new Event('resize'));
});


// 两套坐标配置
const AXES = [
  { id:'base', xKey:'x',  yKey:'y',
    xText:'主动程度  ⟵ 被动 ｜ 主动 ⟶',
    yText:'对结构/体系的态度  ⟵ 反结构 ｜ 亲结构 ⟶',
    note:'当前：横轴=主动程度（左=被动，右=主动） · 纵轴=对结构/体系的态度（下=反结构，上=亲结构）'
  },
  { id:'tone', xKey:'x2', yKey:'y2',
    // 你要求：轻在右、重在左 → x 取相反数；清在上、浊在下 → y 保持正向
    xSign: -1, ySign: 1,
    xText:'重  ⟵           ｜           轻  ⟶',
    yText:'浊  ⟵           ｜           清  ⟶',
    note:'当前：横轴=轻/重（左=重，右=轻） · 纵轴=清/浊（下=浊，上=清）'
  }
];
let CUR = AXES[0];

// ---------- SVG & 尺寸（右侧 GUTTER 专供标签） ----------
const svg = d3.select("#svg")
  .attr("viewBox", "0 0 960 640")
  .attr("preserveAspectRatio", "xMidYMid meet");
const width = 960, height = 640;
const GUTTER = 160;
const margin = {top:20, right:20, bottom:35, left:35};
let w = width  - margin.left - margin.right - GUTTER;
let h = height - margin.top  - margin.bottom;

const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

// 颜色：masc 0=红(更女性化) → 1=蓝(更男性化)
const color = d3.scaleSequential(d3.interpolateRdBu).domain([0,1]);

// 裁剪主绘图区（点/线不越界）
svg.append("defs").append("clipPath").attr("id","plotClip")
  .append("rect").attr("x", margin.left).attr("y", margin.top).attr("width", w).attr("height", h);

// 箭头 marker
svg.append("defs").append("marker")
  .attr("id","arrow").attr("viewBox","0 0 10 10")
  .attr("refX",10).attr("refY",5).attr("markerWidth",6).attr("markerHeight",6)
  .attr("orient","auto-start-reverse")
  .append("path").attr("d","M 0 0 L 10 5 L 0 10 z").attr("fill","#60a5fa").attr("opacity",0.8);

// ---- 坐标/网格
const x = d3.scaleLinear().domain([-100,100]).range([0,w]);
const y = d3.scaleLinear().domain([-100,100]).range([h,0]);

const grid = g.append("g");
const gx = g.append("g").attr("transform",`translate(0,${h})`);
const gy = g.append("g");

const zeroX = g.append("line").attr("stroke","#cbd5e1").attr("stroke-dasharray","3,3");
const zeroY = g.append("line").attr("stroke","#cbd5e1").attr("stroke-dasharray","3,3");

// 右侧 GUTTER 背景 + 分隔线
const gutterBg = g.append("rect").attr("fill", "#f8fafc");
const gutterLine = g.append("line").attr("stroke", "#e5e7eb").attr("stroke-dasharray", "2,4");

// 轴标签
const xLabel = svg.append("text").attr("class","axisLabel").attr("text-anchor","middle");
const yLabel = svg.append("text").attr("class","axisLabel").attr("text-anchor","middle").attr("transform","rotate(-90)");
const axesNote = d3.select("#axesNote");

// ---- 数据：变种→原型链接
const ARCH_INDEX = new Map(POSITIONS.map(d => [d.archetype, d]));
const linksData = POSITIONS.filter(d => d.parent && String(d.parent).trim().length > 0)
  .map(d => ({ source: d, target: ARCH_INDEX.get(d.parent) })).filter(l => l.target);

const childCount = {};
linksData.forEach(l => { childCount[l.target.archetype] = (childCount[l.target.archetype] || 0) + 1; });

// ---- 图层
const linkLayer  = g.append("g").attr("clip-path","url(#plotClip)").style("pointer-events","none");
const nodeLayer  = g.append("g").attr("clip-path","url(#plotClip)");
const pulseLayer = g.append("g").attr("clip-path","url(#plotClip)");
const labelLayer = g.append("g"); // 不裁剪：标签可伸到 GUTTER
gutterBg.style("pointer-events","none");
gutterLine.style("pointer-events","none");
linkLayer.style("pointer-events","none");
labelLayer.style("pointer-events","none");
pulseLayer.style("pointer-events","none");

// 链接
const linkSel = linkLayer.selectAll("line").data(linksData).join("line")
  .attr("stroke", "#9ec5fe").attr("stroke-width", 1.5).attr("opacity", 0.7)
  .attr("marker-end", "url(#arrow)");

// 点
const nodeSel = nodeLayer.selectAll("circle").data(POSITIONS, d=>d.archetype).join("circle")
  .attr("class","node")
  .attr("r", d => childCount[d.archetype] ? 8 : 6)
  .attr("data-arch", d => d.archetype)
  .attr("fill", d => color(+d.masc))
  .attr("stroke", "#0b111a").attr("stroke-width", 1.2);
  
// 工具：取当前坐标值
const getXv = d => (CUR.xSign || 1) * (+d[CUR.xKey]);
const getYv = d => (CUR.ySign || 1) * (+d[CUR.yKey]);  
  
// 命中半径（看起来 8/6，命中圈再大 8px 比较顺手）
const baseR = d => (childCount[d.archetype] ? 8 : 6);

const hitLayer = g.append("g").attr("clip-path","url(#plotClip)");
const hits = hitLayer.selectAll("circle")
  .data(POSITIONS, d=>d.archetype)
  .join("circle")
    .attr("cx", d => x(getXv(d)))
    .attr("cy", d => y(getYv(d)))
    .attr("r",  d => Math.max(baseR(d) + 8, 12))
    .attr("fill", "transparent")
    .style("pointer-events","all")
    .style("cursor","pointer");

// hover 只改可见圆的样式，不改变大小/几何
hits.on("mouseenter", (e,d)=>{
  d3.select(nodeSel.filter(n => n===d).node())
    .attr("opacity", 1)
    .attr("stroke-width", 2.2);
}).on("mouseleave", (e,d)=>{
  d3.select(nodeSel.filter(n => n===d).node())
    .attr("opacity", .9)
    .attr("stroke-width", 1.2);
});

// 点击沿用你原先的逻辑（选中原型 & 显示两块信息）
hits.on("click", (e,d)=>{
  if (selectedArch === d.archetype){
    selectedArch = null;
    nodeSel.classed("selected", false);
    renderArchRoles(null);
  } else {
    selectedArch = d.archetype;
    nodeSel.classed("selected", n => n.archetype === selectedArch);
    renderArchRoles(selectedArch);
  }
});

// 标签
const labelSel = labelLayer.selectAll("text").data(POSITIONS, d=>d.archetype).join("text")
  .attr("class","nodeLabel")
  .each(function(d){ const t = d3.select(this); t.text(null); t.append("tspan").attr("class","arch").text(d.archetype); });



// 布局：默认点右侧；出主区则放入 GUTTER；底部溢出则翻到上方
function layoutOne(sel, d){
  const cx = x(getXv(d)), cy = y(getYv(d));
  let labelX = cx + 8, baseY = cy + 4;
  if (labelX > w - 8) labelX = w + 8; // 放进 GUTTER
  sel.attr("text-anchor","start").attr("x", labelX).attr("y", baseY);
  sel.select("tspan.arch").attr("x", labelX).attr("dy", 0);
  const role = sel.select("tspan.role"); const hasRole = !!role.node();
  if (hasRole) role.attr("x", labelX).attr("dy", 14);
  const box = sel.node().getBBox();
  if (cy + 6 + box.height > h) {
    sel.attr("y", cy - 6);
    sel.select("tspan.arch").attr("dy", 0);
    if (hasRole) role.attr("dy", -14);
  }
}
function layoutAll(){ labelSel.each(function(d){ layoutOne(d3.select(this), d); }); }

// 初始渲染（不带动画）
function positionAll(noAnim=false){
  const s = noAnim ? (sel=>sel) : (sel=>sel.transition().duration(500).ease(d3.easeCubicOut));
  s(nodeSel).attr("cx", d => x(getXv(d))).attr("cy", d => y(getYv(d)));
  s(linkSel) .attr("x1", d => x(getXv(d.source))).attr("y1", d => y(getYv(d.source)))
             .attr("x2", d => x(getXv(d.target))).attr("y2", d => y(getYv(d.target)));
  s(hits)    .attr("cx", d => x(getXv(d))).attr("cy", d => y(getYv(d)));   // ← 新增

  // 标签即时定位（不动画，避免抖动）
  layoutAll();
}

// 先布局静态，再定位元素
layoutStatic();
positionAll(true);

// ---- Works 列表/交互（支持锁定） -------------------------------------
const list = d3.select("#list");
const count = d3.select("#count");
const legend = d3.select("#legend");
const rolesBox = d3.select("#archRoles");
const noteBox = d3.select("#archNote");
const q = document.getElementById('q');
const axesSel = document.getElementById('axesSel');

let lockedWork = null;    // 当前锁定的作品
let currentList = WORKS;  // 当前列表
let selectedArch = null;  // 当前选中的原型

function renderList(items){
  currentList = items;
  list.selectAll("*").remove();
  const row = list.selectAll(".work")
    .data(items, d=>d.name)
    .join("div")
    .attr("class","work")
    .classed("active", d => lockedWork && lockedWork.name === d.name)
    .on("mouseenter", (e,d)=> { if(!lockedWork) highlightWork(d); })
    .on("mouseleave", () => { if(!lockedWork) clearHighlight(); })
    .on("click", (e,d) => {
      if (lockedWork && lockedWork.name === d.name) { setLockedWork(null); }
      else { setLockedWork(d); }
    });
  row.append("div").text(d=>d.name);
  row.append("span").attr("class","muted").text(d=> Object.keys(d.roles).length + " 角色");
  count.text(items.length + " 部作品");
}
renderList(WORKS);

function setLockedWork(work){
  lockedWork = work;
  list.selectAll(".work").classed("active", d => lockedWork && d.name === lockedWork.name);
  if (lockedWork) highlightWork(lockedWork); else clearHighlight();
}

function applyRoleLines(roles){
  labelSel.each(function(d){
    const t = d3.select(this);
    t.selectAll("tspan.role").remove();
    const who = roles[d.archetype];
    if (who){ t.append("tspan").attr("class","role").text(who); }
  });
  layoutAll();
}

function clearHighlight(){
  nodeSel.classed("highlight", false).attr("opacity", .9).attr("stroke-width", 1.2);
  linkSel.attr("stroke", "#9ec5fe").attr("opacity",0.7);
  pulseLayer.selectAll("*").remove();
  legend.selectAll("*").remove();
  applyRoleLines({});
  layoutAll();
}

function highlightWork(work){
  clearHighlight();
  const roles = work.roles;
  const entries = Object.entries(roles);
  const toHi = new Set(entries.map(([arch]) => arch));
  entries.forEach(([arch])=>{ const p = ARCH_INDEX.get(arch)?.parent; if (p) toHi.add(p); });

  nodeSel.each(function(d){
    const isHi = toHi.has(d.archetype);
    d3.select(this).classed("highlight", isHi)
      .attr("opacity", isHi ? 1 : 0.35)
      .attr("stroke-width", isHi ? 2 : 1.2);
    if (isHi){
      pulseLayer.append("circle").attr("class","pulse")
        .attr("cx", x(getXv(d))).attr("cy", y(getYv(d))).attr("r", 0);
    }
  });

  linkSel
    .attr("stroke", d => (toHi.has(d.source.archetype) || toHi.has(d.target.archetype)) ? "#60a5fa" : "#9ec5fe")
    .attr("opacity", d => (toHi.has(d.source.archetype) || toHi.has(d.target.archetype)) ? 0.95 : 0.35);

  applyRoleLines(roles);

  legend.append("h3").text(work.name + " · 角色映射");
  entries.sort((a,b)=> a[0].localeCompare(b[0], 'zh-Hans-CN')).forEach(([arch, who])=>{
    legend.append("div").attr("class","line").text(arch + "： " + who);
  });
}

// 点击原型点：显示“全作品角色”
function renderArchRoles(arch){
  // 先清空
  rolesBox.selectAll("*").remove();
  noteBox.selectAll("*").remove();
  if (!arch) return;

  // 1) 全作品角色
  const items = [];
  WORKS.forEach(w => { if (w.roles[arch]) items.push({work:w.name, who:w.roles[arch]}); });
  rolesBox.append("h3").text(`${arch} · 全作品角色（${items.length}）`);
  items.forEach(it => rolesBox.append("div").attr("class","line").text(`${it.work}： ${it.who}`));

  // 2) 原型注记（来自 NOTES）
  const txt = NOTES[arch];
  noteBox.append("h3").text(`${arch} · 原型注记`);
  noteBox.append("div").attr("class","text").text(txt ? txt : "（暂无笔记）");
}
// 搜索
q.addEventListener('input', () => {
  const term = q.value.trim().toLowerCase();
  const filtered = term ? WORKS.filter(w => w.name.toLowerCase().includes(term)) : WORKS;
  renderList(filtered);
  if (lockedWork) { setLockedWork(lockedWork); }
});

// 切换坐标系
axesSel.addEventListener('change', (e)=>{
  const id = e.target.value;
  CUR = AXES.find(a => a.id === id) || AXES[0];
  // 更新轴标签/注释
  layoutStatic();
  // 清除脉冲，按新坐标重绘位置
  pulseLayer.selectAll("*").remove();
  positionAll(false);
  // 若有锁定作品，按新坐标重新高亮
  if (lockedWork) highlightWork(lockedWork);
});

function layoutStatic(){
  // 这些尺寸不变时只更新文本；若你想将来支持改比例/GUTTER，也可在这里重算 w/h
  x.range([0,w]); y.range([h,0]);
  grid.selectAll("*").remove();
  grid.append("g").call(d3.axisBottom(x).tickSize(-h).ticks(10)).attr("transform",`translate(0,${h})`);
  grid.append("g").call(d3.axisLeft(y).tickSize(-w).ticks(10));
  gx.selectAll("*").remove(); gy.selectAll("*").remove();
  gx.call(d3.axisBottom(x).ticks(5)).attr("transform",`translate(0,${h})`);
  gy.call(d3.axisLeft(y).ticks(5));
  zeroX.attr("x1",x(0)).attr("x2",x(0)).attr("y1",0).attr("y2",h);
  zeroY.attr("y1",y(0)).attr("y2",y(0)).attr("x1",0).attr("x2",w);
  gutterBg.attr("x", w).attr("y", 0).attr("width", 160).attr("height", h);
  gutterLine.attr("x1", w).attr("x2", w).attr("y1", 0).attr("y2", h);
  xLabel.attr("x", margin.left + w/2).attr("y", height-6).text(CUR.xText);
  yLabel.attr("x", - (margin.top + h/2)).attr("y", 14).text(CUR.yText);
  d3.select("#axesNote").text(CUR.note);
}
</script>
</body>
</html>
'''

