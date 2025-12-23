"""
얼굴 감지 모듈.

InsightFace 라이브러리를 사용하여 GPU 가속 얼굴 감지 기능을 제공합니다.
"""

# 표준 라이브러리
import logging
import os
import sys
from typing import Optional

# 외부 라이브러리
import numpy as np

# 내부 모듈
from features.exceptions import FaceDetectionError, ModelLoadError, InvalidImageError

# 로거 설정
logger = logging.getLogger(__name__)


class FaceDetector:
    """
    InsightFace 기반 얼굴 감지 클래스.

    GPU를 활용하여 이미지에서 얼굴을 감지하고 개수를 반환합니다.
    GTX 960 환경에서 최적화되어 있으며, GPU 사용 불가 시 CPU로 자동 전환합니다.

    Attributes:
        gpu_id: 사용할 GPU ID (0=GPU, -1=CPU)
        model: InsightFace 모델 인스턴스
        is_initialized: 모델 초기화 여부

    Example:
        >>> detector = FaceDetector(gpu_id=0)
        >>> detector.initialize()
        >>> face_count = detector.detect(image)
        >>> print(face_count)
        22
        >>> detector.cleanup()
    """

    def __init__(self, gpu_id: int = 0) -> None:
        """
        FaceDetector 인스턴스를 초기화합니다.

        생성자에서는 GPU ID만 설정하고, 실제 모델 로드는
        initialize() 메서드에서 수행합니다.

        Args:
            gpu_id: 사용할 GPU ID
                   0 = GPU 사용 (기본값, GTX 960)
                   -1 = CPU 사용

        Example:
            >>> detector = FaceDetector(gpu_id=0)  # GPU 사용
            >>> detector_cpu = FaceDetector(gpu_id=-1)  # CPU 사용
        """
        self.gpu_id: int = gpu_id
        self.model: Optional[any] = None
        self.is_initialized: bool = False

        logger.info(f"FaceDetector 초기화: gpu_id={gpu_id}")

    def initialize(self) -> None:
        """
        InsightFace 모델을 로드합니다.

        buffalo_l 모델을 로드하고 GPU 또는 CPU로 준비합니다.
        GPU 사용 실패 시 자동으로 CPU 모드로 전환합니다.

        첫 실행 시 ~100MB 모델을 자동 다운로드합니다.
        다운로드 위치: ~/.insightface/models/buffalo_l/

        Raises:
            RuntimeError: 모델 로드 실패 시

        Example:
            >>> detector = FaceDetector(gpu_id=0)
            >>> detector.initialize()  # GPU로 모델 로드
            >>> print(detector.is_initialized)
            True
        """
        if self.is_initialized:
            logger.warning("모델이 이미 초기화되어 있습니다.")
            return

        try:
            # InsightFace 라이브러리 import
            from insightface.app import FaceAnalysis

            logger.info("InsightFace 모델 로드 중...")

            # PyInstaller 실행 환경 확인 및 모델 경로 설정
            if getattr(sys, 'frozen', False):
                # PyInstaller로 패키징된 경우
                base_path = sys._MEIPASS
                model_root = os.path.join(base_path, '.insightface')
                logger.info(f"PyInstaller 환경 감지: 모델 루트={model_root}")
            else:
                # 일반 Python 실행 환경
                model_root = None
                logger.info("일반 Python 환경: 기본 모델 경로 사용")

            # FaceAnalysis 인스턴스 생성 (buffalo_l 모델)
            if model_root:
                self.model = FaceAnalysis(name='buffalo_l', root=model_root)
            else:
                self.model = FaceAnalysis(name='buffalo_l')

            # GPU 사용 시도
            try:
                self.model.prepare(ctx_id=self.gpu_id, det_size=(1024, 1024))
                if self.gpu_id >= 0:
                    logger.info(f"GPU {self.gpu_id} 모드로 모델 로드 완료")
                else:
                    logger.info("CPU 모드로 모델 로드 완료")

            except Exception as gpu_error:
                # GPU 실패 시 CPU로 전환
                logger.warning(f"GPU 사용 실패: {gpu_error}")
                logger.info("CPU 모드로 전환 중...")

                self.gpu_id = -1
                self.model.prepare(ctx_id=-1, det_size=(1024, 1024))
                logger.info("CPU 모드로 모델 로드 완료")

            self.is_initialized = True
            logger.info("FaceDetector 초기화 완료")

        except ImportError as e:
            logger.error(f"InsightFace 라이브러리를 찾을 수 없습니다: {e}", exc_info=True)
            raise ModelLoadError(
                "InsightFace가 설치되지 않았습니다. "
                "'pip install insightface' 명령으로 설치하세요."
            )
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}", exc_info=True)
            raise ModelLoadError(f"InsightFace 모델 로드 실패: {e}")

    def detect(self, image: np.ndarray, min_det_score: float = 0.75) -> int:
        """
        이미지에서 얼굴을 감지하고 유효한 얼굴 개수를 반환합니다.

        InsightFace 모델을 사용하여 이미지에서 얼굴을 감지합니다.
        감지된 얼굴에 대해 신뢰도 점수와 특징점 가시성을 기반으로 필터링하여
        유효한 얼굴만 카운트합니다.

        필터링 기준:
        1. 감지 신뢰도 점수 (가림 감지)
        2. 특징점 가시성 (눈, 코, 입)

        Args:
            image: 얼굴을 감지할 이미지 (numpy array, RGB 형식)
                  shape: (height, width, 3)
                  dtype: uint8
            min_det_score: 최소 감지 신뢰도 점수 (0.0~1.0)
                          가려진 얼굴 필터링 (손/컵 가림)
                          기본값: 0.75

        Returns:
            유효한 얼굴의 개수 (0 이상의 정수)

        Raises:
            FaceDetectionError: 모델이 초기화되지 않았거나 얼굴 감지 실패 시
            InvalidImageError: 이미지 형식이 잘못된 경우

        Filtering Criteria:
            - Detection score >= min_det_score
            - 최소 한쪽 눈 보임 (옆모습 지원)
            - 코 보임
            - 최소 한쪽 입꼬리 보임

        Example:
            >>> detector = FaceDetector(gpu_id=0)
            >>> detector.initialize()
            >>> image = capturer.capture()  # numpy array
            >>> face_count = detector.detect(image, min_det_score=0.6)
            >>> print(face_count)  # 유효하고 가려지지 않은 얼굴만
            20
        """
        # 초기화 확인
        if not self.is_initialized:
            logger.error("모델이 초기화되지 않았습니다")
            raise FaceDetectionError(
                "모델이 초기화되지 않았습니다. "
                "initialize() 메서드를 먼저 호출하세요."
            )

        # 이미지 유효성 검사
        if not isinstance(image, np.ndarray):
            logger.error(f"이미지 타입이 잘못되었습니다: {type(image)}")
            raise InvalidImageError(f"이미지는 numpy array여야 합니다. 현재: {type(image)}")

        if len(image.shape) != 3 or image.shape[2] != 3:
            logger.error(f"이미지 shape이 잘못되었습니다: {image.shape}")
            raise InvalidImageError(
                f"이미지는 (height, width, 3) 형식이어야 합니다. "
                f"현재: {image.shape}"
            )

        try:
            logger.info(f"얼굴 감지 시작: 이미지 크기 {image.shape}")

            # 얼굴 감지 수행
            faces = self.model.get(image)

            # 필터링된 유효 얼굴 리스트
            valid_faces = []

            for face in faces:
                try:
                    # Filter 1: Detection score (가림 감지)
                    if face.det_score < min_det_score:
                        logger.debug(f"얼굴 제외: 낮은 신뢰도 {face.det_score:.2f}")
                        continue

                    # 특징점 존재 여부 검증
                    if not hasattr(face, 'kps') or face.kps is None:
                        logger.warning("얼굴 특징점 누락, 건너뜀")
                        continue

                    if len(face.kps) < 5:
                        logger.warning(f"얼굴 특징점 불완전 ({len(face.kps)}/5), 건너뜀")
                        continue

                    # bbox 추출
                    bbox = face.bbox

                    # 특징점 추출
                    left_eye = face.kps[0]
                    right_eye = face.kps[1]
                    nose = face.kps[2]
                    mouth_left = face.kps[3]
                    mouth_right = face.kps[4]

                    # Filter 2: 눈 (최소 한쪽) + 코 (필수) - bbox 범위만 체크 (margin 없음)
                    eyes_visible = (
                        self._is_in_bbox(left_eye, bbox) or
                        self._is_in_bbox(right_eye, bbox)
                    )
                    nose_visible = self._is_in_bbox(nose, bbox)

                    if not (eyes_visible and nose_visible):
                        logger.debug("얼굴 제외: 눈(최소 한쪽) 또는 코 bbox 밖")
                        continue

                    # Filter 3: 입 (최소 한쪽) - bbox + margin 체크
                    mouth_visible = (
                        self._is_landmark_visible(mouth_left, bbox) or
                        self._is_landmark_visible(mouth_right, bbox)
                    )

                    if not mouth_visible:
                        logger.debug("얼굴 제외: 입 bbox 경계 근처")
                        continue

                    # 모든 필터 통과
                    valid_faces.append(face)
                    logger.debug(f"유효 얼굴: score={face.det_score:.2f}, 모든 특징점 확인")

                except Exception as e:
                    logger.warning(f"얼굴 처리 오류: {e}, 건너뜀")
                    continue

            face_count = len(valid_faces)
            logger.info(
                f"얼굴 감지 완료: {face_count}명 유효 "
                f"(필터링 {len(faces) - face_count}명)"
            )
            return face_count

        except Exception as e:
            logger.error(f"얼굴 감지 실패: {e}", exc_info=True)
            raise FaceDetectionError(f"얼굴 감지 중 오류 발생: {e}")

    def cleanup(self) -> None:
        """
        모델을 정리하고 GPU 메모리를 해제합니다.

        InsightFace 모델 인스턴스를 삭제하고 GPU 메모리를 명시적으로 해제합니다.
        애플리케이션 종료 시 또는 모델을 더 이상 사용하지 않을 때 호출하세요.

        Example:
            >>> detector = FaceDetector(gpu_id=0)
            >>> detector.initialize()
            >>> # ... 얼굴 감지 작업 ...
            >>> detector.cleanup()  # 메모리 해제
        """
        if self.model is not None:
            logger.info("FaceDetector 정리 시작")

            try:
                # 모델 인스턴스 삭제
                del self.model
                self.model = None
                self.is_initialized = False

                logger.info("FaceDetector 정리 완료")

            except Exception as e:
                logger.error(f"FaceDetector 정리 실패: {e}", exc_info=True)
        else:
            logger.info("정리할 모델이 없습니다")

    def _is_in_bbox(
        self,
        landmark: np.ndarray,
        bbox: np.ndarray
    ) -> bool:
        """
        특징점이 bbox 범위 내에 있는지 확인합니다 (margin 없음).

        얼굴 특징점(눈, 코)이 얼굴 bounding box 내부에 위치하는지 검사합니다.
        margin 없이 순수하게 bbox 범위만 체크합니다.

        Args:
            landmark: 특징점 좌표 (x, y)
            bbox: 얼굴 bounding box [x1, y1, x2, y2]

        Returns:
            특징점이 bbox 범위 내에 있으면 True, 아니면 False

        Example:
            >>> detector = FaceDetector(gpu_id=0)
            >>> landmark = np.array([100, 150])
            >>> bbox = np.array([80, 120, 200, 250])
            >>> is_in = detector._is_in_bbox(landmark, bbox)
            >>> print(is_in)
            True
        """
        x, y = landmark
        x1, y1, x2, y2 = bbox
        return x1 <= x <= x2 and y1 <= y <= y2

    def _is_landmark_visible(
        self,
        landmark: np.ndarray,
        bbox: np.ndarray
    ) -> bool:
        """
        특징점이 bbox 범위 내에 있는지 확인합니다 (margin 포함).

        얼굴 특징점(입)이 얼굴 bounding box 경계 내부에 위치하는지 검사합니다.
        Zoom 갤러리 뷰에서 개별 참여자 칸 하단에 입이 잘린 경우를 감지합니다.
        bbox 경계에서 5픽셀 여유를 두어 경계 근처 특징점을 필터링합니다.

        Args:
            landmark: 특징점 좌표 (x, y)
            bbox: 얼굴 bounding box [x1, y1, x2, y2]

        Returns:
            특징점이 bbox 범위 내에 있으면 True, 아니면 False

        Example:
            >>> detector = FaceDetector(gpu_id=0)
            >>> landmark = np.array([100, 150])
            >>> bbox = np.array([80, 120, 200, 250])
            >>> is_visible = detector._is_landmark_visible(landmark, bbox)
            >>> print(is_visible)
            True
        """
        x, y = landmark
        x1, y1, x2, y2 = bbox
        margin = 5  # bbox 경계 여유 (픽셀)
        return (x1 + margin <= x <= x2 - margin and
                y1 + margin <= y <= y2 - margin)
