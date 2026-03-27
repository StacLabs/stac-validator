import subprocess

import pytest


def test_correct_sys_exit_error_python():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            ["stac-validator", "tests/test_data/bad_data/bad_item_v090.json"],
            check=True,
        )


def test_correct_sys_exit_error_recursion():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            [
                "stac-validator",
                "tests/test_data/v100/catalog-with-bad-item.json",
                "--recursive",
                "--max-depth",
                "10",
            ],
            check=True,
        )


def test_false_sys_exit_error_python():
    subprocess.run(
        ["stac-validator", "tests/test_data/v090/items/good_item_v090.json"],
        check=True,
    )


def test_cli_schema_cache_size_option():
    subprocess.run(
        [
            "stac-validator",
            "tests/test_data/v090/items/good_item_v090.json",
            "--schema-cache-size",
            "8",
        ],
        check=True,
    )
