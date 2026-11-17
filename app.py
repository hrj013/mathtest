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
.block-container{max-width:1380px;padding-top:.25rem;padding-bottom:1rem}h1,h2,h3{font-family:'Jua',sans-serif!important}
.hero{text-align:center;color:#f5e8bd;padding:2px 0 7px}.hero h1{color:#f5e8bd;text-shadow:2px 3px #101c59;margin:2px}
.day-strip{display:grid;grid-template-columns:repeat(7,1fr);gap:8px}.day-cell{text-align:center;border:2px solid #101c59;background:#f8edcc;padding:12px 4px;color:#1b2b70;font:13px monospace}.day-cell b{display:block;font:bold 24px monospace;min-height:28px}.day-cell.ok b{color:#008c73}.day-cell.no b{color:#c53b64}
.stButton>button{border:2px solid #101c59!important;border-radius:4px!important;background:#f4df9b!important;color:#1a2934!important;font-family:'Jua',sans-serif!important;box-shadow:0 3px 7px #0005!important}
.note-paper{max-width:850px;margin:20px auto;background:#f3e7c7;color:#29251d;padding:34px 42px;border:1px solid #c5b68f;box-shadow:0 12px 35px #0008;font-family:Georgia,'Noto Serif',serif;line-height:1.75}
.note-paper h1{color:#34302a;text-align:center;border-bottom:1px solid #b7a982;padding-bottom:12px}.note-paper .formula{text-align:center;background:#e8ddbd;padding:12px;font-size:1.15rem;margin:18px 0}
.file-panel{background:#f7edcf;color:#17275f;border:3px solid #101c59;padding:16px;margin:10px 0}
</style>""",unsafe_allow_html=True)


def init_state():
    defaults={"screen":"start","pc_page":"desktop","cycle":1,"day":1,"wins":0,"calendar":[""]*7,"weights":[0.0]*4,"bias":0.0,"routes":[],"target":0,"last_result":None,"loss":None,"gradient":None,"examples":[]}
    for key,value in defaults.items():
        if key not in st.session_state: st.session_state[key]=value


def make_examples():
    rows=[]
    for i in range(40):
        label=int(i>=20); values=[random.uniform(.08,.50) for _ in FEATURES]
        if label:
            j=(i-20)%4; values[j]=random.uniform(.68,.99)
            for k in range(4):
                if k!=j and random.random()<.32: values[k]=random.uniform(.56,.83)
        rows.append({"id":f"P{i+1:02d}","x":values,"y":label})
    random.shuffle(rows); return rows


def make_routes():
    routes=[[random.uniform(.1,.52) for _ in FEATURES] for _ in range(4)]
    target=random.randrange(4); primary=random.randrange(4); routes[target][primary]=random.uniform(.7,.99)
    for j in range(4):
        if j!=primary and random.random()<.4: routes[target][j]=random.uniform(.58,.86)
    return routes,target


def sigmoid(z): return 1/(1+math.exp(-max(-30,min(30,z))))
def predict(x): return sigmoid(st.session_state.bias+sum(st.session_state.weights[j]*x[j] for j in range(4)))


def start_week():
    st.session_state.day=1; st.session_state.wins=0; st.session_state.calendar=[""]*7
    st.session_state.weights=[0.0]*4; st.session_state.bias=0.0; st.session_state.loss=None; st.session_state.gradient=None
    st.session_state.examples=make_examples(); st.session_state.routes,st.session_state.target=make_routes()
    st.session_state.last_result=None; st.session_state.screen="game"


def train(ids,features,epochs):
    rows=[row for row in st.session_state.examples if row["id"] in ids]
    if len(rows)<4 or len({row["y"] for row in rows})<2: return False,"정상·이상 데이터가 모두 있도록 4개 이상의 기록을 선택해주세요."
    if not features: return False,"학습 센서를 하나 이상 선택해주세요."
    active=[FEATURES.index(f) for f in features]; weights=st.session_state.weights[:]
    for j in range(4):
        if j not in active: weights[j]=0.0
    bias=st.session_state.bias; rate=LEARNING_RATE/math.sqrt(len(active)); gradient=0.0; eps=1e-8
    for _ in range(epochs):
        probs=[sigmoid(bias+sum(weights[j]*r["x"][j] for j in active)) for r in rows]
        grad_w=[0.0]*4
        for j in active: grad_w[j]=sum((p-r["y"])*r["x"][j] for p,r in zip(probs,rows))/len(rows)
        grad_b=sum(p-r["y"] for p,r in zip(probs,rows))/len(rows)
        gradient=math.sqrt(sum(grad_w[j]**2 for j in active)+grad_b**2)
        weights=[weights[j]-rate*grad_w[j] for j in range(4)]; bias-=rate*grad_b
    st.session_state.weights=weights; st.session_state.bias=bias; st.session_state.gradient=gradient
    probs=[sigmoid(bias+sum(weights[j]*r["x"][j] for j in active)) for r in rows]
    st.session_state.loss=-sum(r["y"]*math.log(max(eps,p))+(1-r["y"])*math.log(max(eps,1-p)) for r,p in zip(rows,probs))/len(rows)
    scores=[predict(r) for r in st.session_state.routes]; chosen=max(range(4),key=lambda j:scores[j]); success=chosen==st.session_state.target
    st.session_state.calendar[st.session_state.day-1]="O" if success else "X"; st.session_state.wins+=int(success)
    st.session_state.last_result={"success":success,"chosen":chosen,"target":st.session_state.target,"scores":scores}
    if st.session_state.day==7: st.session_state.screen="summary"
    return True,"done"


def calendar_html():
    return '<div class="day-strip">'+''.join(f'<div class="day-cell {"ok" if x=="O" else "no" if x=="X" else ""}">DAY {i+1}<b>{x or "·"}</b></div>' for i,x in enumerate(st.session_state.calendar))+'</div>'


def handle_navigation():
    """Top-level navigation handler; start is a native Streamlit button, not an iframe link."""
    action=st.query_params.get("open")
    if action in {"game","pc","calendar","note"}:
        st.session_state.screen=action
        if action=="pc": st.session_state.pc_page="desktop"
        st.query_params.clear()


def scene_html(image, hotspots):
    buf=BytesIO(); image.save(buf,format="PNG")
    encoded=base64.b64encode(buf.getvalue()).decode("ascii")
    links="".join(f'<a href="?open={action}" target="_top" aria-label="{label}" title="{label}" style="position:absolute;left:{x}%;top:{y}%;width:{w}%;height:{h}%;cursor:pointer"></a>' for x,y,w,h,action,label in hotspots)
    return f'<div style="position:relative;width:100%;aspect-ratio:{image.width}/{image.height};overflow:hidden"><img src="data:image/png;base64,{encoded}" style="display:block;width:100%;height:100%;object-fit:fill">{links}</div>'


def back_link():
    st.markdown('<a href="?open=game" target="_top" style="display:inline-block;color:#d9defa;text-decoration:none;padding:5px 0">← 관제실</a>',unsafe_allow_html=True)


def render_note():
    st.markdown('''<div class="note-paper"><h1>경사하강법이란?</h1><p>경사하강법은 모델의 예측이 정답에 가까워지도록 <b>오차가 줄어드는 방향으로 가중치를 조금씩 조정하는 방법</b>입니다.</p><ol><li>현재 가중치로 관로 이상 확률을 예측합니다.</li><li>예측과 실제 점검 결과의 차이로 손실(Loss)을 계산합니다.</li><li>손실이 감소하는 방향(기울기)을 구합니다.</li><li>학습률만큼 가중치를 이동하고 반복합니다.</li></ol><div class="formula">새 가중치 = 기존 가중치 − 학습률 × 기울기</div><p>수압·소음·침전물·부식 기록을 학습해 CCTV 네 관로 중 이상 위험이 높은 곳을 찾습니다.</p></div>''',unsafe_allow_html=True)


def render_pc():
    st.image(art.zoomed_object(st.session_state.routes,"pc"),use_container_width=True)
    st.markdown('<div class="file-panel"><h3>파일</h3><p>점검 기록과 AI 학습 자료</p></div>',unsafe_allow_html=True)
    files=[("📁 점검 데이터","data"),("📁 경사하강법 안내","guide"),("📁 AI 모델","model"),("📁 오늘의 학습","train")]
    cols=st.columns(4)
    for col,(label,page) in zip(cols,files):
        with col:
            if st.button(label,key=f"folder_{page}",use_container_width=True): st.session_state.pc_page=page
    page=st.session_state.pc_page
    if page=="desktop": return
    if page=="data":
        rows=st.session_state.examples; options=[f'{r["id"]} · {"이상" if r["y"] else "정상"}' for r in rows]; lookup={name:r["id"] for name,r in zip(options,rows)}
        selected=st.multiselect("학습할 기록",options,default=options,key=f"data_{st.session_state.day}"); ids={lookup[x] for x in selected}
        st.dataframe([{"파일":r["id"],"판정":"이상" if r["y"] else "정상",**{FEATURES[j]:round(r["x"][j],2) for j in range(4)},"포함":"✓" if r["id"] in ids else ""} for r in rows],use_container_width=True,hide_index=True)
    elif page=="guide":
        st.markdown('<div class="file-panel"><h2>경사하강법 안내</h2><p>예측 오차를 줄이는 방향으로 모델의 가중치를 반복해서 조정하는 학습 방법입니다.</p><p><code>새 가중치 = 기존 가중치 − 학습률 × 기울기</code></p></div>',unsafe_allow_html=True)
    elif page=="model":
        cols=st.columns(4)
        for j in range(4): cols[j].metric(FEATURES[j],f'{st.session_state.weights[j]:+.3f}')
        st.metric("bias",f'{st.session_state.bias:+.3f}')
    elif page=="train":
        rows=st.session_state.examples; options=[f'{r["id"]} · {"이상" if r["y"] else "정상"}' for r in rows]; lookup={name:r["id"] for name,r in zip(options,rows)}
        selected=st.multiselect("학습 데이터 파일",options,default=options,key=f"train_rows_{st.session_state.day}"); ids={lookup[x] for x in selected}
        features=st.multiselect("사용 센서",FEATURES,default=FEATURES,key=f"features_{st.session_state.day}"); epochs=st.slider("학습 반복 횟수",10,200,80,10,key=f"epochs_{st.session_state.day}")
        if st.button("학습 후 오늘 진단",key=f"run_{st.session_state.day}",use_container_width=True):
            ok,msg=train(ids,features,epochs)
            if ok: st.session_state.screen="summary" if st.session_state.day==7 else "game"; st.rerun()
            else: st.error(msg)


init_state()
handle_navigation()

if st.session_state.screen=="start":
    start_bytes=art.start_scene_gif()
    # Text and title are overlaid on the scene; the native button below reliably starts the game.
    encoded=base64.b64encode(start_bytes).decode("ascii")
    components.html(f'''<div style="position:relative;width:100%;aspect-ratio:5/3;overflow:hidden"><img src="data:image/gif;base64,{encoded}" style="width:100%;height:100%;object-fit:cover"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#f3fff2;font:bold clamp(30px,5vw,64px) 'Malgun Gothic',sans-serif;text-shadow:0 3px 8px #000;text-align:center">하수관 야간정비대</div></div>''',height=590,scrolling=False)
    _,center,_=st.columns([1,1,1])
    with center:
        if st.button("START",key="start_game",use_container_width=True):
            start_week()
            st.rerun()

elif st.session_state.screen=="game":
    st.markdown(f'<div class="hero">근무 {st.session_state.cycle}회차　·　DAY {st.session_state.day}/7</div>',unsafe_allow_html=True)
    st.markdown(scene_html(art.room_scene(st.session_state.routes),[(3,36,29,44,"pc","컴퓨터 확대"),(82,24,17,34,"calendar","달력 확대"),(30,88,45,11,"note","책상 쪽지 보기")]),unsafe_allow_html=True)
    if st.session_state.last_result:
        result=st.session_state.last_result
        if result["success"]: st.success(f'AI가 CAM 0{result["chosen"]+1}의 이상을 찾았습니다.')
        else: st.error(f'AI는 CAM 0{result["chosen"]+1}을 골랐지만 실제 이상은 CAM 0{result["target"]+1}이었습니다.')
        if st.session_state.day<7 and st.button("다음 날 →",key=f"next_{st.session_state.day}"):
            st.session_state.day+=1; st.session_state.routes,st.session_state.target=make_routes(); st.session_state.last_result=None; st.rerun()
        st.caption(f'성공 {st.session_state.wins}/7　·　Loss {st.session_state.loss:.3f}')

elif st.session_state.screen=="pc":
    back_link(); render_pc()
elif st.session_state.screen=="calendar":
    back_link(); st.image(art.zoomed_object(st.session_state.routes,"calendar"),use_container_width=True); st.markdown(calendar_html(),unsafe_allow_html=True)
elif st.session_state.screen=="note":
    back_link(); render_note()
elif st.session_state.screen=="summary":
    wins=st.session_state.wins
    title="승진 축하해요!" if wins>=5 else "다음 주도 부탁해!" if wins>=3 else "근무 종료"
    st.markdown(f'<div class="file-panel"><h1>{title}</h1><p>7일 중 {wins}회 성공</p>{calendar_html()}</div>',unsafe_allow_html=True)
    if st.button("다음 7일" if 3<=wins<5 else "홈으로",key="summary_action"):
        if 3<=wins<5: st.session_state.cycle+=1; start_week()
        else: st.session_state.screen="start"
        st.rerun()
