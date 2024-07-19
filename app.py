from flask import Flask, request, jsonify, render_template, Response
from GroundingDINO.groundingdino.util.inference import load_model, load_image, predict, annotate
import cv2
import numpy as np
import base64
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# GroundingDINO 모델 로드
try:
    logging.info("Loading GroundingDINO model...")
    model = load_model("GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py", "groundingdino_swint_ogc.pth")
    logging.info("Model loaded successfully")
except Exception as e:
    logging.error(f"Error loading model: {str(e)}")
    raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect_objects():
    logging.info("Received detection request")
    
    if 'image' not in request.files:
        logging.error("No image file uploaded")
        return jsonify({'error': 'No image file uploaded'}), 400

    image_file = request.files['image']
    text_prompt = request.form.get('prompt', '')

    if not text_prompt:
        logging.error("No text prompt provided")
        return jsonify({'error': 'No text prompt provided'}), 400

    try:
        # 이미지 저장
        image_path = 'temp_image.jpg'
        image_file.save(image_path)
        logging.info(f"Image saved to {image_path}")

        # GroundingDINO 추론
        logging.info("Loading image for inference")
        image_source, image = load_image(image_path)
        
        logging.info("Running prediction")
        boxes, logits, phrases = predict(
            model=model,
            image=image,
            caption=text_prompt,
            box_threshold=0.35,
            text_threshold=0.25,
            device='cpu'
        )
        logging.info(f"Prediction completed. Detected {len(phrases)} objects")

        # 결과 이미지 생성
        logging.info("Annotating result image")
        annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases)
        result_path = 'result_image.jpg'
        cv2.imwrite(result_path, annotated_frame)
        logging.info(f"Result image saved to {result_path}")

        # 결과 이미지를 base64로 인코딩
        with open(result_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
        logging.info("Image encoded to base64")

        # 임시 파일 삭제
        os.remove(image_path)
        os.remove(result_path)
        logging.info("Temporary files removed")

        # phrases가 이미 리스트인지 확인하고 적절히 처리
        detected_objects = phrases if isinstance(phrases, list) else phrases.tolist() if hasattr(phrases, 'tolist') else list(phrases)

        return jsonify({
            'image_url': f'data:image/jpeg;base64,{img_data}',
            'detected_objects': detected_objects
        })

    except Exception as e:
        logging.error(f"Error during object detection: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)