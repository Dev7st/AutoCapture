"""
CSVLogger 클래스 테스트 스크립트.

CSVLogger의 모든 메서드를 테스트합니다.
"""

# 표준 라이브러리
import csv
import tempfile
from pathlib import Path
from datetime import datetime

# 외부 라이브러리
import pytest

# 내부 모듈
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from features.logger import CSVLogger


@pytest.fixture
def temp_logger():
    """임시 디렉토리에 CSVLogger 인스턴스를 생성하는 fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = CSVLogger(tmpdir)
        yield logger


class TestCSVLoggerInit:
    """CSVLogger 생성자 테스트"""

    def test_init_default_path(self):
        """기본 경로로 초기화 테스트"""
        logger = CSVLogger()
        assert logger.base_path == Path("C:/IBM 비대면")
        assert logger.log_path is None

    def test_init_custom_path(self):
        """사용자 지정 경로로 초기화 테스트"""
        custom_path = "D:/출결로그"
        logger = CSVLogger(custom_path)
        assert logger.base_path == Path(custom_path)

    def test_init_path_conversion(self):
        """문자열 경로가 Path 객체로 변환되는지 테스트"""
        logger = CSVLogger("C:/Test")
        assert isinstance(logger.base_path, Path)


class TestEnsureLogFile:
    """_ensure_log_file() 메서드 테스트"""

    def test_creates_log_file_with_header(self, temp_logger):
        """로그 파일이 헤더와 함께 생성되는지 테스트"""
        temp_logger._ensure_log_file()

        # 파일이 생성되었는지 확인
        assert temp_logger.log_path is not None
        assert temp_logger.log_path.exists()

        # 헤더가 올바른지 확인
        with open(temp_logger.log_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            assert header == [
                '날짜', '시간', '항목', '상태',
                '감지인원', '기준인원', '파일명', '비고'
            ]

    def test_creates_date_folder(self, temp_logger):
        """날짜 폴더가 자동으로 생성되는지 테스트"""
        temp_logger._ensure_log_file()

        today = datetime.now().strftime("%y%m%d")
        date_folder = temp_logger.base_path / today
        assert date_folder.exists()

    def test_log_file_naming(self, temp_logger):
        """로그 파일명이 올바른지 테스트"""
        temp_logger._ensure_log_file()

        today = datetime.now().strftime("%y%m%d")
        expected_name = f"{today}_log.csv"
        assert temp_logger.log_path.name == expected_name

    def test_does_not_recreate_existing_file(self, temp_logger):
        """이미 존재하는 파일을 재생성하지 않는지 테스트"""
        temp_logger._ensure_log_file()

        # 파일 수정 시간 저장
        first_mtime = temp_logger.log_path.stat().st_mtime

        # 다시 호출
        temp_logger._ensure_log_file()

        # 파일이 수정되지 않았는지 확인
        second_mtime = temp_logger.log_path.stat().st_mtime
        assert first_mtime == second_mtime

    def test_utf8_bom_encoding(self, temp_logger):
        """UTF-8-BOM 인코딩이 적용되는지 테스트"""
        temp_logger._ensure_log_file()

        # 파일의 첫 3바이트가 BOM인지 확인
        with open(temp_logger.log_path, 'rb') as f:
            bom = f.read(3)
            assert bom == b'\xef\xbb\xbf'  # UTF-8 BOM

    def test_raises_error_on_invalid_path(self):
        """잘못된 경로일 때 OSError 발생 테스트"""
        logger = CSVLogger("/invalid/path/that/does/not/exist")
        logger.log_path = Path("/invalid/path/file.csv")

        with pytest.raises(OSError):
            logger._ensure_log_file()


class TestLogEvent:
    """log_event() 메서드 테스트"""

    def test_log_event_basic(self, temp_logger):
        """기본 이벤트 로그 기록 테스트"""
        temp_logger.log_event("1교시", "캡처 성공", 20, 22, "251020_1교시.png", "유연 모드")

        # CSV 파일 읽기
        with open(temp_logger.log_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            row = next(reader)

            # 날짜, 시간 확인
            assert row[0] == datetime.now().strftime("%Y-%m-%d")
            assert len(row[1]) == 8  # HH:MM:SS 형식

            # 나머지 데이터 확인
            assert row[2] == "1교시"
            assert row[3] == "캡처 성공"
            assert row[4] == "20"
            assert row[5] == "22"
            assert row[6] == "251020_1교시.png"
            assert row[7] == "유연 모드"

    def test_log_event_with_optional_params(self, temp_logger):
        """선택적 파라미터 없이 로그 기록 테스트"""
        temp_logger.log_event("2교시", "감지 실패", 18, 22)

        with open(temp_logger.log_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더 스킵
            row = next(reader)

            # filename, note가 빈 문자열인지 확인
            assert row[6] == ""
            assert row[7] == ""

    def test_log_multiple_events(self, temp_logger):
        """여러 이벤트를 순차적으로 기록하는지 테스트"""
        temp_logger.log_event("1교시", "캡처 시작", 0, 22)
        temp_logger.log_event("1교시", "얼굴 감지", 20, 22)
        temp_logger.log_event("1교시", "캡처 성공", 20, 22, "251020_1교시.png")

        # 3개 행(헤더 제외)이 있는지 확인
        with open(temp_logger.log_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 4  # 헤더 1 + 데이터 3

    def test_log_event_creates_file_if_not_exists(self, temp_logger):
        """로그 파일이 없을 때 자동으로 생성하는지 테스트"""
        # _ensure_log_file() 호출 없이 바로 log_event 호출
        temp_logger.log_event("1교시", "캡처 성공", 20, 22)

        # 파일이 생성되었는지 확인
        assert temp_logger.log_path is not None
        assert temp_logger.log_path.exists()

    def test_log_event_append_mode(self, temp_logger):
        """이벤트가 기존 파일에 추가되는지 테스트 (덮어쓰기 아님)"""
        temp_logger.log_event("1교시", "첫 번째", 20, 22)
        temp_logger.log_event("2교시", "두 번째", 21, 22)

        with open(temp_logger.log_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
            # 헤더 + 2개 행
            assert len(rows) == 3
            assert rows[1][2] == "1교시"
            assert rows[2][2] == "2교시"

    def test_log_event_raises_error_on_write_failure(self, temp_logger):
        """로그 기록 실패 시 OSError 발생 테스트"""
        # 먼저 로그 파일 생성
        temp_logger._ensure_log_file()

        # 파일을 읽기 전용으로 변경하여 쓰기 실패 유도
        import os
        os.chmod(temp_logger.log_path, 0o444)  # 읽기 전용

        try:
            with pytest.raises(OSError, match="로그 기록 실패"):
                temp_logger.log_event("1교시", "캡처 성공", 20, 22)
        finally:
            # 테스트 후 권한 복구 (cleanup)
            os.chmod(temp_logger.log_path, 0o666)


@pytest.mark.integration
class TestIntegration:
    """통합 테스트"""

    def test_full_workflow(self, temp_logger):
        """전체 워크플로우 테스트 (실제 사용 시나리오)"""
        # 1. 여러 교시 이벤트 기록
        temp_logger.log_event("1교시", "캡처 시작", 0, 22)
        temp_logger.log_event("1교시", "얼굴 감지", 20, 22)
        temp_logger.log_event("1교시", "캡처 성공", 20, 22, "251020_1교시.png", "유연 모드")
        temp_logger.log_event("2교시", "건너뛰기", 0, 22, "", "사용자 요청")
        temp_logger.log_event("퇴실", "캡처 성공", 19, 22, "251020_퇴실.png")

        # 2. 결과 검증
        with open(temp_logger.log_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)

            # 헤더 + 5개 이벤트
            assert len(rows) == 6

            # 헤더 확인
            assert rows[0][0] == '날짜'

            # 각 이벤트 확인
            assert rows[1][2] == "1교시"
            assert rows[1][3] == "캡처 시작"

            assert rows[3][3] == "캡처 성공"
            assert rows[3][6] == "251020_1교시.png"

            assert rows[4][3] == "건너뛰기"
            assert rows[4][7] == "사용자 요청"

            assert rows[5][2] == "퇴실"


if __name__ == "__main__":
    print("CSVLogger 테스트를 실행하려면 pytest를 사용하세요:")
    print("pytest tests/test_logger.py -v")
    print("\n통합 테스트만 실행:")
    print("pytest tests/test_logger.py -m integration -v")
