import math
import random

import streamlit as st

from pixel_art import room_scene, start_scene

st.set_page_config(page_title="하수관 야간정비대", page_icon="🚰", layout="wide", initial_sidebar_state="collapsed")

FEATURES = ["수압", "소음", "침전물", "부식"]
LEARNING_RATE = 0.9

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
:root { --navy:#101c59; --blue:#173b9b; --paper:#f5e8bd; --pink:#ef79ae; --mint:#50d5bd; }
html,body,[class*="css"]{font-family:'Gowun Dodum',sans-serif}.stApp{background:#b9c9eb;color:#17245f}
.block-container{max-width:1420px;padding-top:.45rem;padding-bottom:1.5rem}h1,h2,h3{font-family:'Jua',sans-serif!important}
.hero{text-align:center;padding:2px 0 7px}.hero h1{font-size:clamp(2rem,4vw,3.8rem);margin:0;color:#10246f;text-shadow:3px 4px #f8eab9,-1px -1px #fff;letter-spacing:.04em}
.logo-mark{font-family:'Jua',sans-serif;color:#f8eab9;-webkit-text-stroke:2px #101c59;text-shadow:4px 4px #101c59;font-size:clamp(2.6rem,5vw,4.7rem);letter-spacing:.08em;text-align:center;margin:3px 0 0}
.logo-sub{font:bold 12px monospace;color:#101c59;letter-spacing:.25em;text-align:center;margin-bottom:8px}
.pixel-frame{border:5px solid var(--navy);box-shadow:8px 8px 0 #3153a3;background:#608bd0;overflow:hidden}
.pill{display:inline-block;padding:4px 9px;border:2px solid var(--navy);background:#f7edcf;margin:3px;color:#14256f;font-family:'Jua',sans-serif;box-shadow:2px 2px 0 #3153a3}
.panel{background:#f7edcf;border:3px solid var(--navy);box-shadow:4px 4px 0 #3153a3;padding:11px 13px;margin:6px 0 10px}.panel h3{margin:.1rem 0 .4rem;color:#14256f}
.room-art{border:6px solid var(--navy);background:#7778ad;box-shadow:8px 8px 0 #3153a3;overflow:hidden;line-height:0}
.dialog{border:4px solid #fff4d8;outline:3px solid #101c59;box-shadow:6px 6px 0 #172c77;background:#0c1022;color:#fff6dc;padding:10px 15px;margin:10px auto;max-width:1200px}
.dialog-name{display:inline-block;border:2px solid #fff4d8;background:#20294e;color:#ffe67f;padding:3px 10px;font-family:'Jua',sans-serif}.dialog-text{line-height:1.55;margin-top:5px}
.day-strip{display:grid;grid-template-columns:repeat(7,1fr);gap:5px}.day-cell{text-align:center;border:2px solid #101c59;background:#f8edcc;padding:5px 1px;color:#1b2b70;font:10px monospace}.day-cell b{display:block;font:bold 17px monospace;min-height:19px}.day-cell.ok b{color:#008c73}.day-cell.no b{color:#c53b64}
.desktop{border:5px solid var(--navy);background:#3181c4;padding:14px;min-height:250px;box-shadow:7px 7px 0 #3153a3}.desktop-top{color:#fff4d8;font:12px monospace;padding:4px 7px 12px}.file-icon{text-align:center;border:2px solid #a9c5ff;background:#224eaa;color:#fff4d8;padding:12px 4px;min-height:90px}.file-icon b{display:block;font-size:2rem}
.expanded{background:#f7edcf;border:4px solid var(--navy);box-shadow:6px 6px 0 #3153a3;padding:16px}.stButton>button{border:3px solid #101c59!important;border-radius:0!important;background:#ffe583!important;color:#101c59!important;font-family:'Jua',sans-serif!important;font-size:1.02rem!important;box-shadow:3px 3px 0 #3153a3!important;min-height:2.5rem}.stButton>button:hover{background:#f58bb5!important;border-color:#101c59!important;color:#101c59!important}
div[data-testid="stMetric"]{background:#f7edcf;border:2px solid #101c59;padding:7px;border-radius:0}.stProgress>div>div{background:#176fc3!important}.result-box{text-align:center;background:#f7edcf;border:5px solid #101c59;box-shadow:7px 7px 0 #3153a3;padding:20px}footer{visibility:hidden}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def init_state():
    defaults = {"screen":"start","pc_page":"desktop","cycle":1,"day":1,"wins":0,"calendar":["","","","","","",""],"weights":[0.0]*4,"bias":0.0,"routes":[],"target":0,"last_result":None,"loss":None,"gradient":None,"examples":[]}
    for key,value in defaults.items():
        if key not in st.session_state: st.session_state[key]=value


def make_training_examples():
    examples=[]
    for i in range(40):
        faulty=i>=20; values=[random.uniform(.08,.50) for _ in FEATURES]
        if faulty:
            primary=(i-20)%4; values[primary]=random.uniform(.68,.99)
            for j in range(4):
                if j!=primary and random.random()<.32: values[j]=random.uniform(.56,.83)
        examples.append({"id":f"P{i+1:02d}","features":values,"label":int(faulty)})
    random.shuffle(examples); return examples


def new_routes():
    routes=[[random.uniform(.10,.52) for _ in FEATURES] for _ in range(4)]
    target=random.randrange(4); primary=random.randrange(4); routes[target][primary]=random.uniform(.70,.99)
    for j in range(4):
        if j!=primary and random.random()<.4: routes[target][j]=random.uniform(.58,.86)
    return routes,target


def sigmoid(z): return 1/(1+math.exp(-max(-30,min(30,z))))


def predict(features): return sigmoid(st.session_state.bias+sum(st.session_state.weights[i]*features[i] for i in range(4)))


def start_week():
    st.session_state.day=1; st.session_state.wins=0; st.session_state.calendar=[""]*7
    st.session_state.weights=[0.0]*4; st.session_state.bias=0.0; st.session_state.loss=None; st.session_state.gradient=None
    st.session_state.examples=make_training_examples(); st.session_state.routes,st.session_state.target=new_routes(); st.session_state.last_result=None; st.session_state.screen="game"


def train_and_diagnose(ids,features,epochs):
    rows=[r for r in st.session_state.examples if r["id"] in ids]
    if len(rows)<4 or len({r["label"] for r in rows})<2: return False,"정상·이상 데이터가 모두 있도록 4개 이상의 기록을 골라주세요."
    if not features: return False,"학습에 사용할 센서를 하나 이상 선택해주세요."
    active=[FEATURES.index(f) for f in features]; weights=st.session_state.weights[:]
    for j in range(4):
        if j not in active: weights[j]=0.0
    bias=st.session_state.bias; rate=LEARNING_RATE/math.sqrt(len(active)); grad_size=0.0; eps=1e-8
    for _ in range(epochs):
        probs=[sigmoid(bias+sum(weights[j]*r["features"][j] for j in active)) for r in rows]
        grad=[0.0]*4
        for j in active: grad[j]=sum((p-r["label"])*r["features"][j] for p,r in zip(probs,rows))/len(rows)
        grad_b=sum(p-r["label"] for p,r in zip(probs,rows))/len(rows)
        grad_size=math.sqrt(sum(grad[j]**2 for j in active)+grad_b**2)
        weights=[weights[j]-rate*grad[j] for j in range(4)]; bias-=rate*grad_b
    st.session_state.weights=weights; st.session_state.bias=bias; st.session_state.gradient=grad_size
    probs=[sigmoid(bias+sum(weights[j]*r["features"][j] for j in active)) for r in rows]
    st.session_state.loss=-sum(r["label"]*math.log(max(eps,p))+(1-r["label"])*math.log(max(eps,1-p)) for r,p in zip(rows,probs))/len(rows)
    scores=[predict(r) for r in st.session_state.routes]; chosen=max(range(4),key=lambda j:scores[j]); success=chosen==st.session_state.target
    st.session_state.calendar[st.session_state.day-1]="O" if success else "X"; st.session_state.wins+=int(success)
    st.session_state.last_result={"success":success,"chosen":chosen,"target":st.session_state.target,"scores":scores}
    if st.session_state.day==7: st.session_state.screen="summary"
    return True,"done"


def calendar_html():
    return '<div class="day-strip">'+''.join(f'<div class="day-cell {"ok" if x=="O" else "no" if x=="X" else ""}">DAY {i+1}<b>{x or "·"}</b></div>' for i,x in enumerate(st.session_state.calendar))+'</div>'


def home(): st.session_state.screen="start"; st.session_state.pc_page="desktop"; st.rerun()


init_state()

if st.session_state.screen=="start":
    st.markdown('<div class="logo-mark">하수관 야간정비대</div><div class="logo-sub">DRAIN TOWN · NIGHT WATCH</div>',unsafe_allow_html=True)
    st.markdown('<div class="pixel-frame">'+start_scene()+'</div>',unsafe_allow_html=True)
    st.markdown('<div class="hero"><span class="pill">7일 야간 근무</span><span class="pill">4분할 CCTV</span><span class="pill">경사하강법으로 AI 학습</span></div>',unsafe_allow_html=True)
    _,c,_=st.columns([1,1.3,1])
    with c:
        if st.button("▶▶▶　　 START　　 ◀◀◀",use_container_width=True,key="start"): st.session_state.cycle=1; start_week(); st.rerun()

elif st.session_state.screen=="game":
    st.markdown(f'<div class="hero"><span class="pill">근무 {st.session_state.cycle}회차</span><span class="pill">DAY {st.session_state.day} / 7</span><span class="pill">NIGHT {st.session_state.day} · 1 AM</span><h1>관제실</h1></div>',unsafe_allow_html=True)
    st.markdown('<div class="room-art">'+room_scene(st.session_state.routes)+'</div>',unsafe_allow_html=True)
    left,center,right=st.columns([.85,2.4,.85],gap="small")
    with left:
        st.markdown('<div class="panel"><h3>🖥 벽면 PC</h3><span>학습 파일을 열어요</span></div>',unsafe_allow_html=True)
        if st.button("PC 확대 / 파일 열기",key="pc_open",use_container_width=True): st.session_state.screen="pc"; st.session_state.pc_page="desktop"; st.rerun()
    with center:
        st.markdown('<div class="panel"><h3>거대한 CCTV 스크린 · 4채널</h3><span>PC에서 오늘의 학습을 실행하면 AI가 네 화면을 판별합니다.</span></div>',unsafe_allow_html=True)
        if st.session_state.last_result:
            r=st.session_state.last_result
            (st.success if r["success"] else st.error)(f'AI 선택 CAM 0{r["chosen"]+1} · 실제 이상 CAM 0{r["target"]+1}')
            if st.session_state.day<7 and st.button("다음 날 근무 →",key=f"next{st.session_state.day}",use_container_width=True):
                st.session_state.day+=1; st.session_state.routes,st.session_state.target=new_routes(); st.session_state.last_result=None; st.rerun()
    with right:
        st.markdown('<div class="panel"><h3>벽면 달력</h3>'+calendar_html()+'</div>',unsafe_allow_html=True)
        if st.button("달력 확대 보기",key="calendar_open",use_container_width=True): st.session_state.screen="calendar"; st.rerun()
    st.markdown('<div class="dialog"><span class="dialog-name">야간 정비사</span><div class="dialog-text">PC에서 데이터 파일과 학습할 센서를 골라 AI를 훈련시켜. 그 결과에 따라 오늘의 CCTV 진단 성공 여부가 결정돼.</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns([5,1])
    with c1:
        if st.session_state.loss is not None:
            m1,m2,m3=st.columns(3); m1.metric("Loss · BCE",f'{st.session_state.loss:.3f}'); m2.metric("Gradient",f'{st.session_state.gradient:.3f}'); m3.metric("성공",f'{st.session_state.wins}/7')
    with c2:
        if st.button("⌂ 홈으로",key="game_home",use_container_width=True): home()

elif st.session_state.screen=="pc":
    a,b,c=st.columns([1,4,1])
    with a:
        if st.button("← 관제실",key="pc_back"): st.session_state.screen="game"; st.rerun()
    with b: st.markdown(f'<div class="hero"><span class="pill">PC DISPLAY · DAY {st.session_state.day}/7</span><h1>정비실 컴퓨터</h1></div>',unsafe_allow_html=True)
    with c:
        if st.button("⌂ 홈",key="pc_home"): home()
    st.markdown('<div class="desktop"><div class="desktop-top">DRAIN TOWN MAINTENANCE OS　● ONLINE　/　 FILES</div>',unsafe_allow_html=True)
    files=[("📊","점검 데이터.csv","data"),("📘","경사하강법.txt","guide"),("🧠","AI 모델.bin","model"),("🛠","오늘의 학습.exe","train")]
    cols=st.columns(4)
    for col,(icon,label,page) in zip(cols,files):
        with col:
            st.markdown(f'<div class="file-icon"><b>{icon}</b>{label}</div>',unsafe_allow_html=True)
            if st.button("열기",key=f"file_{page}_{st.session_state.day}",use_container_width=True): st.session_state.pc_page=page; st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)
    page=st.session_state.pc_page
    if page=="data":
        st.markdown('<div class="expanded"><h2>점검 데이터 파일</h2><p>정상 및 이상 관로의 센서 기록입니다. 학습에 포함할 데이터를 확인하세요.</p></div>',unsafe_allow_html=True)
        rows=st.session_state.examples; options=[f'{r["id"]} · {"이상" if r["label"] else "정상"}' for r in rows]; maps={s:r["id"] for s,r in zip(options,rows)}
        chosen=st.multiselect("기록 선택",options,default=options,key=f"data_{st.session_state.cycle}_{st.session_state.day}"); ids={maps[s] for s in chosen}
        st.dataframe([{"파일":r["id"],"판정":"이상" if r["label"] else "정상",**{FEATURES[i]:round(r["features"][i],2) for i in range(4)},"사용":"✓" if r["id"] in ids else ""} for r in rows],use_container_width=True,hide_index=True,height=260)
    elif page=="guide":
        st.markdown('<div class="expanded"><h2>경사하강법.txt</h2><p>모델은 수압·소음·침전물·부식 기록으로 관로의 이상 확률을 예측합니다. 예측과 점검 라벨의 차이를 손실(Loss)로 계산하고, 경사(Gradient)를 따라 가중치를 조금씩 바꿉니다.</p><p><code>새 가중치 = 기존 가중치 − 학습률 × 기울기</code></p><p>PC에서 선택한 데이터와 센서 특징에 따라 학습 결과가 달라지고, 그 결과로 오늘의 CCTV 진단을 합니다.</p></div>',unsafe_allow_html=True)
    elif page=="model":
        st.markdown('<div class="expanded"><h2>AI 모델.bin</h2><p>현재 모델 파라미터</p></div>',unsafe_allow_html=True)
        ms=st.columns(4)
        for i,label in enumerate(FEATURES): ms[i].metric(label,f'{st.session_state.weights[i]:+.3f}')
        st.metric("bias",f'{st.session_state.bias:+.3f}')
        if st.session_state.loss is not None: st.metric("Loss",f'{st.session_state.loss:.4f}')
    elif page=="train":
        st.markdown('<div class="expanded"><h2>오늘의 학습.exe</h2><p>선택한 점검 기록과 센서로 로지스틱 회귀 모델을 경사하강법 학습한 뒤, 오늘의 CCTV 네 화면을 진단합니다.</p></div>',unsafe_allow_html=True)
        rows=st.session_state.examples; options=[f'{r["id"]} · {"이상" if r["label"] else "정상"}' for r in rows]; maps={s:r["id"] for s,r in zip(options,rows)}
        selected=st.multiselect("학습 데이터 선택",options,default=options,key=f"train_data_{st.session_state.cycle}_{st.session_state.day}"); ids={maps[s] for s in selected}
        features=st.multiselect("사용할 센서",FEATURES,default=FEATURES,key=f"train_features_{st.session_state.cycle}_{st.session_state.day}")
        epochs=st.slider("경사하강법 반복 횟수",10,200,80,10,key=f"epochs_{st.session_state.cycle}_{st.session_state.day}")
        st.caption(f"학습률 η={LEARNING_RATE:.2f} · BCE 손실의 기울기로 모델을 업데이트합니다.")
        if st.session_state.last_result: st.info("오늘의 진단은 이미 완료됐습니다. 다음 날 PC에서 다시 학습하세요.")
        elif st.button("학습하고 오늘의 CCTV 진단",key=f"train_{st.session_state.day}",use_container_width=True):
            ok,msg=train_and_diagnose(ids,features,epochs)
            if ok: st.session_state.screen="summary" if st.session_state.day==7 else "game"; st.rerun()
            else: st.error(msg)
    if st.button("⌂ 홈으로 돌아가기",key="pc_home_bottom"): home()

elif st.session_state.screen=="calendar":
    l,m,r=st.columns([1,4,1])
    with l:
        if st.button("← 관제실",key="calendar_back"): st.session_state.screen="game"; st.rerun()
    with m: st.markdown(f'<div class="hero"><span class="pill">WEEK {st.session_state.cycle}</span><h1>주간 점검 달력</h1></div>',unsafe_allow_html=True)
    with r:
        if st.button("⌂ 홈",key="calendar_home"): home()
    st.markdown('<div class="expanded">'+calendar_html()+'</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><h3>기록 안내</h3><p>AI가 실제 이상 관로를 맞히면 O, 틀리면 X로 기록됩니다.</p></div>',unsafe_allow_html=True)

elif st.session_state.screen=="summary":
    wins=st.session_state.wins
    if wins>=5: title,emoji,msg,button,action="승진 축하해요!","★",f"7일 중 {wins}회 성공! 야간정비대 관제반장으로 승진했습니다.","홈으로","home"
    elif wins>=3: title,emoji,msg,button,action="다음 주도 부탁해!","✿",f"7일 중 {wins}회 성공. 다음 7일을 계속 근무합니다.","다음 7일 시작","retry"
    else: title,emoji,msg,button,action="근무 종료","×",f"7일 중 {wins}회 성공. 이번 주 결과가 부족해 회사를 떠나게 되었습니다.","홈으로","home"
    st.markdown(f'<div class="result-box"><div style="font-size:4rem;color:#173b9b">{emoji}</div><div class="small-label">WEEK REPORT · {st.session_state.cycle}</div><h1>{title}</h1><p>{msg}</p>{calendar_html()}</div>',unsafe_allow_html=True)
    _,c,_=st.columns([1,1.2,1])
    with c:
        if st.button(button,key="summary_action",use_container_width=True):
            if action=="retry": st.session_state.cycle+=1; start_week()
            else: st.session_state.screen="start"
            st.rerun()
    if st.button("⌂ 홈으로 돌아가기",key="summary_home"): home()
