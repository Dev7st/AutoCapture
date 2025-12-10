"""
얼굴 감지 결과 시각화 스크립트

각 얼굴에 번호와 det_score를 표시한 이미지를 생성합니다.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from features.face_detection import FaceDetector


def visualize_faces(image_path: str, output_path: str = None):
    """
    이미지에서 얼굴을 감지하고 번호/점수를 표시한 이미지 저장

    Args:
        image_path: 입력 이미지 경로
        output_path: 출력 이미지 경로 (None이면 자동 생성)
    """
    print(f"이미지 로드 중: {image_path}")

    # 이미지 로드
    img = Image.open(image_path)
    img_array = np.array(img)

    # 시각화용 이미지 복사
    img_vis = img.copy()
    draw = ImageDraw.Draw(img_vis)

    print(f"이미지 크기: {img_array.shape}")

    # FaceDetector 초기화
    print("\nFaceDetector 초기화 중...")
    detector = FaceDetector(gpu_id=0)
    detector.initialize()

    print("\n얼굴 감지 시작...")

    # 얼굴 감지
    faces = detector.model.get(img_array)

    print(f"\n감지된 전체 얼굴: {len(faces)}명\n")
    print("=" * 80)

    # 폰트 설정 (없으면 기본 폰트 사용)
    try:
        # Windows 기본 한글 폰트
        font_large = ImageFont.truetype("malgun.ttf", 40)
        font_small = ImageFont.truetype("malgun.ttf", 30)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 얼굴별 정보 출력 및 시각화
    for idx, face in enumerate(faces, 1):
        bbox = face.bbox
        x1, y1, x2, y2 = bbox

        print(f"얼굴 #{idx}:")
        print(f"  - det_score: {face.det_score:.4f}")
        print(f"  - 위치: x={x1:.0f}~{x2:.0f}, y={y1:.0f}~{y2:.0f}")

        # bbox가 화면 중심 기준 어디인지 표시
        img_h, img_w = img_array.shape[:2]
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        pos_x = "왼쪽" if center_x < img_w / 2 else "오른쪽"
        pos_y = "위" if center_y < img_h / 2 else "아래"
        print(f"  - 화면상 위치: {pos_x} {pos_y}")

        # 특징점 정보
        if hasattr(face, 'kps') and face.kps is not None:
            print(f"  - 특징점 개수: {len(face.kps)}")
        else:
            print(f"  - 특징점: 없음")

        print("-" * 80)

        # bbox 그리기
        # 색상: det_score에 따라 변경 (낮으면 빨강, 높으면 초록)
        if face.det_score >= 0.8:
            color = (0, 255, 0)  # 녹색 (높음)
        elif face.det_score >= 0.65:
            color = (255, 165, 0)  # 주황색 (중간)
        else:
            color = (255, 0, 0)  # 빨강 (낮음)

        # 박스 그리기 (두께 5)
        draw.rectangle([x1, y1, x2, y2], outline=color, width=5)

        # 번호와 점수 표시
        text = f"#{idx}\n{face.det_score:.3f}"

        # 텍스트 배경 (가독성 향상)
        text_bbox = draw.textbbox((x1, y1 - 80), text, font=font_small)
        draw.rectangle(text_bbox, fill=(0, 0, 0, 200))

        # 텍스트 그리기
        draw.text((x1, y1 - 80), text, fill=color, font=font_small)

    # 출력 경로 결정
    if output_path is None:
        input_path = Path(image_path)
        output_path = input_path.parent / f"{input_path.stem}_faces{input_path.suffix}"

    # 이미지 저장
    img_vis.save(output_path)
    print(f"\n시각화 이미지 저장: {output_path}")

    # 필터링 테스트
    print("\n필터링 테스트:")
    for threshold in [0.5, 0.6, 0.65, 0.7, 0.75, 0.8]:
        count = detector.detect(img_array, min_det_score=threshold)
        filtered = len(faces) - count
        print(f"  min_det_score={threshold:.2f} → {count}명 통과 ({filtered}명 필터링)")

    # Cleanup
    detector.cleanup()
    print("\n완료!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python visualize_faces.py <이미지_파일_경로> [출력_파일_경로]")
        print("예: python visualize_faces.py C:/Users/imgan/Desktop/123.png")
        sys.exit(1)

    image_path = sys.argv[1]

    if not Path(image_path).exists():
        print(f"오류: 파일을 찾을 수 없습니다 - {image_path}")
        sys.exit(1)

    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    visualize_faces(image_path, output_path)
