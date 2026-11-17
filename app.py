import base64
import math
import random
from io import BytesIO
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import pixel_art as art

st.set_page_config(page_title="하수관 야간정비대", page_icon="🚰", layout="wide", initial_sidebar_state="collapsed")
FEATURES = ["수압", "소음", "침전물", "부식"]
LEARNING_RATE = 0.9
ASSETS = Path(__file__).parent / "assets"

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap');
:root{--navy:#101c59;--paper:#f5e8bd}
html,body,[class*="css"]{font-family:'Gowun Dodum',sans-serif}.stApp{background:#15182e;color:#f5e8bd}
.block-container{max-width:1380px;padding-top:.25rem;padding-bottom:1rem}h1,h2,h3{font-family:'Jua',sans-serif!important}
.hero{text-align:center;color:#f5e8bd;padding:2px 0 7px}.hero h1{color:#f5e8bd;text-shadow:2px 3px #101c59;margin:2px}
.day-strip{display:grid;grid-template-columns:repeat(7,1fr);gap:8px}.day-cell{text-align:center;border:2px solid #101c59;background:#f8edcc;padding:12px 4px;color:#1b2b70;font:13px monospace}.day-cell b{display:block;font:bold 24px monospace;min-height:28px}.day-cell.ok b{color:#008c73}.day-cell.no b{color:#c53b64}
.stButton>button{border:2px solid #101c59!important;border-radius:3px!important;background:#ffe583!important;color:#101c59!important;font-family:'Jua',sans-serif!important;box-shadow:2px 2px #3153a3!important}
.note-paper{max-width:850px;margin:20px auto;background:#f3e7c7;color:#29251d;padding:34px 42px;border:1px solid #c5b68f;box-shadow:0 12px 35px #0008;font-family:Georgia,'Noto Serif',serif;line-height:1.75}
.note-paper h1{color:#34302a;text-align:center;border-bottom:1px solid #b7a982;padding-bottom:12px}.note-paper .formula{text-align:center;background:#e8ddbd;padding:12px;font-size:1.15rem;margin:18px 0}
.file-panel{background:#f7edcf;color:#17275f;border:3px solid #101c59;padding:16px;margin:10px 0}
</style>""",unsafe_allow_html=True)


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


def route_from_query():
    """Handle clicks on the scene hotspots and desktop folders."""
    action=st.query_params.get("open")
    file_page=st.query_params.get("file")
    if st.query_params.get("start") == "1":
        start_week()
    elif action in {"pc","calendar","note","game"}:
        st.session_state.screen=action
        if action=="pc":
            st.session_state.pc_page="desktop"
    elif file_page in {"data","guide","model","train"}:
        st.session_state.screen="pc"
        st.session_state.pc_page=file_page
    if action or file_page or st.query_params.get("start"):
        st.query_params.clear()


def image_bytes(which):
    """Use supplied image files when present; otherwise keep the in-repo art fallback.

    Put the two reference images at assets/start_scene.png and
    assets/control_room.png to use those exact illustrations in the app.
    """
    path=ASSETS / ("start_scene.png" if which=="start" else "control_room.png")
    if path.exists():
        return path.read_bytes(), ImageRatio.read(path)
    scene=art.start_scene() if which=="start" else art.room_scene(st.session_state.routes)
    buffer=BytesIO()
    scene.save(buffer,format="PNG")
    return buffer.getvalue(), scene.width/scene.height


class ImageRatio:
    @staticmethod
    def read(path):
        from PIL import Image
        with Image.open(path) as image:
            return image.width/image.height


def render_start_screen():
    gif_fn=getattr(art,"start_scene_gif",None)
    if (ASSETS/"start_scene.png").exists():
        data,ratio=image_bytes("start")
        encoded=base64.b64encode(data).decode("ascii")
        source=f"data:image/png;base64,{encoded}"
    elif callable(gif_fn):
        encoded=base64.b64encode(gif_fn()).decode("ascii")
        source=f"data:image/gif;base64,{encoded}"
        ratio=16/9
    else:
        data,ratio=image_bytes("start")
        encoded=base64.b64encode(data).decode("ascii")
        source=f"data:image/png;base64,{encoded}"
    height=max(430,min(760,int(1320/ratio)))
    components.html(f'''<div style="position:relative;width:100%;aspect-ratio:{ratio};overflow:hidden;background:#10182b">
<img src="{source}" alt="하수구에서 물이 흐르는 장면" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">
<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;background:linear-gradient(transparent 25%,rgba(0,0,0,.2) 75%)">
<div style="font-family:'Malgun Gothic',sans-serif;font-weight:800;font-size:clamp(34px,6vw,72px);letter-spacing:.04em;color:#fff4d6;text-shadow:0 3px 4px #071c28,2px 5px 0 #122b35;text-align:center">하수관 야간정비대</div>
<a href="?start=1" target="_top" style="display:inline-block;text-decoration:none;padding:12px 44px;background:rgba(13,44,55,.86);border:2px solid #b9eee0;border-radius:4px;color:#f3fff7;font:700 20px 'Malgun Gothic',sans-serif;letter-spacing:.12em;box-shadow:0 3px 14px #06151d">START</a>
</div></div>''',height=height,scrolling=False)


def render_room():
    data,ratio=image_bytes("room")
    encoded=base64.b64encode(data).decode("ascii")
    # Hotspots correspond to the PC, calendar, and middle desk in the supplied room reference.
    # On the 640x360 fallback, these boxes are mapped to the matching drawn objects.
    if (ASSETS/"control_room.png").exists():
        pc=(3,39,26,27); calendar=(82,17,17,34); desk=(28,76,45,20)
    else:
        pc=(8,40,20,23); calendar=(85,25,12,25); desk=(2,60,32,28)
    height=max(430,min(760,int(1320/ratio)))
    components.html(f'''<div style="position:relative;width:100%;aspect-ratio:{ratio};overflow:hidden;background:#10182b">
<img src="data:image/png;base64,{encoded}" alt="야간 하수관 관제실" style="position:absolute;inset:0;width:100%;height:100%;object-fit:fill">
<a href="?open=pc" target="_top" title="컴퓨터 확대" aria-label="컴퓨터 확대" style="position:absolute;left:{pc[0]}%;top:{pc[1]}%;width:{pc[2]}%;height:{pc[3]}%;cursor:pointer"></a>
<a href="?open=calendar" target="_top" title="달력 확대" aria-label="달력 확대" style="position:absolute;left:{calendar[0]}%;top:{calendar[1]}%;width:{calendar[2]}%;height:{calendar[3]}%;cursor:pointer"></a>
<a href="?open=note" target="_top" title="경사하강법 쪽지 보기" aria-label="책상 위 쪽지 보기" style="position:absolute;left:{desk[0]}%;top:{desk[1]}%;width:{desk[2]}%;height:{desk[3]}%;cursor:pointer"></a>
</div>''',height=height,scrolling=False)


def render_pc_desktop():
    folders=[("점검 데이터","data"),("경사하강법 안내","guide"),("AI 모델","model"),("오늘의 학습","train")]
    folder_svg='''<svg viewBox="0 0 64 50" width="56" height="44" aria-hidden="true"><path d="M4 10a4 4 0 0 1 4-4h18l6 7h24a4 4 0 0 1 4 4v25a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z" fill="#d99a18"/><path d="M4 17a4 4 0 0 1 4-4h48a4 4 0 0 1 4 4v25a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z" fill="#f4c542"/><path d="M7 20h50v2H7z" fill="#ffdf72"/></svg>'''
    icons="".join(f'''<a href="?file={page}" target="_top" style="width:86px;height:80px;display:flex;flex-direction:column;align-items:center;gap:3px;text-decoration:none;color:white;text-shadow:1px 1px 2px #17243b;font:12px 'Segoe UI',Arial,sans-serif">{folder_svg}<span>{label}</span></a>''' for label,page in folders)
    markup=f'''<div style="height:420px;position:relative;overflow:hidden;font-family:'Segoe UI',Arial,sans-serif;color:white;background:radial-gradient(ellipse at 68% 48%,#21a7d6 0%,#087bb8 20%,transparent 42%),radial-gradient(ellipse at 27% 82%,#1362a7 0%,#183b78 34%,transparent 58%),linear-gradient(135deg,#10264f,#087bb4 55%,#164e8c);border:1px solid #263c61">
<div style="position:absolute;left:12px;top:12px;display:grid;grid-template-columns:repeat(2,90px);gap:5px">{icons}</div>
<div style="position:absolute;left:0;right:0;bottom:0;height:43px;display:flex;align-items:center;justify-content:center;gap:10px;background:rgba(24,36,55,.84);border-top:1px solid #ffffff36"><b style="font-size:23px;color:#77c7ff">⊞</b><span style="width:210px;height:27px;border-radius:15px;background:#e2edf8;color:#354254;padding:5px 12px;font-size:12px">⌕　검색</span><span style="position:absolute;right:15px;font-size:11px">◖)))　▰　오후 11:00</span></div></div>'''
    components.html(markup,height=420,scrolling=False)


def back_link(target="game"):
    text="← 관제실" if target=="game" else "← 컴퓨터"
    href="?open=game" if target=="game" else "?open=pc"
    st.markdown(f'<a href="{href}" target="_top" style="display:inline-block;color:#d9defa;text-decoration:none;padding:5px 0">{text}</a>',unsafe_allow_html=True)


def render_note():
    st.markdown('''<div class="note-paper"><h1>경사하강법이란?</h1>
<p>경사하강법은 모델의 예측이 정답에 가까워지도록 <b>오차가 줄어드는 방향으로 모델의 가중치를 조금씩 조정하는 방법</b>입니다.</p>
<ol><li>현재 가중치로 관로 이상 확률을 예측합니다.</li><li>예측과 실제 점검 결과의 차이로 손실(Loss)을 계산합니다.</li><li>손실이 가장 빠르게 줄어드는 방향(기울기)을 구합니다.</li><li>학습률만큼 가중치를 이동하고 이 과정을 반복합니다.</li></ol>
<div class="formula">새 가중치 = 기존 가중치 − 학습률 × 기울기</div>
<p>이 게임에서는 수압·소음·침전물·부식 기록을 학습해 CCTV 네 관로 중 이상 위험이 가장 높은 곳을 찾습니다.</p></div>''',unsafe_allow_html=True)


def show_page_details(page):
    if page=="data":
        st.markdown('<div class="file-panel"><h2>점검 데이터</h2><p>정상·이상 점검 기록을 선택하세요.</p></div>',unsafe_allow_html=True)
        rows=st.session_state.examples
        options=[f'{row["id"]} · {"이상" if row["y"] else "정상"}' for row in rows]
        lookup={name:row["id"] for name,row in zip(options,rows)}
        selected=st.multiselect("학습할 기록",options,default=options,key=f"data_{st.session_state.cycle}_{st.session_state.day}")
        ids={lookup[name] for name in selected}
        st.dataframe([{"파일":row["id"],"판정":"이상" if row["y"] else "정상",**{FEATURES[j]:round(row["x"][j],2) for j in range(4)},"포함":"✓" if row["id"] in ids else ""} for row in rows],use_container_width=True,hide_index=True,height=270)
    elif page=="guide":
        st.markdown('<div class="file-panel"><h2>경사하강법 안내</h2><p>예측 오차를 줄이도록 가중치를 조금씩 조정하는 학습 방법입니다. 손실(Loss)의 기울기(Gradient)를 계산하고 학습률에 따라 가중치를 갱신합니다.</p><p><code>새 가중치 = 기존 가중치 − 학습률 × 기울기</code></p></div>',unsafe_allow_html=True)
    elif page=="model":
        st.markdown('<div class="file-panel"><h2>AI 모델</h2><p>현재 모델 파라미터</p></div>',unsafe_allow_html=True)
        cols=st.columns(4)
        for j in range(4):
            cols[j].metric(FEATURES[j],f'{st.session_state.weights[j]:+.3f}')
        st.metric("bias",f'{st.session_state.bias:+.3f}')
    elif page=="train":
        st.markdown('<div class="file-panel"><h2>오늘의 진단</h2><p>점검 기록으로 AI를 학습시킨 뒤 CCTV의 네 관로를 판별합니다.</p></div>',unsafe_allow_html=True)
        rows=st.session_state.examples
        options=[f'{row["id"]} · {"이상" if row["y"] else "정상"}' for row in rows]
        lookup={name:row["id"] for name,row in zip(options,rows)}
        selected=st.multiselect("학습 데이터 파일",options,default=options,key=f"train_rows_{st.session_state.cycle}_{st.session_state.day}")
        ids={lookup[name] for name in selected}
        features=st.multiselect("사용 센서",FEATURES,default=FEATURES,key=f"features_{st.session_state.cycle}_{st.session_state.day}")
        epochs=st.slider("학습 반복 횟수",10,200,80,10,key=f"epochs_{st.session_state.cycle}_{st.session_state.day}")
        if st.session_state.last_result:
            st.info("오늘의 판정은 완료됐습니다. 다음 날 다시 학습할 수 있어요.")
        elif st.button("학습 후 오늘 진단",key=f"run_{st.session_state.day}",use_container_width=True):
            ok,message=train(ids,features,epochs)
            if ok:
                st.session_state.screen="summary" if st.session_state.day==7 else "game"
                st.rerun()
            else:
                st.error(message)
        if st.session_state.loss is not None:
            st.metric("Loss · BCE",f'{st.session_state.loss:.4f}')


init_state()
route_from_query()

if st.session_state.screen=="start":
    render_start_screen()

elif st.session_state.screen=="game":
    st.markdown(f'<div class="hero"><span>근무 {st.session_state.cycle}회차　·　DAY {st.session_state.day}/7</span></div>',unsafe_allow_html=True)
    render_room()
    if st.session_state.last_result:
        result=st.session_state.last_result
        if result["success"]:
            st.success(f'AI가 CAM 0{result["chosen"]+1}의 이상을 찾았습니다.')
        else:
            st.error(f'AI는 CAM 0{result["chosen"]+1}을 골랐지만 실제 이상은 CAM 0{result["target"]+1}이었습니다.')
        if st.session_state.day<7 and st.button("다음 날 →",key=f"next_{st.session_state.day}"):
            st.session_state.day+=1
            st.session_state.routes,st.session_state.target=make_routes()
            st.session_state.last_result=None
            st.rerun()
        st.caption(f'주간 성공 {st.session_state.wins}/7　·　Loss {st.session_state.loss:.3f}　·　Gradient {st.session_state.gradient:.3f}')

elif st.session_state.screen=="pc":
    back_link()
    render_pc_desktop()
    show_page_details(st.session_state.pc_page)

elif st.session_state.screen=="calendar":
    back_link()
    st.markdown(f'<div class="hero">WEEK {st.session_state.cycle}　·　달력</div>',unsafe_allow_html=True)
    st.markdown(calendar_html(),unsafe_allow_html=True)
    st.caption("AI 진단 성공은 O, 실패는 X로 기록됩니다.")

elif st.session_state.screen=="note":
    back_link()
    render_note()

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
