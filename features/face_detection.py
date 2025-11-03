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
