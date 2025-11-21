"""
파일 저장 관리 모듈.

캡처된 이미지를 날짜별 폴더에 저장하고 파일명 규칙을 관리합니다.
"""

# 표준 라이브러리
import logging
from datetime import datetime
from pathlib import Path

# 외부 라이브러리
import numpy as np
from PIL import Image

# 로거 설정
logger = logging.getLogger(__name__)


class FileManager:
    """
    파일 저장 관리 클래스.

    캡처된 이미지를 날짜별 폴더에 저장하고, 교시별 파일명 규칙을 적용합니다.
    중복 파일 처리(덮어쓰기/수정본) 로직을 포함합니다.

    Attributes:
        base_path: 기본 저장 경로 (Path 객체)
        current_date: 현재 날짜 문자열 (YYMMDD 형식)

    Example:
        >>> fm = FileManager("C:/IBM 비대면")
        >>> file_path = fm.save_image(image, period=1, is_within_window=True)
        "C:/IBM 비대면/251104/251104_1교시.png"
    """

    def __init__(self, base_path: str = None) -> None:
        """
        FileManager 인스턴스를 초기화합니다.

        기본 저장 경로를 설정하고 현재 날짜를 YYMMDD 형식으로 계산합니다.

        Args:
            base_path: 기본 저장 경로 (기본값: 바탕화면)

        Example:
            >>> fm = FileManager()  # 바탕화면 사용
            >>> fm = FileManager("C:/IBM 비대면")  # 사용자 지정 경로
            >>> fm = FileManager("D:/출결관리")  # 사용자 지정 경로
        """
        if base_path is None:
            base_path = str(Path.home() / "Desktop")

        self.base_path: Path = Path(base_path)
        self.current_date: str = datetime.now().strftime("%y%m%d")

        logger.info(f"FileManager 초기화: base_path={self.base_path}, date={self.current_date}")

    def ensure_folder_exists(self) -> None:
        """
        날짜별 폴더를 생성합니다.

        base_path 아래에 current_date 폴더를 생성합니다.
        폴더가 이미 존재하면 아무 작업도 하지 않습니다.

        Raises:
            PermissionError: 폴더 생성 권한이 없을 때
            OSError: 폴더 생성 중 오류 발생 시

        Example:
            >>> fm = FileManager("C:/IBM 비대면")
            >>> fm.ensure_folder_exists()
            # C:/IBM 비대면/251104/ 폴더 생성
        """
        try:
            folder_path = self.base_path / self.current_date
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"폴더 확인/생성 완료: {folder_path}")

        except PermissionError as e:
            logger.error(f"폴더 생성 권한 없음: {folder_path}", exc_info=True)
            raise PermissionError(f"폴더를 생성할 권한이 없습니다: {folder_path}")

        except Exception as e:
            logger.error(f"폴더 생성 실패: {e}", exc_info=True)
            raise OSError(f"폴더 생성 중 오류 발생: {e}")

    def get_file_path(self, period: int, is_within_window: bool) -> Path:
        """
        파일 경로를 생성합니다.

        교시 번호와 캡처 시간대 여부에 따라 파일 경로를 생성합니다.

        Args:
            period: 교시 번호 (0=퇴실, 1~8=교시)
            is_within_window: 캡처 시간대 내 여부
                - True: 시간대 내 → 덮어쓰기
                - False: 시간대 종료 후 → _수정.png

        Returns:
            Path: 생성된 파일 경로

        Raises:
            ValueError: period가 0~8 범위를 벗어날 때

        Example:
            >>> fm = FileManager("C:/IBM 비대면")
            >>> path = fm.get_file_path(1, True)
            Path("C:/IBM 비대면/251104/251104_1교시.png")

            >>> path = fm.get_file_path(1, False)
            Path("C:/IBM 비대면/251104/251104_1교시_수정.png")

            >>> path = fm.get_file_path(0, True)
            Path("C:/IBM 비대면/251104/251104_퇴실.png")
        """
        # period 유효성 검사
        if not isinstance(period, int):
            logger.error(f"period는 정수여야 합니다. 현재: {type(period)}")
            raise ValueError(f"period는 정수여야 합니다. 현재: {type(period)}")

        if period < 0 or period > 8:
            logger.error(f"period는 0~8 범위여야 합니다. 현재: {period}")
            raise ValueError(f"period는 0~8 범위여야 합니다. 현재: {period}")

        # 교시명 가져오기
        period_name = self._get_period_name(period)

        # 파일명 생성
        if is_within_window:
            filename = f"{self.current_date}_{period_name}.png"
        else:
            filename = f"{self.current_date}_{period_name}_수정.png"

        # 전체 경로 생성
        file_path = self.base_path / self.current_date / filename

        logger.info(f"파일 경로 생성: {file_path}")
        return file_path

    def save_image(
        self,
        image: np.ndarray,
        period: int,
        is_within_window: bool
    ) -> str:
        """
        이미지를 저장합니다.

        numpy array 형식의 이미지를 PNG 파일로 저장합니다.
        캡처 시간대 여부에 따라 덮어쓰기 또는 수정본으로 저장됩니다.

        Args:
            image: 저장할 이미지 (numpy array, RGB)
            period: 교시 번호 (0=퇴실, 1~8=교시)
            is_within_window: 캡처 시간대 내 여부
                - True: 시간대 내 → 덮어쓰기
                - False: 시간대 종료 후 → _수정.png

        Returns:
            str: 저장된 파일 경로

        Raises:
            ValueError: 이미지가 유효하지 않을 때
            PermissionError: 파일 저장 권한이 없을 때
            OSError: 디스크 공간 부족 또는 저장 실패 시

        Example:
            >>> fm = FileManager()
            >>> image = np.array([[[255, 0, 0]]])  # 1x1 빨간색 이미지
            >>> path = fm.save_image(image, 1, True)
            "C:/IBM 비대면/251104/251104_1교시.png"
            >>> path = fm.save_image(image, 1, False)
            "C:/IBM 비대면/251104/251104_1교시_수정.png"
        """
        try:
            # 1. 이미지 유효성 검사
            self._validate_image(image)

            # 2. 폴더 생성
            self.ensure_folder_exists()

            # 3. 파일 경로 생성
            file_path = self.get_file_path(period, is_within_window)

            # 4. numpy array → PIL Image 변환
            pil_image = Image.fromarray(image)

            # 5. PNG 파일로 저장
            pil_image.save(file_path, format="PNG")

            logger.info(f"이미지 저장 성공: {file_path}")
            return str(file_path)

        except ValueError as e:
            logger.error(f"이미지 유효성 검사 실패: {e}", exc_info=True)
            raise

        except PermissionError as e:
            logger.error(f"파일 저장 권한 없음: {file_path}", exc_info=True)
            raise PermissionError(f"파일을 저장할 권한이 없습니다: {file_path}")

        except OSError as e:
            logger.error(f"파일 저장 실패 (디스크 공간 부족 가능): {e}", exc_info=True)
            raise OSError(f"파일 저장 중 오류 발생: {e}")

        except Exception as e:
            logger.error(f"예상치 못한 오류 발생: {e}", exc_info=True)
            raise RuntimeError(f"이미지 저장 중 예상치 못한 오류: {e}")

    def _validate_image(self, image: np.ndarray) -> None:
        """
        이미지 유효성을 검사합니다.

        numpy array가 유효한 이미지 데이터인지 확인합니다.

        Args:
            image: 검사할 이미지 (numpy array)

        Raises:
            ValueError: 이미지가 None이거나 비어있거나 형식이 잘못되었을 때

        Example:
            >>> fm = FileManager()
            >>> valid_image = np.zeros((100, 100, 3), dtype=np.uint8)
            >>> fm._validate_image(valid_image)  # 정상 통과

            >>> invalid_image = None
            >>> fm._validate_image(invalid_image)  # ValueError 발생
        """
        # None 체크
        if image is None:
            raise ValueError("이미지가 None입니다.")

        # numpy array 타입 체크
        if not isinstance(image, np.ndarray):
            raise ValueError(
                f"이미지는 numpy array여야 합니다. 현재 타입: {type(image)}"
            )

        # 빈 이미지 체크
        if image.size == 0:
            raise ValueError("이미지가 비어있습니다.")

        # shape 체크 (2D 또는 3D array)
        if image.ndim not in [2, 3]:
            raise ValueError(
                f"이미지는 2D 또는 3D array여야 합니다. 현재 차원: {image.ndim}"
            )

        # RGB 이미지인 경우 채널 수 체크
        if image.ndim == 3 and image.shape[2] not in [1, 3, 4]:
            raise ValueError(
                f"이미지 채널은 1(Grayscale), 3(RGB), 4(RGBA)여야 합니다. "
                f"현재 채널: {image.shape[2]}"
            )

        logger.debug(f"이미지 유효성 검사 통과: shape={image.shape}, dtype={image.dtype}")

    def _get_period_name(self, period: int) -> str:
        """
        교시 번호를 교시명으로 변환합니다.

        Args:
            period: 교시 번호 (0=퇴실, 1~8=교시)

        Returns:
            str: 교시명 ("퇴실" 또는 "N교시")

        Example:
            >>> fm = FileManager()
            >>> fm._get_period_name(0)
            "퇴실"
            >>> fm._get_period_name(1)
            "1교시"
            >>> fm._get_period_name(8)
            "8교시"
        """
        if period == 0:
            return "퇴실"
        else:
            return f"{period}교시"
