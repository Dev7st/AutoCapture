"""
FileManager 클래스 테스트 스크립트.

FileManager의 모든 메서드를 테스트합니다.
"""

# 표준 라이브러리
import os
import tempfile
from pathlib import Path
from datetime import datetime

# 외부 라이브러리
import numpy as np
import pytest

# 내부 모듈
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from features.file_manager import FileManager


class TestFileManagerInit:
    """FileManager 생성자 테스트"""

    def test_init_default_path(self):
        """기본 경로로 초기화 테스트"""
        fm = FileManager()
        assert fm.base_path == Path("C:/IBM 비대면")
        assert fm.current_date == datetime.now().strftime("%y%m%d")

    def test_init_custom_path(self):
        """사용자 지정 경로로 초기화 테스트"""
        custom_path = "D:/출결관리"
        fm = FileManager(custom_path)
        assert fm.base_path == Path(custom_path)

    def test_init_path_conversion(self):
        """문자열 경로가 Path 객체로 변환되는지 테스트"""
        fm = FileManager("C:/Test")
        assert isinstance(fm.base_path, Path)


class TestFolderCreation:
    """폴더 생성 테스트"""

    def test_ensure_folder_exists_creates_folder(self):
        """폴더가 없을 때 생성되는지 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)
            fm.ensure_folder_exists()

            expected_folder = Path(tmpdir) / fm.current_date
            assert expected_folder.exists()
            assert expected_folder.is_dir()

    def test_ensure_folder_exists_idempotent(self):
        """폴더가 이미 존재할 때 에러 없이 통과하는지 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)

            # 첫 번째 호출
            fm.ensure_folder_exists()

            # 두 번째 호출 (에러 없이 통과해야 함)
            fm.ensure_folder_exists()

            expected_folder = Path(tmpdir) / fm.current_date
            assert expected_folder.exists()

    def test_ensure_folder_creates_parent_folders(self):
        """부모 폴더가 없을 때 함께 생성되는지 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "level1" / "level2"
            fm = FileManager(str(nested_path))
            fm.ensure_folder_exists()

            expected_folder = nested_path / fm.current_date
            assert expected_folder.exists()


class TestFilePathGeneration:
    """파일 경로 생성 테스트"""

    def test_get_file_path_period_1_normal(self):
        """1교시 일반 파일 경로 생성 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)
            path = fm.get_file_path(1, False)

            expected_filename = f"{fm.current_date}_1교시.png"
            assert path.name == expected_filename
            assert path.parent == Path(tmpdir) / fm.current_date

    def test_get_file_path_period_1_modified(self):
        """1교시 수정본 파일 경로 생성 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)
            path = fm.get_file_path(1, True)

            expected_filename = f"{fm.current_date}_1교시_수정.png"
            assert path.name == expected_filename

    def test_get_file_path_period_0_checkout(self):
        """퇴실 파일 경로 생성 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)
            path = fm.get_file_path(0, False)

            expected_filename = f"{fm.current_date}_퇴실.png"
            assert path.name == expected_filename

    def test_get_file_path_all_periods(self):
        """모든 교시(0~8) 경로 생성 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)

            for period in range(9):
                path = fm.get_file_path(period, False)
                assert path.suffix == ".png"
                assert path.parent == Path(tmpdir) / fm.current_date

    def test_get_file_path_invalid_period_negative(self):
        """잘못된 period (음수) 테스트"""
        fm = FileManager()
        with pytest.raises(ValueError, match="0~8 범위"):
            fm.get_file_path(-1, False)

    def test_get_file_path_invalid_period_too_large(self):
        """잘못된 period (9 이상) 테스트"""
        fm = FileManager()
        with pytest.raises(ValueError, match="0~8 범위"):
            fm.get_file_path(9, False)

    def test_get_file_path_invalid_period_type(self):
        """잘못된 period 타입 테스트"""
        fm = FileManager()
        with pytest.raises(ValueError, match="정수여야"):
            fm.get_file_path("1", False)


class TestImageSaving:
    """이미지 저장 테스트"""

    def test_save_image_normal_rgb(self):
        """RGB 이미지 저장 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)

            # 100x100 빨간색 이미지 생성
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            image[:, :] = [255, 0, 0]  # 빨간색

            saved_path = fm.save_image(image, 1, False)

            assert Path(saved_path).exists()
            assert Path(saved_path).suffix == ".png"

    def test_save_image_grayscale(self):
        """Grayscale 이미지 저장 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)

            # 100x100 회색 이미지 생성
            image = np.full((100, 100), 128, dtype=np.uint8)

            saved_path = fm.save_image(image, 1, False)
            assert Path(saved_path).exists()

    def test_save_image_overwrite(self):
        """파일 덮어쓰기 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)
            image = np.zeros((100, 100, 3), dtype=np.uint8)

            # 첫 번째 저장
            path1 = fm.save_image(image, 1, False)
            mtime1 = os.path.getmtime(path1)

            # 잠시 대기 (파일 수정 시간 차이를 위해)
            import time
            time.sleep(0.1)

            # 두 번째 저장 (덮어쓰기)
            path2 = fm.save_image(image, 1, False)
            mtime2 = os.path.getmtime(path2)

            # 같은 경로에 저장되고, 수정 시간이 달라야 함
            assert path1 == path2
            assert mtime2 > mtime1

    def test_save_image_modified_version(self):
        """수정본 파일 저장 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)
            image = np.zeros((100, 100, 3), dtype=np.uint8)

            # 일반 파일 저장
            path1 = fm.save_image(image, 1, False)

            # 수정본 저장
            path2 = fm.save_image(image, 1, True)

            # 두 파일 모두 존재해야 함
            assert Path(path1).exists()
            assert Path(path2).exists()
            assert "_수정" in path2
            assert "_수정" not in path1

    def test_save_image_all_periods(self):
        """모든 교시 저장 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)
            image = np.zeros((50, 50, 3), dtype=np.uint8)

            saved_paths = []
            for period in range(9):
                path = fm.save_image(image, period, False)
                saved_paths.append(path)
                assert Path(path).exists()

            # 모든 파일이 다른 경로여야 함
            assert len(set(saved_paths)) == 9

    def test_save_image_invalid_none(self):
        """None 이미지 저장 시 에러 테스트"""
        fm = FileManager()
        with pytest.raises(ValueError, match="None"):
            fm.save_image(None, 1, False)

    def test_save_image_invalid_empty(self):
        """빈 이미지 저장 시 에러 테스트"""
        fm = FileManager()
        empty_image = np.array([])
        with pytest.raises(ValueError, match="비어있습니다"):
            fm.save_image(empty_image, 1, False)

    def test_save_image_invalid_shape_1d(self):
        """1D 이미지 저장 시 에러 테스트"""
        fm = FileManager()
        image_1d = np.array([1, 2, 3, 4, 5])
        with pytest.raises(ValueError, match="2D 또는 3D"):
            fm.save_image(image_1d, 1, False)

    def test_save_image_invalid_channel(self):
        """잘못된 채널 수 이미지 저장 시 에러 테스트"""
        fm = FileManager()
        # 5채널 이미지 (잘못된 형식)
        image_5ch = np.zeros((100, 100, 5), dtype=np.uint8)
        with pytest.raises(ValueError, match="채널은"):
            fm.save_image(image_5ch, 1, False)


class TestPrivateMethods:
    """Private 메서드 테스트"""

    def test_get_period_name_checkout(self):
        """_get_period_name(0) -> 퇴실 테스트"""
        fm = FileManager()
        assert fm._get_period_name(0) == "퇴실"

    def test_get_period_name_periods(self):
        """_get_period_name(1~8) -> N교시 테스트"""
        fm = FileManager()
        for period in range(1, 9):
            expected = f"{period}교시"
            assert fm._get_period_name(period) == expected

    def test_validate_image_valid_rgb(self):
        """유효한 RGB 이미지 검증 테스트"""
        fm = FileManager()
        valid_image = np.zeros((100, 100, 3), dtype=np.uint8)

        # 에러 없이 통과해야 함
        fm._validate_image(valid_image)

    def test_validate_image_valid_grayscale(self):
        """유효한 Grayscale 이미지 검증 테스트"""
        fm = FileManager()
        valid_image = np.zeros((100, 100), dtype=np.uint8)

        # 에러 없이 통과해야 함
        fm._validate_image(valid_image)

    def test_validate_image_valid_rgba(self):
        """유효한 RGBA 이미지 검증 테스트"""
        fm = FileManager()
        valid_image = np.zeros((100, 100, 4), dtype=np.uint8)

        # 에러 없이 통과해야 함
        fm._validate_image(valid_image)

    def test_validate_image_invalid_not_array(self):
        """numpy array가 아닌 객체 검증 테스트"""
        fm = FileManager()
        with pytest.raises(ValueError, match="numpy array"):
            fm._validate_image([1, 2, 3])


if __name__ == "__main__":
    # pytest 실행
    pytest.main([__file__, "-v", "--tb=short"])
