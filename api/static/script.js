
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const predictionDiv = document.getElementById('prediction');
    const confidenceDiv = document.getElementById('confidence');
    const imagePreview = document.getElementById('imagePreview');

    // --- WebSocket 연결 설정 ---
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws`);

    ws.onopen = () => {
        console.log('WebSocket connection established');
    };

    ws.onmessage = (event) => {
        console.log('Message from server: ', event.data);
        const message = JSON.parse(event.data);
        if (message.type === 'defect_detected') {
            // 브라우저 알림 요청
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification('결함 감지 알림', {
                        body: `파일 '${message.filename}'에서 결함이 감지되었습니다.`,
                        icon: '/static/warning.png' // (옵션) 알림 아이콘
                    });
                }
            });
            alert(`결함 감지: ${message.filename}`);
        }
    };

    ws.onclose = () => {
        console.log('WebSocket connection closed');
    };

    // --- API 호출 및 결과 표시 ---
    uploadButton.addEventListener('click', async () => {
        if (!fileInput.files.length) {
            alert('이미지 파일을 선택해주세요.');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        // 로딩 표시
        predictionDiv.textContent = '분석 중...';
        confidenceDiv.textContent = '-';
        predictionDiv.className = '';
        imagePreview.innerHTML = '';

        try {
            const response = await fetch('/predict/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();

            // 결과 표시
            predictionDiv.textContent = result.prediction;
            predictionDiv.className = result.prediction; // CSS 클래스 적용
            confidenceDiv.textContent = `신뢰도: ${result.confidence}`;

            // 이미지 미리보기
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                imagePreview.appendChild(img);
            }
            reader.readAsDataURL(file);

        } catch (error) {
            console.error('Error during fetch:', error);
            predictionDiv.textContent = '오류 발생';
        }
    });
});
