import base64
import math
import random

import streamlit as st
import streamlit.components.v1 as components

# Import the module, not an individual symbol: this also tolerates a stale
# cached pixel_art.py that predates start_scene_gif().
try:
    import pixel_art as art
except ImportError as exc:
    st.error(
        "그림 모듈을 불러오지 못했습니다. requirements.txt에 Pillow가 있는지 "
        "확인한 뒤 앱을 재배포해주세요. 상세 오류: " + str(exc)
    )
    st.stop()

room_scene = art.room_scene
start_scene = art.start_scene
start_scene_gif = getattr(art, "start_scene_gif", None)

st.set_page_config(
    page_title="하수관 야간정비대",
    page_icon="🚰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FEATURES = ["수압", "소음", "침전물", "부식"]
LEARNING_RATE = 0.9

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
    :root { --navy:#101c59; --paper:#f5e8bd; }
    html, body, [class*="css"] { font-family:'Gowun Dodum',sans-serif; }
    .stApp { background:#15182e; color:#f5e8bd; }
    .block-container { max-width:1380px; padding-top:.35rem; padding-bottom:1.2rem; }
    h1,h2,h3 { font-family:'Jua',sans-serif!important; }
    .hero { text-align:center; padding:2px 0 7px; color:#f5e8bd; }
    .hero h1 { color:#f5e8bd; text-shadow:2px 3px #101c59; margin:2px; }
    .logo-mark { font-family:'Jua',sans-serif; color:#f8eab9; -webkit-text-stroke:2px #101c59;
      text-shadow:4px 4px #101c59; font-size:clamp(2.5rem,5vw,4.2rem); text-align:center; letter-spacing:.06em; margin:0 0 4px; }
    .pill { display:inline-block; background:#f7edcf; border:2px solid var(--navy); padding:4px 9px;
      margin:3px; color:#14256f; font-family:'Jua',sans-serif; box-shadow:2px 2px #3153a3; }
    .dialog { border:4px solid #fff4d8; outline:2px solid #101c59; box-shadow:5px 5px #172c77;
      background:#0c1022; color:#fff6dc; padding:9px 14px; margin:9px auto; max-width:1200px; }
    .dialog-name { display:inline-block; border:2px solid #fff4d8; background:#20294e; color:#ffe67f; padding:3px 9px; font-family:'Jua',sans-serif; }
    .day-strip { display:grid; grid-template-columns:repeat(7,1fr); gap:5px; }
    .day-cell { text-align:center; border:2px solid #101c59; background:#f8edcc; padding:5px 1px; color:#1b2b70; font:10px monospace; }
    .day-cell b { display:block; font:bold 17px monospace; min-height:19px; }
    .day-cell.ok b { color:#008c73; } .day-cell.no b { color:#c53b64; }
    .desktop-shell { background:linear-gradient(145deg,#fae8ff,#b69aff 42%,#734be0 85%,#f0a8fb);
      border:5px solid #6f38d5; border-radius:20px; padding:12px; box-shadow:0 0 18px #cb78ff, inset 0 0 0 3px #f4c8ff; }
    .desktop-screen { min-height:205px; padding:14px; border:3px solid #d5c6ff; border-radius:13px;
      background:radial-gradient(ellipse at 50% 10%,#aeeaff,#668be4 48%,#5841b9 100%); }
    .desktop-top { color:#fff7ff; font:12px monospace; padding:3px 5px 14px; text-shadow:1px 1px #54358e; }
    .folder { text-align:center; min-height:118px; padding:10px 5px 7px; margin:3px 0;
      background:linear-gradient(160deg,rgba(255,255,255,.46),rgba(215,195,255,.24));
      border:1px solid rgba(255,255,255,.7); border-radius:12px; color:#fff; text-shadow:1px 1px #49368d;
      box-shadow:0 4px 10px rgba(48,31,116,.22); }
    .folder-icon { position:relative; margin:7px auto 10px; width:53px; height:37px; border-radius:7px 8px 8px 8px;
      background:linear-gradient(145deg,#fff1a7,#ffadcf 52%,#c18aff); box-shadow:0 4px 0 #7444c4,0 0 13px rgba(255,255,255,.62); }
    .folder-icon:before { content:''; position:absolute; left:3px; top:-8px; width:23px; height:11px;
      border-radius:5px 5px 0 0; background:#ffe5a0; }
    .folder-icon span { position:absolute; inset:5px 0 auto; font-size:22px; line-height:26px; }
    .file-icon { text-align:center; color:#fff8ff; padding:0 3px; font-size:.78rem; min-height:23px; }
    .expanded { background:#f7edcf; color:#17275f; border:4px solid var(--navy); box-shadow:5px 5px #3153a3; padding:15px; }
    .stButton>button { border:3px solid #101c59!important; border-radius:0!important; background:#ffe583!important; color:#101c59!important;
      font-family:'Jua',sans-serif!important; font-size:1rem!important; box-shadow:3px 3px #3153a3!important; min-height:2.4rem; }
    .stButton>button:hover { background:#f58bb5!important; color:#101c59!important; }
    div[data-testid="stMetric"] { background:#f7edcf; color:#17275f; border:2px solid #101c59; padding:7px; }
    .stProgress>div>div { background:#176fc3!important; }
    .result-box { text-align:center; background:#f7edcf; color:#17275f; border:5px solid #101c59; box-shadow:6px 6px #3153a3; padding:20px; }
    footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "screen": "start", "pc_page": "desktop", "cycle": 1, "day": 1,
        "wins": 0, "calendar": [""] * 7, "weights": [0.0] * 4,
        "bias": 0.0, "routes": [], "target": 0, "last_result": None,
        "loss": None, "gradient": None, "examples": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def make_examples():
    rows = []
    for i in range(40):
        label = int(i >= 20)
        values = [random.uniform(.08, .50) for _ in FEATURES]
        if label:
            primary = (i - 20) % len(FEATURES)
            values[primary] = random.uniform(.68, .99)
            for sensor in range(len(FEATURES)):
                if sensor != primary and random.random() < .32:
                    values[sensor] = random.uniform(.56, .83)
        rows.append({"id": f"P{i+1:02d}", "x": values, "y": label})
    random.shuffle(rows)
    return rows


def make_routes():
    routes = [[random.uniform(.10, .52) for _ in FEATURES] for _ in range(4)]
    target = random.randrange(4)
    primary = random.randrange(4)
    routes[target][primary] = random.uniform(.70, .99)
    for sensor in range(4):
        if sensor != primary and random.random() < .40:
            routes[target][sensor] = random.uniform(.58, .86)
    return routes, target


def sigmoid(value):
    return 1 / (1 + math.exp(-max(-30, min(30, value))))


def predict(features):
    score = st.session_state.bias + sum(
        st.session_state.weights[i] * features[i] for i in range(4)
    )
    return sigmoid(score)


def start_week():
    st.session_state.day = 1
    st.session_state.wins = 0
    st.session_state.calendar = [""] * 7
    st.session_state.weights = [0.0] * 4
    st.session_state.bias = 0.0
    st.session_state.loss = None
    st.session_state.gradient = None
    st.session_state.examples = make_examples()
    st.session_state.routes, st.session_state.target = make_routes()
    st.session_state.last_result = None
    st.session_state.screen = "game"


def train_and_diagnose(selected_ids, selected_features, epochs):
    examples = [row for row in st.session_state.examples if row["id"] in selected_ids]
    if len(examples) < 4 or len({row["y"] for row in examples}) < 2:
        return False, "정상·이상 데이터가 모두 있도록 4개 이상의 기록을 선택해주세요."
    if not selected_features:
        return False, "학습 센서를 하나 이상 선택해주세요."

    active = [FEATURES.index(feature) for feature in selected_features]
    weights = st.session_state.weights[:]
    for index in range(4):
        if index not in active:
            weights[index] = 0.0

    bias = st.session_state.bias
    rate = LEARNING_RATE / math.sqrt(len(active))
    epsilon = 1e-8
    gradient_size = 0.0

    for _ in range(epochs):
        probabilities = [
            sigmoid(bias + sum(weights[i] * row["x"][i] for i in active))
            for row in examples
        ]
        grad_w = [0.0] * 4
        for index in active:
            grad_w[index] = sum(
                (p - row["y"]) * row["x"][index]
                for p, row in zip(probabilities, examples)
            ) / len(examples)
        grad_b = sum(p - row["y"] for p, row in zip(probabilities, examples)) / len(examples)
        gradient_size = math.sqrt(sum(grad_w[i] ** 2 for i in active) + grad_b ** 2)
        weights = [weights[i] - rate * grad_w[i] for i in range(4)]
        bias -= rate * grad_b

    st.session_state.weights = weights
    st.session_state.bias = bias
    st.session_state.gradient = gradient_size
    final_probs = [
        sigmoid(bias + sum(weights[i] * row["x"][i] for i in active))
        for row in examples
    ]
    st.session_state.loss = -sum(
        row["y"] * math.log(max(epsilon, p))
        + (1 - row["y"]) * math.log(max(epsilon, 1 - p))
        for row, p in zip(examples, final_probs)
    ) / len(examples)

    scores = [predict(route) for route in st.session_state.routes]
    chosen = max(range(4), key=lambda i: scores[i])
    success = chosen == st.session_state.target
    st.session_state.calendar[st.session_state.day - 1] = "O" if success else "X"
    st.session_state.wins += int(success)
    st.session_state.last_result = {
        "success": success, "chosen": chosen, "target": st.session_state.target,
        "scores": scores,
    }
    if st.session_state.day == 7:
        st.session_state.screen = "summary"
    return True, "학습과 오늘의 진단이 완료됐어요."


def calendar_html():
    cells = []
    for index, result in enumerate(st.session_state.calendar):
        cls = "ok" if result == "O" else "no" if result == "X" else ""
        cells.append(f'<div class="day-cell {cls}">DAY {index+1}<b>{result or "·"}</b></div>')
    return '<div class="day-strip">' + "".join(cells) + "</div>"


def go_home():
    st.session_state.screen = "start"
    st.session_state.pc_page = "desktop"
    st.rerun()


def navigation():
    back_col, home_col = st.columns([1, 5])
    with back_col:
        if st.button("← 관제실", key=f"back_{st.session_state.screen}"):
            st.session_state.screen = "game"
            st.rerun()
    with home_col:
        if st.button("⌂ 홈으로 돌아가기", key=f"home_{st.session_state.screen}"):
            go_home()


def render_start_art():
    if callable(start_scene_gif):
        gif_data = base64.b64encode(start_scene_gif()).decode("ascii")
        components.html(
            f'''<div style="width:100%;line-height:0;border:5px solid #101c59;box-shadow:7px 7px #3153a3;overflow:hidden">
            <img src="data:image/gif;base64,{gif_data}" style="display:block;width:100%;height:auto" alt="정중앙 하수구에서 물이 흐르는 장면"></div>''',
            height=390,
            scrolling=False,
        )
    else:
        # Fallback for an older cached pixel_art.py without the GIF helper.
        st.image(start_scene(), use_container_width=True)


def render_desktop():
    st.markdown(
        '<div class="desktop-shell"><div class="desktop-screen">'
        '<div class="desktop-top">DRAIN TOWN ✦ NIGHT OFFICE　 /　 MY FILES</div>',
        unsafe_allow_html=True,
    )
    files = [
        ("📊", "점검 데이터", "data"),
        ("📘", "경사하강법 안내", "guide"),
        ("💠", "AI 모델", "model"),
        ("🧪", "오늘의 학습", "train"),
    ]
    cols = st.columns(4)
    for col, (icon, label, page) in zip(cols, files):
        with col:
            st.markdown(
                f'<div class="folder"><div class="folder-icon"><span>{icon}</span></div>'
                f'<div class="file-icon">{label}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("열기", key=f"file_{page}_{st.session_state.day}", use_container_width=True):
                st.session_state.pc_page = page
                st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)


init_state()

if st.session_state.screen == "start":
    st.markdown('<div class="logo-mark">하수관 야간정비대</div>', unsafe_allow_html=True)
    render_start_art()
    _, center_col, _ = st.columns([1, 1.3, 1])
    with center_col:
        if st.button("▶　　 START　　 ◀", use_container_width=True, key="start_game"):
            st.session_state.cycle = 1
            start_week()
            st.rerun()

elif st.session_state.screen == "game":
    st.markdown(
        f'<div class="hero"><span class="pill">근무 {st.session_state.cycle}회차</span>'
        f'<span class="pill">DAY {st.session_state.day} / 7</span>'
        f'<span class="pill">NIGHT {st.session_state.day} · 1 AM</span>'
        '<h1>야간 하수관 관제실</h1></div>',
        unsafe_allow_html=True,
    )
    st.image(room_scene(st.session_state.routes), use_container_width=True)
    left_col, center_col, right_col = st.columns([1.15, 3.8, 1.15], gap="small")
    with left_col:
        if st.button("▣ 책상 PC 열기", key="pc_open", use_container_width=True):
            st.session_state.screen = "pc"
            st.session_state.pc_page = "desktop"
            st.rerun()
    with center_col:
        st.caption("중앙 대형 스크린 · CCTV 4분할")
        feed_cols = st.columns(2)
        for index, route in enumerate(st.session_state.routes):
            feed_cols[index % 2].metric(f"CAM 0{index+1} · AI 위험도", f"{predict(route):.0%}")
    with right_col:
        st.markdown(calendar_html(), unsafe_allow_html=True)
        if st.button("▦ 오른쪽 벽 달력", key="calendar_open", use_container_width=True):
            st.session_state.screen = "calendar"
            st.rerun()
    st.markdown(
        '<div class="dialog"><span class="dialog-name">야간 정비사</span>'
        '<div>왼쪽 벽에 붙은 업무 책상 PC에서 데이터를 골라 AI를 학습시켜. 그 결과가 오늘 CCTV 진단을 결정해.</div></div>',
        unsafe_allow_html=True,
    )
    result_col, home_col = st.columns([5, 1])
    with result_col:
        if st.session_state.last_result:
            result = st.session_state.last_result
            if result["success"]:
                st.success(f'AI가 CAM 0{result["chosen"]+1}의 이상을 찾았습니다.')
            else:
                st.error(f'AI는 CAM 0{result["chosen"]+1}을 골랐지만 실제 이상은 CAM 0{result["target"]+1}이었습니다.')
            if st.session_state.day < 7 and st.button("다음 날 근무 →", key=f"next_{st.session_state.day}"):
                st.session_state.day += 1
                st.session_state.routes, st.session_state.target = make_routes()
                st.session_state.last_result = None
                st.rerun()
        if st.session_state.loss is not None:
            metric_cols = st.columns(3)
            metric_cols[0].metric("최근 Loss", f'{st.session_state.loss:.3f}')
            metric_cols[1].metric("Gradient", f'{st.session_state.gradient:.3f}')
            metric_cols[2].metric("성공", f'{st.session_state.wins}/7')
    with home_col:
        if st.button("⌂ 홈", key="game_home", use_container_width=True):
            go_home()

elif st.session_state.screen == "pc":
    navigation()
    st.markdown(
        f'<div class="hero"><span class="pill">PC DISPLAY · DAY {st.session_state.day}/7</span>'
        '<h1>업무용 컴퓨터</h1></div>',
        unsafe_allow_html=True,
    )
    render_desktop()
    page = st.session_state.pc_page

    if page == "data":
        st.markdown('<div class="expanded"><h2>점검 데이터</h2><p>정상·이상 기록을 선택하고 센서 특징을 확인하세요.</p></div>', unsafe_allow_html=True)
        rows = st.session_state.examples
        options = [f'{r["id"]} · {"이상" if r["y"] else "정상"}' for r in rows]
        lookup = {label: row["id"] for label, row in zip(options, rows)}
        selected = st.multiselect("학습할 기록", options, default=options, key=f"data_{st.session_state.cycle}_{st.session_state.day}")
        ids = {lookup[label] for label in selected}
        st.dataframe([{"파일":r["id"],"판정":"이상" if r["y"] else "정상",**{FEATURES[i]:round(r["x"][i],2) for i in range(4)},"포함":"✓" if r["id"] in ids else ""} for r in rows], use_container_width=True, hide_index=True, height=270)
    elif page == "guide":
        st.markdown('<div class="expanded"><h2>경사하강법 안내</h2><p>모델은 수압·소음·침전물·부식 기록으로 관로의 이상 확률을 예측합니다. 예측과 점검 라벨의 차이로 손실(Loss)을 계산하고 기울기(Gradient)를 따라 가중치를 갱신합니다.</p><p><code>새 가중치 = 기존 가중치 − 학습률 × 기울기</code></p></div>', unsafe_allow_html=True)
    elif page == "model":
        st.markdown('<div class="expanded"><h2>AI 모델</h2><p>현재 모델 파라미터</p></div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i in range(4):
            cols[i].metric(FEATURES[i], f'{st.session_state.weights[i]:+.3f}')
        st.metric("bias", f'{st.session_state.bias:+.3f}')
        if st.session_state.loss is not None:
            st.metric("최근 Loss", f'{st.session_state.loss:.4f}')
    elif page == "train":
        st.markdown('<div class="expanded"><h2>오늘의 학습</h2><p>선택한 점검 기록으로 AI를 학습한 뒤 중앙 대형 스크린의 네 관로를 판별합니다.</p></div>', unsafe_allow_html=True)
        rows = st.session_state.examples
        options = [f'{r["id"]} · {"이상" if r["y"] else "정상"}' for r in rows]
        lookup = {label: row["id"] for label, row in zip(options, rows)}
        selected = st.multiselect("학습 데이터 파일 선택", options, default=options, key=f"train_rows_{st.session_state.cycle}_{st.session_state.day}")
        ids = {lookup[label] for label in selected}
        selected_features = st.multiselect("사용 센서", FEATURES, default=FEATURES, key=f"features_{st.session_state.cycle}_{st.session_state.day}")
        epochs = st.slider("경사하강법 반복 횟수", 10, 200, 80, 10, key=f"epochs_{st.session_state.cycle}_{st.session_state.day}")
        if st.session_state.last_result:
            st.info("오늘의 판정은 완료됐습니다. 다음 날 다시 학습할 수 있어요.")
        elif st.button("학습 후 오늘 CCTV 진단", key=f"run_{st.session_state.day}", use_container_width=True):
            ok, message = train_and_diagnose(ids, selected_features, epochs)
            if ok:
                st.session_state.screen = "summary" if st.session_state.day == 7 else "game"
                st.rerun()
            else:
                st.error(message)
        if st.session_state.loss is not None:
            st.metric("Loss · BCE", f'{st.session_state.loss:.4f}')
            st.metric("Gradient", f'{st.session_state.gradient:.4f}')

elif st.session_state.screen == "calendar":
    navigation()
    st.markdown(f'<div class="hero"><span class="pill">WEEK {st.session_state.cycle}</span><h1>오른쪽 벽 달력 · 확대</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="expanded">' + calendar_html() + '</div>', unsafe_allow_html=True)

elif st.session_state.screen == "summary":
    wins = st.session_state.wins
    if wins >= 5:
        title, mark, message, label, action = "승진 축하해요!", "★", f"7일 중 {wins}회 성공! 야간정비대 관제반장으로 승진했습니다.", "홈으로", "home"
    elif wins >= 3:
        title, mark, message, label, action = "다음 주도 부탁해!", "✿", f"7일 중 {wins}회 성공. 다음 7일을 계속 근무합니다.", "다음 7일", "retry"
    else:
        title, mark, message, label, action = "근무 종료", "×", f"7일 중 {wins}회 성공. 이번 주 결과가 부족해 회사를 떠나게 되었습니다.", "홈으로", "home"
    st.markdown(f'<div class="result-box"><div style="font-size:4rem;color:#173b9b">{mark}</div><h1>{title}</h1><p>{message}</p>{calendar_html()}</div>', unsafe_allow_html=True)
    if st.button(label, key="summary_action", use_container_width=True):
        if action == "retry":
            st.session_state.cycle += 1
            start_week()
        else:
            st.session_state.screen = "start"
        st.rerun()
    if st.button("⌂ 홈으로 돌아가기", key="summary_home"):
        go_home()
