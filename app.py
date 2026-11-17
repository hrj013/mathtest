import math
import random

import streamlit as st

st.set_page_config(page_title="하수관 AI 정비대", page_icon="🫧", layout="wide", initial_sidebar_state="collapsed")

FEATURES = ["압력", "소음", "침전물", "부식"]
FEATURE_KEYS = ["pressure", "noise", "sediment", "corrosion"]
FEATURE_LABELS = dict(zip(FEATURE_KEYS, FEATURES))
LEARNING_RATE = 1.2

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
:root { --ink:#34365e; --outline:#6263a4; --lav:#d9c9f3; --pink:#f5aed1; --mint:#a7e5d3; --paper:#fff8ee; }
html, body, [class*="css"] { font-family:'Gowun Dodum',sans-serif; }
.stApp { background:#c9d8fa; color:var(--ink); }
.block-container { max-width:1300px; padding-top:.7rem; padding-bottom:2rem; }
h1,h2,h3 { font-family:'Jua',sans-serif!important; }
.hero { text-align:center; padding:4px 0 7px; }
.hero h1 { font-size:2.55rem; margin:.05rem 0; color:#414879; text-shadow:2px 3px #fff; }
.hero p { color:#555d89; line-height:1.55; margin:.2rem 0; }
.pill { display:inline-block; padding:4px 10px; border:2px solid #7479ad; background:#fff8ee; margin:3px; color:#4b5685; font-family:'Jua',sans-serif; }
.pixel-panel { background:#fff8ee; border:3px solid var(--outline); box-shadow:4px 4px 0 #9299c5; padding:12px 14px; margin:6px 0 12px; }
.pixel-panel h3 { margin:.1rem 0 .45rem; color:#414879; }
.small-label { color:#666e9a; font-size:.86rem; }
.room-frame { border:4px solid #6263a4; box-shadow:6px 6px 0 #9299c5; background:#b9c9e6; padding:10px; }
.room-wall { background:#8d88b4; border:4px solid #68628f; min-height:84px; padding:12px; text-align:center; color:#fff1cf; font:13px monospace; letter-spacing:.08em; }
.monitor-card { border:3px solid #666b90; background:#25293b; padding:5px; box-shadow:inset 0 0 0 2px #171a28; margin:4px 0 8px; }
.monitor-label { font:12px monospace; color:#e4e6d9; background:#1d2030; padding:5px 7px; }
.monitor-art { border:2px solid #8588ad; line-height:0; background:#8fa4d1; }
.sensor-readout { font:11px monospace; color:#e6e2d5; line-height:1.55; padding:5px 4px 1px; }
.furniture { min-height:220px; background:#ece4f4; border:3px solid #7679a9; box-shadow:4px 4px 0 #a5a9ca; text-align:center; padding:12px 8px; margin:5px 0; }
.furniture h3 { color:#454b7b; margin:7px 0; }
.furniture-art { margin:12px auto; width:100%; max-width:210px; }
.chair { text-align:center; padding:7px; color:#646993; }
.dialog { border:4px solid #f8f3ec; outline:3px solid #35354c; box-shadow:5px 5px 0 #34364e; background:#11131d; color:#fff9ed; padding:11px 16px; margin:10px auto 12px; max-width:1150px; }
.dialog-name { display:inline-block; border:2px solid #eee6d4; background:#1b1d2b; padding:3px 10px; color:#ffe78d; font-family:'Jua',sans-serif; }
.dialog-text { font-size:.96rem; line-height:1.6; margin-top:5px; }
.stButton > button { border:3px solid #5d6399!important; border-radius:2px!important; background:#fff0af!important; color:#34365e!important; font-family:'Jua',sans-serif!important; font-size:1rem!important; box-shadow:3px 3px 0 #9299c5!important; min-height:2.5rem; }
.stButton > button:hover { background:#ffc9dc!important; border-color:#8e5c9c!important; color:#34365e!important; }
div[data-testid="stMetric"] { background:#fff8ee; border:2px solid #aeb4d5; padding:8px; border-radius:2px; }
.day-strip { display:grid; grid-template-columns:repeat(7,1fr); gap:5px; }
.day-cell { text-align:center; border:2px solid #aeb4d5; background:#fff8ee; padding:6px 2px; color:#69719b; font-size:.76rem; }
.day-cell b { display:block; color:#414879; font-size:1.1rem; min-height:1.2rem; }
.day-cell.ok b { color:#188e77; } .day-cell.no b { color:#d2547d; }
.expanded { background:#fff8ee; border:4px solid #6263a4; box-shadow:7px 7px 0 #9299c5; padding:18px; }
.stProgress > div > div { background:#5ab7a4!important; }
footer { visibility:hidden; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def init_state():
    defaults = {
        "screen": "start", "cycle": 1, "day": 1, "wins": 0,
        "calendar": ["", "", "", "", "", "", ""],
        "weights": [0.0, 0.0, 0.0, 0.0], "bias": 0.0,
        "routes": [], "target": 0, "last_result": None,
        "loss": None, "gradient": None, "examples": [], "trained_days": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def make_training_examples():
    """Create a balanced labeled teaching set with varied fault signatures."""
    examples = []
    for i in range(32):
        faulty = i >= 16
        features = [random.uniform(.08, .55) for _ in FEATURES]
        if faulty:
            # Different defects show different sensor clues; no single sensor is always enough.
            primary = (i - 16) % len(FEATURES)
            features[primary] = random.uniform(.68, .98)
            for j in range(len(FEATURES)):
                if j != primary and random.random() < .38:
                    features[j] = random.uniform(.55, .82)
        examples.append({"id": f"R{i+1:02d}", "features": features, "label": int(faulty)})
    random.shuffle(examples)
    return examples


def make_day_routes():
    routes = [[random.uniform(.12, .53) for _ in FEATURES] for _ in range(4)]
    target = random.randrange(4)
    primary = random.randrange(len(FEATURES))
    routes[target][primary] = random.uniform(.72, .98)
    for j in range(len(FEATURES)):
        if j != primary and random.random() < .45:
            routes[target][j] = random.uniform(.57, .84)
    return routes, target


def town_svg():
    return '''<svg viewBox="0 0 960 300" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated">
    <rect width="960" height="300" fill="#b7d9f3"/><rect y="0" width="960" height="102" fill="#a6c8ed"/>
    <path d="M0 102h960v45H0z" fill="#626b9d"/><path d="M0 115h960v23H0z" fill="#7896bd"/><path d="M0 147h960v153H0z" fill="#747da8"/>
    <rect x="30" y="46" width="194" height="64" rx="22" fill="#e4c57b" stroke="#5d6399" stroke-width="6"/><rect x="45" y="57" width="164" height="42" rx="16" fill="#415d87"/>
    <circle cx="78" cy="78" r="9" fill="#5ad3dc" stroke="#f7e6a8" stroke-width="4"/><circle cx="118" cy="78" r="9" fill="#5ad3dc" stroke="#f7e6a8" stroke-width="4"/><circle cx="158" cy="78" r="9" fill="#5ad3dc" stroke="#f7e6a8" stroke-width="4"/><path d="M58 91h39v7H58zm72 0h44v7h-44z" fill="#ef94b5"/>
    <path d="M250 0h178v102H250zM620 0h192v102H620z" fill="#6077ad"/><g fill="#f58eb8"><rect x="278" y="48" width="15" height="15"/><rect x="320" y="61" width="20" height="12"/><rect x="375" y="37" width="24" height="14"/><rect x="665" y="53" width="21" height="14"/><rect x="744" y="32" width="17" height="13"/></g><g fill="#51c7be"><rect x="345" y="17" width="25" height="15"/><rect x="690" y="15" width="29" height="15"/><rect x="718" y="23" width="20" height="14"/></g>
    <path d="M0 174h960v7H0zm0 98h960v7H0z" fill="#e3e5f5"/><path d="M0 225h960v3H0z" fill="#b4bedb"/>
    <g stroke="#6f5798" stroke-width="5" stroke-linecap="square"><path d="M270 173v-32l-14-13m14 22 18-16m-18-1-12-11M514 173v-35l-15-13m15 24 17-16m-17-2-12-12M841 173v-32l-14-13m14 22 18-16"/></g><g fill="#f29abd"><rect x="247" y="127" width="16" height="12"/><rect x="280" y="144" width="16" height="12"/><rect x="490" y="125" width="16" height="12"/><rect x="526" y="143" width="17" height="12"/><rect x="816" y="127" width="16" height="12"/></g>
    <path d="M220 174h520v10H220z" fill="#f2e7d5"/><g fill="#222c49"><rect x="385" y="165" width="11" height="17"/><rect x="401" y="161" width="10" height="21"/><rect x="417" y="166" width="11" height="16"/><rect x="433" y="162" width="10" height="20"/></g>
    <rect x="855" y="187" width="11" height="90" fill="#fff1c8"/><path d="M855 197h11v10h-11zm0 23h11v10h-11zm0 23h11v10h-11zm0 23h11v10h-11" fill="#e783a4"/><text x="771" y="43" font-size="14" font-family="monospace" fill="#fff1c8">DRAIN TOWN</text></svg>'''


def room_svg():
    return '''<svg viewBox="0 0 1000 130" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated">
    <rect width="1000" height="130" fill="#d5c6e8"/><rect width="1000" height="22" fill="#8581ad"/><path d="M0 22h1000v8H0zM0 114h1000v16H0z" fill="#a88eb8"/>
    <path d="M25 35h110v65H25zM865 35h110v65H865z" fill="#827ca9" stroke="#f3d9e8" stroke-width="5"/><path d="M36 47h88v43H36zM876 47h88v43h-88z" fill="#b5d4dc"/>
    <path d="M160 32h680v7H160z" fill="#b08fae"/><path d="M470 0h60v22h-60z" fill="#ffe6a0"/><path d="M478 20h44v7h-44z" fill="#fff3c8"/>
    <path d="M0 107h1000v7H0z" fill="#f1e2db"/><g fill="#f3c5d8"><rect x="190" y="53" width="30" height="12"/><rect x="780" y="53" width="30" height="12"/></g>
    <text x="22" y="17" fill="#fff2d6" font-family="monospace" font-size="12">DRAIN TOWN · NIGHT SHIFT CONTROL ROOM</text></svg>'''


def pc_svg():
    return '''<svg class="furniture-art" viewBox="0 0 200 130" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated"><rect x="21" y="18" width="158" height="83" fill="#525780" stroke="#353854" stroke-width="7"/><rect x="32" y="29" width="136" height="60" fill="#9de2dd"/><path d="M39 69h121v12H39z" fill="#66b8b8"/><path d="M50 48h38v5H50zm0 10h61v5H50z" fill="#edf8d9"/><rect x="90" y="101" width="20" height="15" fill="#696c98"/><rect x="65" y="116" width="70" height="8" fill="#4d507c"/><circle cx="159" cy="95" r="3" fill="#ef7196"/></svg>'''


def calendar_svg():
    return '''<svg class="furniture-art" viewBox="0 0 200 130" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated"><rect x="29" y="19" width="142" height="99" fill="#fff3d4" stroke="#6a6799" stroke-width="7"/><rect x="29" y="19" width="142" height="25" fill="#df89ad"/><path d="M53 12v18m94-18v18" stroke="#615f91" stroke-width="8"/><g fill="#8589b4"><rect x="45" y="55" width="17" height="13"/><rect x="73" y="55" width="17" height="13"/><rect x="101" y="55" width="17" height="13"/><rect x="129" y="55" width="17" height="13"/><rect x="45" y="79" width="17" height="13"/><rect x="73" y="79" width="17" height="13"/><rect x="101" y="79" width="17" height="13"/><rect x="129" y="79" width="17" height="13"/></g><path d="M74 98l8 8 16-18" fill="none" stroke="#48a982" stroke-width="6"/></svg>'''


def monitor_svg(route, idx):
    water = int(route[0] * 22 + 15)
    debris = int(route[2] * 7)
    corrosion = int(route[3] * 5)
    debris_marks = "".join(f'<rect x="{205+j*14}" y="{74-(j%2)*7}" width="7" height="6" fill="{["#cb6882", "#52b9ad", "#d7ad62"][j%3]}"/>' for j in range(debris))
    rust_marks = "".join(f'<rect x="{88+j*20}" y="{45+(j%2)*22}" width="8" height="7" fill="#bd7784"/>' for j in range(corrosion))
    return f'''<svg viewBox="0 0 320 135" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated"><rect width="320" height="135" fill="#9ec7e8"/><rect y="12" width="320" height="110" fill="#64769e"/><path d="M0 20h320v8H0zm0 85h320v11H0z" fill="#9da8ce"/><rect x="29" y="36" width="262" height="68" rx="30" fill="#d3b6cd" stroke="#f1dfdb" stroke-width="6"/><rect x="44" y="56" width="232" height="46" rx="21" fill="#31586e"/><rect x="46" y="{102-water}" width="228" height="{water}" rx="12" fill="#63c9cf"/><path d="M60 {100-water}h39v4H60zm92 8h30v3h-30z" fill="#d8fff1" opacity=".8"/>{debris_marks}{rust_marks}<rect x="6" y="4" width="46" height="14" fill="#202338"/><text x="10" y="15" font-size="9" font-family="monospace" fill="#fff2d6">CAM 0{idx+1}</text><circle cx="300" cy="12" r="4" fill="#ec7c91"/><rect y="122" width="320" height="13" fill="#30334a"/></svg>'''


def sigmoid(z):
    z = max(-30, min(30, z))
    return 1.0 / (1.0 + math.exp(-z))


def predict(features):
    return sigmoid(st.session_state.bias + sum(st.session_state.weights[i] * features[i] for i in range(4)))


def make_new_day():
    st.session_state.routes, st.session_state.target = make_day_routes()
    st.session_state.last_result = None
    st.session_state.screen = "game"


def start_week():
    st.session_state.day = 1
    st.session_state.wins = 0
    st.session_state.calendar = ["", "", "", "", "", "", ""]
    st.session_state.weights = [0.0, 0.0, 0.0, 0.0]
    st.session_state.bias = 0.0
    st.session_state.loss = None
    st.session_state.gradient = None
    st.session_state.trained_days = 0
    st.session_state.examples = make_training_examples()
    st.session_state.screen = "game"
    make_new_day()


def train_and_diagnose(sample_ids, selected_features, epochs):
    examples = [row for row in st.session_state.examples if row["id"] in sample_ids]
    labels = [row["label"] for row in examples]
    if len(examples) < 4 or len(set(labels)) < 2:
        return False, "정상·이상 데이터가 모두 포함되도록 4개 이상의 학습 기록을 골라주세요."
    if not selected_features:
        return False, "학습에 사용할 센서 특징을 하나 이상 선택해주세요."

    active = [FEATURE_KEYS.index(name) for name in selected_features]
    # Exclude unselected sensors so data selection directly changes the model.
    for i in range(4):
        if i not in active:
            st.session_state.weights[i] = 0.0

    weights = st.session_state.weights[:]
    bias = st.session_state.bias
    rate = LEARNING_RATE / max(1, len(active) ** 0.5)
    eps = 1e-8
    gradient_size = 0.0

    for _ in range(epochs):
        probabilities = [sigmoid(bias + sum(weights[i] * row["features"][i] for i in active)) for row in examples]
        grad_w = [0.0] * 4
        for i in active:
            grad_w[i] = sum((p - row["label"]) * row["features"][i] for p, row in zip(probabilities, examples)) / len(examples)
        grad_b = sum(p - row["label"] for p, row in zip(probabilities, examples)) / len(examples)
        gradient_size = math.sqrt(sum(grad_w[i] ** 2 for i in active) + grad_b ** 2)
        weights = [weights[i] - rate * grad_w[i] for i in range(4)]
        bias -= rate * grad_b

    st.session_state.weights = weights
    st.session_state.bias = bias
    final_probs = [sigmoid(bias + sum(weights[i] * row["features"][i] for i in active)) for row in examples]
    st.session_state.loss = -sum(row["label"] * math.log(max(eps, p)) + (1-row["label"]) * math.log(max(eps, 1-p)) for row, p in zip(examples, final_probs)) / len(examples)
    st.session_state.gradient = gradient_size
    st.session_state.trained_days += 1

    scores = [predict(route) for route in st.session_state.routes]
    chosen = max(range(4), key=lambda i: scores[i])
    success = chosen == st.session_state.target
    st.session_state.calendar[st.session_state.day - 1] = "O" if success else "X"
    if success:
        st.session_state.wins += 1
    st.session_state.last_result = {"success": success, "chosen": chosen, "target": st.session_state.target, "scores": scores}
    if st.session_state.day == 7:
        st.session_state.screen = "summary"
    return True, "학습과 오늘의 진단이 완료됐어요."


def calendar_html():
    cells = []
    for day, result in enumerate(st.session_state.calendar, 1):
        cls = "ok" if result == "O" else "no" if result == "X" else ""
        cells.append(f'<div class="day-cell {cls}">DAY {day}<b>{result or "·"}</b></div>')
    return '<div class="day-strip">' + "".join(cells) + '</div>'


def next_day():
    st.session_state.day += 1
    make_new_day()


def reset_week():
    st.session_state.cycle += 1
    start_week()


init_state()

if st.session_state.screen == "start":
    st.markdown('<div class="hero"><div class="small-label">A COZY PIXEL-ART SEWER TOWN STORY</div><h1>하수관 AI 정비대</h1><p>작은 마을의 야간 정비사가 되어 CCTV 속 이상을 찾아보세요.<br>PC에서 학습 데이터를 골라 경사하강법으로 AI를 가르칩니다.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="pixel-frame">' + town_svg() + '</div>', unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1, 1])
    with center:
        if st.button("▶  START  ◀", use_container_width=True, key="start_game"):
            st.session_state.cycle = 1
            start_week()
            st.rerun()
    st.markdown('<div class="hero"><span class="pill">7일 야간 근무</span><span class="pill">CCTV 4분할</span><span class="pill">경사하강법 AI 학습</span></div>', unsafe_allow_html=True)

elif st.session_state.screen == "game":
    st.markdown(f'<div class="hero"><span class="pill">근무 {st.session_state.cycle}회차</span><span class="pill">DAY {st.session_state.day} / 7</span><span class="pill">NIGHT {st.session_state.day} · 1 AM</span><h1>작은 하수도 마을의 관제실</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="room-frame"><div class="room-wall">DRAIN TOWN · NIGHT SHIFT CONTROL ROOM</div>', unsafe_allow_html=True)
    left, center, right = st.columns([0.85, 2.5, 0.85], gap="small")
    with left:
        st.markdown('<div class="furniture"><h3>🖥️ PC</h3>' + pc_svg() + '<div class="small-label">AI 학습 / 데이터 선택</div></div>', unsafe_allow_html=True)
        if st.button("PC 확대 · AI 학습", key="open_pc", use_container_width=True):
            st.session_state.screen = "pc"
            st.rerun()
    with center:
        st.markdown('<div class="pixel-panel"><h3>📺 CCTV 감시 화면</h3><span class="small-label">PC에서 학습을 마치면 AI가 네 관로를 판별합니다.</span></div>', unsafe_allow_html=True)
        monitor_cols = st.columns(2, gap="small")
        for idx, route in enumerate(st.session_state.routes):
            with monitor_cols[idx % 2]:
                score = predict(route)
                readout = "　".join(f"{label} {route[i]:.2f}" for i, label in enumerate(FEATURES))
                st.markdown(f'<div class="monitor-card"><div class="monitor-label">CAM 0{idx+1}　·　AI 위험도 {score:.0%}</div><div class="monitor-art">{monitor_svg(route, idx)}</div><div class="sensor-readout">{readout}</div></div>', unsafe_allow_html=True)
        if st.session_state.last_result:
            result = st.session_state.last_result
            if result["success"]:
                st.success(f'오늘의 진단 성공! AI가 CAM 0{result["chosen"]+1}을 이상 관로로 골랐어요.')
            else:
                st.error(f'오늘의 진단 실패. AI는 CAM 0{result["chosen"]+1}을 골랐지만 실제 이상은 CAM 0{result["target"]+1}이었어요.')
            st.caption("확률은 오늘 학습에 사용한 데이터와 센서 선택에 따라 달라집니다.")
            if st.session_state.day < 7 and st.button("다음 날 근무하기 →", key=f"next_{st.session_state.day}", use_container_width=True):
                next_day()
                st.rerun()
        elif st.session_state.day_result if "day_result" in st.session_state else False:
            pass
        st.markdown('<div class="chair">▰　정비사의 의자　▰</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="furniture"><h3>🗓️ 달력</h3>' + calendar_svg() + '<div class="small-label">이번 주 근무 기록</div></div>', unsafe_allow_html=True)
        if st.button("달력 확대 · 기록 보기", key="open_calendar", use_container_width=True):
            st.session_state.screen = "calendar"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="dialog"><span class="dialog-name">야간 정비사</span><div class="dialog-text">PC를 눌러 학습 데이터와 센서 특징을 골라봐. 경사하강법으로 학습한 AI가 가장 위험한 관로를 고르고, 그 예측이 오늘의 성공과 실패를 결정해!</div></div>', unsafe_allow_html=True)
    if st.session_state.loss is not None:
        a, b, c = st.columns(3)
        a.metric("최근 Loss · BCE", f'{st.session_state.loss:.3f}')
        b.metric("Gradient 크기", f'{st.session_state.gradient:.3f}')
        c.metric("주간 성공", f'{st.session_state.wins} / 7')

elif st.session_state.screen == "pc":
    st.markdown(f'<div class="hero"><span class="pill">PC 확대 화면</span><span class="pill">DAY {st.session_state.day} / 7</span><h1>AI 학습 데이터 선택</h1><p>선택한 정상·이상 기록으로 로지스틱 회귀 모델을 경사하강법으로 학습합니다.</p></div>', unsafe_allow_html=True)
    if st.button("← 관제실로 돌아가기", key="pc_back"):
        st.session_state.screen = "game"
        st.rerun()
    st.markdown('<div class="expanded">', unsafe_allow_html=True)
    st.markdown('<div class="pixel-panel"><h3>1. 학습 기록 선택</h3><span class="small-label">서로 다른 날의 관로 점검 기록입니다. 정상/이상 라벨이 모두 포함되어야 학습할 수 있어요.</span></div>', unsafe_allow_html=True)
    examples = st.session_state.examples
    options = [f'{row["id"]} · {"이상" if row["label"] else "정상"}' for row in examples]
    id_by_option = {label: row["id"] for label, row in zip(options, examples)}
    selected_rows = st.multiselect("학습에 사용할 기록 (32개 중 선택)", options, default=options, key="training_rows")
    selected_ids = {id_by_option[label] for label in selected_rows}
    table_rows = []
    for row in examples:
        table_rows.append({"기록": row["id"], "정답": "이상" if row["label"] else "정상", **{FEATURES[i]: round(row["features"][i], 2) for i in range(4)}, "선택됨": "✓" if row["id"] in selected_ids else ""})
    st.dataframe(table_rows, use_container_width=True, hide_index=True, height=300)
    st.markdown('<div class="pixel-panel"><h3>2. AI가 살펴볼 센서 선택</h3><span class="small-label">선택하지 않은 센서는 모델 예측에 사용하지 않아요. 일부 단서만 고르면 진단이 어려워질 수 있습니다.</span></div>', unsafe_allow_html=True)
    selected_features = st.multiselect("학습 특징", FEATURES, default=FEATURES, key="training_features")
    epochs = st.slider("경사하강법 반복 횟수 (epochs)", min_value=10, max_value=200, value=80, step=10, key="training_epochs")
    st.caption(f"학습률 η = {LEARNING_RATE:.2f} · 매 epoch마다 Binary Cross-Entropy 손실의 기울기를 계산해 가중치를 갱신합니다.")
    if st.session_state.last_result:
        st.info("오늘의 진단은 이미 끝났습니다. 다시 학습하려면 다음 날 관제실에서 PC를 여세요.")
    elif st.button("선택한 데이터로 학습하고 오늘 진단하기", key=f"train_{st.session_state.day}", use_container_width=True):
        ok, message = train_and_diagnose(selected_ids, selected_features, epochs)
        if ok:
            st.session_state.screen = "summary" if st.session_state.day == 7 else "game"
            st.rerun()
        else:
            st.error(message)
    if st.session_state.loss is not None:
        st.markdown('<div class="pixel-panel"><h3>현재 모델 파라미터</h3></div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i, label in enumerate(FEATURES):
            cols[i].metric(f"{label} 가중치", f"{st.session_state.weights[i]:+.2f}")
        m1, m2 = st.columns(2)
        m1.metric("최근 Loss · BCE", f'{st.session_state.loss:.4f}')
        m2.metric("마지막 Gradient 크기", f'{st.session_state.gradient:.4f}')
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.screen == "calendar":
    st.markdown(f'<div class="hero"><span class="pill">달력 확대 화면</span><span class="pill">근무 {st.session_state.cycle}회차</span><h1>이번 주 점검 기록</h1><p>매일 PC에서 AI 학습 후 내려진 진단 결과입니다.</p></div>', unsafe_allow_html=True)
    if st.button("← 관제실로 돌아가기", key="calendar_back"):
        st.session_state.screen = "game"
        st.rerun()
    st.markdown('<div class="expanded">' + calendar_html() + '</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="pixel-panel"><h3>주간 요약</h3><p>성공은 O, 실패는 X로 표시됩니다. AI는 매일 선택된 학습 기록을 보고 모델 가중치를 업데이트합니다.</p></div>', unsafe_allow_html=True)
    st.metric("성공 횟수", f'{st.session_state.wins} / {sum(bool(v) for v in st.session_state.calendar)}')

elif st.session_state.screen == "summary":
    wins = st.session_state.wins
    if wins >= 5:
        heading, mood, message = "승진 축하해요!", "🌟", f"7일 중 {wins}회 성공! 작은 마을 하수관 관리팀의 팀장으로 승진했습니다."
        next_label, action = "처음 화면으로", "start"
    elif wins >= 3:
        heading, mood, message = "한 주 더 도전!", "🌱", f"7일 중 {wins}회 성공했습니다. 조금 더 경험을 쌓을 기회가 생겼어요. 다음 7일을 시작합니다."
        next_label, action = "다음 7일 시작", "retry"
    else:
        heading, mood, message = "오늘은 여기까지…", "🌧️", f"7일 중 {wins}회 성공했습니다. 이번에는 회사를 떠나게 되었지만, 다음엔 더 나은 데이터를 골라보세요."
        next_label, action = "처음 화면으로", "start"
    st.markdown(f'<div class="expanded" style="text-align:center"><div style="font-size:4rem">{mood}</div><div class="small-label">주간 근무 결산 · {st.session_state.cycle}회차</div><h1>{heading}</h1><p>{message}</p>{calendar_html()}</div>', unsafe_allow_html=True)
    if st.session_state.last_result:
        result = st.session_state.last_result
        st.info(f'마지막 날 AI 예측: CAM 0{result["chosen"]+1} · 실제 이상: CAM 0{result["target"]+1} · Loss {st.session_state.loss:.3f}')
    _, center, _ = st.columns([1, 1, 1])
    with center:
        if st.button(next_label, use_container_width=True, key="summary_action"):
            if action == "retry":
                reset_week()
            else:
                st.session_state.screen = "start"
            st.rerun()
