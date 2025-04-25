import pytest
import requests
import threading # 导入 threading 但注意 pytest-xdist 是更好的并发执行方式
from concurrent.futures import ThreadPoolExecutor, as_completed



# --- Fixtures ---
# Fixtures 是 Pytest 的强大功能，用于设置测试环境或提供测试数据

@pytest.fixture(scope="session") # scope="session" 表示这个 fixture 在整个测试会话中只运行一次
def base_url():
    """提供 API 的基础 URL"""
    return "https://jsonplaceholder.typicode.com"

@pytest.fixture
def new_post_payload():
    """提供一个用于创建新帖子的数据字典 (payload)"""
    return {
        "title": "My Test Post via Pytest",
        "body": "This is the content of the post created during testing.",
        "userId": 999 # 使用一个不太可能冲突的 userId
    }

# --- Test Functions ---
# 测试函数以 `test_` 开头

@pytest.mark.smoke # 标记为烟雾测试，通常是一些快速的关键路径检查
def test_get_all_posts_status_code(base_url):
    """测试获取所有帖子接口是否返回 200 OK"""
    print(f"\n[Thread: {threading.current_thread().name}] Running test_get_all_posts_status_code") # 打印线程信息
    response = requests.get(f"{base_url}/posts")
    # Pytest 使用简单的 assert 语句进行断言
    assert response.status_code == 200, f"预期状态码 200, 但实际为 {response.status_code}"

def test_get_all_posts_returns_list(base_url):
    """测试获取所有帖子接口返回的是一个列表"""
    print(f"\n[Thread: {threading.current_thread().name}] Running test_get_all_posts_returns_list")
    response = requests.get(f"{base_url}/posts")
    assert response.status_code == 200 # 最好先检查状态码
    data = response.json()
    assert isinstance(data, list), f"预期返回类型为 list, 但实际为 {type(data)}"
    assert len(data) > 0, "预期返回的列表不为空" # JSONPlaceholder 应该有 > 100 个帖子

# --- Parameterization ---
# 使用 @pytest.mark.parametrize 可以用不同的参数多次运行同一个测试函数

@pytest.mark.regression # 标记为回归测试
@pytest.mark.parametrize("post_id, expected_user_id, expected_title_part", [
    (1, 1, "sunt aut facere"), # 测试帖子 ID 1
    (10, 1, "optio molestias"), # 测试帖子 ID 10
    (50, 5, "repellendus qui"), # 测试帖子 ID 50
    pytest.param(99, 10, "provident", marks=pytest.mark.smoke), # 也可以在参数级别应用标记
])
def test_get_specific_post(base_url, post_id, expected_user_id, expected_title_part):
    """使用参数化测试获取特定帖子的详情"""
    print(f"\n[Thread: {threading.current_thread().name}] Running test_get_specific_post with post_id={post_id}")
    response = requests.get(f"{base_url}/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["id"] == post_id, f"预期帖子 ID 为 {post_id}, 实际为 {data.get('id')}"
    assert data["userId"] == expected_user_id, f"预期用户 ID 为 {expected_user_id}, 实际为 {data.get('userId')}"
    assert expected_title_part in data["title"], f"预期标题包含 '{expected_title_part}', 实际为 '{data.get('title')}'"

def test_get_non_existent_post(base_url):
    """测试获取一个不存在的帖子应该返回 404 Not Found"""
    print(f"\n[Thread: {threading.current_thread().name}] Running test_get_non_existent_post")
    non_existent_id = 99999
    response = requests.get(f"{base_url}/posts/{non_existent_id}")
    assert response.status_code == 404, f"预期状态码 404, 但实际为 {response.status_code}"

@pytest.mark.regression
def test_create_post(base_url, new_post_payload):
    """测试创建一个新的帖子 (POST请求)"""
    print(f"\n[Thread: {threading.current_thread().name}] Running test_create_post")
    headers = {"Content-type": "application/json; charset=UTF-8"}
    response = requests.post(f"{base_url}/posts", json=new_post_payload, headers=headers)

    # JSONPlaceholder 创建成功会返回 201 Created
    assert response.status_code == 201, f"预期状态码 201, 但实际为 {response.status_code}"
    data = response.json()
    assert isinstance(data, dict)
    # 验证返回的数据是否包含了我们发送的数据（注意：id 由服务器分配）
    assert data["title"] == new_post_payload["title"]
    assert data["body"] == new_post_payload["body"]
    assert data["userId"] == new_post_payload["userId"]
    assert "id" in data, "预期响应中包含 'id' 字段"
    assert isinstance(data["id"], int) and data["id"] > 100, "预期新帖子的 ID 是一个大于 100 的整数 (JSONPlaceholder 行为)"
    # 注意：JSONPlaceholder 不会真的保存你的帖子，下次请求时它就消失了

# --- Markers: skip and xfail ---

@pytest.mark.skip(reason="此测试用例使用skip标记，会暂时跳过，作为示例")
def test_something_to_skip():
    """这个测试将不会被执行
    """
    print("\n这个打印不会显示，因为测试被跳过了")
    assert 1 == 2 # 这是一个必然失败的断言，但因为 skip 而不会执行

@pytest.mark.xfail(reason="预期此功能会失败或尚未实现")
def test_expected_to_fail(base_url):
    """标记为 xfail (Expected Failure)，如果它失败了，测试结果是 XFAIL，如果意外成功了，是 XPASS"""
    print(f"\n[Thread: {threading.current_thread().name}] Running test_expected_to_fail")
    # 假设我们期望删除一个不存在的资源会返回 400 而不是 404
    response = requests.delete(f"{base_url}/posts/99999")
    # 这个断言会失败（因为实际返回 404 或其他），但因为 xfail，测试不算作失败
    assert response.status_code == 400, f"预期状态码为400，实际为{response.status_code}"

# --- Simulating Concurrency (using requests within a test) ---
# 注意：这种方式是在 *单个测试* 内部模拟并发请求，而不是并行运行 *多个测试*。
# pytest-xdist 用于后者，通常是更好的选择。

@pytest.mark.regression
def test_concurrent_requests_to_same_endpoint(base_url):
    """在单个测试中使用线程池模拟并发请求（不推荐作为标准做法，仅作演示）"""
    print(f"\n[Thread: {threading.current_thread().name}] Running test_concurrent_requests_to_same_endpoint")
    post_ids_to_fetch = [1, 2, 3, 4, 5]
    results = {}
    failed_requests = 0

    def fetch_post(post_id):
        try:
            response = requests.get(f"{base_url}/posts/{post_id}", timeout=10) # 设置超时
            response.raise_for_status() # 如果状态码不是 2xx，则抛出异常
            return post_id, response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 post {post_id} 失败: {e}")
            return post_id, None # 返回 None 表示失败

    # 使用线程池执行并发请求
    with ThreadPoolExecutor(max_workers=len(post_ids_to_fetch)) as executor:
        # submit() 返回 Future 对象
        futures = {executor.submit(fetch_post, pid): pid for pid in post_ids_to_fetch}

        for future in as_completed(futures):
            post_id = futures[future] # 获取对应的 post_id
            try:
                pid_result, data = future.result() # 获取 fetch_post 的返回值
                print("zhuzhu")
                print(future.result())

                if data:
                    results[pid_result] = data
                else:
                    failed_requests += 1
            except Exception as e:
                print(f"获取 post {post_id} 结果时出错: {e}")
                failed_requests += 1

    # 断言所有请求都成功返回了数据
    assert failed_requests == 0, f"有 {failed_requests} 个并发请求失败"
    assert len(results) == len(post_ids_to_fetch), "并非所有帖子的数据都被成功获取"
    # 可以添加更多对 results 内容的检查
    for post_id in post_ids_to_fetch:
        assert post_id in results
        assert results[post_id]["id"] == post_id

# --- Test Class Example ---
# 你也可以将相关的测试组织在类中

@pytest.mark.regression
class TestPostModification:
    """测试帖子的修改和删除操作 (PUT, DELETE)"""

    def test_update_post(self, base_url, new_post_payload):
        """测试更新一个帖子 (PUT)"""
        print(f"\n[Thread: {threading.current_thread().name}] Running TestPostModification.test_update_post")
        post_id_to_update = 1 # 选择一个已存在的帖子 ID
        updated_payload = {
            "id": post_id_to_update, # PUT 请求通常需要包含 ID
            "title": "Updated Title",
            "body": "Updated body content.",
            "userId": new_post_payload["userId"] # 可以保持也可以修改 userId
        }
        headers = {"Content-type": "application/json; charset=UTF-8"}
        response = requests.put(f"{base_url}/posts/{post_id_to_update}", json=updated_payload, headers=headers)

        assert response.status_code == 200, f"预期状态码 200, 但实际为 {response.status_code}"
        data = response.json()
        assert data["title"] == updated_payload["title"]
        assert data["body"] == updated_payload["body"]
        assert data["id"] == post_id_to_update

    def test_delete_post(self, base_url):
        """测试删除一个帖子 (DELETE)"""
        print(f"\n[Thread: {threading.current_thread().name}] Running TestPostModification.test_delete_post")
        post_id_to_delete = 1
        response = requests.delete(f"{base_url}/posts/{post_id_to_delete}")

        # JSONPlaceholder 对 DELETE 请求成功也返回 200 OK
        assert response.status_code == 200, f"预期状态码 200, 但实际为 {response.status_code}"
        # 理论上，再次 GET 这个 ID 应该返回 404，但 JSONPlaceholder 的 DELETE 是模拟的，
        # 它可能不会真的删除。所以我们只检查 DELETE 操作本身的状态码。
        # 如果是真实的 API，这里通常会跟一个 GET 请求来验证资源确实被删除了。