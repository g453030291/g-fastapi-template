
def test_health_check(client):
    """
    测试健康检查接口
    :param client:
    :return:
    """
    response = client.get("/health")
    # 自动断言
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
