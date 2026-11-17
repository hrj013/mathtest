import math
import random

import streamlit as st

st.set_page_config(page_title="하수관 AI 정비대", page_icon="📡", layout="wide", initial_sidebar_state="collapsed")

FEATURES = ["압력", "소음", "침전물", "부식"]
LEARNING_RATE = 0.85

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
:root { --ink:#33445f; --blue:#829be0; --lav:#d5d9ff; --mint:#b6edda; --pink:#ffb1cb; --paper:#f6f5ff; }
html, body, [class*="css"] { font-family:'Gowun Dodum',sans-serif; }
.block-container { max-width:1280px; padding-top:1rem; padding-bottom:2rem; }
h1,h2,h3 { font-family:'Jua',sans-serif!important; }
.hero { text-align:center; padding:7px 0 0; }
.hero h1 { font-size:3rem; margin:.1rem 0; color:#394c79; text-shadow:2px 3px #fff; }
.hero p { font-size:1.04rem; line-height:1.6; color:#53668f; }
.small-label { color:#7181ac; font-size:.88rem; letter-spacing:.04em; }
.scene-frame { border:4px solid #7189c6; box-shadow:7px 7px 0 #9eacd9; overflow:hidden; background:#b9c9f5; }
.pill { display:inline-block; padding:5px 11px; border:2px solid #8999c7; background:#f7f6ff; margin:4px; color:#4b608e; font-family:'Jua',sans-serif; }
.pixel-card { background:#fbfaff; border:3px solid #7189c6; box-shadow:4px 4px 0 #9eacd9; padding:13px 15px; margin:5px 0 12px; }
.pixel-card h3 { margin:.1rem 0 .45rem; color:#384c76; }
.stButton > button { border:3px solid #667faf!important; border-radius:3px!important; background:#fff3be!important; color:#394c76!important; font-family:'Jua',sans-serif!important; font-size:1.03rem!important; box-shadow:3px 3px 0 #7b88ad!important; min-height:2.55rem; }
.stButton > button:hover { background:#ffe5ef!important; border-color:#d67fa3!important; color:#394c76!important; }
div[data-testid="stMetric"] { background:#f8f7ff; border:2px solid #c1cae9; padding:8px; border-radius:3px; }
.day-strip { display:grid; grid-template-columns:repeat(7,1fr); gap:5px; }
.day-cell { text-align:center; border:2px solid #adb9df; background:#f8f7ff; padding:6px 2px; color:#7181ac; font-size:.76rem; }
.day-cell b { display:block; color:#3e527e; font-size:1.1rem; min-height:1.25rem; }
.day-cell.ok b { color:#28a77e; } .day-cell.no b { color:#d6658c; }
.result-box { text-align:center; padding:22px; background:#fbfaff; border:4px solid #7189c6; box-shadow:6px 6px 0 #9eacd9; }
footer { visibility:hidden; }
</style>
"""

DARK_CSS = """
<style>
.stApp { background:radial-gradient(ellipse at 50% 28%,#273142 0%,#151923 48%,#0b0d13 100%); color:#e7e8ef; }
.block-container { max-width:1320px; }
section[data-testid="stMain"] { color:#e7e8ef; }
.game-header { text-align:center; color:#e8e7ed; padding:0 0 8px; }
.game-header h1 { color:#f0e9dd; text-shadow:0 0 12px #f7a359,2px 3px #111; font-size:2rem; margin:3px 0; }
.game-header .badge { display:inline-block; background:#171b24; border:1px solid #72717a; color:#f0d7a1; padding:5px 12px; margin:3px; font-family:'Jua',sans-serif; letter-spacing:.06em; }
.room-art { max-width:1120px; margin:0 auto; border:3px solid #46434a; border-bottom:0; box-shadow:0 0 30px #000; }
.control-caption { text-align:center; color:#b5b4be; font-size:.88rem; padding:4px 0 9px; }
.screen-frame { max-width:1120px; margin:0 auto; padding:12px; background:linear-gradient(145deg,#42444b,#191b22 18%,#282a31 80%,#505058); border:5px solid #77767a; box-shadow:0 0 0 3px #111,0 12px 30px #000; }
.screen-titlebar { display:flex; justify-content:space-between; color:#b9c3cf; background:#0b0d12; border:1px solid #545864; padding:5px 10px; font:12px monospace; letter-spacing:.08em; margin-bottom:9px; }
.monitor-card { border:4px solid #585a61; background:#080b10; padding:5px; box-shadow:inset 0 0 16px #000; }
.monitor-label { font:12px monospace; letter-spacing:.08em; color:#b9c5d0; background:#10141a; padding:5px 7px; }
.monitor-art { border:2px solid #242a31; line-height:0; background:#101720; }
.sensor-readout { font:11px monospace; color:#aab8ba; line-height:1.55; padding:5px 4px 1px; }
.camera-hint { max-width:1120px; margin:9px auto 0; text-align:center; color:#bab8c0; font-size:.88rem; }
.desk-art { max-width:1120px; margin:0 auto; border-top:3px solid #76513c; box-shadow:0 11px 22px #000; }
.side-card { background:#171a22; border:1px solid #555660; padding:12px; margin:6px 0 12px; color:#dddce3; box-shadow:0 4px 12px #0008; }
.side-card h3 { color:#f0d4a0; font-size:1.12rem; margin:0 0 8px; }
.side-card p,.side-card span { color:#c1c2cb; }
.dark-day-strip { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; }
.dark-day { background:#0d1016; border:1px solid #494b55; text-align:center; color:#aeb1ba; padding:5px 1px; font:10px monospace; }
.dark-day b { display:block; min-height:19px; font: bold 16px monospace; color:#e6d9bb; }
.dark-day.ok b { color:#76d6a4; } .dark-day.no b { color:#ef8291; }
.stButton > button { border:2px solid #7a7170!important; border-radius:1px!important; background:#252831!important; color:#f0e8da!important; font-family:'Jua',sans-serif!important; font-size:.96rem!important; box-shadow:2px 3px 0 #08090d!important; min-height:2.4rem; }
.stButton > button:hover { background:#3c414c!important; border-color:#dfaa77!important; color:#fff!important; }
div[data-testid="stMetric"] { background:#141820; border:1px solid #555b66; color:#eee; padding:7px; }
div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#e6e1d8; }
.stProgress > div > div { background:#d39558!important; }
[data-testid="stCaptionContainer"] { color:#acaeb9; }
</style>
"""

st.markdown(BASE_CSS, unsafe_allow_html=True)


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


def start_scene_svg():
    return '''<svg viewBox="0 0 900 390" width="100%" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated;display:block">
    <rect width="900" height="390" fill="#b9ccf7"/><rect y="0" width="900" height="125" fill="#9eb4ec"/>
    <path d="M0 124h900v75H0z" fill="#707eac"/><path d="M0 138h900v47H0z" fill="#8fa4d1"/>
    <rect x="44" y="72" width="210" height="71" rx="25" fill="#576583" stroke="#e1e3ff" stroke-width="8"/><rect x="57" y="84" width="184" height="47" rx="20" fill="#3e617f"/>
    <path d="M60 106h179v16H60z" fill="#7de2df"/><path d="M100 108h28v5h-28zm55-3h24v5h-24zm43 6h22v5h-22z" fill="#d5fbef"/>
    <path d="M0 208h900v182H0z" fill="#63769b"/><path d="M0 231h900v8H0zm0 135h900v8H0z" fill="#e6e8ff"/>
    <path d="M0 292h900v3H0z" fill="#aab7dc"/><rect x="308" y="212" width="280" height="18" fill="#dbe2ff"/><rect x="330" y="197" width="13" height="23" fill="#384968"/><rect x="346" y="193" width="12" height="27" fill="#222d4c"/><rect x="362" y="199" width="13" height="21" fill="#744d9c"/><rect x="378" y="195" width="12" height="25" fill="#586daa"/>
    <rect x="24" y="257" width="56" height="37" fill="#f2bd72"/><rect x="33" y="245" width="38" height="14" fill="#e987a8"/><rect x="42" y="267" width="12" height="27" fill="#9c739e"/>
    <rect x="727" y="245" width="12" height="114" fill="#fff0c1"/><rect x="727" y="256" width="12" height="13" fill="#e9819d"/><rect x="727" y="283" width="12" height="13" fill="#e9819d"/><rect x="727" y="310" width="12" height="13" fill="#e9819d"/><rect x="727" y="337" width="12" height="13" fill="#e9819d"/>
    <g stroke="#6e5fa5" stroke-width="4" stroke-linecap="square"><path d="M121 205v-40l-12-13m12 30 14-14m-14-1-12-12M614 201v-42l-12-12m12 28 15-17m-15-3-10-12M806 203v-33l-13-12m13 24 13-14"/></g>
    <g fill="#f47ca8"><rect x="104" y="149" width="12" height="9"/><rect x="129" y="172" width="13" height="9"/><rect x="596" y="146" width="12" height="9"/><rect x="623" y="164" width="14" height="9"/><rect x="791" y="154" width="12" height="9"/></g>
    <g fill="#45bcb5"><rect x="176" y="114" width="21" height="8"/><rect x="166" y="106" width="16" height="8"/><rect x="195" y="105" width="15" height="9"/><rect x="485" y="120" width="22" height="9"/><rect x="479" y="111" width="16" height="10"/><rect x="505" y="111" width="16" height="10"/></g>
    <text x="705" y="72" font-size="15" font-family="monospace" fill="#4d5e8e">SEWER TOWN</text></svg>'''


def room_header_svg():
    return '''<svg viewBox="0 0 1120 190" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated">
    <defs><radialGradient id="lamp"><stop stop-color="#ffcf80" stop-opacity=".8"/><stop offset="1" stop-color="#ffb34e" stop-opacity="0"/></radialGradient></defs>
    <rect width="1120" height="190" fill="#12151c"/><path d="M0 0h1120v48H0z" fill="#20232b"/>
    <path d="M0 54h1120v8H0zm0 121h1120v15H0z" fill="#34353b"/>
    <path d="M105 0h18v175h-18zm881 0h17v175h-17z" fill="#282a30"/>
    <path d="M0 62h100v99H0zM1020 61h100v100h-100z" fill="#1b1d24" stroke="#535057" stroke-width="3"/>
    <path d="M15 83h66v53H15zM1038 83h67v53h-67z" fill="#080b10" stroke="#63584f" stroke-width="4"/>
    <path d="M28 94h40v4H28zm0 10h28v3H28zm0 10h36v3H28zm1021-20h44v5h-44zm0 12h30v4h-30z" fill="#5a7b83"/>
    <path d="M0 61h90l18 13H0zm1120 0h-90l-18 13h108z" fill="#75513c"/>
    <ellipse cx="560" cy="61" rx="210" ry="103" fill="url(#lamp)"/>
    <path d="M490 41h140l-14 14h-112z" fill="#4c4039"/><rect x="541" y="49" width="38" height="8" fill="#ffce79"/>
    <path d="M210 51h42l18 25h-78zM868 51h42l18 25h-78z" fill="#312f35" stroke="#8c5b50" stroke-width="4"/>
    <path d="M218 58h26m-26 8h26m624-8h26m-26 8h26" stroke="#e5b678" stroke-width="3"/>
    <path d="M78 164h964" stroke="#111319" stroke-width="9"/><circle cx="86" cy="173" r="3" fill="#c87763"/><circle cx="1036" cy="173" r="3" fill="#c87763"/>
    <text x="19" y="27" fill="#b8c2c7" font-family="monospace" font-size="13">SEWER CONTROL / NIGHT WATCH</text>
    </svg>'''


def desk_svg():
    return '''<svg viewBox="0 0 1120 92" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated">
    <rect width="1120" height="92" fill="#17151a"/><path d="M0 7h1120v13H0z" fill="#805a40"/><path d="M0 20h1120v9H0z" fill="#49352f"/>
    <path d="M0 29h1120v63H0z" fill="#262329"/><path d="M83 47h225l-20 23H101z" fill="#ded7cb"/><path d="M103 52h166v4H103zm12 9h126v3H115z" fill="#9b9ba0"/>
    <rect x="430" y="40" width="74" height="26" fill="#31343d" stroke="#777780" stroke-width="3"/><rect x="439" y="46" width="56" height="12" fill="#91bbbd"/><circle cx="457" cy="52" r="3" fill="#f4c679"/>
    <path d="M842 44h35v27h-35z" fill="#201b28" stroke="#796176" stroke-width="3"/><circle cx="853" cy="54" r="5" fill="#f37ea8"/><circle cx="868" cy="54" r="5" fill="#f37ea8"/><path d="M854 64h13" stroke="#f5d2cd" stroke-width="2"/>
    <path d="M1027 33h14v49h-14z" fill="#dadbe2"/><path d="M1021 31h27v6h-27z" fill="#ce7480"/><path d="M1027 45h14v5h-14zm0 13h14v5h-14z" fill="#526b9a"/>
    <circle cx="600" cy="52" r="12" fill="#363942" stroke="#797b81" stroke-width="3"/><path d="M600 40v24m-12-12h24m-20-8 16 16m0-16-16 16" stroke="#a4a8ae" stroke-width="2"/>
    </svg>'''


def monitor_svg(route, idx):
    water = int(route[0] * 24 + 14)
    debris = int(route[2] * 8)
    rust_count = int(route[3] * 5)
    debris_rects = "".join(f'<rect x="{218+j*17}" y="{74-(j%2)*8}" width="8" height="7" fill="{["#cb6882","#52b9ad","#d7ad62"][j%3]}"/>' for j in range(debris))
    rust_rects = "".join(f'<rect x="{85+j*21}" y="{44+(j%2)*24}" width="9" height="8" fill="#a75d61"/>' for j in range(rust_count))
    glints = "".join(f'<rect x="{35+j*51}" y="{18+(j%3)*9}" width="2" height="2" fill="#b6c4bd" opacity=".55"/>' for j in range(10))
    return f'''<svg viewBox="0 0 330 155" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated">
    <rect width="330" height="155" fill="#111722"/><rect y="12" width="330" height="127" fill="#252a35"/>
    <path d="M0 21h330v10H0zm0 96h330v13H0z" fill="#343943"/><path d="M12 41h32v61H12zm276-5h28v66h-28z" fill="#1b2029"/>
    <rect x="31" y="40" width="268" height="72" rx="32" fill="#45464a" stroke="#858184" stroke-width="7"/>
    <rect x="46" y="61" width="238" height="47" rx="22" fill="#203c48"/>
    <rect x="48" y="{108-water}" width="234" height="{water}" rx="12" fill="#4f8d91"/><path d="M63 {106-water}h39v4H63zm95 8h32v3h-32zm68-10h39v4h-39z" fill="#bed2c6" opacity=".8"/>
    {debris_rects}{rust_rects}{glints}
    <path d="M78 45l19 11m149-7-15 12" stroke="#a9a39a" stroke-width="3" opacity=".5"/>
    <rect x="7" y="5" width="47" height="15" fill="#0a0d12"/><text x="11" y="16" font-size="10" font-family="monospace" fill="#c4cbd0">CAM 0{idx+1}</text>
    <circle cx="310" cy="13" r="4" fill="#c66a72"/><rect y="140" width="330" height="15" fill="#151922"/>
    <text x="12" y="151" font-size="8" font-family="monospace" fill="#9ca6aa">LIVE / DRAIN {idx+1:02d}</text></svg>'''


def risk(route):
    z = st.session_state.bias + sum(w * x for w, x in zip(st.session_state.weights, route))
    z = max(-20, min(20, z))
    return 1 / (1 + math.exp(-z))


def new_day():
    routes = [[random.uniform(.13, .52), random.uniform(.10, .48), random.uniform(.08, .45), random.uniform(.10, .48)] for _ in range(4)]
    target = random.randrange(4)
    for j in range(4):
        routes[target][j] = min(.98, routes[target][j] + random.uniform(.38, .56))
    st.session_state.routes = routes
    st.session_state.target = target
    st.session_state.last_result = None
    st.session_state.screen = "game"


def train_after_reveal():
    routes, target = st.session_state.routes, st.session_state.target
    labels = [1.0 if i == target else 0.0 for i in range(4)]
    probs = [risk(route) for route in routes]
    grad_w = [sum((p-y)*route[k] for route, p, y in zip(routes, probs, labels))/4 for k in range(4)]
    grad_b = sum(p-y for p, y in zip(probs, labels))/4
    magnitude = math.sqrt(sum(g*g for g in grad_w) + grad_b*grad_b)
    st.session_state.weights = [w - LEARNING_RATE*g for w, g in zip(st.session_state.weights, grad_w)]
    st.session_state.bias -= LEARNING_RATE * grad_b
    eps = 1e-8
    after = [risk(route) for route in routes]
    st.session_state.loss = -sum(y*math.log(max(eps,p))+(1-y)*math.log(max(eps,1-p)) for y,p in zip(labels,after))/4
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


def calendar_html(dark=False):
    cells = []
    for i, result in enumerate(st.session_state.calendar, 1):
        cls = "ok" if result == "O" else "no" if result == "X" else ""
        if dark:
            cells.append(f'<div class="dark-day {cls}">D{i}<b>{result or "·"}</b></div>')
        else:
            cells.append(f'<div class="day-cell {cls}">DAY {i}<b>{result or "·"}</b></div>')
    return '<div class="dark-day-strip">' + "".join(cells) + '</div>' if dark else '<div class="day-strip">' + "".join(cells) + '</div>'


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
    st.markdown('<div class="scene-frame">' + start_scene_svg() + '</div>', unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1, 1])
    with center:
        if st.button("▶  START  ◀", use_container_width=True, key="start_game"):
            st.session_state.day = 1
            st.session_state.wins = 0
            st.session_state.calendar = ["", "", "", "", "", "", ""]
            st.session_state.weights = [0.35, 0.35, 0.35, 0.35]
            st.session_state.bias = -0.75
            new_day()
            st.rerun()
    st.markdown('<div class="hero"><p><span class="pill">4분할 CCTV</span><span class="pill">7일 근무</span><span class="pill">AI 경사하강법</span></p></div>', unsafe_allow_html=True)

elif st.session_state.screen == "game":
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(f'<div class="game-header"><span class="badge">하수관 관리부 · 야간 근무</span><span class="badge">NIGHT {st.session_state.day}</span><span class="badge">1 AM</span><h1>관제실 — 이상 관로를 찾아라</h1><div>네 개의 CCTV를 확인하고 문제가 있는 관로를 선택하세요.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="room-art">' + room_header_svg() + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="screen-frame"><div class="screen-titlebar"><span>▣ SEWER CCTV ARRAY</span><span>REC ● &nbsp; SIGNAL STABLE</span></div>', unsafe_allow_html=True)
    monitor_cols = st.columns(2, gap="small")
    for idx, route in enumerate(st.session_state.routes):
        col = monitor_cols[idx % 2]
        with col:
            score = risk(route)
            st.markdown(f'<div class="monitor-card"><div class="monitor-label">CAM 0{idx+1}　/　AI 이상 확률 {score:.0%}</div><div class="monitor-art">{monitor_svg(route, idx)}</div><div class="sensor-readout">압력 {route[0]:.2f}　소음 {route[1]:.2f}<br>침전물 {route[2]:.2f}　부식 {route[3]:.2f}</div></div>', unsafe_allow_html=True)
            if st.button(f"CAM 0{idx+1} · 관로 점검", key=f"inspect_{st.session_state.cycle}_{st.session_state.day}_{idx}", use_container_width=True):
                choose_route(idx)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="camera-hint">▣ 화면의 센서 기록을 비교해 이상이 있는 관로를 골라주세요. 선택하면 정답 공개 후 AI가 학습합니다.</div>', unsafe_allow_html=True)
    st.markdown('<div class="desk-art">' + desk_svg() + '</div>', unsafe_allow_html=True)

    left, right = st.columns([1.5, 1], gap="medium")
    with left:
        st.markdown('<div class="side-card"><h3>🧠 경사하강법 학습 노트</h3><span>로지스틱 회귀가 압력·소음·침전물·부식 특징의 가중치를 학습합니다.</span></div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Loss · BCE", "대기" if st.session_state.loss is None else f'{st.session_state.loss:.3f}')
        m2.metric("Gradient 크기", "대기" if st.session_state.gradient is None else f'{st.session_state.gradient:.3f}')
        for label, weight in zip(FEATURES, st.session_state.weights):
            st.progress(min(1.0, max(0.0, (weight + 1) / 2)), text=f"{label} 가중치　{weight:+.2f}")
        st.caption(f"학습률 η = {LEARNING_RATE:.2f} · 매 점검 후 4개 관로 라벨로 업데이트")
    with right:
        st.markdown('<div class="side-card"><h3>📅 이번 주 근무 달력</h3>' + calendar_html(dark=True) + f'<p style="margin:.7rem 0 0">현재까지 성공: {st.session_state.wins}회</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="side-card"><h3>근무 지침</h3><span>7일 동안 이상 관로를 찾아보세요. 5회 이상 성공하면 승진, 3~4회면 다음 주 재도전, 3회 미만이면 해고입니다.</span></div>', unsafe_allow_html=True)
    if st.session_state.last_result:
        result = st.session_state.last_result
        if result["success"]:
            st.success(f'정확해요! CAM 0{result["target"]+1}에서 이상을 찾았습니다. 경사하강법 업데이트 후 Loss: {st.session_state.loss:.3f}')
        else:
            st.error(f'놓쳤습니다. 선택한 곳은 CAM 0{result["chosen"]+1}, 실제 이상은 CAM 0{result["target"]+1}이었습니다. Loss: {st.session_state.loss:.3f}')
        if st.button("다음 야간 근무 →", key=f"next_{st.session_state.cycle}_{st.session_state.day}", use_container_width=True):
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
    _, center, _ = st.columns([1, 1, 1])
    with center:
        if st.button(next_label, use_container_width=True, key="summary_action"):
            if action == "retry":
                restart_cycle()
            else:
                st.session_state.screen = "start"
            st.rerun()
