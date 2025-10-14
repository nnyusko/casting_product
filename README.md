
# 주조 제품 결함 감지 시스템 (Casting Product Defect Detection System)

이 프로젝트는 주조 공정에서 생산된 제품의 이미지를 분석하여 결함 여부를 자동으로 판별하는 딥러닝 모델과 이를 서비스하는 웹 애플리케이션입니다.

## ✨ 주요 기능

- **AI 기반 결함 감지:** CNN 딥러닝 모델을 사용하여 제품 이미지의 결함 여부를 '정상(ok_front)' 또는 '결함(def_front)'으로 분류합니다.
- **웹 인터페이스:** 사용자가 쉽게 이미지를 업로드하고 예측 결과를 확인할 수 있는 웹 UI를 제공합니다.
- **실시간 알림:** 결함이 감지되었을 경우, 사용자에게 즉시 브라우저 데스크톱 알림을 보냅니다.
- **API 제공:** `/predict` 엔드포인트를 통해 다른 서비스와 연동할 수 있는 API를 제공합니다.

## 📂 프로젝트 구조

```
/
├── api/                  # API 서버 및 웹 프론트엔드 관련 파일
│   ├── static/           # HTML, CSS, JS 파일
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   └── main.py           # FastAPI 애플리케이션
├── data/                 # 이미지 데이터셋 (외부 다운로드 필요)
├── models/               # 훈련된 모델이 저장되는 폴더
│   └── *.keras
├── report/               # 프로젝트 진행 보고서
│   └── guide.md
├── .gitignore            # Git 추적 제외 파일 목록
├── detect_defects.py     # 모델 훈련 스크립트
├── requirements.txt      # 프로젝트 필요 라이브러리 목록
└── README.md             # 프로젝트 안내 파일
```

## ⚙️ 설치 방법

1.  **Git 리포지토리 복제:**
    ```bash
    git clone <repository_url>
    cd casting_product
    ```

2.  **필요 라이브러리 설치:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **데이터셋 준비:**
    - `data` 폴더에 `casting_data` 폴더를 위치시켜야 합니다.
    - 데이터셋은 [Kaggle](https://www.kaggle.com/datasets/ravirajsinh45/real-life-industrial-dataset-of-casting-product) 등에서 다운로드할 수 있습니다.

## ▶️ 실행 방법

### 1. 모델 훈련 (선택 사항)

이미 훈련된 모델이 있지만, 모델을 다시 훈련하고 싶을 경우 다음 명령어를 실행합니다.

```bash
py detect_defects.py
```

### 2. API 및 웹 서버 실행

프로젝트의 핵심인 API 서버와 웹 UI를 실행합니다.

```bash
py -m uvicorn api.main:app --reload
```

## 🚀 사용 방법

1.  서버 실행 후, 웹 브라우저에서 `http://127.0.0.1:8000` 주소로 접속합니다.
2.  웹 페이지의 '파일 선택' 버튼을 눌러 검사하고 싶은 이미지를 선택합니다.
3.  '검사 시작' 버튼을 누르면 잠시 후 예측 결과와 신뢰도가 화면에 표시됩니다.
4.  만약 결함이 감지되면 브라우저에서 데스크톱 알림이 전송됩니다. (최초 1회 권한 허용 필요)

