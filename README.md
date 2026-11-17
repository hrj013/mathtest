# 하수관 야간정비대

Streamlit으로 만든 하수관 유지보수 AI 체험 게임입니다. 배경 장면은 320×180 저해상도 픽셀 캔버스로 직접 그려 확대해도 각진 도트 느낌을 유지합니다.

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit Community Cloud 설정: 저장소 `hrj013/mathtest`, 브랜치 `main`, 메인 파일 `app.py`.

## 화면 구성

- 시작: 둥근 하수관 입구 정면에서 수로로 물이 흘러나오는 장면, 큰 로고와 시작 버튼.
- 관제실: 원근감 있는 사무실. 가운데 벽의 대형 단일 스크린 안에 CCTV 4개가 2×2로 표시됩니다. 책상 위 PC는 왼쪽, 벽 달력은 오른쪽에 놓입니다.
- PC 확대: 바탕화면의 데이터, 경사하강법 설명, AI 모델, 오늘의 학습 파일을 엽니다. 학습 데이터/센서/epochs 선택 후 학습시켜 AI가 오늘의 CCTV 이상 관로를 예측합니다.
- 달력 확대: 7일간 성공(O) / 실패(X) 기록을 봅니다.
- 결산: 5회 이상 승진, 3~4회 다음 주 계속 근무, 3회 미만 퇴사 결말.

`pixel_art.py` contains the low-resolution scenes; the office is composed as one coherent perspective room with a large central monitor, left desk PC, and right wall calendar.
