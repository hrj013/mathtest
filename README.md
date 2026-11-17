# 하수관 야간정비대

작은 마을의 야간 정비사가 CCTV와 관로 점검 데이터를 살펴보며 경사하강법을 체험하는 Streamlit 게임입니다.

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit Community Cloud에서는 저장소 `hrj013/mathtest`, 브랜치 `main`, 메인 파일 `app.py`를 지정합니다.

## 화면 구성

- 시작 화면은 정면에서 본 둥근 하수관 입구와 강물로 흘러드는 물을 표현합니다.
- 관제실 장면은 640×360의 세밀한 픽셀 캔버스로 그립니다. 중앙 벽에는 영화관처럼 큰 하나의 2×2 CCTV 스크린, 왼쪽 벽 쪽에는 책상과 그 위 PC, 오른쪽 벽에는 달력이 있습니다.
- PC 화면의 파일 아이콘에서 점검 기록, 경사하강법 안내, AI 모델, 오늘의 학습 화면으로 들어갑니다.
- 학습 데이터/센서/epochs 선택 후 학습한 모델이 그날 CCTV 화면을 판별합니다.
- 달력은 확대 화면에서 7일 성공(O)/실패(X) 기록을 보여줍니다.
- 7일 후 5회 이상 성공은 승진, 3~4회는 다음 주 계속 근무, 3회 미만은 퇴사 결말입니다.

`pixel_art.py` contains hand-authored scenes on a finer 640×360 pixel canvas. The office composition uses a perspective shell, central giant quad monitor, a desk-mounted PC on the left, and a wall calendar on the right.
