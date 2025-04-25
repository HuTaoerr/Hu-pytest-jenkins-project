from email.policy import strict

import pytest

@pytest.mark.skip(reason="此测试用例被标记为无条件跳过")
def test_skip():
    assert True

a = 2
@pytest.mark.skipif(a < 3,reason="需要a小于3时才跳过")
def test_skipif_f():
    assert True

b = 5
@pytest.mark.skipif(b < 3,reason="需要b小于3时才跳过")
def test_skipif_t():
    assert True

@pytest.mark.xfail(strict=True,reason="修复后移除此标记")
def test_xfail():
    a = 1
    assert a == 2

@pytest.mark.smoke
def test_smoke():
    a = 2
    b = 3
    assert a < b

@pytest.mark.regression
def test_regression():
    h = "hello"
    assert "e" in h