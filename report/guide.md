About Dataset
Context
This dataset is of casting manufacturing product.
Casting is a manufacturing process in which a liquid material is usually poured into a mould, which contains a hollow cavity of the desired shape, and then allowed to solidify.
Reason for collect this data is casting defects!!
Casting defect is an undesired irregularity in a metal casting process.
There are many types of defect in casting like blow holes, pinholes, burr, shrinkage defects, mould material defects, pouring metal defects, metallurgical defects, etc.
Defects are an unwanted thing in casting industry. For removing this defective product all industry have their quality inspection department. But the main problem is this inspection process is carried out manually. It is a very time-consuming process and due to human accuracy, this is not 100% accurate. This can because of the rejection of the whole order. So it creates a big loss in the company.

We decided to make the inspection process automatic and for this, we need to make deep learning classification model for this problem.

contain
These all photos are top view of submersible pump impeller(google search for better understanding).
The dataset contains total 7348 image data. These all are the size of (300*300) pixels grey-scaled images. In all images, augmentation already applied.

Also uploaded images size of 512x512 grayscale. This data set is without Augmentation. This contains 519 ok_front and 781 def_front impeller images.

For capturing these images requires stable lighting, for this we made a special arrangement.

there are mainly two categories:-
1) Defective
2)Ok

making classification model we already split data for training and testing into two folders.
Both train and test folder contains def_front and ok_front subfolders.

train:- def_front have 3758 and ok_front have 2875 images
test:- def_front have:- def_front have 453 and ok_front have 262 images

Acknowledgements
We wouldn't be here without the help of PILOT TECHNOCAST, Shapar, Rajkot. we have to thank them for constant support and allowing us to work for this problem.

Prototype
We also made Working prototype using this dataset. Click here

Contact detail
If you want to know more about project and dataset drop mail on ravirajsinhdabhi86@gmail.com or DM me on LinkedIn

---

## 프로젝트 진행 과정 (2025-10-14)

### 1. 목표
- 주조 제품 이미지 데이터를 사용하여 정상/불량 제품을 자동으로 분류하는 딥러닝 모델 개발.

### 2. 환경 설정
- Python 환경에서 다음 라이브러리를 설치:
  - `tensorflow`: 딥러닝 모델 구축 및 훈련
  - `pillow`: 이미지 데이터 처리
  - `matplotlib`: 훈련 결과 시각화

### 3. 모델 개발 및 훈련
- `detect_defects.py` 스크립트를 작성하여 전체 프로세스를 자동화.
- **모델:** CNN(합성곱 신경망) 기반의 이미지 분류 모델을 사용.
- **1차 훈련:** 
  - 1 에포크(epoch)만 훈련하여 기본적인 성능을 테스트.
  - 테스트 정확도: **63.36%**
- **2차 훈련:**
  - 정확도 향상을 위해 훈련 에포크를 15로 늘림.
  - 훈련 과정의 정확도와 손실을 `training_history.png` 그래프로 시각화하여 과적합 여부를 판단할 수 있도록 함.
  - 테스트 정확도: **93.85%** 로 크게 향상됨.
  - 훈련된 모델은 `casting_defect_detection_model.keras` 파일로 저장됨.

### 4. Git 저장소 관리
- **문제 발생:** `git push` 시 원격 저장소에서 오류가 발생하며 푸시가 거부됨.
- **원인 분석:** 훈련된 모델 파일(`casting_defect_detection_model.keras`)의 크기가 약 204MB로, GitHub의 단일 파일 업로드 용량 제한(100MB)을 초과함.
- **해결:**
  - `git rm --cached` 명령어로 Git 추적에서 대용량 모델 파일을 제거.
  - `.gitignore` 파일에 `*.keras` 및 `*.png` 패턴을 추가하여 향후 관련 파일들이 커밋되지 않도록 설정.
  - `git commit --amend` 명령어로 마지막 커밋을 수정하여 위의 변경사항을 적용.
  - 수정된 커밋을 원격 저장소에 성공적으로 푸시함.

---

## API 서비스 개발 (2025-10-14)

### 1. 목표
- 훈련된 딥러닝 모델을 사용하여 이미지 파일을 받아 예측 결과를 반환하는 웹 API를 구축.

### 2. 프로젝트 구조 변경
- 코드의 역할을 분리하기 위해 새로운 폴더를 생성:
  - `api/`: API 관련 소스 코드를 저장.
  - `models/`: 훈련된 모델 파일(`.keras`)을 저장.
- 기존의 `casting_defect_detection_model.keras` 파일을 `models/` 폴더로 이동.

### 3. API 서버 구축
- **기술 스택:** `FastAPI`와 `Uvicorn`을 사용하여 API 서버를 구축.
- **구현:** `api/main.py` 스크립트를 작성하여 다음 기능을 구현:
  - 서버 시작 시 `models/` 폴더의 Keras 모델을 자동으로 로드.
  - `/` 경로: API 동작을 확인하는 기본 메시지 반환.
  - `/predict/` 경로: 이미지 파일을 업로드받아, 모델을 통해 예측을 수행하고 결과를 JSON 형식(예측 클래스, 신뢰도)으로 반환.

### 4. 문제 해결
- **경로 문제:** 모델 로드 시 파일 경로가 잘못 지정된 문제를 `models/`로 수정하여 해결.
- **서버 응답 없음 문제:** `model.predict()`가 서버의 메인 프로세스를 차단하는 현상을 `run_in_threadpool`을 사용하여 별도 스레드에서 예측을 실행하도록 변경하여 해결.

### 5. 최종 테스트
- FastAPI의 자동 문서 페이지 (`/docs`)를 통해 이미지 업로드 및 예측 기능의 정상 동작을 확인함.

---

## 웹 UI 및 실시간 알림 기능 개발 (2025-10-14)

### 1. 목표
- 사용자가 쉽게 모델을 사용할 수 있는 웹 UI를 구축하고, 결함 감지 시 실시간으로 알림을 제공.

### 2. 프론트엔드 개발
- `api/static` 폴더를 생성하고 내부에 다음 파일들을 작성:
  - `index.html`: 파일 업로드, 결과 표시 등 기본 UI 구조.
  - `style.css`: 사용자 경험을 위한 스타일 시트.
  - `script.js`: API 호출, WebSocket 통신, 동적 결과 표시 등 클라이언트 측 로직 처리.

### 3. 백엔드 개발
- `api/main.py`를 수정하여 다음 기능을 추가:
  - **정적 파일 제공:** `index.html`을 포함한 `static` 폴더의 파일들을 웹 페이지로 제공.
  - **WebSocket 지원:** `/ws` 경로를 통해 클라이언트와 실시간 양방향 통신 채널을 구축.
  - **알림 기능:** `/predict` 경로에서 결함(`def_front`)이 감지되면, 연결된 모든 클라이언트에게 WebSocket을 통해 알림 메시지를 전송.

### 4. 문제 해결
- **WebSocket URL 오류:** `script.js`에서 잘못된 WebSocket 접속 주소(`ws:://`)를 생성하는 버그를 올바른 주소(`ws://`)로 수정하여 해결.

### 5. 최종 결과
- 사용자는 이제 `http://127.0.0.1:8000` 주소로 접속하여 웹페이지에서 직접 이미지를 업로드하고 예측 결과를 확인할 수 있음.
- 결함 이미지 예측 시 브라우저를 통해 데스크톱 알림을 받게 됨.

---

## 현재 프로젝트 파일 구조

```
C:/Users/user/Documents/GitHub/casting_product/
├── api/
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   └── main.py
├── data/
│   └── ... (생략)
├── models/
│   └── casting_defect_detection_model.keras
├── report/
│   └── guide.md
├── .gitignore
├── detect_defects.py
└── training_history.png
```

---

## 데이터 파이프라인 아키텍처 설계 및 구축 (2025-10-14)

### 1. 목표
- 기존의 단일 서비스 구조를 MSA(마이크로서비스 아키텍처) 기반의 확장 가능한 데이터 파이프라인으로 전환.
- Docker, Kubernetes, Kafka 등의 클라우드 네이티브 기술을 도입하여 시스템의 안정성과 확장성을 확보.

### 2. 아키텍처 설계
- 사용자 요청부터 데이터 분석, 시각화까지 이어지는 전체 과정을 여러 단계로 분리.
- **구성 요소**: FastAPI, Docker, Kubernetes, Kafka, Hadoop HDFS, Spark, BI Tool.
- 상세 설계 내용을 `report/서비스아키텍쳐.md` 파일로 작성하여 포트폴리오에 활용할 수 있도록 함.

### 3. 실시간 데이터 파이프라인 구축
- **Dockerize**: FastAPI 애플리케이션을 컨테이너화하기 위한 `Dockerfile` 작성.
- **Kubernetes Manifests**: Kubernetes 환경에 서비스를 배포하기 위한 `k8s/deployment.yaml` 및 `k8s/service.yaml` 작성.
- **Kafka 연동 환경 구축**:
    - 로컬에서 Kafka를 포함한 전체 개발 환경을 쉽게 구축할 수 있도록 `docker-compose.yml` 파일 작성.
    - Zookeeper, Kafka, API, Consumer 서비스를 정의.
- **Producer 개발**: `api/main.py`를 수정하여 예측 결과를 Kafka 토픽(`prediction_results`)으로 전송하도록 기능 추가 (`kafka-python` 라이브러리 사용).
- **Consumer 개발**:
    - Kafka로부터 데이터를 수신하여 처리하는 `consumers/hdfs_consumer.py` 스크립트 작성.
    - `docker-compose.yml`에 컨슈머를 별도의 서비스로 추가하여 API와 독립적으로 실행되도록 구성.

### 4. 현재 상태
- API 서버, Kafka, 컨슈머로 이어지는 실시간 데이터 파이프라인의 모든 코드와 실행 환경(Docker Compose) 정의가 완료됨.
- 로컬에 Docker 환경이 갖춰지면 `docker-compose up` 명령으로 전체 파이프라인을 실행하고 테스트할 수 있는 상태.

---

## 내일 진행할 내용 (2025-10-15)

### 1. 목표
- 실시간으로 수집된 데이터를 저장하고 분석하는 **배치(Batch) 처리 시스템** 구축.

### 2. 세부 계획
- **Hadoop (HDFS) 연동**:
    - `docker-compose.yml`에 HDFS(Namenode, Datanode) 서비스를 추가.
    - `consumers/hdfs_consumer.py` 스크립트를 수정하여, Kafka에서 받은 데이터를 HDFS에 파일 형태로 저장하도록 로직 변경 (`hdfs` 라이브러리 사용).
- **Spark 연동**:
    - `docker-compose.yml`에 Spark(Master, Worker) 서비스를 추가.
    - HDFS에 저장된 데이터를 주기적으로 분석하여 통계를 내는 Spark 애플리케이션(`spark_job.py`) 작성.
- **데이터베이스 연동 (선택 사항)**:
    - Spark 분석 결과를 BI 툴에서 쉽게 사용하도록 PostgreSQL 같은 RDBMS에 저장하는 기능 추가.
