import math
import random

import streamlit as st

st.set_page_config(page_title="하수관 AI 정비대", page_icon="🫧", layout="wide", initial_sidebar_state="collapsed")

FEATURES = ["압력", "소음", "침전물", "부식"]
LEARNING_RATE = 0.85

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
:root { --ink:#34365e; --outline:#6263a4; --lav:#d9c9f3; --pink:#f5aed1; --mint:#a7e5d3; --paper:#fff8ee; }
html, body, [class*="css"] { font-family:'Gowun Dodum',sans-serif; }
.stApp { background:#c9d8fa; color:var(--ink); }
.block-container { max-width:1260px; padding-top:.8rem; padding-bottom:2rem; }
h1,h2,h3 { font-family:'Jua',sans-serif!important; }
.hero { text-align:center; padding:5px 0 8px; }
.hero h1 { font-size:2.9rem; margin:.05rem 0; color:#414879; text-shadow:2px 3px #fff; }
.hero p { color:#555d89; line-height:1.55; }
.pixel-frame { border:4px solid var(--outline); box-shadow:6px 6px 0 #9299c5; background:#fff8ee; }
.pixel-panel { background:#fff8ee; border:3px solid var(--outline); box-shadow:4px 4px 0 #9299c5; padding:12px 14px; margin:6px 0 12px; }
.pixel-panel h3 { margin:.1rem 0 .45rem; color:#414879; }
.small-label { color:#666e9a; font-size:.86rem; }
.pill { display:inline-block; padding:4px 10px; border:2px solid #7479ad; background:#fff8ee; margin:3px; color:#4b5685; font-family:'Jua',sans-serif; }
.stButton > button { border:3px solid #5d6399!important; border-radius:2px!important; background:#fff0af!important; color:#34365e!important; font-family:'Jua',sans-serif!important; font-size:1.02rem!important; box-shadow:3px 3px 0 #9299c5!important; min-height:2.55rem; }
.stButton > button:hover { background:#ffc9dc!important; border-color:#8e5c9c!important; color:#34365e!important; }
div[data-testid="stMetric"] { background:#fff8ee; border:2px solid #aeb4d5; padding:8px; border-radius:2px; }
.day-strip { display:grid; grid-template-columns:repeat(7,1fr); gap:5px; }
.day-cell { text-align:center; border:2px solid #aeb4d5; background:#fff8ee; padding:6px 2px; color:#69719b; font-size:.76rem; }
.day-cell b { display:block; color:#414879; font-size:1.1rem; min-height:1.2rem; }
.day-cell.ok b { color:#188e77; } .day-cell.no b { color:#d2547d; }
.dialog { border:4px solid #f8f3ec; outline:3px solid #35354c; box-shadow:5px 5px 0 #34364e; background:#11131d; color:#fff9ed; padding:12px 17px; margin:10px auto 12px; max-width:1120px; font-family:'Gowun Dodum',sans-serif; }
.dialog-name { display:inline-block; border:2px solid #eee6d4; background:#1b1d2b; padding:3px 10px; margin-top:-27px; color:#ffe78d; font-family:'Jua',sans-serif; }
.dialog-text { font-size:1rem; line-height:1.6; margin-top:5px; }
.room-scene { max-width:1120px; margin:0 auto; border:4px solid #53577e; box-shadow:6px 6px 0 #9299c5; }
.screen-frame { max-width:1120px; margin:8px auto 0; padding:10px; background:#555773; border:4px solid #34354e; box-shadow:0 0 0 3px #8588ad,6px 8px 0 #444765; }
.screen-titlebar { display:flex; justify-content:space-between; color:#def4e5; background:#292d42; border:2px solid #73789a; padding:5px 10px; font:12px monospace; letter-spacing:.06em; margin-bottom:8px; }
.monitor-card { border:3px solid #666b90; background:#25293b; padding:5px; box-shadow:inset 0 0 0 2px #171a28; }
.monitor-label { font:12px monospace; color:#e4e6d9; background:#1d2030; padding:5px 7px; }
.monitor-art { border:2px solid #8588ad; line-height:0; background:#8fa4d1; }
.sensor-readout { font:11px monospace; color:#e6e2d5; line-height:1.55; padding:5px 4px 1px; }
.dark-day-strip { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; }
.dark-day { background:#333750; border:2px solid #777ca0; text-align:center; color:#e4e2d6; padding:5px 1px; font:10px monospace; }
.dark-day b { display:block; min-height:19px; font:bold 16px monospace; color:#f6e8ac; }
.dark-day.ok b { color:#8ee3b6; } .dark-day.no b { color:#ff9caf; }
.side-card { background:#fff8ee; border:3px solid #7178a8; box-shadow:3px 3px 0 #a4a9cc; padding:11px; margin:6px 0 12px; color:#404668; }
.side-card h3 { color:#474b7b; font-size:1.1rem; margin:0 0 7px; }
.stProgress > div > div { background:#5ab7a4!important; }
footer { visibility:hidden; }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


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


def town_svg():
    return '''<svg viewBox="0 0 960 410" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated">
    <rect width="960" height="410" fill="#b7d9f3"/><rect y="0" width="960" height="160" fill="#a6c8ed"/>
    <path d="M0 148h960v57H0z" fill="#626b9d"/><path d="M0 160h960v31H0z" fill="#7896bd"/>
    <rect x="22" y="67" width="194" height="76" rx="25" fill="#e4c57b" stroke="#5d6399" stroke-width="6"/><rect x="38" y="80" width="164" height="50" rx="18" fill="#415d87"/>
    <circle cx="72" cy="103" r="11" fill="#5ad3dc" stroke="#f7e6a8" stroke-width="4"/><circle cx="112" cy="103" r="11" fill="#5ad3dc" stroke="#f7e6a8" stroke-width="4"/><circle cx="152" cy="103" r="11" fill="#5ad3dc" stroke="#f7e6a8" stroke-width="4"/><path d="M53 119h39v9H53zm72 0h44v9h-44z" fill="#ef94b5"/>
    <path d="M0 205h960v205H0z" fill="#747da8"/><path d="M0 224h960v9H0zm0 151h960v9H0z" fill="#e3e5f5"/><path d="M0 292h960v4H0z" fill="#b4bedb"/>
    <path d="M241 0h190v149H241zM616 0h192v149H616z" fill="#6077ad"/><path d="M255 10h162v122H255zM630 10h164v122H630z" fill="#7792c2"/>
    <g fill="#f58eb8"><rect x="274" y="86" width="15" height="15"/><rect x="303" y="66" width="20" height="12"/><rect x="371" y="103" width="24" height="14"/><rect x="657" y="80" width="21" height="14"/><rect x="740" y="45" width="17" height="13"/></g>
    <g fill="#51c7be"><rect x="333" y="26" width="25" height="15"/><rect x="347" y="15" width="23" height="14"/><rect x="689" y="33" width="29" height="15"/><rect x="710" y="23" width="20" height="14"/></g>
    <g stroke="#6f5798" stroke-width="5" stroke-linecap="square"><path d="M270 207v-43l-14-13m14 30 18-18m-18-1-12-13M514 207v-48l-15-14m15 32 17-17m-17-2-12-14M841 207v-42l-14-14m14 29 18-17"/></g>
    <g fill="#f29abd"><rect x="247" y="148" width="16" height="12"/><rect x="280" y="168" width="16" height="12"/><rect x="490" y="140" width="16" height="13"/><rect x="526" y="164" width="17" height="12"/><rect x="816" y="148" width="16" height="12"/></g>
    <g fill="#54c9c1"><rect x="391" y="175" width="25" height="12"/><rect x="382" y="164" width="19" height="13"/><rect x="410" y="163" width="19" height="13"/><rect x="779" y="177" width="25" height="12"/></g>
    <path d="M217 210h523v12H217z" fill="#f2e7d5"/><g fill="#222c49"><rect x="385" y="199" width="11" height="18"/><rect x="401" y="195" width="10" height="22"/><rect x="417" y="200" width="11" height="17"/><rect x="433" y="196" width="10" height="21"/></g>
    <rect x="854" y="220" width="12" height="134" fill="#fff1c8"/><path d="M854 231h12v13h-12zm0 29h12v13h-12zm0 29h12v13h-12zm0 29h12v13h-12" fill="#e783a4"/>
    <rect x="37" y="252" width="62" height="41" fill="#f2bd72"/><rect x="48" y="240" width="40" height="14" fill="#df89ad"/><rect x="62" y="267" width="12" height="26" fill="#635b91"/>
    <rect x="698" y="247" width="58" height="40" fill="#e8b3c9"/><rect x="705" y="235" width="44" height="14" fill="#f1d98c"/><rect x="718" y="261" width="14" height="26" fill="#726193"/>
    <g fill="#f8e6a5"><circle cx="318" cy="207" r="5"/><circle cx="571" cy="207" r="5"/><circle cx="797" cy="207" r="5"/></g>
    <text x="771" y="62" font-size="14" font-family="monospace" fill="#fff1c8">DRAIN TOWN</text></svg>'''


def room_svg():
    return '''<svg viewBox="0 0 1120 175" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated">
    <rect width="1120" height="175" fill="#827cac"/><rect y="0" width="1120" height="29" fill="#625d88"/><path d="M0 148h1120v27H0z" fill="#d5bde3"/>
    <path d="M0 30h1120v8H0zM0 136h1120v8H0z" fill="#b699c9"/><path d="M61 38h125v89H61zM934 38h125v89H934z" fill="#706d9f" stroke="#d5c2df" stroke-width="5"/>
    <path d="M76 53h96v62H76zM949 53h96v62h-96z" fill="#24334f"/><path d="M84 91h80v20H84zM957 88h82v23h-82z" fill="#506f9b"/>
    <path d="M237 0h646v29H237z" fill="#5f5a84"/><path d="M518 0h83v22h-83z" fill="#f4d184"/><path d="M530 22h59v6h-59z" fill="#fff0c1"/>
    <path d="M297 35h13v93h-13zm512 0h13v93h-13z" fill="#aa8db7"/><path d="M309 56h500v9H309z" fill="#dbb6c8"/>
    <g fill="#4b4c71"><rect x="239" y="74" width="34" height="42"/><rect x="846" y="72" width="38" height="44"/></g>
    <path d="M256 84h17m573-2h18" stroke="#a9d8d0" stroke-width="4"/><path d="M0 163h1120" stroke="#765d82" stroke-width="4"/>
    <text x="22" y="22" fill="#f4e9d8" font-family="monospace" font-size="13">DRAIN TOWN · NIGHT SHIFT CONTROL ROOM</text>
    </svg>'''


def monitor_svg(route, idx):
    water = int(route[0] * 24 + 14)
    debris = int(route[2] * 8)
    rust_count = int(route[3] * 5)
    debris_rects = "".join(f'<rect x="{218+j*17}" y="{74-(j%2)*8}" width="8" height="7" fill="{["#cb6882", "#52b9ad", "#d7ad62"][j%3]}"/>' for j in range(debris))
    rust_rects = "".join(f'<rect x="{85+j*21}" y="{44+(j%2)*24}" width="9" height="8" fill="#a75d61"/>' for j in range(rust_count))
    return f'''<svg viewBox="0 0 330 155" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated">
    <rect width="330" height="155" fill="#9ec7e8"/><rect y="12" width="330" height="127" fill="#64769e"/>
    <path d="M0 21h330v10H0zm0 96h330v13H0z" fill="#9da8ce"/><path d="M12 41h32v61H12zm276-5h28v66h-28z" fill="#5b5c82"/>
    <rect x="31" y="40" width="268" height="72" rx="32" fill="#d3b6cd" stroke="#f1dfdb" stroke-width="7"/>
    <rect x="46" y="61" width="238" height="47" rx="22" fill="#31586e"/>
    <rect x="48" y="{108-water}" width="234" height="{water}" rx="12" fill="#63c9cf"/><path d="M63 {106-water}h39v4H63zm95 8h32v3h-32zm68-10h39v4h-39z" fill="#d8fff1" opacity=".8"/>
    {debris_rects}{rust_rects}<path d="M78 45l19 11m149-7-15 12" stroke="#916580" stroke-width="3" opacity=".65"/>
    <rect x="7" y="5" width="47" height="15" fill="#202338"/><text x="11" y="16" font-size="10" font-family="monospace" fill="#fff2d6">CAM 0{idx+1}</text>
    <circle cx="310" cy="13" r="4" fill="#ec7c91"/><rect y="140" width="330" height="15" fill="#30334a"/>
    <text x="12" y="151" font-size="8" font-family="monospace" fill="#d6e4dc">LIVE / DRAIN {idx+1:02d}</text></svg>'''


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
    st.session_state.gradient = math.sqrt(sum(g*g for g in grad_w) + grad_b*grad_b)
    st.session_state.weights = [w - LEARNING_RATE*g for w, g in zip(st.session_state.weights, grad_w)]
    st.session_state.bias -= LEARNING_RATE * grad_b
    eps = 1e-8
    after = [risk(route) for route in routes]
    st.session_state.loss = -sum(y*math.log(max(eps,p))+(1-y)*math.log(max(eps,1-p)) for y,p in zip(labels,after))/4


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


def reset_week(increment=False):
    if increment:
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
    st.markdown('<div class="hero"><div class="small-label">A PIXEL-ART SEWER TOWN STORY</div><h1>하수관 AI 정비대</h1><p>작은 마을의 하수관을 지키는 야간 정비사가 되어<br>네 개의 CCTV 속 이상 징후를 찾아보세요.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="pixel-frame">' + town_svg() + '</div>', unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1, 1])
    with center:
        if st.button("▶  START  ◀", use_container_width=True, key="start_game"):
            st.session_state.cycle = 1
            reset_week()
            st.rerun()
    st.markdown('<div class="hero"><p><span class="pill">4분할 CCTV</span><span class="pill">7일 야간 근무</span><span class="pill">경사하강법으로 AI 학습</span></p></div>', unsafe_allow_html=True)

elif st.session_state.screen == "game":
    st.markdown(f'<div class="hero"><span class="pill">근무 {st.session_state.cycle}회차</span><span class="pill">DAY {st.session_state.day} / 7</span><span class="pill">NIGHT {st.session_state.day} · 1 AM</span><h1>작은 하수도 마을의 관제실</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="room-scene">' + room_svg() + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="screen-frame"><div class="screen-titlebar"><span>▣ SEWER CCTV ARRAY</span><span>REC ● &nbsp; SIGNAL STABLE</span></div>', unsafe_allow_html=True)
    monitor_cols = st.columns(2, gap="small")
    for idx, route in enumerate(st.session_state.routes):
        with monitor_cols[idx % 2]:
            score = risk(route)
            st.markdown(f'<div class="monitor-card"><div class="monitor-label">CAM 0{idx+1}　/　AI 이상 확률 {score:.0%}</div><div class="monitor-art">{monitor_svg(route, idx)}</div><div class="sensor-readout">압력 {route[0]:.2f}　소음 {route[1]:.2f}<br>침전물 {route[2]:.2f}　부식 {route[3]:.2f}</div></div>', unsafe_allow_html=True)
            if st.button(f"CAM 0{idx+1} · 관로 점검", key=f"inspect_{st.session_state.cycle}_{st.session_state.day}_{idx}", use_container_width=True):
                choose_route(idx)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="dialog"><span class="dialog-name">야간 정비사</span><div class="dialog-text">네 개의 CCTV를 확인해 이상이 있는 하수관을 골라야 해. 작은 단서를 잘 살펴보자… AI도 매일 정답을 배워서 조금씩 나아질 거야!</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.5, 1], gap="medium")
    with left:
        st.markdown('<div class="side-card"><h3>🧠 경사하강법 학습 노트</h3><span>관로 센서 특징에 따라 이상 확률을 예측하고, 점검 결과의 오차로 모델 가중치를 업데이트합니다.</span></div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Loss · BCE", "대기 중" if st.session_state.loss is None else f'{st.session_state.loss:.3f}')
        m2.metric("Gradient 크기", "대기 중" if st.session_state.gradient is None else f'{st.session_state.gradient:.3f}')
        for label, weight in zip(FEATURES, st.session_state.weights):
            st.progress(min(1.0, max(0.0, (weight + 1) / 2)), text=f"{label} 가중치　{weight:+.2f}")
        st.caption(f"학습률 η = {LEARNING_RATE:.2f} · 매 점검 후 네 구간 라벨을 이용해 갱신")
    with right:
        st.markdown('<div class="side-card"><h3>📅 이번 주 기록</h3>' + calendar_html(dark=True) + f'<p style="margin:.7rem 0 0">현재까지 성공: {st.session_state.wins}회</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="side-card"><h3>근무 지침</h3><span>7일 동안 이상 관로를 찾아보세요. 5회 이상 성공하면 승진, 3~4회면 다음 주 재도전, 3회 미만이면 해고입니다.</span></div>', unsafe_allow_html=True)
    if st.session_state.last_result:
        result = st.session_state.last_result
        if result["success"]:
            st.success(f'찾았다! CAM 0{result["target"]+1}에 이상이 있었어. 경사하강법이 새 기록을 학습했어. (Loss {st.session_state.loss:.3f})')
        else:
            st.error(f'아차, 이상은 CAM 0{result["target"]+1}이었어. 다음에는 AI가 이번 오차를 반영할 거야. (Loss {st.session_state.loss:.3f})')
        if st.session_state.day < 7 and st.button("다음 날 근무하기 →", key=f"next_{st.session_state.cycle}_{st.session_state.day}", use_container_width=True):
            st.session_state.day += 1
            st.session_state.last_result = None
            new_day()
            st.rerun()

elif st.session_state.screen == "summary":
    wins = st.session_state.wins
    if wins >= 5:
        heading, mood, message = "승진 축하해요!", "🌟", f"7일 중 {wins}회 성공! 작은 마을 하수관 관리팀의 팀장으로 승진했습니다."
        next_label, action = "처음 화면으로", "start"
    elif wins >= 3:
        heading, mood, message = "한 주 더 도전!", "🌱", f"7일 중 {wins}회 성공했습니다. 조금 더 경험을 쌓을 기회가 생겼어요."
        next_label, action = "다음 7일 시작", "retry"
    else:
        heading, mood, message = "오늘은 여기까지…", "🌧️", f"7일 중 {wins}회 성공했습니다. 이번에는 회사를 떠나게 되었지만, 배운 내용을 기억해요."
        next_label, action = "처음 화면으로", "start"
    st.markdown(f'<div class="result-box"><div style="font-size:4rem">{mood}</div><div class="small-label">주간 근무 결산 · {st.session_state.cycle}회차</div><h1>{heading}</h1><p>{message}</p>{calendar_html()}</div>', unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1, 1])
    with center:
        if st.button(next_label, use_container_width=True, key="summary_action"):
            if action == "retry":
                reset_week(increment=True)
            else:
                st.session_state.screen = "start"
            st.rerun()
