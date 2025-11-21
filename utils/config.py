"""
설정 관리 모듈.

config.json 파일을 통해 프로그램 설정을 저장하고 로드합니다.
"""

# 표준 라이브러리
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# 로거 설정
logger = logging.getLogger(__name__)

# 기본 설정값
DEFAULT_CONFIG: Dict[str, Any] = {
    "monitor_id": 1,
    "save_path": str(Path.home() / "Desktop"),
    "mode": "flexible",
    "student_count": 1,
    "threshold_ratio": 0.9,
    "last_updated": None
}


class Config:
    """
    설정 관리 클래스.

    config.json 파일을 통해 프로그램 설정을 저장하고 로드합니다.

    Attributes:
        config_path (Path): 설정 파일 경로
        data (dict): 현재 설정 데이터

    Example:
        >>> config = Config()
        >>> config.load()
        >>> monitor_id = config.get('monitor_id', 1)
        >>> config.set('student_count', 22)
    """

    def __init__(self, config_path: str = "config.json") -> None:
        """
        설정 관리 인스턴스를 초기화합니다.

        Args:
            config_path: 설정 파일 경로 (기본값: "config.json")

        Example:
            >>> config = Config()
            >>> config = Config("custom_config.json")
        """
        self.config_path: Path = Path(config_path)
        self.data: Dict[str, Any] = {}
        logger.info(f"Config 인스턴스 생성: {self.config_path}")

    def load(self) -> Dict[str, Any]:
        """
        설정 파일을 읽어 설정값을 로드합니다.

        파일이 없거나 읽기 실패 시 기본값을 반환합니다.

        Returns:
            dict: 로드된 설정 데이터

        Example:
            >>> config = Config()
            >>> data = config.load()
            >>> print(data['mode'])
            'flexible'
        """
        try:
            # 파일이 존재하지 않으면 기본값 사용
            if not self.config_path.exists():
                logger.warning(
                    f"설정 파일이 없습니다. 기본값을 사용합니다: {self.config_path}"
                )
                return self._use_default_config()

            # JSON 파일 읽기
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            logger.info(f"설정 파일 로드 완료: {self.config_path}")
            return self.data

        except json.JSONDecodeError as e:
            logger.error(
                f"설정 파일 JSON 파싱 실패: {e}. 기본값을 사용합니다.",
                exc_info=True
            )
            return self._use_default_config()

        except PermissionError as e:
            logger.error(
                f"설정 파일 읽기 권한 없음: {e}. 기본값을 사용합니다.",
                exc_info=True
            )
            return self._use_default_config()

        except Exception as e:
            logger.error(
                f"설정 파일 로드 실패: {e}. 기본값을 사용합니다.",
                exc_info=True
            )
            return self._use_default_config()

    def save(self, data: Dict[str, Any]) -> None:
        """
        설정값을 파일에 저장합니다.

        Args:
            data: 저장할 설정 데이터

        Raises:
            PermissionError: 파일 쓰기 권한이 없을 때
            OSError: 디스크 공간 부족 등 파일 저장 실패 시

        Example:
            >>> config = Config()
            >>> config.save({'monitor_id': 2, 'mode': 'exact'})
        """
        try:
            # 현재 시간 기록
            data['last_updated'] = datetime.now().isoformat()

            # JSON 파일 쓰기 (들여쓰기 포함)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.data = data
            logger.info(f"설정 파일 저장 완료: {self.config_path}")

        except PermissionError as e:
            logger.error(f"설정 파일 쓰기 권한 없음: {e}", exc_info=True)
            raise

        except OSError as e:
            logger.error(f"설정 파일 저장 실패: {e}", exc_info=True)
            raise

        except Exception as e:
            logger.error(f"설정 파일 저장 중 예상치 못한 오류: {e}", exc_info=True)
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """
        설정 값을 조회합니다.

        Args:
            key: 조회할 설정 키
            default: 키가 없을 때 반환할 기본값

        Returns:
            Any: 설정 값 또는 기본값

        Example:
            >>> config = Config()
            >>> config.load()
            >>> monitor_id = config.get('monitor_id', 1)
            >>> print(monitor_id)
            2
        """
        value = self.data.get(key, default)
        logger.debug(f"설정 값 조회: {key} = {value}")
        return value

    def set(self, key: str, value: Any) -> None:
        """
        설정 값을 저장하고 파일에 즉시 반영합니다.

        Args:
            key: 설정 키
            value: 설정 값

        Example:
            >>> config = Config()
            >>> config.load()
            >>> config.set('student_count', 22)
        """
        self.data[key] = value
        logger.info(f"설정 값 변경: {key} = {value}")

        # 즉시 파일에 저장
        try:
            self.save(self.data)
        except Exception as e:
            logger.error(f"설정 값 저장 실패: {e}", exc_info=True)
            # 저장 실패 시 메모리에는 남아있음

    def _use_default_config(self) -> Dict[str, Any]:
        """
        기본 설정을 적용합니다 (Private).

        중복 코드 제거를 위한 헬퍼 메서드입니다.
        load() 메서드의 여러 예외 처리 블록에서 공통으로 사용됩니다.

        Returns:
            Dict[str, Any]: 기본 설정 데이터

        Example:
            >>> config = Config()
            >>> default = config._use_default_config()
            >>> print(default['mode'])
            'flexible'
        """
        self.data = DEFAULT_CONFIG.copy()
        return self.data
