// 파일 입력 요소
const fileInput = document.getElementById('image-upload');
// 커스텀 업로드 버튼
const customUpload = document.querySelector('.custum-file-upload');

// 커스텀 업로드 버튼 클릭 이벤트
customUpload.addEventListener('click', () => {
    fileInput.click();
});

// 파일이 선택되었을 때의 이벤트
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        // 파일이 선택되면 커스텀 업로드 버튼의 텍스트를 변경
        const fileName = e.target.files[0].name;
        customUpload.querySelector('.text span').textContent = `Selected: ${fileName}`;
    }
});

// 폼 제출 이벤트
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    
    // 이미지 파일 추가
    const imageFile = fileInput.files[0];
    if (imageFile) {
        formData.append('image', imageFile);
    } else {
        alert('Please select an image file.');
        return;
    }
    
    // 텍스트 프롬프트 추가
    const textPrompt = document.getElementById('text-prompt').value;
    formData.append('prompt', textPrompt);
    
    try {
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `
                <h3>Detection Result:</h3>
                <img src="${result.image_url}" alt="Annotated Image">
                <p>Detected objects: ${result.detected_objects.join(', ')}</p>
            `;
        } else {
            alert('Error occurred during detection');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error occurred during detection');
    }
});