
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

## 🏗️ 시스템 아키텍처 (System Architecture)

이 프로젝트는 실시간 데이터 처리를 위한 확장 가능한 마이크로서비스 아키텍처(MSA)를 기반으로 설계되었습니다.

- **실시간 예측**: FastAPI 서버가 Docker 컨테이너로 실행되며, 사용자 요청에 따라 실시간으로 결함을 예측합니다.
- **이벤트 스트리밍**: 예측 결과는 즉시 Apache Kafka 토픽으로 전송되어, 시스템의 다른 부분과 비동기적으로 통신합니다.
- **데이터 처리 및 저장**: 별도의 Kafka Consumer가 이벤트를 수신하여, 향후 분석을 위해 Hadoop HDFS와 같은 대용량 스토리지에 데이터를 저장합니다.
- **배치 분석**: Apache Spark를 사용하여 HDFS에 저장된 데이터를 주기적으로 분석하고 비즈니스 인사이트를 도출합니다.
- **컨테이너 오케스트레이션**: 모든 서비스는 Kubernetes 환경에서 관리되어 자동 스케일링, 배포, 및 복구를 통해 높은 안정성과 확장성을 보장합니다.

더 상세한 아키텍처는 `report/서비스아키텍쳐.md` 파일에서 확인할 수 있습니다.

## ▶️ 실행 방법 (Local Development)

### 1. Docker Compose 사용 (권장)

로컬 환경에서 전체 파이프라인(API, Kafka, Consumer)을 가장 쉽게 실행하는 방법입니다.

**사전 준비물:**
- [Docker](https://www.docker.com/get-started/)
- [Docker Compose](https://docs.docker.com/compose/install/) (Docker Desktop에 포함)

**실행 명령어:**

프로젝트 루트 디렉터리에서 다음 명령어를 실행합니다.

```bash
docker-compose up --build
```

이 명령어는 `docker-compose.yml`에 정의된 모든 서비스(Zookeeper, Kafka, API, Consumer)를 빌드하고 실행합니다.

**사용 방법:**

1.  서비스가 모두 실행되면, 웹 브라우저에서 `http://127.0.0.1:8000` 주소로 접속합니다.
2.  이미지를 업로드하고 예측을 수행합니다.
3.  API 서버의 로그와 별개로, `hdfs_consumer` 서비스의 터미널 로그에서 Kafka로 주고받은 예측 결과 메시지를 실시간으로 확인할 수 있습니다.

### 2. 수동 실행

Docker를 사용하지 않고 직접 파이썬 환경에서 실행하는 방법입니다.

**사전 준비물:**
- Python 3.9+
- `requirements.txt`에 명시된 라이브러리

**설치:**
```bash
pip install -r requirements.txt
```

**실행:**
```bash
python -m uvicorn api.main:app --reload
```
*참고: 이 방법으로는 Kafka 연동 기능을 테스트할 수 없습니다.*

## 🚀 Kubernetes 배포

Kubernetes 클러스터가 준비된 환경에 배포하는 방법입니다.

**사전 준비물:**
- 동작 중인 Kubernetes 클러스터 (예: Minikube, Docker Desktop Kubernetes)
- `kubectl` CLI

**배포 절차:**

1.  **Docker 이미지 빌드:**
    아직 이미지를 빌드하지 않았다면, 다음 명령어로 Docker 이미지를 생성합니다.
    ```bash
    docker build -t casting-product-api:latest .
    ```
    *Minikube 사용 시: `minikube image load casting-product-api:latest` 명령어로 이미지를 클러스터에 로드해야 할 수 있습니다.*

2.  **Kubernetes Manifest 적용:**
    `k8s` 디렉터리에 있는 설정 파일들을 클러스터에 적용합니다.
    ```bash
    kubectl apply -f k8s/
    ```

3.  **서비스 확인 및 접속:**
    - 배포 상태 확인: `kubectl get all`
    - 서비스 접속: `service.yaml`에서 `type: NodePort`로 설정했으므로, Minikube 환경에서는 `minikube service casting-api-service` 명령어로 브라우저에서 바로 서비스를 열 수 있습니다. 또는 `(클러스터 IP):30007` 주소로 직접 접속할 수 있습니다.

