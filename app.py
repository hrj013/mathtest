import math
import random

import streamlit as st

st.set_page_config(page_title="하수관 야간정비대", page_icon="🚰", layout="wide", initial_sidebar_state="collapsed")

FEATURES = ["수압", "소음", "침전물", "부식"]
FEATURE_KEYS = ["pressure", "noise", "sediment", "corrosion"]
LEARNING_RATE = 0.9

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
:root { --navy:#101c59; --blue:#173b9b; --midblue:#2859c7; --sky:#55bce8; --paper:#f5e8bd; --pink:#ef79ae; --mint:#50d5bd; --wall:#8584bd; }
html, body, [class*="css"] { font-family:'Gowun Dodum',sans-serif; }
.stApp { background:#b9c9eb; color:#17245f; }
.block-container { max-width:1420px; padding-top:.55rem; padding-bottom:1.6rem; }
h1,h2,h3 { font-family:'Jua',sans-serif!important; }
.hero { text-align:center; padding:2px 0 7px; }
.hero h1 { font-size:clamp(2rem,4vw,3.8rem); margin:0; color:#10246f; text-shadow:3px 4px #f8eab9,-1px -1px #fff; letter-spacing:.04em; }
.hero p { color:#17275f; line-height:1.5; }
.logo-mark { font-family:'Jua',sans-serif; color:#f8eab9; -webkit-text-stroke:2px #101c59; text-shadow:4px 4px #101c59; font-size:clamp(2.4rem,5vw,4.6rem); letter-spacing:.08em; text-align:center; margin:4px 0 0; }
.logo-sub { font: bold 12px monospace; color:#101c59; letter-spacing:.25em; text-align:center; margin-bottom:8px; }
.pixel-frame { border:5px solid var(--navy); box-shadow:8px 8px 0 #3153a3; background:#608bd0; }
.pixel-panel { background:#f7edcf; border:3px solid var(--navy); box-shadow:4px 4px 0 #3153a3; padding:10px 12px; margin:5px 0 10px; }
.pixel-panel h3 { margin:.1rem 0 .4rem; color:#14256f; }
.pill { display:inline-block; padding:4px 9px; border:2px solid var(--navy); background:#f7edcf; margin:3px; color:#14256f; font-family:'Jua',sans-serif; box-shadow:2px 2px 0 #3153a3; }
.small-label { color:#263a78; font-size:.84rem; }
.room-wall { border:5px solid var(--navy); background:#7878ae; box-shadow:7px 7px 0 #3153a3; padding:10px; }
.wall-banner { border:3px solid #101c59; background:#64699f; color:#fff0c8; font:12px monospace; letter-spacing:.12em; padding:7px 10px; margin-bottom:9px; }
.fixture { min-height:310px; border:4px solid var(--navy); background:#7778ad; box-shadow:5px 5px 0 #344b9a; padding:8px; text-align:center; color:#fff0c8; }
.fixture-title { color:#fff0c8; font: bold 13px monospace; letter-spacing:.08em; background:#172459; border:2px solid #101c59; padding:5px; }
.fixture-art { width:100%; max-width:210px; margin:10px auto 4px; display:block; }
.fixture-caption { color:#fff0c8; font-size:.78rem; min-height:38px; }
.screen-bezel { background:#151b35; border:7px solid #101c59; box-shadow:inset 0 0 0 3px #4d61a8,7px 7px 0 #263d88; padding:9px; }
.screen-header { display:flex; justify-content:space-between; color:#e7edff; background:#101a44; border:2px solid #5669ac; padding:5px 9px; margin-bottom:8px; font:12px monospace; letter-spacing:.08em; }
.cctv-card { background:#17214b; border:4px solid #101c59; box-shadow:inset 0 0 0 2px #5468ac; padding:5px; margin-bottom:8px; }
.cctv-label { background:#0f1738; color:#d5e6ff; font:11px monospace; padding:4px 6px; }
.cctv-art { border:2px solid #243b83; line-height:0; }
.sensor-readout { color:#eaf1dd; font:10px monospace; padding:4px 2px 1px; }
.furniture-svg { display:block; width:100%; max-width:250px; margin:10px auto; }
.chair-label { text-align:center; color:#fff0c8; padding:7px; font:12px monospace; }
.dialog { border:4px solid #fff4d8; outline:3px solid #101c59; box-shadow:6px 6px 0 #172c77; background:#0c1022; color:#fff6dc; padding:10px 15px; margin:10px auto; max-width:1200px; }
.dialog-name { display:inline-block; border:2px solid #fff4d8; background:#20294e; color:#ffe67f; padding:3px 10px; font-family:'Jua',sans-serif; }
.dialog-text { line-height:1.55; margin-top:5px; }
.day-strip { display:grid; grid-template-columns:repeat(7,1fr); gap:5px; }
.day-cell { text-align:center; border:2px solid #101c59; background:#f8edcc; padding:5px 1px; color:#1b2b70; font:10px monospace; }
.day-cell b { display:block; font:bold 17px monospace; min-height:19px; }
.day-cell.ok b { color:#008c73; } .day-cell.no b { color:#c53b64; }
.desktop { border:5px solid var(--navy); background:#3181c4; padding:14px; min-height:390px; box-shadow:7px 7px 0 #3153a3; }
.desktop-top { color:#fff4d8; font:12px monospace; padding:4px 7px 12px; }
.file-icon { text-align:center; border:2px solid #a9c5ff; background:#224eaa; color:#fff4d8; padding:12px 4px; min-height:90px; }
.file-icon b { display:block; font-size:2rem; }
.expanded-panel { background:#f7edcf; border:4px solid var(--navy); box-shadow:6px 6px 0 #3153a3; padding:16px; }
.stButton > button { border:3px solid #101c59!important; border-radius:0!important; background:#ffe583!important; color:#101c59!important; font-family:'Jua',sans-serif!important; font-size:1.02rem!important; box-shadow:3px 3px 0 #3153a3!important; min-height:2.5rem; }
.stButton > button:hover { background:#f58bb5!important; border-color:#101c59!important; color:#101c59!important; }
div[data-testid="stMetric"] { background:#f7edcf; border:2px solid #101c59; padding:7px; border-radius:0; }
.stProgress > div > div { background:#176fc3!important; }
.result-box { text-align:center; background:#f7edcf; border:5px solid #101c59; box-shadow:7px 7px 0 #3153a3; padding:20px; }
footer { visibility:hidden; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def init_state():
    defaults = {
        "screen": "start", "pc_page": "desktop", "cycle": 1, "day": 1, "wins": 0,
        "calendar": ["", "", "", "", "", "", ""],
        "weights": [0.0, 0.0, 0.0, 0.0], "bias": 0.0,
        "routes": [], "target": 0, "last_result": None,
        "loss": None, "gradient": None, "examples": [], "trained_days": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sewer_entry_svg():
    # Front-facing circular pipe mouth; water visibly spills outward from its opening.
    return '''<svg viewBox="0 0 1000 390" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges">
    <rect width="1000" height="390" fill="#6e9bd7"/><rect y="0" width="1000" height="155" fill="#4e7fc7"/>
    <rect x="0" y="155" width="1000" height="235" fill="#344c9e"/><path d="M0 204h1000v10H0zm0 133h1000v9H0z" fill="#d5dcf4"/>
    <rect x="112" y="70" width="294" height="234" fill="#233c87" stroke="#101c59" stroke-width="15"/><rect x="132" y="89" width="254" height="197" fill="#8aaddb" stroke="#f0d99c" stroke-width="8"/>
    <circle cx="259" cy="187" r="113" fill="#a2b3c5" stroke="#101c59" stroke-width="14"/><circle cx="259" cy="187" r="91" fill="#56687f" stroke="#d7c48f" stroke-width="8"/><circle cx="259" cy="187" r="68" fill="#123e6b"/>
    <path d="M193 196h132v35H193z" fill="#41c8e4"/><path d="M204 181h111v14H204z" fill="#a4f3ef"/><path d="M210 212h98v12h-98z" fill="#c4f8e8"/>
    <path d="M214 250h90v37h-90z" fill="#27b5dc"/><path d="M229 282v46h62v-46z" fill="#1ba7d2"/><path d="M184 327h150v15H184zm-35 22h220v12H149z" fill="#8ee5ee"/><path d="M165 365h187v8H165" fill="#c3f5e7"/>
    <rect x="97" y="47" width="26" height="286" fill="#e6d49d" stroke="#101c59" stroke-width="7"/><rect x="399" y="47" width="26" height="286" fill="#e6d49d" stroke="#101c59" stroke-width="7"/>
    <g fill="#f07eaf"><rect x="530" y="175" width="18" height="14"/><rect x="571" y="148" width="22" height="15"/><rect x="624" y="190" width="18" height="13"/><rect x="700" y="122" width="20" height="15"/><rect x="778" y="168" width="18" height="14"/><rect x="866" y="128" width="20" height="16"/></g>
    <g fill="#59d6c6"><rect x="609" y="74" width="28" height="17"/><rect x="638" y="62" width="20" height="16"/><rect x="805" y="85" width="24" height="16"/><rect x="827" y="73" width="20" height="15"/></g>
    <path d="M0 154h1000v12H0z" fill="#182c71"/><text x="556" y="48" font-size="25" font-family="monospace" fill="#fff0c8">DRAIN TOWN WATERWAY</text>
    <g fill="#f8e581"><rect x="465" y="207" width="10" height="10"/><rect x="501" y="224" width="8" height="8"/><rect x="390" y="239" width="9" height="9"/></g></svg>'''


def room_wall_svg():
    return '''<svg viewBox="0 0 1200 170" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges">
    <rect width="1200" height="170" fill="#7979ae"/><rect width="1200" height="22" fill="#4b518e"/><path d="M0 22h1200v8H0zM0 151h1200v19H0z" fill="#394b8b"/>
    <path d="M22 33h190v102H22zM988 33h190v102h-190z" fill="#5b629b" stroke="#101c59" stroke-width="7"/>
    <path d="M38 48h158v70H38zM1004 48h158v70h-158z" fill="#263c7d"/><path d="M52 93h130v18H52zm966-4h128v22h-128z" fill="#58b9cb"/>
    <path d="M230 32h740v9H230z" fill="#a994c2"/><rect x="558" y="0" width="84" height="24" fill="#ffe181" stroke="#101c59" stroke-width="5"/><rect x="572" y="22" width="56" height="10" fill="#fff1b7"/>
    <path d="M0 140h1200v10H0z" fill="#ddc5da"/><text x="23" y="18" fill="#fff1bd" font-family="monospace" font-size="13">DRAIN TOWN · NIGHT SHIFT CONTROL ROOM</text>
    </svg>'''


def desk_svg():
    return '''<svg viewBox="0 0 1200 120" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges">
    <rect width="1200" height="120" fill="#344986"/><rect y="8" width="1200" height="18" fill="#684d68"/><rect y="26" width="1200" height="8" fill="#111c59"/><rect y="34" width="1200" height="86" fill="#4d5e9d"/>
    <path d="M106 47h229l-18 25H124z" fill="#f1e2bb" stroke="#101c59" stroke-width="5"/><path d="M140 55h160v5H140zm10 9h129v4H150z" fill="#8b8ba8"/>
    <rect x="512" y="47" width="88" height="33" fill="#222d63" stroke="#101c59" stroke-width="5"/><rect x="522" y="54" width="68" height="16" fill="#52c4dd"/><circle cx="570" cy="61" r="4" fill="#ffdf70"/>
    <rect x="1020" y="45" width="48" height="37" fill="#26336b" stroke="#101c59" stroke-width="4"/><circle cx="1034" cy="58" r="6" fill="#f482b2"/><circle cx="1053" cy="58" r="6" fill="#f482b2"/><path d="M1035 72h17" stroke="#fff0c8" stroke-width="3"/>
    <path d="M431 51h42v40h-42z" fill="#59679b" stroke="#101c59" stroke-width="4"/><path d="M451 51v40m-20-20h42" stroke="#a8d7e5" stroke-width="4"/>
    </svg>'''


def pc_svg():
    return '''<svg viewBox="0 0 200 130" class="furniture-svg" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated;shape-rendering:crispEdges"><rect x="17" y="15" width="166" height="86" fill="#101c59" stroke="#f4df9d" stroke-width="6"/><rect x="29" y="27" width="142" height="61" fill="#3198d3"/><path d="M36 67h127v14H36z" fill="#36c7d9"/><rect x="45" y="41" width="43" height="7" fill="#b9eff0"/><rect x="45" y="52" width="70" height="6" fill="#f5e9bd"/><rect x="91" y="101" width="18" height="15" fill="#101c59"/><rect x="62" y="116" width="76" height="8" fill="#101c59"/><rect x="151" y="78" width="7" height="7" fill="#f277a8"/></svg>'''


def calendar_svg():
    return '''<svg viewBox="0 0 200 130" class="furniture-svg" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated;shape-rendering:crispEdges"><rect x="25" y="15" width="150" height="105" fill="#f5e8bd" stroke="#101c59" stroke-width="7"/><rect x="25" y="15" width="150" height="28" fill="#e975a8"/><path d="M55 8v22m90-22v22" stroke="#101c59" stroke-width="8"/><g fill="#3356a5"><rect x="42" y="55" width="20" height="14"/><rect x="73" y="55" width="20" height="14"/><rect x="104" y="55" width="20" height="14"/><rect x="135" y="55" width="20" height="14"/><rect x="42" y="81" width="20" height="14"/><rect x="73" y="81" width="20" height="14"/><rect x="104" y="81" width="20" height="14"/><rect x="135" y="81" width="20" height="14"/></g><path d="M73 105l8 7 16-17" fill="none" stroke="#008d7c" stroke-width="6"/></svg>'''


def monitor_svg(route, idx):
    # Playful pixel sewer view, with the selected fault expressed by sensor-driven details.
    water_y = int(89 - route[0] * 38)
    deposit_count = max(1, int(route[2] * 9))
    rust_count = max(1, int(route[3] * 6))
    deposits = "".join(f'<rect x="{118+j*15}" y="{97-(j%2)*7}" width="9" height="7" fill="{["#f179ad", "#50d5bd", "#f3d567"][j%3]}"/>' for j in range(deposit_count))
    rust = "".join(f'<rect x="{44+j*18}" y="{40+(j%2)*23}" width="10" height="8" fill="#e47793"/>' for j in range(rust_count))
    return f'''<svg viewBox="0 0 360 160" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges"><rect width="360" height="160" fill="#65a9dc"/><rect y="13" width="360" height="131" fill="#425d9d"/><path d="M0 24h360v10H0zm0 99h360v11H0z" fill="#b6c4df"/><rect x="35" y="39" width="290" height="80" fill="#d4b8ce" stroke="#101c59" stroke-width="8"/><rect x="52" y="57" width="256" height="54" fill="#153d70"/><rect x="54" y="{water_y}" width="252" height="{111-water_y}" fill="#35c4df"/><path d="M65 {water_y-5}h48v6H65zm105 9h38v5h-38zm73-7h53v6h-53z" fill="#caf7ed"/>{deposits}{rust}<rect x="5" y="4" width="54" height="17" fill="#101c59"/><text x="10" y="17" font-size="11" font-family="monospace" fill="#fff0c8">CAM 0{idx+1}</text><rect x="330" y="4" width="23" height="17" fill="#101c59"/><circle cx="341" cy="12" r="5" fill="#ff778f"/><rect y="144" width="360" height="16" fill="#101c59"/><text x="10" y="156" font-size="9" font-family="monospace" fill="#fff0c8">LIVE / PIPE {idx+1:02d}</text></svg>'''


def make_training_examples():
    examples = []
    for i in range(40):
        faulty = i >= 20
        features = [random.uniform(.08, .50) for _ in FEATURES]
        if faulty:
            primary = (i - 20) % len(FEATURES)
            features[primary] = random.uniform(.68, .99)
            for j in range(len(FEATURES)):
                if j != primary and random.random() < .32:
                    features[j] = random.uniform(.56, .83)
        examples.append({"id": f"P{i+1:02d}", "features": features, "label": int(faulty)})
    random.shuffle(examples)
    return examples


def make_day_routes():
    routes = [[random.uniform(.1, .52) for _ in FEATURES] for _ in range(4)]
    target = random.randrange(4)
    primary = random.randrange(len(FEATURES))
    routes[target][primary] = random.uniform(.7, .99)
    for j in range(len(FEATURES)):
        if j != primary and random.random() < .4:
            routes[target][j] = random.uniform(.58, .86)
    return routes, target


def sigmoid(z):
    z = max(-30, min(30, z))
    return 1.0 / (1.0 + math.exp(-z))


def predict(features):
    return sigmoid(st.session_state.bias + sum(st.session_state.weights[i] * features[i] for i in range(4)))


def new_day():
    st.session_state.routes, st.session_state.target = make_day_routes()
    st.session_state.last_result = None
    st.session_state.screen = "game"


def start_week():
    st.session_state.day = 1
    st.session_state.wins = 0
    st.session_state.calendar = ["", "", "", "", "", "", ""]
    st.session_state.weights = [0.0] * 4
    st.session_state.bias = 0.0
    st.session_state.loss = None
    st.session_state.gradient = None
    st.session_state.trained_days = 0
    st.session_state.examples = make_training_examples()
    new_day()


def train_and_diagnose(sample_ids, selected_features, epochs):
    examples = [row for row in st.session_state.examples if row["id"] in sample_ids]
    if len(examples) < 4 or len({row["label"] for row in examples}) < 2:
        return False, "정상·이상 데이터가 모두 있도록 4개 이상의 기록을 골라주세요."
    if not selected_features:
        return False, "AI가 사용할 센서를 하나 이상 선택해주세요."
    active = [FEATURES.index(name) for name in selected_features]
    weights = st.session_state.weights[:]
    for i in range(4):
        if i not in active:
            weights[i] = 0.0
    bias = st.session_state.bias
    rate = LEARNING_RATE / math.sqrt(len(active))
    gradient_size = 0.0
    eps = 1e-8
    for _ in range(epochs):
        probabilities = [sigmoid(bias + sum(weights[i] * row["features"][i] for i in active)) for row in examples]
        grad_w = [0.0] * 4
        for i in active:
            grad_w[i] = sum((p-row["label"]) * row["features"][i] for p, row in zip(probabilities, examples)) / len(examples)
        grad_b = sum(p-row["label"] for p, row in zip(probabilities, examples)) / len(examples)
        gradient_size = math.sqrt(sum(grad_w[i]**2 for i in active) + grad_b**2)
        weights = [weights[i] - rate*grad_w[i] for i in range(4)]
        bias -= rate * grad_b
    st.session_state.weights = weights
    st.session_state.bias = bias
    probs = [sigmoid(bias + sum(weights[i] * row["features"][i] for i in active)) for row in examples]
    st.session_state.loss = -sum(row["label"]*math.log(max(eps,p)) + (1-row["label"])*math.log(max(eps,1-p)) for row,p in zip(examples,probs))/len(examples)
    st.session_state.gradient = gradient_size
    st.session_state.trained_days += 1
    scores = [predict(route) for route in st.session_state.routes]
    chosen = max(range(4), key=lambda i: scores[i])
    success = chosen == st.session_state.target
    st.session_state.calendar[st.session_state.day-1] = "O" if success else "X"
    st.session_state.wins += int(success)
    st.session_state.last_result = {"success": success, "chosen": chosen, "target": st.session_state.target, "scores": scores}
    if st.session_state.day == 7:
        st.session_state.screen = "summary"
    return True, "학습 완료"


def calendar_html():
    cells = []
    for day, result in enumerate(st.session_state.calendar, 1):
        cls = "ok" if result == "O" else "no" if result == "X" else ""
        cells.append(f'<div class="day-cell {cls}">DAY {day}<b>{result or "·"}</b></div>')
    return '<div class="day-strip">' + "".join(cells) + '</div>'


def go_home():
    st.session_state.screen = "start"
    st.session_state.pc_page = "desktop"
    st.rerun()


init_state()

if st.session_state.screen == "start":
    st.markdown('<div class="logo-mark">하수관 야간정비대</div><div class="logo-sub">DRAIN TOWN · NIGHT WATCH</div>', unsafe_allow_html=True)
    st.markdown('<div class="pixel-frame">' + sewer_entry_svg() + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero"><p><span class="pill">7일 야간 근무</span><span class="pill">4분할 CCTV</span><span class="pill">경사하강법으로 AI 학습</span></p></div>', unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.3, 1])
    with center:
        if st.button("▶▶▶   START   ◀◀◀", use_container_width=True, key="start_game"):
            st.session_state.cycle = 1
            start_week()
            st.rerun()

elif st.session_state.screen == "game":
    st.markdown(f'<div class="hero"><span class="pill">근무 {st.session_state.cycle}회차</span><span class="pill">DAY {st.session_state.day} / 7</span><span class="pill">NIGHT {st.session_state.day} · 1 AM</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="room-wall"><div class="wall-banner">DRAIN TOWN WATERWORKS　 /　 NIGHT SHIFT CONTROL ROOM</div>' + room_wall_svg(), unsafe_allow_html=True)
    left, center, right = st.columns([.82, 2.5, .82], gap="small")
    with left:
        st.markdown('<div class="fixture"><div class="fixture-title">WALL PC</div>' + pc_svg() + '<div class="fixture-caption">학습실로 들어가려면<br>PC를 눌러주세요</div></div>', unsafe_allow_html=True)
        if st.button("🖥 PC 화면 열기", key="open_pc", use_container_width=True):
            st.session_state.screen = "pc"
            st.session_state.pc_page = "desktop"
            st.rerun()
    with center:
        st.markdown('<div class="screen-bezel"><div class="screen-header"><span>▣ MAIN CCTV ARRAY / 4 CHANNELS</span><span>REC ●　 SIGNAL</span></div>', unsafe_allow_html=True)
        cols = st.columns(2, gap="small")
        for idx, route in enumerate(st.session_state.routes):
            with cols[idx % 2]:
                score = predict(route)
                sensors = "　".join(f"{FEATURES[i]} {route[i]:.2f}" for i in range(4))
                st.markdown(f'<div class="cctv-card"><div class="cctv-label">CAM 0{idx+1}　·　AI {score:.0%}</div><div class="cctv-art">{monitor_svg(route, idx)}</div><div class="sensor-readout">{sensors}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="fixture"><div class="fixture-title">WALL CALENDAR</div>' + calendar_svg() + '<div class="fixture-caption">점검 결과가 O / X로<br>기록됩니다</div>' + calendar_html() + '</div>', unsafe_allow_html=True)
        if st.button("▦ 달력 확대 보기", key="open_calendar", use_container_width=True):
            st.session_state.screen = "calendar"
            st.rerun()
    st.markdown('<div class="chair-label">▼　정비사 의자　▼</div><div class="pixel-frame">' + desk_svg() + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="dialog"><span class="dialog-name">야간 정비사</span><div class="dialog-text">벽에 붙은 PC에서 데이터를 골라 AI를 학습시켜야 해. 학습이 끝나면 가운데 거대한 CCTV 스크린의 네 관로를 AI가 판별할 거야.</div></div>', unsafe_allow_html=True)
    top_left, top_right = st.columns([5,1])
    with top_left:
        if st.session_state.last_result:
            result = st.session_state.last_result
            if result["success"]:
                st.success(f'오늘은 성공! AI가 CAM 0{result["chosen"]+1}의 이상을 찾아냈어요.')
            else:
                st.error(f'오늘은 실패. AI는 CAM 0{result["chosen"]+1}을 골랐지만 이상은 CAM 0{result["target"]+1}이었어요.')
            if st.session_state.day < 7 and st.button("다음 날 근무 →", key=f"next_{st.session_state.day}"):
                st.session_state.day += 1
                new_day()
                st.rerun()
    with top_right:
        if st.button("⌂ 홈으로", key="home_game", use_container_width=True):
            go_home()
    if st.session_state.loss is not None:
        a, b, c = st.columns(3)
        a.metric("최근 Loss", f'{st.session_state.loss:.3f}')
        b.metric("Gradient 크기", f'{st.session_state.gradient:.3f}')
        c.metric("성공 횟수", f'{st.session_state.wins} / 7')

elif st.session_state.screen == "pc":
    back, title, home = st.columns([1, 4, 1])
    with back:
        if st.button("← 관제실", key="pc_back"):
            st.session_state.screen = "game"
            st.rerun()
    with title:
        st.markdown(f'<div class="hero"><span class="pill">PC DISPLAY · DAY {st.session_state.day}/7</span><h1>정비실 컴퓨터</h1></div>', unsafe_allow_html=True)
    with home:
        if st.button("⌂ 홈", key="home_pc"):
            go_home()
    st.markdown('<div class="desktop"><div class="desktop-top">DRAIN TOWN MAINTENANCE OS　　● ONLINE　　/　 FILES</div>', unsafe_allow_html=True)
    icon_cols = st.columns(4)
    file_buttons = [("📊", "점검 데이터.csv", "data"), ("📘", "경사하강법.txt", "guide"), ("🧠", "AI 모델.bin", "model"), ("🛠", "오늘의 학습.exe", "train")]
    for col, (icon, label, page) in zip(icon_cols, file_buttons):
        with col:
            st.markdown(f'<div class="file-icon"><b>{icon}</b>{label}</div>', unsafe_allow_html=True)
            if st.button(f"열기: {label}", key=f"file_{page}_{st.session_state.day}", use_container_width=True):
                st.session_state.pc_page = page
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    page = st.session_state.pc_page
    if page == "data":
        st.markdown('<div class="expanded-panel"><h2>📊 과거 관로 점검 데이터</h2><p>AI 학습에 사용할 정상·이상 라벨과 센서 측정값입니다. 학습할 기록을 선택하세요.</p></div>', unsafe_allow_html=True)
        examples = st.session_state.examples
        options = [f'{row["id"]} · {"이상" if row["label"] else "정상"}' for row in examples]
        id_map = {label: row["id"] for label, row in zip(options, examples)}
        selected = st.multiselect("학습 기록 선택", options, default=options, key=f"records_{st.session_state.cycle}_{st.session_state.day}")
        ids = {id_map[label] for label in selected}
        rows = [{"파일": r["id"], "판정": "이상" if r["label"] else "정상", **{FEATURES[i]: round(r["features"][i], 2) for i in range(4)}, "학습에 포함": "✓" if r["id"] in ids else ""} for r in examples]
        st.dataframe(rows, use_container_width=True, hide_index=True, height=280)
        st.caption("학습을 진행하려면 정상/이상 데이터가 모두 포함된 4개 이상의 기록을 선택하세요.")
    elif page == "guide":
        st.markdown('<div class="expanded-panel"><h2>📘 파일: 경사하강법.txt</h2><h3>AI는 어떻게 배우나요?</h3><p>모델은 각 관로의 수압·소음·침전물·부식 값을 받아 이상일 확률을 계산합니다. 과거 점검 결과와 예측의 차이를 <b>손실(Loss)</b>로 측정합니다.</p><p><b>경사하강법</b>은 손실이 줄어드는 방향을 기울기(Gradient)로 구해, 가중치를 조금씩 업데이트하는 방법입니다.</p><p><code>새 가중치 = 기존 가중치 − 학습률 × 기울기</code></p><p>학습률이 너무 크면 정답을 지나칠 수 있고, 너무 작으면 학습이 느립니다. PC에서 데이터와 센서를 골라 학습한 뒤 CCTV 진단이 어떻게 달라지는지 확인해보세요.</p></div>', unsafe_allow_html=True)
    elif page == "model":
        st.markdown('<div class="expanded-panel"><h2>🧠 파일: AI 모델.bin</h2><p>현재 모델의 가중치입니다. PC에서 학습할수록 선택한 데이터의 패턴에 맞춰 변합니다.</p></div>', unsafe_allow_html=True)
        metrics = st.columns(4)
        for i, label in enumerate(FEATURES):
            metrics[i].metric(label, f'{st.session_state.weights[i]:+.3f}')
        st.metric("편향 (bias)", f'{st.session_state.bias:+.3f}')
        if st.session_state.loss is not None:
            st.metric("최근 학습 손실 (BCE)", f'{st.session_state.loss:.4f}')
    elif page == "train":
        st.markdown('<div class="expanded-panel"><h2>🛠 파일: 오늘의 학습.exe</h2><p>학습 데이터 파일에서 선택한 기록을 불러와 경사하강법으로 학습한 후, 모델이 오늘의 CCTV를 자동 진단합니다.</p></div>', unsafe_allow_html=True)
        examples = st.session_state.examples
        options = [f'{row["id"]} · {"이상" if row["label"] else "정상"}' for row in examples]
        id_map = {label: row["id"] for label, row in zip(options, examples)}
        selected_rows = st.multiselect("학습 기록 파일 선택", options, default=options, key=f"train_records_{st.session_state.cycle}_{st.session_state.day}")
        selected_ids = {id_map[label] for label in selected_rows}
        selected_features = st.multiselect("학습에 사용할 센서 특징", FEATURES, default=FEATURES, key=f"features_{st.session_state.cycle}_{st.session_state.day}")
        epochs = st.slider("경사하강법 반복 횟수 (epochs)", 10, 200, 80, 10, key=f"epochs_{st.session_state.cycle}_{st.session_state.day}")
        st.caption(f"학습률 η = {LEARNING_RATE:.2f} · Binary Cross-Entropy 손실의 기울기로 모델 가중치를 업데이트합니다.")
        if st.session_state.last_result:
            result = st.session_state.last_result
            st.info(f'오늘 진단 완료: CAM 0{result["chosen"]+1} 선택 · 실제 이상 CAM 0{result["target"]+1}')
        elif st.button("데이터 학습 후 오늘 CCTV 진단", key=f"run_training_{st.session_state.cycle}_{st.session_state.day}", use_container_width=True):
            ok, message = train_and_diagnose(selected_ids, selected_features, epochs)
            if ok:
                st.session_state.screen = "summary" if st.session_state.day == 7 else "game"
                st.rerun()
            else:
                st.error(message)
        if st.session_state.loss is not None:
            st.metric("최근 Loss · BCE", f'{st.session_state.loss:.4f}')
            st.metric("마지막 Gradient 크기", f'{st.session_state.gradient:.4f}')
    if st.button("⌂ 홈으로 돌아가기", key="home_pc_bottom"):
        go_home()

elif st.session_state.screen == "calendar":
    left, title, home = st.columns([1, 4, 1])
    with left:
        if st.button("← 관제실", key="calendar_back"):
            st.session_state.screen = "game"
            st.rerun()
    with title:
        st.markdown(f'<div class="hero"><span class="pill">CALENDAR DISPLAY · WEEK {st.session_state.cycle}</span><h1>주간 점검 달력</h1></div>', unsafe_allow_html=True)
    with home:
        if st.button("⌂ 홈", key="home_calendar"):
            go_home()
    st.markdown('<div class="expanded-panel">' + calendar_html() + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="pixel-panel"><h3>기록 안내</h3><p>PC에서 선택한 학습 데이터로 AI가 CCTV 네 구간을 판별합니다. 실제 이상 관로를 맞히면 O, 틀리면 X가 기록됩니다.</p></div>', unsafe_allow_html=True)
    st.metric("이번 주 성공", f'{st.session_state.wins} / {sum(bool(v) for v in st.session_state.calendar)}')

elif st.session_state.screen == "summary":
    wins = st.session_state.wins
    if wins >= 5:
        heading, mood, message = "승진 축하해요!", "★", f"7일 중 {wins}회 성공! 야간정비대의 관제반장으로 승진했습니다."
        label, action = "처음 화면으로", "home"
    elif wins >= 3:
        heading, mood, message = "다음 주도 부탁해!", "✿", f"7일 중 {wins}회 성공. 회사를 계속 다니며 다음 7일을 다시 시작합니다."
        label, action = "다음 7일 시작", "retry"
    else:
        heading, mood, message = "근무 종료", "×", f"7일 중 {wins}회 성공. 이번 주 결과가 부족해 회사를 떠나게 되었습니다."
        label, action = "홈으로 돌아가기", "home"
    st.markdown(f'<div class="result-box"><div style="font-size:4rem;color:#173b9b">{mood}</div><div class="small-label">WEEK REPORT · {st.session_state.cycle}</div><h1>{heading}</h1><p>{message}</p>{calendar_html()}</div>', unsafe_allow_html=True)
    if st.session_state.last_result:
        r = st.session_state.last_result
        st.info(f'마지막 진단: AI는 CAM 0{r["chosen"]+1}을 선택, 실제 이상은 CAM 0{r["target"]+1} · Loss {st.session_state.loss:.3f}')
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        if st.button(label, key="summary_action", use_container_width=True):
            if action == "retry":
                st.session_state.cycle += 1
                start_week()
            else:
                st.session_state.screen = "start"
            st.rerun()
