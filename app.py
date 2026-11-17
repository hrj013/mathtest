import math
import random

import streamlit as st
from pixel_art import room_scene, start_scene


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

    :root {
        --navy: #101c59;
        --blue: #173b9b;
        --paper: #f5e8bd;
    }

    html, body, [class*="css"] {
        font-family: 'Gowun Dodum', sans-serif;
    }

    .stApp {
        background: #bdcbe5;
        color: #17275f;
    }

    .block-container {
        max-width: 1380px;
        padding-top: .4rem;
        padding-bottom: 1.4rem;
    }

    h1, h2, h3 {
        font-family: 'Jua', sans-serif !important;
    }

    .hero {
        text-align: center;
        padding: 2px 0 7px;
    }

    .hero h1 {
        color: #10246f;
        text-shadow: 2px 3px #f8eab9;
        margin: 2px;
    }

    .logo-mark {
        font-family: 'Jua', sans-serif;
        color: #f8eab9;
        -webkit-text-stroke: 2px #101c59;
        text-shadow: 4px 4px #101c59;
        font-size: clamp(2.5rem, 5vw, 4.2rem);
        text-align: center;
        letter-spacing: .06em;
        margin: 0 0 4px;
    }

    .pill {
        display: inline-block;
        background: #f7edcf;
        border: 2px solid var(--navy);
        padding: 4px 9px;
        margin: 3px;
        font-family: 'Jua', sans-serif;
        box-shadow: 2px 2px #3153a3;
    }

    .panel {
        background: #f7edcf;
        border: 3px solid var(--navy);
        box-shadow: 3px 3px #3153a3;
        padding: 9px 12px;
        margin: 5px 0;
    }

    .panel h3 {
        margin: .1rem 0 .4rem;
    }

    .dialog {
        border: 4px solid #fff4d8;
        outline: 2px solid #101c59;
        box-shadow: 5px 5px #172c77;
        background: #0c1022;
        color: #fff6dc;
        padding: 9px 14px;
        margin: 9px auto;
        max-width: 1200px;
    }

    .dialog-name {
        display: inline-block;
        border: 2px solid #fff4d8;
        background: #20294e;
        color: #ffe67f;
        padding: 3px 9px;
        font-family: 'Jua', sans-serif;
    }

    .day-strip {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
    }

    .day-cell {
        text-align: center;
        border: 2px solid #101c59;
        background: #f8edcc;
        padding: 5px 1px;
        color: #1b2b70;
        font: 10px monospace;
    }

    .day-cell b {
        display: block;
        font: bold 17px monospace;
        min-height: 19px;
    }

    .day-cell.ok b {
        color: #008c73;
    }

    .day-cell.no b {
        color: #c53b64;
    }

    .desktop {
        border: 5px solid var(--navy);
        background: #3181c4;
        padding: 14px;
        min-height: 230px;
        box-shadow: 6px 6px #3153a3;
    }

    .desktop-top {
        color: #fff4d8;
        font: 12px monospace;
        padding: 4px 7px 12px;
    }

    .file-icon {
        text-align: center;
        border: 2px solid #a9c5ff;
        background: #224eaa;
        color: #fff4d8;
        padding: 12px 4px;
        min-height: 85px;
    }

    .file-icon b {
        display: block;
        font-size: 2rem;
    }

    .expanded {
        background: #f7edcf;
        border: 4px solid var(--navy);
        box-shadow: 5px 5px #3153a3;
        padding: 15px;
    }

    .stButton > button {
        border: 3px solid #101c59 !important;
        border-radius: 0 !important;
        background: #ffe583 !important;
        color: #101c59 !important;
        font-family: 'Jua', sans-serif !important;
        font-size: 1rem !important;
        box-shadow: 3px 3px #3153a3 !important;
        min-height: 2.4rem;
    }

    .stButton > button:hover {
        background: #f58bb5 !important;
        color: #101c59 !important;
    }

    div[data-testid="stMetric"] {
        background: #f7edcf;
        border: 2px solid #101c59;
        padding: 7px;
    }

    .stProgress > div > div {
        background: #176fc3 !important;
    }

    .result-box {
        text-align: center;
        background: #f7edcf;
        border: 5px solid #101c59;
        box-shadow: 6px 6px #3153a3;
        padding: 20px;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "screen": "start",
        "pc_page": "desktop",
        "cycle": 1,
        "day": 1,
        "wins": 0,
        "calendar": [""] * 7,
        "weights": [0.0] * 4,
        "bias": 0.0,
        "routes": [],
        "target": 0,
        "last_result": None,
        "loss": None,
        "gradient": None,
        "examples": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def make_examples():
    """Create labeled practice data: normal and faulty pipe inspections."""
    rows = []

    for i in range(40):
        label = int(i >= 20)
        values = [random.uniform(0.08, 0.50) for _ in FEATURES]

        if label:
            primary_sensor = (i - 20) % len(FEATURES)
            values[primary_sensor] = random.uniform(0.68, 0.99)

            for sensor in range(len(FEATURES)):
                if sensor != primary_sensor and random.random() < 0.32:
                    values[sensor] = random.uniform(0.56, 0.83)

        rows.append({
            "id": f"P{i + 1:02d}",
            "x": values,
            "y": label,
        })

    random.shuffle(rows)
    return rows


def make_routes():
    """Create four CCTV pipe readings and one hidden faulty pipe."""
    routes = [
        [random.uniform(0.10, 0.52) for _ in FEATURES]
        for _ in range(4)
    ]

    target = random.randrange(4)
    primary_sensor = random.randrange(4)
    routes[target][primary_sensor] = random.uniform(0.70, 0.99)

    for sensor in range(4):
        if sensor != primary_sensor and random.random() < 0.40:
            routes[target][sensor] = random.uniform(0.58, 0.86)

    return routes, target


def sigmoid(value):
    value = max(-30, min(30, value))
    return 1.0 / (1.0 + math.exp(-value))


def predict(features):
    score = st.session_state.bias + sum(
        st.session_state.weights[i] * features[i]
        for i in range(len(FEATURES))
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
    """Train logistic regression with gradient descent, then diagnose today's CCTV."""
    examples = [
        row for row in st.session_state.examples
        if row["id"] in selected_ids
    ]

    if len(examples) < 4 or len({row["y"] for row in examples}) < 2:
        return False, "정상·이상 데이터가 모두 있도록 4개 이상의 기록을 선택해주세요."

    if not selected_features:
        return False, "학습 센서를 하나 이상 선택해주세요."

    active_features = [
        FEATURES.index(feature)
        for feature in selected_features
    ]

    weights = st.session_state.weights[:]

    # Features not selected on the PC are excluded from the model.
    for index in range(len(FEATURES)):
        if index not in active_features:
            weights[index] = 0.0

    bias = st.session_state.bias
    learning_rate = LEARNING_RATE / math.sqrt(len(active_features))
    gradient_size = 0.0
    epsilon = 1e-8

    for _ in range(epochs):
        probabilities = [
            sigmoid(
                bias + sum(
                    weights[index] * row["x"][index]
                    for index in active_features
                )
            )
            for row in examples
        ]

        weight_gradients = [0.0] * len(FEATURES)

        for index in active_features:
            weight_gradients[index] = sum(
                (probability - row["y"]) * row["x"][index]
                for probability, row in zip(probabilities, examples)
            ) / len(examples)

        bias_gradient = sum(
            probability - row["y"]
            for probability, row in zip(probabilities, examples)
        ) / len(examples)

        gradient_size = math.sqrt(
            sum(weight_gradients[index] ** 2 for index in active_features)
            + bias_gradient ** 2
        )

        weights = [
            weights[index] - learning_rate * weight_gradients[index]
            for index in range(len(FEATURES))
        ]
        bias -= learning_rate * bias_gradient

    st.session_state.weights = weights
    st.session_state.bias = bias
    st.session_state.gradient = gradient_size

    final_probabilities = [
        sigmoid(
            bias + sum(
                weights[index] * row["x"][index]
                for index in active_features
            )
        )
        for row in examples
    ]

    st.session_state.loss = -sum(
        row["y"] * math.log(max(epsilon, probability))
        + (1 - row["y"]) * math.log(max(epsilon, 1 - probability))
        for row, probability in zip(examples, final_probabilities)
    ) / len(examples)

    # The trained model—not a user guess—chooses the highest-risk CCTV route.
    scores = [predict(route) for route in st.session_state.routes]
    chosen = max(range(len(scores)), key=lambda index: scores[index])
    success = chosen == st.session_state.target

    st.session_state.calendar[st.session_state.day - 1] = (
        "O" if success else "X"
    )

    if success:
        st.session_state.wins += 1

    st.session_state.last_result = {
        "success": success,
        "chosen": chosen,
        "target": st.session_state.target,
        "scores": scores,
    }

    if st.session_state.day == 7:
        st.session_state.screen = "summary"

    return True, "학습과 오늘의 진단이 완료됐어요."


def calendar_html():
    cells = []

    for index, result in enumerate(st.session_state.calendar):
        if result == "O":
            result_class = "ok"
        elif result == "X":
            result_class = "no"
        else:
            result_class = ""

        cells.append(
            f'<div class="day-cell {result_class}">'
            f'DAY {index + 1}<b>{result or "·"}</b></div>'
        )

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


init_state()


if st.session_state.screen == "start":
    st.markdown(
        '<div class="logo-mark">하수관 야간정비대</div>',
        unsafe_allow_html=True,
    )

    # start_scene() returns a Pillow Image, so display it with st.image().
    st.image(start_scene(), use_container_width=True)

    _, center_col, _ = st.columns([1, 1.3, 1])

    with center_col:
        if st.button(
            "▶　　 START　　 ◀",
            use_container_width=True,
            key="start_game",
        ):
            st.session_state.cycle = 1
            start_week()
            st.rerun()


elif st.session_state.screen == "game":
    st.markdown(
        f"""
        <div class="hero">
            <span class="pill">근무 {st.session_state.cycle}회차</span>
            <span class="pill">DAY {st.session_state.day} / 7</span>
            <span class="pill">NIGHT {st.session_state.day} · 1 AM</span>
            <h1>야간 하수관 관제실</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # room_scene() also returns a Pillow Image, not HTML/SVG text.
    st.image(room_scene(st.session_state.routes), use_container_width=True)

    left_col, center_col, right_col = st.columns(
        [1.15, 3.8, 1.15],
        gap="small",
    )

    with left_col:
        if st.button(
            "▣ 책상 PC 열기",
            key="pc_open",
            use_container_width=True,
        ):
            st.session_state.screen = "pc"
            st.session_state.pc_page = "desktop"
            st.rerun()

    with center_col:
        st.caption("중앙 대형 스크린 · CCTV 4분할")
        feed_cols = st.columns(2)

        for index, route in enumerate(st.session_state.routes):
            feed_cols[index % 2].metric(
                f"CAM 0{index + 1} · AI 위험도",
                f"{predict(route):.0%}",
            )

    with right_col:
        st.markdown(calendar_html(), unsafe_allow_html=True)

        if st.button(
            "▦ 오른쪽 벽 달력",
            key="calendar_open",
            use_container_width=True,
        ):
            st.session_state.screen = "calendar"
            st.rerun()

    st.markdown(
        """
        <div class="dialog">
            <span class="dialog-name">야간 정비사</span>
            <div>
                왼쪽 책상 PC에서 학습 데이터를 고르고 AI를 훈련시켜.
                그 결과가 오늘 CCTV 진단을 결정해.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    result_col, home_col = st.columns([5, 1])

    with result_col:
        if st.session_state.last_result:
            result = st.session_state.last_result

            if result["success"]:
                st.success(
                    f'AI가 CAM 0{result["chosen"] + 1}의 이상을 찾았습니다.'
                )
            else:
                st.error(
                    f'AI는 CAM 0{result["chosen"] + 1}을 골랐지만, '
                    f'실제 이상은 CAM 0{result["target"] + 1}이었습니다.'
                )

            if st.session_state.day < 7 and st.button(
                "다음 날 근무 →",
                key=f"next_{st.session_state.day}",
            ):
                st.session_state.day += 1
                st.session_state.routes, st.session_state.target = make_routes()
                st.session_state.last_result = None
                st.rerun()

        if st.session_state.loss is not None:
            metric_cols = st.columns(3)
            metric_cols[0].metric("최근 Loss", f'{st.session_state.loss:.3f}')
            metric_cols[1].metric(
                "Gradient",
                f'{st.session_state.gradient:.3f}',
            )
            metric_cols[2].metric("성공", f'{st.session_state.wins}/7')

    with home_col:
        if st.button("⌂ 홈", key="game_home", use_container_width=True):
            go_home()


elif st.session_state.screen == "pc":
    navigation()

    st.markdown(
        f"""
        <div class="hero">
            <span class="pill">PC DISPLAY · DAY {st.session_state.day}/7</span>
            <h1>업무용 컴퓨터</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="desktop">
            <div class="desktop-top">
                DRAIN TOWN OFFICE OS　● ONLINE　/　 FILES
            </div>
        """,
        unsafe_allow_html=True,
    )

    files = [
        ("▦", "점검 데이터.csv", "data"),
        ("▤", "경사하강법.txt", "guide"),
        ("▣", "AI 모델.bin", "model"),
        ("▶", "오늘의 학습.exe", "train"),
    ]

    file_cols = st.columns(4)

    for col, (icon, label, page) in zip(file_cols, files):
        with col:
            st.markdown(
                f'<div class="file-icon"><b>{icon}</b>{label}</div>',
                unsafe_allow_html=True,
            )

            if st.button(
                "파일 열기",
                key=f"file_{page}_{st.session_state.day}",
                use_container_width=True,
            ):
                st.session_state.pc_page = page
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    page = st.session_state.pc_page

    if page == "data":
        st.markdown(
            """
            <div class="expanded">
                <h2>점검 데이터.csv</h2>
                <p>정상·이상 기록을 선택하고 센서 특징을 살펴보세요.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rows = st.session_state.examples
        options = [
            f'{row["id"]} · {"이상" if row["y"] else "정상"}'
            for row in rows
        ]
        lookup = {
            label: row["id"]
            for label, row in zip(options, rows)
        }

        selected = st.multiselect(
            "학습할 기록",
            options,
            default=options,
            key=f"data_{st.session_state.cycle}_{st.session_state.day}",
        )
        selected_ids = {lookup[label] for label in selected}

        st.dataframe(
            [
                {
                    "파일": row["id"],
                    "판정": "이상" if row["y"] else "정상",
                    **{
                        FEATURES[index]: round(row["x"][index], 2)
                        for index in range(4)
                    },
                    "포함": "✓" if row["id"] in selected_ids else "",
                }
                for row in rows
            ],
            use_container_width=True,
            hide_index=True,
            height=270,
        )

    elif page == "guide":
        st.markdown(
            """
            <div class="expanded">
                <h2>경사하강법.txt</h2>
                <p>
                    모델은 수압·소음·침전물·부식 기록으로 관로의 이상 확률을
                    예측합니다. 예측과 점검 라벨의 차이로 손실(Loss)을 계산하고
                    기울기(Gradient)를 따라 가중치를 조금씩 갱신합니다.
                </p>
                <p><code>새 가중치 = 기존 가중치 − 학습률 × 기울기</code></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif page == "model":
        st.markdown(
            """
            <div class="expanded">
                <h2>AI 모델.bin</h2>
                <p>현재 모델 파라미터</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        model_cols = st.columns(4)

        for index in range(4):
            model_cols[index].metric(
                FEATURES[index],
                f'{st.session_state.weights[index]:+.3f}',
            )

        st.metric("bias", f'{st.session_state.bias:+.3f}')

        if st.session_state.loss is not None:
            st.metric("최근 Loss", f'{st.session_state.loss:.4f}')

    elif page == "train":
        st.markdown(
            """
            <div class="expanded">
                <h2>오늘의 학습.exe</h2>
                <p>
                    선택한 점검 기록으로 AI를 학습한 뒤 중앙 대형 스크린의
                    네 관로를 판별합니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rows = st.session_state.examples
        options = [
            f'{row["id"]} · {"이상" if row["y"] else "정상"}'
            for row in rows
        ]
        lookup = {
            label: row["id"]
            for label, row in zip(options, rows)
        }

        selected = st.multiselect(
            "학습 데이터 파일 선택",
            options,
            default=options,
            key=f"train_rows_{st.session_state.cycle}_{st.session_state.day}",
        )
        selected_ids = {lookup[label] for label in selected}

        selected_features = st.multiselect(
            "사용 센서",
            FEATURES,
            default=FEATURES,
            key=f"features_{st.session_state.cycle}_{st.session_state.day}",
        )

        epochs = st.slider(
            "경사하강법 반복 횟수",
            min_value=10,
            max_value=200,
            value=80,
            step=10,
            key=f"epochs_{st.session_state.cycle}_{st.session_state.day}",
        )

        if st.session_state.last_result:
            st.info("오늘의 판정은 완료됐습니다. 다음 날 다시 학습할 수 있어요.")
        elif st.button(
            "학습 후 오늘 CCTV 진단",
            key=f"run_{st.session_state.day}",
            use_container_width=True,
        ):
            success, message = train_and_diagnose(
                selected_ids,
                selected_features,
                epochs,
            )

            if success:
                st.session_state.screen = (
                    "summary" if st.session_state.day == 7 else "game"
                )
                st.rerun()
            else:
                st.error(message)

        if st.session_state.loss is not None:
            st.metric("Loss · BCE", f'{st.session_state.loss:.4f}')
            st.metric("Gradient", f'{st.session_state.gradient:.4f}')


elif st.session_state.screen == "calendar":
    navigation()

    st.markdown(
        f"""
        <div class="hero">
            <span class="pill">WEEK {st.session_state.cycle}</span>
            <h1>오른쪽 벽 달력 · 확대</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="expanded">' + calendar_html() + "</div>",
        unsafe_allow_html=True,
    )


elif st.session_state.screen == "summary":
    wins = st.session_state.wins

    if wins >= 5:
        title = "승진 축하해요!"
        mark = "★"
        message = f"7일 중 {wins}회 성공! 야간정비대 관제반장으로 승진했습니다."
        button_label = "홈으로"
        action = "home"
    elif wins >= 3:
        title = "다음 주도 부탁해!"
        mark = "✿"
        message = f"7일 중 {wins}회 성공. 다음 7일을 계속 근무합니다."
        button_label = "다음 7일"
        action = "retry"
    else:
        title = "근무 종료"
        mark = "×"
        message = f"7일 중 {wins}회 성공. 이번 주 결과가 부족해 회사를 떠나게 되었습니다."
        button_label = "홈으로"
        action = "home"

    st.markdown(
        f"""
        <div class="result-box">
            <div style="font-size:4rem;color:#173b9b">{mark}</div>
            <h1>{title}</h1>
            <p>{message}</p>
            {calendar_html()}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        button_label,
        key="summary_action",
        use_container_width=True,
    ):
        if action == "retry":
            st.session_state.cycle += 1
            start_week()
        else:
            st.session_state.screen = "start"

        st.rerun()

    if st.button("⌂ 홈으로 돌아가기", key="summary_home"):
        go_home()
