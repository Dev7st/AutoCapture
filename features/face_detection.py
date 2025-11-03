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
