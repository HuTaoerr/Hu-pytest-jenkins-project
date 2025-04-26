from http.client import responses

import pytest
import json
import requests


@pytest.fixture
def base_url():
    """提供 API 的基础 URL"""
    return "https://jsonplaceholder.typicode.com"


# --- Test Case ---
# 1. 测试 GET /posts (获取列表)
def test_get_posts_list(base_url):
    """测试获取帖子列表/posts"""

    get_url = f"{base_url}/posts"
    response = requests.get(get_url)

    # 断言状态码
    assert response.status_code == 200, f"预期状态码：200，实际为{response.status_code}"

    # 断言响应体是一个列表
    posts_list = response.json()
    assert isinstance(posts_list, list), "响应体应该是一个列表"

    # 断言列表不为空
    assert len(posts_list) > 0, "帖子列表为空，不符合预期"

    if posts_list:
        data = json.dumps(posts_list[0], indent=2, ensure_ascii=False)
        print(f"\n打印第一条帖子内容:\n{data}")
        assert "userId" in data, "帖子应包含 'userId' 字段"
        assert "fuck" not in data, "fuck字段不应该存在贴子中"
    print("————————————————————————————用例断言通过————————————————————————————")


# 2. 测试GET获取/posts/{id} (获取单个帖子，使用参数化)
@pytest.mark.parametrize("post_id,expected_code,case_desc", [
    (1, 200, "获取存在的帖子 ID=1"),
    (-1, 404, "获取无效的帖子 ID=-1"),
    ("a", 404, "获取无效的帖子 ID=a"),
    (999, 404, "获取无效的帖子 ID=999"),
], ids=["get_existing_post_id_1",
        "get_invalid_post_id_neg1",
        "get_invalid_post_id_string_a",
        "get_nonexistent_post_id_999"])
def test_get_single_post(base_url, post_id, expected_code, case_desc):
    """测试获取单个帖子接口 (包括存在和不存在的情况)"""

    get_url = f"{base_url}/posts/{post_id}"
    response = requests.get(get_url)
    data = json.dumps(response.json(), indent=2, ensure_ascii=False)
    print(f"\n打印帖子内容{data}")

    assert response.status_code == expected_code, f"预期状态码为{expected_code},实际为{response.status_code}"

    # 如果请求成功，进一步断言响应体内容
    if response.status_code == 200:
        assert "title" in data, "帖子中字段title缺失"
        print(f"{case_desc}断言通过")
    else:
        print(f"\n{case_desc}(预期失败)断言通过")


# 3. 测试POST /posts (创建新帖子，使用参数化)
@pytest.fixture  # Function 范围，如果需要每次测试都用默认头
def common_headers():
    """提供通用的请求头，例如 Content-Type"""
    # 对于 JSONPlaceholder 的 GET/DELETE，不强制需要，但 POST/PUT/PATCH 最好加上
    return {"Content-Type": "application/json; charset=UTF-8"}


# @pytest.mark.smoke
@pytest.mark.parametrize("title,body,userId", [
    ("pytest新标题01", "新内容", "101"),
    ("pytest新标题02", "AI爆发", "101"),
    ("pytest新标题03", "盛世金融", "101"),
], ids=[
    "new title 01", "new title 02", "new title 03",
])
def test_create_post(base_url, title, body, userId, common_headers):
    post_url = f"{base_url}/posts"
    payload = {
        "title": title,
        "body": body,
        "userId": userId
    }
    response = requests.post(post_url, payload, common_headers)

    # 断言状态码
    assert response.status_code == 201, f"预期状态码 201，实际为 {response.status_code}"

    # 断言响应体
    data = response.json()
    print(data)
    assert data["title"] == title, \
        "返回的title应与上传的一致才对"
    assert data["userId"] == userId, \
        "返回的userId应与上传的一致才对"
    assert "id" in data, \
        "服务器应自动生成新id"


# 4. 测试 PUT /posts/{id} (完整更新帖子)
@pytest.mark.skip
def test_update_post_put(base_url, common_headers):
    """测试 PUT 方法完整更新一个帖子"""
    put_id = 101
    put_url = f"{base_url}/post/{put_id}"
    payload = {
        "id": put_id,
        "title": "更新后的title",
        "body": "更新后的body",
        "userId": 1
    }
    response = requests.put(put_url, json=payload, headers=common_headers)

    assert response.status_code == 200
    update_date = response.json()
    print(update_date)
