"""
얼굴 감지 모듈.

InsightFace 라이브러리를 사용하여 GPU 가속 얼굴 감지 기능을 제공합니다.
"""

# 표준 라이브러리
import logging
from typing import Optional

# 외부 라이브러리
import numpy as np

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

            # FaceAnalysis 인스턴스 생성 (buffalo_l 모델)
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
            raise RuntimeError(
                "InsightFace가 설치되지 않았습니다. "
                "'pip install insightface' 명령으로 설치하세요."
            )
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}", exc_info=True)
            raise RuntimeError(f"InsightFace 모델 로드 실패: {e}")

    def detect(self, image: np.ndarray) -> int:
        """
        이미지에서 얼굴을 감지하고 개수를 반환합니다.

        InsightFace 모델을 사용하여 이미지에서 얼굴을 감지합니다.
        GPU 또는 CPU 모드에서 동작하며, 감지된 얼굴의 개수를 반환합니다.

        Args:
            image: 얼굴을 감지할 이미지 (numpy array, RGB 형식)
                  shape: (height, width, 3)
                  dtype: uint8

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
            raise ValueError(
                "모델이 초기화되지 않았습니다. "
                "initialize() 메서드를 먼저 호출하세요."
            )

        # 이미지 유효성 검사
        if not isinstance(image, np.ndarray):
            logger.error(f"이미지 타입이 잘못되었습니다: {type(image)}")
            raise ValueError(f"이미지는 numpy array여야 합니다. 현재: {type(image)}")

        if len(image.shape) != 3 or image.shape[2] != 3:
            logger.error(f"이미지 shape이 잘못되었습니다: {image.shape}")
            raise ValueError(
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
            raise RuntimeError(f"얼굴 감지 중 오류 발생: {e}")
