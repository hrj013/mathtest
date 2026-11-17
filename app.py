import math
import random
import streamlit as st
from pixel_art import room_scene, start_scene

st.set_page_config(page_title="하수관 야간정비대", page_icon="🚰", layout="wide", initial_sidebar_state="collapsed")
FEATURES = ["수압", "소음", "침전물", "부식"]
LEARNING_RATE = 0.9

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
:root{--navy:#101c59;--blue:#173b9b;--paper:#f5e8bd}
html,body,[class*="css"]{font-family:'Gowun Dodum',sans-serif}.stApp{background:#bdcbe5;color:#17275f}.block-container{max-width:1380px;padding-top:.4rem;padding-bottom:1.4rem}
h1,h2,h3{font-family:'Jua',sans-serif!important}.hero{text-align:center}.hero h1{color:#10246f;text-shadow:2px 3px #f8eab9;margin:2px}
.logo-mark{font-family:'Jua',sans-serif;color:#f8eab9;-webkit-text-stroke:2px #101c59;text-shadow:4px 4px #101c59;font-size:clamp(2.5rem,5vw,4.2rem);text-align:center;letter-spacing:.06em;margin:0 0 4px}.logo-sub{text-align:center;font:12px monospace;letter-spacing:.2em;color:#101c59;margin-bottom:8px}
.pixel-frame{border:5px solid var(--navy);box-shadow:7px 7px 0 #3153a3;overflow:hidden;line-height:0}.pill{display:inline-block;background:#f7edcf;border:2px solid var(--navy);padding:4px 9px;margin:3px;font-family:'Jua',sans-serif;box-shadow:2px 2px #3153a3}
.panel{background:#f7edcf;border:3px solid var(--navy);box-shadow:3px 3px #3153a3;padding:9px 12px;margin:5px 0}.panel h3{margin:.1rem 0 .4rem}.room-art{border:5px solid var(--navy);box-shadow:7px 7px #3153a3;line-height:0;overflow:hidden}.dialog{border:4px solid #fff4d8;outline:2px solid #101c59;box-shadow:5px 5px #172c77;background:#0c1022;color:#fff6dc;padding:9px 14px;margin:9px auto;max-width:1200px}.dialog-name{display:inline-block;border:2px solid #fff4d8;background:#20294e;color:#ffe67f;padding:3px 9px;font-family:'Jua',sans-serif}
.day-strip{display:grid;grid-template-columns:repeat(7,1fr);gap:5px}.day-cell{text-align:center;border:2px solid #101c59;background:#f8edcc;padding:5px 1px;color:#1b2b70;font:10px monospace}.day-cell b{display:block;font:bold 17px monospace;min-height:19px}.day-cell.ok b{color:#008c73}.day-cell.no b{color:#c53b64}
.desktop{border:5px solid var(--navy);background:#3181c4;padding:14px;min-height:230px;box-shadow:6px 6px #3153a3}.desktop-top{color:#fff4d8;font:12px monospace;padding:4px 7px 12px}.file-icon{text-align:center;border:2px solid #a9c5ff;background:#224eaa;color:#fff4d8;padding:12px 4px;min-height:85px}.file-icon b{display:block;font-size:2rem}.expanded{background:#f7edcf;border:4px solid var(--navy);box-shadow:5px 5px #3153a3;padding:15px}
.stButton>button{border:3px solid #101c59!important;border-radius:0!important;background:#ffe583!important;color:#101c59!important;font-family:'Jua',sans-serif!important;font-size:1rem!important;box-shadow:3px 3px #3153a3!important;min-height:2.4rem}.stButton>button:hover{background:#f58bb5!important;color:#101c59!important}div[data-testid="stMetric"]{background:#f7edcf;border:2px solid #101c59;padding:7px}.stProgress>div>div{background:#176fc3!important}.result-box{text-align:center;background:#f7edcf;border:5px solid #101c59;box-shadow:6px 6px #3153a3;padding:20px}footer{visibility:hidden}
</style>''',unsafe_allow_html=True)


def init_state():
    defaults={"screen":"start","pc_page":"desktop","cycle":1,"day":1,"wins":0,"calendar":[""]*7,"weights":[0.0]*4,"bias":0.0,"routes":[],"target":0,"last_result":None,"loss":None,"gradient":None,"examples":[]}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v


def make_examples():
    rows=[]
    for i in range(40):
        y=int(i>=20); x=[random.uniform(.08,.5) for _ in FEATURES]
        if y:
            j=(i-20)%4; x[j]=random.uniform(.68,.99)
            for k in range(4):
                if k!=j and random.random()<.32:x[k]=random.uniform(.56,.83)
        rows.append({"id":f"P{i+1:02d}","x":x,"y":y})
    random.shuffle(rows); return rows


def make_routes():
    xs=[[random.uniform(.1,.52) for _ in FEATURES] for _ in range(4)]; target=random.randrange(4); j=random.randrange(4); xs[target][j]=random.uniform(.7,.99)
    for k in range(4):
        if k!=j and random.random()<.4:xs[target][k]=random.uniform(.58,.86)
    return xs,target


def sigmoid(z):return 1/(1+math.exp(-max(-30,min(30,z))))
def predict(x):return sigmoid(st.session_state.bias+sum(st.session_state.weights[j]*x[j] for j in range(4)))


def start_week():
    st.session_state.day=1;st.session_state.wins=0;st.session_state.calendar=[""]*7;st.session_state.weights=[0.0]*4;st.session_state.bias=0.0
    st.session_state.loss=None;st.session_state.gradient=None;st.session_state.examples=make_examples();st.session_state.routes,st.session_state.target=make_routes();st.session_state.last_result=None;st.session_state.screen="game"


def train(ids,features,epochs):
    rows=[r for r in st.session_state.examples if r["id"] in ids]
    if len(rows)<4 or len({r["y"] for r in rows})<2:return False,"정상·이상 데이터가 모두 있도록 4개 이상의 기록을 선택해주세요."
    if not features:return False,"학습 센서를 하나 이상 선택해주세요."
    active=[FEATURES.index(f) for f in features];w=st.session_state.weights[:]
    for j in range(4):
        if j not in active:w[j]=0.0
    b=st.session_state.bias;rate=LEARNING_RATE/math.sqrt(len(active));grad_size=0.0;eps=1e-8
    for _ in range(epochs):
        ps=[sigmoid(b+sum(w[j]*r["x"][j] for j in active)) for r in rows];g=[0.0]*4
        for j in active:g[j]=sum((p-r["y"])*r["x"][j] for p,r in zip(ps,rows))/len(rows)
        gb=sum(p-r["y"] for p,r in zip(ps,rows))/len(rows);grad_size=math.sqrt(sum(g[j]**2 for j in active)+gb**2)
        w=[w[j]-rate*g[j] for j in range(4)];b-=rate*gb
    st.session_state.weights=w;st.session_state.bias=b;st.session_state.gradient=grad_size
    ps=[sigmoid(b+sum(w[j]*r["x"][j] for j in active)) for r in rows]
    st.session_state.loss=-sum(r["y"]*math.log(max(eps,p))+(1-r["y"])*math.log(max(eps,1-p)) for r,p in zip(rows,ps))/len(rows)
    scores=[predict(x) for x in st.session_state.routes];chosen=max(range(4),key=lambda j:scores[j]);success=chosen==st.session_state.target
    st.session_state.calendar[st.session_state.day-1]="O" if success else "X";st.session_state.wins+=int(success)
    st.session_state.last_result={"success":success,"chosen":chosen,"target":st.session_state.target,"scores":scores}
    if st.session_state.day==7:st.session_state.screen="summary"
    return True,"done"


def calendar_html():
    return '<div class="day-strip">'+''.join(f'<div class="day-cell {"ok" if x=="O" else "no" if x=="X" else ""}">DAY {i+1}<b>{x or "·"}</b></div>' for i,x in enumerate(st.session_state.calendar))+'</div>'


def go_home():st.session_state.screen="start";st.session_state.pc_page="desktop";st.rerun()

def nav():
    a,b=st.columns([1,5])
    with a:
        if st.button("← 관제실",key=f"back_{st.session_state.screen}"):st.session_state.screen="game";st.rerun()
    with b:
        if st.button("⌂ 홈으로 돌아가기",key=f"home_{st.session_state.screen}"):go_home()

init_state()

if st.session_state.screen=="start":
    # Title sits immediately above the illustrated scene; no redundant keyword chips.
    st.markdown('<div class="logo-mark">하수관 야간정비대</div>',unsafe_allow_html=True)
    st.markdown('<div class="pixel-frame">'+start_scene()+'</div>',unsafe_allow_html=True)
    _,c,_=st.columns([1,1.3,1])
    with c:
        if st.button("▶　　 START　　 ◀",use_container_width=True,key="start_game"):st.session_state.cycle=1;start_week();st.rerun()

elif st.session_state.screen=="game":
    st.markdown(f'<div class="hero"><span class="pill">근무 {st.session_state.cycle}회차</span><span class="pill">DAY {st.session_state.day} / 7</span><span class="pill">NIGHT {st.session_state.day} · 1 AM</span><h1>야간 하수관 관제실</h1></div>',unsafe_allow_html=True)
    st.markdown('<div class="room-art">'+room_scene(st.session_state.routes)+'</div>',unsafe_allow_html=True)
    # Click targets are aligned beneath the corresponding objects in the illustrated room.
    left,center,right=st.columns([1.15,3.8,1.15],gap="small")
    with left:
        if st.button("▣ 책상 PC 열기",key="pc_open",use_container_width=True):st.session_state.screen="pc";st.session_state.pc_page="desktop";st.rerun()
    with center:
        st.caption("중앙 대형 스크린 · CCTV 4분할")
        feeds=st.columns(2)
        for i,x in enumerate(st.session_state.routes):feeds[i%2].metric(f"CAM 0{i+1} · AI 위험도",f"{predict(x):.0%}")
    with right:
        st.markdown(calendar_html(),unsafe_allow_html=True)
        if st.button("▦ 오른쪽 벽 달력",key="calendar_open",use_container_width=True):st.session_state.screen="calendar";st.rerun()
    st.markdown('<div class="dialog"><span class="dialog-name">야간 정비사</span><div>왼쪽 책상 PC에서 학습 데이터를 고르고 AI를 훈련시켜. 그 결과가 오늘 CCTV 진단을 결정해.</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns([5,1])
    with c1:
        if st.session_state.last_result:
            r=st.session_state.last_result
            (st.success if r["success"] else st.error)(f'AI 선택 CAM 0{r["chosen"]+1} · 실제 이상 CAM 0{r["target"]+1}')
            if st.session_state.day<7 and st.button("다음 날 근무 →",key=f"next_{st.session_state.day}"):
                st.session_state.day+=1;st.session_state.routes,st.session_state.target=make_routes();st.session_state.last_result=None;st.rerun()
        if st.session_state.loss is not None:
            a,b,c=st.columns(3);a.metric("최근 Loss",f'{st.session_state.loss:.3f}');b.metric("Gradient",f'{st.session_state.gradient:.3f}');c.metric("성공",f'{st.session_state.wins}/7')
    with c2:
        if st.button("⌂ 홈으로",key="game_home",use_container_width=True):go_home()

elif st.session_state.screen=="pc":
    nav()
    st.markdown(f'<div class="hero"><span class="pill">PC DISPLAY · DAY {st.session_state.day}/7</span><h1>업무용 컴퓨터</h1></div>',unsafe_allow_html=True)
    st.markdown('<div class="desktop"><div class="desktop-top">DRAIN TOWN OFFICE OS　● ONLINE　/　 FILES</div>',unsafe_allow_html=True)
    files=[("▦","점검 데이터.csv","data"),("▤","경사하강법.txt","guide"),("▣","AI 모델.bin","model"),("▶","오늘의 학습.exe","train")]
    cols=st.columns(4)
    for col,(icon,label,page) in zip(cols,files):
        with col:
            st.markdown(f'<div class="file-icon"><b>{icon}</b>{label}</div>',unsafe_allow_html=True)
            if st.button("파일 열기",key=f"file_{page}_{st.session_state.day}",use_container_width=True):st.session_state.pc_page=page;st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)
    page=st.session_state.pc_page
    if page=="data":
        st.markdown('<div class="expanded"><h2>점검 데이터.csv</h2><p>정상·이상 기록을 선택하고 센서 특징을 살펴보세요.</p></div>',unsafe_allow_html=True)
        rows=st.session_state.examples;opts=[f'{r["id"]} · {"이상" if r["y"] else "정상"}' for r in rows];lookup={q:r["id"] for q,r in zip(opts,rows)}
        selected=st.multiselect("학습할 기록",opts,default=opts,key=f"data_{st.session_state.cycle}_{st.session_state.day}");ids={lookup[q] for q in selected}
        st.dataframe([{"파일":r["id"],"판정":"이상" if r["y"] else "정상",**{FEATURES[j]:round(r["x"][j],2) for j in range(4)},"포함":"✓" if r["id"] in ids else ""} for r in rows],use_container_width=True,hide_index=True,height=270)
    elif page=="guide":
        st.markdown('<div class="expanded"><h2>경사하강법.txt</h2><p>모델은 수압·소음·침전물·부식 기록으로 관로의 이상 확률을 예측합니다. 예측과 점검 라벨의 차이로 손실(Loss)을 계산하고 기울기(Gradient)를 따라 가중치를 조금씩 갱신합니다.</p><p><code>새 가중치 = 기존 가중치 − 학습률 × 기울기</code></p></div>',unsafe_allow_html=True)
    elif page=="model":
        st.markdown('<div class="expanded"><h2>AI 모델.bin</h2><p>현재 모델 파라미터</p></div>',unsafe_allow_html=True)
        cols=st.columns(4)
        for j in range(4):cols[j].metric(FEATURES[j],f'{st.session_state.weights[j]:+.3f}')
        st.metric("bias",f'{st.session_state.bias:+.3f}')
    elif page=="train":
        st.markdown('<div class="expanded"><h2>오늘의 학습.exe</h2><p>선택한 점검 기록으로 AI를 학습한 뒤 중앙 대형 스크린의 네 관로를 판별합니다.</p></div>',unsafe_allow_html=True)
        rows=st.session_state.examples;opts=[f'{r["id"]} · {"이상" if r["y"] else "정상"}' for r in rows];lookup={q:r["id"] for q,r in zip(opts,rows)}
        selected=st.multiselect("학습 데이터 파일 선택",opts,default=opts,key=f"train_rows_{st.session_state.cycle}_{st.session_state.day}");ids={lookup[q] for q in selected}
        features=st.multiselect("사용 센서",FEATURES,default=FEATURES,key=f"features_{st.session_state.cycle}_{st.session_state.day}")
        epochs=st.slider("경사하강법 반복 횟수",10,200,80,10,key=f"epochs_{st.session_state.cycle}_{st.session_state.day}")
        if st.session_state.last_result:st.info("오늘의 판정은 완료��습니다. 다음 날 다시 학습할 수 있어요.")
        elif st.button("학습 후 오늘 CCTV 진단",key=f"run_{st.session_state.day}",use_container_width=True):
            ok,msg=train(ids,features,epochs)
            if ok:st.session_state.screen="summary" if st.session_state.day==7 else "game";st.rerun()
            else:st.error(msg)
        if st.session_state.loss is not None:st.metric("Loss · BCE",f'{st.session_state.loss:.4f}');st.metric("Gradient",f'{st.session_state.gradient:.4f}')

elif st.session_state.screen=="calendar":
    nav();st.markdown(f'<div class="hero"><span class="pill">WEEK {st.session_state.cycle}</span><h1>오른쪽 벽 달력 · 확대</h1></div>',unsafe_allow_html=True)
    st.markdown('<div class="expanded">'+calendar_html()+'</div>',unsafe_allow_html=True)

elif st.session_state.screen=="summary":
    n=st.session_state.wins
    if n>=5:title,mark,text,button,action="승진 축하해요!","★",f"7일 중 {n}회 성공! 야간정비대 관제반장으로 승진했습니다.","홈으로","home"
    elif n>=3:title,mark,text,button,action="다음 주도 부탁해!","✿",f"7일 중 {n}회 성공. 다음 7일을 계속 근무합니다.","다음 7일","retry"
    else:title,mark,text,button,action="근무 종료","×",f"7일 중 {n}회 성공. 이번 주 결과가 부족해 회사를 떠나게 되었습니다.","홈으로","home"
    st.markdown(f'<div class="result-box"><div style="font-size:4rem;color:#173b9b">{mark}</div><div class="logo-sub">WEEK REPORT · {st.session_state.cycle}</div><h1>{title}</h1><p>{text}</p>{calendar_html()}</div>',unsafe_allow_html=True)
    if st.button(button,key="summary_action",use_container_width=True):
        if action=="retry":st.session_state.cycle+=1;start_week()
        else:st.session_state.screen="start"
        st.rerun()
    if st.button("⌂ 홈으로 돌아가기",key="summary_home"):go_home()
