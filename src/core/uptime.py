"""服务运行时长跟踪模块"""
import time

# 服务启动时间
_START_TIME = time.time()


def get_uptime() -> int:
    """获取服务运行时长(秒)

    Returns:
        服务运行时长(秒)
    """
    return int(time.time() - _START_TIME)
