"""
모니터 감지 및 선택 유틸리티 모듈.

듀얼 모니터 환경에서 모니터 목록을 조회하고
선택할 수 있는 기능을 제공합니다.
"""

# 외부 라이브러리
import mss
from typing import List, Dict


def get_monitors() -> List[Dict]:
    """
    시스템에 연결된 모니터 목록을 반환합니다.

    mss 라이브러리를 사용하여 모니터 정보를 조회합니다.
    첫 번째 항목(인덱스 0)은 전체 화면이므로 제외됩니다.

    Returns:
        List[Dict]: 모니터 정보 리스트.
                   각 항목은 {'id', 'name', 'width', 'height', 'left', 'top'} 포함

    Example:
        >>> monitors = get_monitors()
        >>> for monitor in monitors:
        ...     print(f"{monitor['name']}: {monitor['width']}x{monitor['height']}")
        모니터 1: 1920x1080
        모니터 2: 1920x1080
    """
    try:
        with mss.mss() as sct:
            # mss.monitors[0]은 전체 화면, [1:]부터 실제 모니터
            raw_monitors = sct.monitors[1:]

            monitors = []
            for idx, monitor in enumerate(raw_monitors, start=1):
                monitors.append({
                    'id': idx,
                    'name': f"모니터 {idx}",
                    'width': monitor['width'],
                    'height': monitor['height'],
                    'left': monitor['left'],
                    'top': monitor['top']
                })

            return monitors

    except Exception as e:
        # 모니터 조회 실패 시 빈 리스트 반환
        print(f"모니터 조회 실패: {e}")
        return []


def get_monitor_count() -> int:
    """
    연결된 모니터 개수를 반환합니다.

    Returns:
        int: 모니터 개수

    Example:
        >>> count = get_monitor_count()
        >>> print(f"모니터 {count}개 감지됨")
        모니터 2개 감지됨
    """
    monitors = get_monitors()
    return len(monitors)


def get_monitor_names() -> List[str]:
    """
    모니터 이름 목록을 반환합니다.

    InitDialog의 드롭다운에서 사용됩니다.

    Returns:
        List[str]: 모니터 이름 리스트 (예: ["모니터 1", "모니터 2"])

    Example:
        >>> names = get_monitor_names()
        >>> print(names)
        ['모니터 1', '모니터 2']
    """
    monitors = get_monitors()
    return [monitor['name'] for monitor in monitors]