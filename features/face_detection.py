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
                self.model.prepare(ctx_id=self.gpu_id, det_size=(640, 640))
                if self.gpu_id >= 0:
                    logger.info(f"GPU {self.gpu_id} 모드로 모델 로드 완료")
                else:
                    logger.info("CPU 모드로 모델 로드 완료")

            except Exception as gpu_error:
                # GPU 실패 시 CPU로 전환
                logger.warning(f"GPU 사용 실패: {gpu_error}")
                logger.info("CPU 모드로 전환 중...")

                self.gpu_id = -1
                self.model.prepare(ctx_id=-1, det_size=(640, 640))
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

    def detect(self, image: np.ndarray, min_det_score: float = 0.6) -> int:
        """
        이미지에서 얼굴을 감지하고 개수를 반환합니다.

        InsightFace 모델을 사용하여 이미지에서 얼굴을 감지합니다.
        GPU 또는 CPU 모드에서 동작하며, 감지된 얼굴의 개수를 반환합니다.

        Args:
            image: 얼굴을 감지할 이미지 (numpy array, RGB 형식)
                  shape: (height, width, 3)
                  dtype: uint8
            min_det_score: 최소 감지 신뢰도 점수 (0.0~1.0)
                          가려진 얼굴 필터링 (손/컵 가림)
                          기본값: 0.6

        Returns:
            감지된 얼굴의 개수 (0 이상의 정수)

        Raises:
            ValueError: 모델이 초기화되지 않았거나 이미지 형식이 잘못된 경우
            RuntimeError: 얼굴 감지 실패 시

        Example:
            >>> detector = FaceDetector(gpu_id=0)
            >>> detector.initialize()
            >>> image = capturer.capture()  # numpy array
            >>> face_count = detector.detect(image)
            >>> print(face_count)
            22
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
            face_count = len(faces)

            logger.info(f"얼굴 감지 완료: {face_count}명")
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
