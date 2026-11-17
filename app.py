import math
import random

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="하수관 AI 정비대", page_icon="🫧", layout="wide", initial_sidebar_state="collapsed")

FEATURES = ["압력", "소음", "침전물", "부식"]
FEATURE_KEYS = ["pressure", "noise", "sediment", "corrosion"]
LEARNING_RATE = 0.85

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
:root { --ink:#33445f; --blue:#829be0; --lav:#d5d9ff; --mint:#b6edda; --pink:#ffb1cb; --paper:#f6f5ff; }
html, body, [class*="css"] { font-family:'Gowun Dodum',sans-serif; color:var(--ink); }
.stApp { background:linear-gradient(180deg,#c8d6ff 0%,#dce4ff 46%,#f4eaff 100%); }
.block-container { max-width:1220px; padding-top:1.2rem; padding-bottom:2.2rem; }
h1,h2,h3,.pixel-title { font-family:'Jua',sans-serif!important; color:#384c76; }
.pixel-card { background:#fbfaff; border:3px solid #7189c6; box-shadow:5px 5px 0 #9eacd9; border-radius:5px; padding:16px 18px; margin:7px 0 15px; }
.pixel-card h3 { margin:.1rem 0 .55rem; font-size:1.25rem; }
.small-label { color:#7181ac; font-size:.88rem; letter-spacing:.06em; }
.hero { text-align:center; padding:10px 0 0; }
.hero h1 { font-size:3.1rem; margin:.1rem 0; color:#394c79; text-shadow:2px 3px #fff; }
.hero p { font-size:1.08rem; line-height:1.65; color:#53668f; }
.scene-frame { border:4px solid #7189c6; box-shadow:7px 7px 0 #9eacd9; border-radius:5px; overflow:hidden; background:#b9c9f5; }
.monitor-card { border:3px solid #7189c6; box-shadow:4px 4px 0 #a9b5dc; background:#f7f6ff; border-radius:4px; padding:10px 12px 4px; margin-bottom:8px; }
.monitor-card h3 { margin:0; font-size:1.1rem; }
.monitor-art { border:2px solid #8494c6; background:#bccaf1; margin:8px 0; line-height:0; }
.sensor-line { font-size:.9rem; color:#4e6088; padding:4px 0; }
.stButton > button { border:3px solid #667faf!important; border-radius:4px!important; background:#fff3be!important; color:#394c76!important; font-family:'Jua',sans-serif!important; font-size:1.1rem!important; box-shadow:3px 3px 0 #9eacd9!important; min-height:2.75rem; }
.stButton > button:hover { background:#ffe5ef!important; border-color:#d67fa3!important; color:#394c76!important; transform:translateY(-1px); }
div[data-testid="stMetric"] { background:#f8f7ff; border:2px solid #c1cae9; padding:10px; border-radius:4px; box-shadow:2px 2px 0 #d9def3; }
.day-strip { display:grid; grid-template-columns:repeat(7,1fr); gap:6px; }
.day-cell { text-align:center; border:2px solid #adb9df; background:#f8f7ff; padding:8px 3px; border-radius:3px; color:#7181ac; font-size:.85rem; }
.day-cell b { display:block; color:#3e527e; font-size:1.18rem; min-height:1.35rem; }
.day-cell.ok b { color:#28a77e; } .day-cell.no b { color:#d6658c; }
.pill { display:inline-block; padding:5px 11px; border:2px solid #8999c7; background:#f7f6ff; border-radius:4px; margin-right:6px; color:#4b608e; font-family:'Jua',sans-serif; }
.result-box { text-align:center; padding:22px; background:#fbfaff; border:4px solid #7189c6; box-shadow:6px 6px 0 #9eacd9; border-radius:5px; }
.result-box h1 { font-size:2.5rem; }
footer { visibility:hidden; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def init_state():
    defaults = {
        "screen": "start", "cycle": 1, "day": 1, "wins": 0,
        "calendar": ["", "", "", "", "", "", ""],
        "weights": [0.35, 0.35, 0.35, 0.35], "bias": -0.75,
        "routes": [], "target": 0, "last_result": None,
        "loss": None, "gradient": None, "seen": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def svg_scene():
    return '''<svg viewBox="0 0 900 390" width="100%" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated;display:block">
    <rect width="900" height="390" fill="#b9ccf7"/><rect y="0" width="900" height="125" fill="#9eb4ec"/>
    <path d="M0 124h900v75H0z" fill="#707eac"/><path d="M0 138h900v47H0z" fill="#8fa4d1"/>
    <rect x="44" y="72" width="210" height="71" rx="25" fill="#576583" stroke="#e1e3ff" stroke-width="8"/><rect x="57" y="84" width="184" height="47" rx="20" fill="#3e617f"/>
    <path d="M60 106h179v16H60z" fill="#7de2df"/><path d="M100 108h28v5h-28zm55-3h24v5h-24zm43 6h22v5h-22z" fill="#d5fbef"/>
    <path d="M0 208h900v182H0z" fill="#63769b"/><path d="M0 231h900v8H0zm0 135h900v8H0z" fill="#e6e8ff"/>
    <path d="M0 292h900v3H0z" fill="#aab7dc"/><rect x="308" y="212" width="280" height="18" fill="#dbe2ff"/><rect x="330" y="197" width="13" height="23" fill="#384968"/><rect x="346" y="193" width="12" height="27" fill="#222d4c"/><rect x="362" y="199" width="13" height="21" fill="#744d9c"/><rect x="378" y="195" width="12" height="25" fill="#586daa"/>
    <rect x="24" y="257" width="56" height="37" fill="#f2bd72"/><rect x="33" y="245" width="38" height="14" fill="#e987a8"/><rect x="42" y="267" width="12" height="27" fill="#9c739e"/>
    <rect x="727" y="245" width="12" height="114" fill="#fff0c1"/><rect x="727" y="256" width="12" height="13" fill="#e9819d"/><rect x="727" y="283" width="12" height="13" fill="#e9819d"/><rect x="727" y="310" width="12" height="13" fill="#e9819d"/><rect x="727" y="337" width="12" height="13" fill="#e9819d"/>
    <g fill="#516d89"><rect x="104" y="100" width="9" height="10"/><rect x="704" y="92" width="10" height="8"/><rect x="827" y="163" width="8" height="12"/></g>
    <g stroke="#6e5fa5" stroke-width="4" stroke-linecap="square"><path d="M121 205v-40l-12-13m12 30 14-14m-14-1-12-12M614 201v-42l-12-12m12 28 15-17m-15-3-10-12M806 203v-33l-13-12m13 24 13-14"/></g>
    <g fill="#f47ca8"><rect x="104" y="149" width="12" height="9"/><rect x="129" y="172" width="13" height="9"/><rect x="596" y="146" width="12" height="9"/><rect x="623" y="164" width="14" height="9"/><rect x="791" y="154" width="12" height="9"/></g>
    <g fill="#45bcb5"><rect x="176" y="114" width="21" height="8"/><rect x="166" y="106" width="16" height="8"/><rect x="195" y="105" width="15" height="9"/><rect x="485" y="120" width="22" height="9"/><rect x="479" y="111" width="16" height="10"/><rect x="505" y="111" width="16" height="10"/></g>
    <rect x="38" y="202" width="74" height="8" fill="#f2f1ff"/><rect x="122" y="202" width="10" height="8" fill="#b4c6ee"/><rect x="682" y="202" width="48" height="8" fill="#f2f1ff"/>
    <text x="705" y="72" font-size="15" font-family="monospace" fill="#4d5e8e">SEWER TOWN</text></svg>'''


def monitor_svg(route, idx):
    water = int(route[0] * 24 + 14)
    debris = int(route[2] * 8)
    corrosion = int(route[3] * 4)
    debris_rects = "".join(f'<rect x="{220+j*17}" y="{69-(j%2)*7}" width="8" height="7" fill="{["#f57fb0","#56c6b7","#e8c574"][j%3]}"/>' for j in range(debris))
    rust_rects = "".join(f'<rect x="{91+j*19}" y="{43+(j%2)*25}" width="8" height="8" fill="#d77b91"/>' for j in range(corrosion))
    return f'''<svg viewBox="0 0 330 130" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated">
    <rect width="330" height="130" fill="#aebde8"/><rect y="14" width="330" height="95" fill="#7f8eae"/>
    <rect x="34" y="29" width="262" height="65" rx="28" fill="#505c78" stroke="#e4e6ff" stroke-width="7"/>
    <rect x="49" y="52" width="232" height="42" rx="18" fill="#315d76"/>
    <rect x="51" y="{94-water}" width="228" height="{water}" rx="9" fill="#69d5dc"/><path d="M65 {91-water}h42v5H65zm89 6h32v4h-32zm76-8h35v4h-35z" fill="#d8fff1"/>
    {debris_rects}{rust_rects}<rect x="0" y="108" width="330" height="22" fill="#d4dcf6"/>
    <rect x="12" y="10" width="39" height="14" fill="#edf0ff"/><text x="16" y="21" font-size="10" font-family="monospace" fill="#495c89">CAM 0{idx+1}</text>
    <circle cx="309" cy="17" r="5" fill="#ef7b9b"/></svg>'''


def risk(route):
    z = st.session_state.bias + sum(w * x for w, x in zip(st.session_state.weights, route))
    z = max(-20, min(20, z))
    return 1 / (1 + math.exp(-z))


def new_day():
    routes = []
    for _ in range(4):
        routes.append([random.uniform(.13, .52), random.uniform(.10, .48), random.uniform(.08, .45), random.uniform(.10, .48)])
    target = random.randrange(4)
    # The hidden fault produces a combination of elevated sensor readings.
    for j in range(4):
        routes[target][j] = min(.98, routes[target][j] + random.uniform(.38, .56))
    st.session_state.routes = routes
    st.session_state.target = target
    st.session_state.last_result = None
    st.session_state.screen = "game"


def train_after_reveal():
    routes, target = st.session_state.routes, st.session_state.target
    labels = [1.0 if i == target else 0.0 for i in range(4)]
    probs = [risk(x) for x in routes]
    eps = 1e-8
    before_loss = -sum(y * math.log(max(eps, p)) + (1-y) * math.log(max(eps, 1-p)) for y, p in zip(labels, probs)) / 4
    grad_w = [sum((p-y)*route[k] for route, p, y in zip(routes, probs, labels))/4 for k in range(4)]
    grad_b = sum(p-y for p, y in zip(probs, labels))/4
    magnitude = math.sqrt(sum(g*g for g in grad_w) + grad_b*grad_b)
    st.session_state.weights = [w - LEARNING_RATE*g for w, g in zip(st.session_state.weights, grad_w)]
    st.session_state.bias -= LEARNING_RATE * grad_b
    after = [risk(x) for x in routes]
    after_loss = -sum(y * math.log(max(eps, p)) + (1-y) * math.log(max(eps, 1-p)) for y, p in zip(labels, after)) / 4
    st.session_state.loss = after_loss
    st.session_state.gradient = magnitude


def choose_route(idx):
    success = idx == st.session_state.target
    st.session_state.calendar[st.session_state.day - 1] = "O" if success else "X"
    if success:
        st.session_state.wins += 1
    st.session_state.seen += 1
    train_after_reveal()
    st.session_state.last_result = {"success": success, "chosen": idx, "target": st.session_state.target}
    if st.session_state.day == 7:
        st.session_state.screen = "summary"


def calendar_html():
    cells = []
    for i, result in enumerate(st.session_state.calendar, 1):
        cls = "ok" if result == "O" else "no" if result == "X" else ""
        cells.append(f'<div class="day-cell {cls}">DAY {i}<b>{result or "·"}</b></div>')
    return '<div class="day-strip">' + "".join(cells) + "</div>"


def restart_cycle():
    st.session_state.cycle += 1
    st.session_state.day = 1
    st.session_state.wins = 0
    st.session_state.calendar = ["", "", "", "", "", "", ""]
    st.session_state.weights = [0.35, 0.35, 0.35, 0.35]
    st.session_state.bias = -0.75
    st.session_state.loss = None
    st.session_state.gradient = None
    new_day()


init_state()

if st.session_state.screen == "start":
    st.markdown('<div class="hero"><div class="small-label">PIXEL SEWER MAINTENANCE SIMULATOR</div><h1>하수관 AI 정비대</h1><p>작은 단서들을 모아 이상 관로를 찾아내세요.<br>경사하강법으로 AI도 함께 성장합니다!</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="scene-frame">' + svg_scene() + '</div>', unsafe_allow_html=True)
    left, center, right = st.columns([1, 1, 1])
    with center:
        if st.button("▶  START  ◀", use_container_width=True, key="start_game"):
            st.session_state.day = 1
            st.session_state.wins = 0
            st.session_state.calendar = ["", "", "", "", "", "", ""]
            st.session_state.weights = [0.35, 0.35, 0.35, 0.35]
            st.session_state.bias = -0.75
            new_day()
            st.rerun()
    st.markdown('<div class="hero"><p><span class="pill">4개 CCTV</span><span class="pill">7일 근무</span><span class="pill">AI 경사하강법</span></p></div>', unsafe_allow_html=True)

elif st.session_state.screen == "game":
    st.markdown(f'<div class="hero"><span class="pill">근무 {st.session_state.cycle}회차</span><span class="pill">DAY {st.session_state.day} / 7</span><h1>관제실</h1></div>', unsafe_allow_html=True)
    left, right = st.columns([2.15, 1])
    with left:
        st.markdown('<div class="pixel-card"><h3>📡 CCTV 모니터</h3><span class="small-label">센서 기록과 화면을 살펴보고 이상이 의심되는 관로를 고르세요.</span></div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, (col, route) in enumerate(zip([cols[0], cols[1], cols[0], cols[1]], st.session_state.routes)):
            with col:
                score = risk(route)
                st.markdown(f'<div class="monitor-card"><h3>관로 {idx+1:02d}　<span class="small-label">AI 위험도 {score:.0%}</span></h3><div class="monitor-art">{monitor_svg(route, idx)}</div><div class="sensor-line">압력　{route[0]:.2f}　·　소음　{route[1]:.2f}<br>침전물　{route[2]:.2f}　·　부식　{route[3]:.2f}</div></div>', unsafe_allow_html=True)
                if st.button(f"관로 {idx+1} 점검", key=f"inspect_{st.session_state.cycle}_{st.session_state.day}_{idx}", use_container_width=True):
                    choose_route(idx)
                    st.rerun()
    with right:
        st.markdown('<div class="pixel-card"><h3>📅 이번 주 기록</h3>' + calendar_html() + '</div>', unsafe_allow_html=True)
        loss_text = "대기 중" if st.session_state.loss is None else f'{st.session_state.loss:.3f}'
        grad_text = "대기 중" if st.session_state.gradient is None else f'{st.session_state.gradient:.3f}'
        st.markdown('<div class="pixel-card"><h3>🧠 경사하강법 학습실</h3><span class="small-label">관로 특징에 따라 이상 확률을 계산합니다.</span></div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Loss (BCE)", loss_text)
        m2.metric("Gradient 크기", grad_text)
        for label, weight in zip(FEATURES, st.session_state.weights):
            st.progress(min(1.0, max(0.0, (weight + 1) / 2)), text=f"{label} 가중치　{weight:+.2f}")
        st.caption(f"학습률 η = {LEARNING_RATE:.2f} · 매일 점검 후 4개 관로의 라벨로 가중치를 업데이트합니다.")
        st.markdown('<div class="pixel-card"><h3>🧰 오늘의 업무</h3><span class="small-label">이상 관로를 선택하면 정답을 확인하고 AI가 경사하강법으로 학습합니다. 7일 중 5회 이상 성공하면 승진!</span></div>', unsafe_allow_html=True)
    if st.session_state.last_result:
        result = st.session_state.last_result
        if result["success"]:
            st.success(f'정확해요! 관로 {result["target"]+1}에 이상이 있었습니다. 업데이트된 Loss: {st.session_state.loss:.3f}')
        else:
            st.error(f'아쉬워요. 선택한 곳은 관로 {result["chosen"]+1}, 실제 이상은 관로 {result["target"]+1}이었습니다. Loss: {st.session_state.loss:.3f}')
        if st.button("다음 날 근무하기 →", key=f"next_{st.session_state.cycle}_{st.session_state.day}", use_container_width=True):
            st.session_state.day += 1
            st.session_state.last_result = None
            new_day()
            st.rerun()

elif st.session_state.screen == "summary":
    wins = st.session_state.wins
    if wins >= 5:
        heading, mood, message = "승진 축하해요!", "🌟", f"7일 중 {wins}회 성공! 관제팀의 믿음직한 팀장으로 승진했습니다."
        next_label, action = "처음 화면으로", "start"
    elif wins >= 3:
        heading, mood, message = "한 주 더 도전!", "🌱", f"7일 중 {wins}회 성공했습니다. 조금 더 경험을 쌓을 기회가 생겼어요. 다음 7일을 시작합니다!"
        next_label, action = "다음 7일 시작", "retry"
    else:
        heading, mood, message = "오늘은 여기까지…", "🌧️", f"7일 중 {wins}회 성공했습니다. 이번에는 회사를 떠나게 되었지만, 배운 내용을 기억해요."
        next_label, action = "처음 화면으로", "start"
    st.markdown(f'<div class="result-box"><div style="font-size:4rem">{mood}</div><div class="small-label">주간 근무 결산 · {st.session_state.cycle}회차</div><h1>{heading}</h1><p>{message}</p>{calendar_html()}</div>', unsafe_allow_html=True)
    st.write("")
    a, b, c = st.columns([1, 1, 1])
    with b:
        if st.button(next_label, use_container_width=True, key="summary_action"):
            if action == "retry":
                restart_cycle()
            else:
                st.session_state.screen = "start"
            st.rerun()

# A successful or failed inspection on day seven goes straight to the weekly report.
if st.session_state.screen == "summary" and st.session_state.last_result:
    result = st.session_state.last_result
    if result["success"]:
        st.info("마지막 날 점검 성공! 아래에서 이번 주 결산을 확인하세요.")
    else:
        st.info("마지막 날 점검 결과가 기록됐습니다. 아래에서 이번 주 결산을 확인하세요.")
