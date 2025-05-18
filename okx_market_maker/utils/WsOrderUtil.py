from okx.websocket.WsUtils import isNotBlankStr, getParamKey, initSubscribeSet
from okx_market_maker.utils.OkxEnum import OrderOp

import shortuuid

# 这个文件提供了一些与 WebSocket 请求相关的工具函数
# 主要用于处理 WebSocket 请求的参数校验、唯一标识生成以及订阅参数的初始化等功能。

def get_request_uuid(op: str) -> str:
    """
    生成一个唯一的请求 ID，用于标识 WebSocket 请求。

    Args:
        op (str): 操作类型，如 "order"、"position" 等。
    Returns:
        str: 生成的唯一请求 ID。
    """
    return f"{op}{str(shortuuid.uuid())}"


def check_socket_request_params(
    op: str, 
    args: list, 
    channel_args: dict, 
    channel_param_map: dict
) -> None:
    """
    检查 WebSocket 请求的参数是否合法。
    
    Args:
        op (str): 操作类型，如 "order"、"position" 等。
        args (list): 请求参数列表，每个参数都是一个字典。
        channel_args (dict): 存储通道参数的字典。
        channel_param_map (dict): 存储通道参数映射的字典。
    Returns:
        None
    """
    if not op:
        raise ValueError("op must not none")
    if op not in OrderOp:
        raise ValueError(f"invalid op {op}")
    request_id = get_request_uuid(op)
    for arg in args:
        channel = arg['channel'].strip()
        if not channel:
            raise ValueError("channel must not none")
        arg_set = channel_param_map.get(channel, set())
        arg_key = getParamKey(arg)
        if arg_key in arg_set:
            continue
        else:
            valid_params = initSubscribeSet(arg)
        if len(valid_params) < 1:
            continue
        p = {}
        for k in arg:
            p[k.strip()] = arg.get(k).strip()
        channel_param_map[channel] = channel_param_map.get(channel, set()) | valid_params
        if channel not in channel_args:
            channel_args[channel] = []
        channel_args[channel].append(p)


def get_request_param_key(arg: dict) -> str:
    """
    获取请求参数的唯一标识符。

    Args:
        arg (dict): 请求参数字典。
    Returns:
        str: 生成的唯一标识符。
    """
    s = ""
    for k in arg:
        if k == 'channel':
            continue
        s = s + "@" + arg.get(k)
    return s


def init_request_set(arg: dict) -> set:
    """
    初始化请求参数集合。

    Args:
        arg (dict): 请求参数字典。
    Returns:
        set: 包含请求参数的集合。
    """
    params_set = set()
    if arg is None:
        return params_set
    elif isinstance(arg, dict):
        params_set.add(get_request_param_key(arg))
        return params_set
    else:
        raise ValueError("arg must dict")
