import base64
import math
import random
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components
import pixel_art as art

st.set_page_config(page_title="하수관 야간정비대", page_icon="🚰", layout="wide", initial_sidebar_state="collapsed")
FEATURES = ["수압", "소음", "침전물", "부식"]
LEARNING_RATE = 0.9

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
:root{--navy:#101c59;--paper:#f5e8bd}
html,body,[class*="css"]{font-family:'Gowun Dodum',sans-serif}.stApp{background:#15182e;color:#f5e8bd}
.block-container{max-width:1380px;padding-top:.35rem;padding-bottom:1rem}h1,h2,h3{font-family:'Jua',sans-serif!important}
.hero{text-align:center;color:#f5e8bd;padding:2px 0 7px}.hero h1{color:#f5e8bd;text-shadow:2px 3px #101c59;margin:2px}
.logo-mark{font-family:'Jua',sans-serif;color:#f8eab9;-webkit-text-stroke:2px #101c59;text-shadow:4px 4px #101c59;font-size:clamp(2.5rem,5vw,4.2rem);text-align:center;letter-spacing:.06em;margin:0 0 4px}
.pill{display:inline-block;background:#f7edcf;border:2px solid var(--navy);padding:4px 9px;margin:3px;color:#14256f;font-family:'Jua',sans-serif;box-shadow:2px 2px #3153a3}
.dialog{border:3px solid #fff4d8;box-shadow:4px 4px #172c77;background:#0c1022;color:#fff6dc;padding:9px 14px;margin:9px auto;max-width:1200px}
.dialog-name{display:inline-block;border:2px solid #fff4d8;background:#20294e;color:#ffe67f;padding:3px 9px;font-family:'Jua',sans-serif}
.day-strip{display:grid;grid-template-columns:repeat(7,1fr);gap:7px}.day-cell{text-align:center;border:2px solid #101c59;background:#f8edcc;padding:12px;color:#1b2b70;font:13px monospace}.day-cell b{display:block;font:bold 24px monospace;min-height:28px}.day-cell.ok b{color:#008c73}.day-cell.no b{color:#c53b64}
.expanded{background:#f7edcf;color:#17275f;border:4px solid var(--navy);box-shadow:5px 5px #3153a3;padding:15px}
.stButton>button{border:2px solid #101c59!important;border-radius:3px!important;background:#ffe583!important;color:#101c59!important;font-family:'Jua',sans-serif!important;box-shadow:2px 2px #3153a3!important}
div[data-testid="stMetric"]{background:#f7edcf;color:#17275f;border:2px solid #101c59;padding:7px}.result-box{text-align:center;background:#f7edcf;color:#17275f;border:5px solid #101c59;box-shadow:6px 6px #3153a3;padding:20px}footer{visibility:hidden}
</style>""", unsafe_allow_html=True)


def init_state():
    defaults={"screen":"start","pc_page":"desktop","cycle":1,"day":1,"wins":0,"calendar":[""]*7,"weights":[0.0]*4,"bias":0.0,"routes":[],"target":0,"last_result":None,"loss":None,"gradient":None,"examples":[]}
    for key,value in defaults.items():
        if key not in st.session_state:
            st.session_state[key]=value


def make_examples():
    rows=[]
    for i in range(40):
        label=int(i>=20)
        values=[random.uniform(.08,.50) for _ in FEATURES]
        if label:
            primary=(i-20)%4
            values[primary]=random.uniform(.68,.99)
            for j in range(4):
                if j!=primary and random.random()<.32:
                    values[j]=random.uniform(.56,.83)
        rows.append({"id":f"P{i+1:02d}","x":values,"y":label})
    random.shuffle(rows)
    return rows


def make_routes():
    routes=[[random.uniform(.1,.52) for _ in FEATURES] for _ in range(4)]
    target=random.randrange(4)
    primary=random.randrange(4)
    routes[target][primary]=random.uniform(.7,.99)
    for j in range(4):
        if j!=primary and random.random()<.4:
            routes[target][j]=random.uniform(.58,.86)
    return routes,target


def sigmoid(z):
    return 1/(1+math.exp(-max(-30,min(30,z))))


def predict(x):
    return sigmoid(st.session_state.bias+sum(st.session_state.weights[j]*x[j] for j in range(4)))


def start_week():
    st.session_state.day=1
    st.session_state.wins=0
    st.session_state.calendar=[""]*7
    st.session_state.weights=[0.0]*4
    st.session_state.bias=0.0
    st.session_state.loss=None
    st.session_state.gradient=None
    st.session_state.examples=make_examples()
    st.session_state.routes,st.session_state.target=make_routes()
    st.session_state.last_result=None
    st.session_state.screen="game"


def train(ids,features,epochs):
    rows=[row for row in st.session_state.examples if row["id"] in ids]
    if len(rows)<4 or len({row["y"] for row in rows})<2:
        return False,"정상·이상 데이터가 모두 있도록 4개 이상의 기록을 선택해주세요."
    if not features:
        return False,"학습 센서를 하나 이상 선택해주세요."
    active=[FEATURES.index(feature) for feature in features]
    weights=st.session_state.weights[:]
    for j in range(4):
        if j not in active:
            weights[j]=0.0
    bias=st.session_state.bias
    rate=LEARNING_RATE/math.sqrt(len(active))
    gradient=0.0
    eps=1e-8
    for _ in range(epochs):
        probabilities=[sigmoid(bias+sum(weights[j]*row["x"][j] for j in active)) for row in rows]
        grad_w=[0.0]*4
        for j in active:
            grad_w[j]=sum((p-row["y"])*row["x"][j] for p,row in zip(probabilities,rows))/len(rows)
        grad_b=sum(p-row["y"] for p,row in zip(probabilities,rows))/len(rows)
        gradient=math.sqrt(sum(grad_w[j]**2 for j in active)+grad_b**2)
        weights=[weights[j]-rate*grad_w[j] for j in range(4)]
        bias-=rate*grad_b
    st.session_state.weights=weights
    st.session_state.bias=bias
    st.session_state.gradient=gradient
    probabilities=[sigmoid(bias+sum(weights[j]*row["x"][j] for j in active)) for row in rows]
    st.session_state.loss=-sum(row["y"]*math.log(max(eps,p))+(1-row["y"])*math.log(max(eps,1-p)) for row,p in zip(rows,probabilities))/len(rows)
    scores=[predict(route) for route in st.session_state.routes]
    chosen=max(range(4),key=lambda j:scores[j])
    success=chosen==st.session_state.target
    st.session_state.calendar[st.session_state.day-1]="O" if success else "X"
    st.session_state.wins+=int(success)
    st.session_state.last_result={"success":success,"chosen":chosen,"target":st.session_state.target,"scores":scores}
    if st.session_state.day==7:
        st.session_state.screen="summary"
    return True,"done"


def calendar_html():
    cells=[]
    for i,value in enumerate(st.session_state.calendar):
        state="ok" if value=="O" else "no" if value=="X" else ""
        cells.append(f'<div class="day-cell {state}">DAY {i+1}<b>{value or "·"}</b></div>')
    return '<div class="day-strip">'+"".join(cells)+"</div>"


def set_from_query():
    opened=st.query_params.get("open")
    file_page=st.query_params.get("file")
    if opened in {"pc","calendar","game"}:
        st.session_state.screen=opened
        if opened=="pc":
            st.session_state.pc_page="desktop"
    if file_page in {"data","guide","model","train"}:
        st.session_state.screen="pc"
        st.session_state.pc_page=file_page
    if opened or file_page:
        st.query_params.clear()


def render_start_art():
    gif_fn=getattr(art,"start_scene_gif",None)
    if callable(gif_fn):
        encoded=base64.b64encode(gif_fn()).decode("ascii")
        components.html(f'<img src="data:image/gif;base64,{encoded}" style="display:block;width:100%;height:auto" alt="중앙 하수구에서 흐르는 물">',height=390,scrolling=False)
    else:
        st.image(art.start_scene(),use_container_width=True)


def render_clickable_room():
    image=art.room_scene(st.session_state.routes)
    buffer=BytesIO()
    image.save(buffer,format="PNG")
    encoded=base64.b64encode(buffer.getvalue()).decode("ascii")
    components.html(f'''<div style="position:relative;width:100%;aspect-ratio:16/9;overflow:hidden;border-radius:5px">
<img src="data:image/png;base64,{encoded}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:fill" alt="야간 관제실">
<a href="?open=pc" target="_top" aria-label="책상 위 컴퓨터 열기" title="컴퓨터 열기" style="position:absolute;left:2%;top:38%;width:31%;height:49%;cursor:pointer"></a>
<a href="?open=calendar" target="_top" aria-label="벽 달력 확대" title="달력 확대" style="position:absolute;left:84%;top:24%;width:14%;height:30%;cursor:pointer"></a>
</div>''',height=640,scrolling=False)


def render_desktop():
    # Plain Windows-style desktop: standard yellow folders, desktop labels and taskbar.
    folders=[("점검 데이터","data"),("학습 안내","guide"),("AI 모델","model"),("오늘의 진단","train")]
    folder_svg='''<svg viewBox="0 0 64 50" width="64" height="50" aria-hidden="true"><path d="M4 10a4 4 0 0 1 4-4h18l6 7h24a4 4 0 0 1 4 4v25a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z" fill="#d99a18"/><path d="M4 17a4 4 0 0 1 4-4h48a4 4 0 0 1 4 4v25a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z" fill="#f4c542"/><path d="M7 20h50v2H7z" fill="#ffdf72" opacity=".8"/></svg>'''
    icons=[]
    for label,page in folders:
        icons.append(f'''<a class="win-icon" href="?file={page}" target="_top" aria-label="{label} 폴더 열기"><span class="win-folder">{folder_svg}</span><span class="win-label">{label}</span></a>''')
    markup='''<div class="win-desktop">
      <div class="win-icons">'''+"".join(icons)+'''</div>
      <div class="win-taskbar"><div class="win-start" title="시작">⊞</div><div class="win-search"><span>⌕</span> 검색</div><div class="win-task-spacer"></div><div class="win-tray">◉　◖)))　▰　<small>오후 11:00<br>11/17</small></div></div>
    </div>'''
    components.html(markup,height=420,scrolling=False)


def back_to_room():
    st.markdown('<a href="?open=game" target="_top" style="display:inline-block;color:#d9defa;text-decoration:none;padding:4px 0">← 관제실</a>',unsafe_allow_html=True)


init_state()
set_from_query()

if st.session_state.screen=="start":
    st.markdown('<div class="logo-mark">하수관 야간정비대</div>',unsafe_allow_html=True)
    render_start_art()
    _,center,_=st.columns([1,1.3,1])
    with center:
        if st.button("▶　　 START　　 ◀",use_container_width=True,key="start_game"):
            st.session_state.cycle=1
            start_week()
            st.rerun()

elif st.session_state.screen=="game":
    st.markdown(f'<div class="hero"><span class="pill">근무 {st.session_state.cycle}회차</span><span class="pill">DAY {st.session_state.day} / 7</span><span class="pill">NIGHT {st.session_state.day} · 1 AM</span><h1>야간 하수관 관제실</h1></div>',unsafe_allow_html=True)
    render_clickable_room()
    st.caption("그림 속 책상 위 컴퓨터 또는 벽 달력을 눌러 열 수 있어요.")
    st.markdown('<div class="dialog"><span class="dialog-name">야간 정비사</span><br>컴퓨터에서 점검 기록을 선택해 AI를 학습시키고, 오늘의 관로를 진단하세요.</div>',unsafe_allow_html=True)
    if st.session_state.last_result:
        result=st.session_state.last_result
        if result["success"]:
            st.success(f'AI가 CAM 0{result["chosen"]+1}의 이상을 찾았습니다.')
        else:
            st.error(f'AI는 CAM 0{result["chosen"]+1}을 골랐지만 실제 이상은 CAM 0{result["target"]+1}이었습니다.')
        if st.session_state.day<7 and st.button("다음 날 근무 →",key=f"next_{st.session_state.day}"):
            st.session_state.day+=1
            st.session_state.routes,st.session_state.target=make_routes()
            st.session_state.last_result=None
            st.rerun()
        st.caption(f'주간 성공 {st.session_state.wins}/7　·　Loss {st.session_state.loss:.3f}　·　Gradient {st.session_state.gradient:.3f}')

elif st.session_state.screen=="pc":
    back_to_room()
    render_desktop()
    page=st.session_state.pc_page
    if page=="data":
        st.markdown('<div class="expanded"><h2>점검 데이터</h2><p>정상·이상 점검 기록을 선택하세요.</p></div>',unsafe_allow_html=True)
        rows=st.session_state.examples
        options=[f'{row["id"]} · {"이상" if row["y"] else "정상"}' for row in rows]
        lookup={name:row["id"] for name,row in zip(options,rows)}
        selected=st.multiselect("학습할 기록",options,default=options,key=f"data_{st.session_state.cycle}_{st.session_state.day}")
        ids={lookup[name] for name in selected}
        st.dataframe([{"파일":row["id"],"판정":"이상" if row["y"] else "정상",**{FEATURES[j]:round(row["x"][j],2) for j in range(4)},"포함":"✓" if row["id"] in ids else ""} for row in rows],use_container_width=True,hide_index=True,height=270)
    elif page=="guide":
        st.markdown('<div class="expanded"><h2>학습 안내</h2><p>수압·소음·침전물·부식 기록으로 관로의 이상 확률을 예측합니다. 예측과 점검 라벨의 차이로 손실(Loss)을 계산하고 기울기(Gradient)를 따라 가중치를 갱신합니다.</p><p><code>새 가중치 = 기존 가중치 − 학습률 × 기울기</code></p></div>',unsafe_allow_html=True)
    elif page=="model":
        st.markdown('<div class="expanded"><h2>AI 모델</h2><p>현재 모델 파라미터</p></div>',unsafe_allow_html=True)
        cols=st.columns(4)
        for j in range(4):
            cols[j].metric(FEATURES[j],f'{st.session_state.weights[j]:+.3f}')
        st.metric("bias",f'{st.session_state.bias:+.3f}')
    elif page=="train":
        st.markdown('<div class="expanded"><h2>오늘의 진단</h2><p>점검 기록으로 AI를 학습시킨 뒤 중앙 화면의 네 관로를 진단합니다.</p></div>',unsafe_allow_html=True)
        rows=st.session_state.examples
        options=[f'{row["id"]} · {"이상" if row["y"] else "정상"}' for row in rows]
        lookup={name:row["id"] for name,row in zip(options,rows)}
        selected=st.multiselect("학습 데이터 파일",options,default=options,key=f"train_rows_{st.session_state.cycle}_{st.session_state.day}")
        ids={lookup[name] for name in selected}
        features=st.multiselect("사용 센서",FEATURES,default=FEATURES,key=f"features_{st.session_state.cycle}_{st.session_state.day}")
        epochs=st.slider("경사하강법 반복 횟수",10,200,80,10,key=f"epochs_{st.session_state.cycle}_{st.session_state.day}")
        if st.session_state.last_result:
            st.info("오늘의 판정은 완료됐습니다. 다음 날 다시 학습할 수 있어요.")
        elif st.button("학습 후 오늘 CCTV 진단",key=f"run_{st.session_state.day}",use_container_width=True):
            ok,message=train(ids,features,epochs)
            if ok:
                st.session_state.screen="summary" if st.session_state.day==7 else "game"
                st.rerun()
            else:
                st.error(message)
        if st.session_state.loss is not None:
            st.metric("Loss · BCE",f'{st.session_state.loss:.4f}')

elif st.session_state.screen=="calendar":
    back_to_room()
    st.markdown(f'<div class="hero"><span class="pill">WEEK {st.session_state.cycle}</span><h1>달력</h1></div>',unsafe_allow_html=True)
    st.markdown('<div class="expanded">'+calendar_html()+'</div>',unsafe_allow_html=True)
    st.caption("하루의 AI 진단을 마치면 성공은 O, 실패는 X로 기록됩니다.")

elif st.session_state.screen=="summary":
    wins=st.session_state.wins
    if wins>=5:
        title,mark,message,label,action="승진 축하해요!","★",f"7일 중 {wins}회 성공! 야간정비대 관제반장으로 승진했습니다.","홈으로","home"
    elif wins>=3:
        title,mark,message,label,action="다음 주도 부탁해!","✿",f"7일 중 {wins}회 성공. 다음 7일을 계속 근무합니다.","다음 7일","retry"
    else:
        title,mark,message,label,action="근무 종료","×",f"7일 중 {wins}회 성공. 이번 주 결과가 부족해 회사를 떠나게 되었습니다.","홈으로","home"
    st.markdown(f'<div class="result-box"><div style="font-size:4rem;color:#173b9b">{mark}</div><h1>{title}</h1><p>{message}</p>{calendar_html()}</div>',unsafe_allow_html=True)
    if st.button(label,key="summary_action",use_container_width=True):
        if action=="retry":
            st.session_state.cycle+=1
            start_week()
        else:
            st.session_state.screen="start"
        st.rerun()

# Windows desktop styling is kept separate so the Streamlit app chrome remains usable.
components.html("""<style></style>""",height=0)
st.markdown("""<style>
.win-desktop{position:relative;height:400px;overflow:hidden;color:#fff;font-family:'Segoe UI',Arial,sans-serif;background:radial-gradient(ellipse at 68% 48%,#21a7d6 0%,#087bb8 20%,transparent 42%),radial-gradient(ellipse at 27% 82%,#1362a7 0%,#183b78 34%,transparent 58%),linear-gradient(135deg,#10264f,#087bb4 55%,#164e8c);border:1px solid #263c61;box-shadow:0 12px 30px rgba(0,0,0,.35)}
.win-icons{position:absolute;inset:12px auto 46px 10px;display:grid;grid-auto-flow:column;grid-template-rows:repeat(4,82px);gap:3px 12px;align-content:start}
.win-icon{width:88px;height:78px;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding:3px 2px;color:#fff!important;text-decoration:none!important;text-align:center;border:1px solid transparent;text-shadow:1px 1px 2px #17243b;font:12px 'Segoe UI',Arial,sans-serif}
.win-icon:hover{background:rgba(160,205,245,.22);border-color:rgba(220,238,255,.55)}.win-folder{height:51px;display:flex;align-items:center;justify-content:center;filter:drop-shadow(0 2px 2px rgba(0,0,0,.35))}.win-folder svg{width:48px;height:38px}.win-label{line-height:16px;max-width:84px;overflow-wrap:anywhere}
.win-taskbar{position:absolute;left:0;right:0;bottom:0;height:43px;display:flex;align-items:center;justify-content:center;gap:8px;background:rgba(24,36,55,.82);backdrop-filter:blur(18px);border-top:1px solid rgba(255,255,255,.17)}
.win-start{font-size:23px;color:#77c7ff;padding:0 9px}.win-search{height:27px;width:210px;border-radius:15px;background:rgba(226,237,248,.92);color:#354254;display:flex;align-items:center;gap:8px;padding:0 12px;font-size:12px}.win-search span{font-size:18px}.win-task-spacer{width:30px}.win-tray{position:absolute;right:15px;display:flex;align-items:center;gap:8px;font-size:12px;color:#fff}.win-tray small{text-align:right;font-size:10px;line-height:13px}
</style>""",unsafe_allow_html=True)
