# humanloop_manager.py
import os
from gohumanloop  import DefaultHumanLoopManager , APIProvider
#from gohumanloop import   APIProvider
from gohumanloop.adapters.langgraph_adapter import HumanloopAdapter
from gohumanloop.providers.terminal_provider import TerminalProvider 
from gohumanloop.utils import get_secret_from_env
# 设置环境变量
os.environ["GOHUMANLOOP_API_KEY"] = "577992f3-3092-4ba1-95e9-5d8a6c540687"

# Initialize HumanLoopManager and HumanloopAdapter for GoHumanLoop
# This is done in a separate file to avoid circular imports
# humanloop_manager = DefaultHumanLoopManager(
#     initial_providers=TerminalProvider(name="TerminalProvider")
# )
# humanloop_adapter = HumanloopAdapter(humanloop_manager, default_timeout=60)

# 创建 GoHumanLoopManager 实例
humanloop_manager = DefaultHumanLoopManager(
    APIProvider(
        name="ApiProvider",
        api_base_url="http://127.0.0.1:9800/api", # 换成自己飞书应用的URL
        api_key=get_secret_from_env("GOHUMANLOOP_API_KEY"),  # get_secret_from_env("GOHUMANLOOP_API_KEY"),
        default_platform="feishu"
    )
)
# 创建 LangGraphAdapter 实例
humanloop_adapter = HumanloopAdapter(
    manager=humanloop_manager,
    default_timeout=300,  # 默认超时时间为5分钟
)