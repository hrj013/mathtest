# 하수관 AI 정비대

파스텔 픽셀풍의 하수관 유지보수 체험 게임입니다. 플레이어는 4개의 CCTV 관로를 점검하고, AI는 매일 공개되는 관로 센서 라벨을 이용해 경사하강법으로 이상 징후 모델을 업데이트합니다.

## Streamlit으로 실행하기

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 표시된 로컬 주소(보통 `http://localhost:8501`)를 엽니다.

## Streamlit Community Cloud 배포

1. GitHub 저장소를 연결합니다.
2. 앱 설정에서 브랜치 `main`, 메인 파일 경로 `app.py`를 선택합니다.
3. 배포합니다. 의존성은 `requirements.txt`에서 설치됩니다.

## 게임 방법

- 매일 CCTV 모니터 4개와 압력·소음·침전물·부식 데이터를 살펴봅니다.
- 이상하다고 생각하는 관로의 점검 버튼을 누릅니다.
- 정답 공개 후 AI가 로지스틱 회귀의 Binary Cross-Entropy 손실에 대한 기울기를 계산하고 가중치와 편향을 갱신합니다.
- 달력에는 성공 `O`, 실패 `X`가 기록되며 7일 후 5회 이상 성공하면 승진, 3~4회면 다음 주 재도전, 3회 미만이면 해고 결말입니다.

## 파일

- `app.py` — Streamlit 인터페이스, 픽셀풍 SVG 장면, 게임 및 경사하강법 로직
- `requirements.txt` — Python 의존성
