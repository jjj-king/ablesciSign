#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import os
import requests
import json
import urllib.parse

# 通知服务配置
SCKEY = os.getenv("SCKEY", "").strip()  # Server酱的SCKEY
XZKEY = os.getenv("XZKEY", "").strip()  # 息知的XZKEY
PUSH_PLUS_TOKEN = os.getenv("PUSH_PLUS_TOKEN", "").strip()  # PushPlus的TOKEN

# 消息容器
message_info = ''''''

def serverJ(title, content):
    """Server酱通知"""
    if not SCKEY:
        print("Server酱的SCKEY未设置")
        return
    
    print("Server酱服务启动")
    data = {
        "text": title,
        "desp": content.replace("\n", "\n\n")
    }
    response = requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data=data).json()
    if response.get('code') == 0 or response.get('data', {}).get('errno') == 0:
        print('Server酱推送成功！')
    else:
        print('Server酱推送失败！')

def xizhi(title, content):
    """息知通知：请求一次，失败交给上层通知器记录。"""
    if not XZKEY:
        raise RuntimeError("未配置XZKEY，请在当前仓库的Actions Secrets中添加息知密钥。")
    
    print("息知服务启动")
    headers = {'Content-Type': 'application/json'}
    json_data = {
        'title': title,
        'content': content.replace("\n", "\n\n")
    }
    data = json.dumps(json_data).encode('utf-8')
    try:
        response = requests.post(
            f"https://xizhi.qqoq.net/{XZKEY}.send", data=data, headers=headers,
            timeout=20, allow_redirects=False
        )
        if response.status_code != 200:
            raise RuntimeError(f"息知请求失败，HTTP状态码：{response.status_code}；未自动重试。")
        result = response.json()
    except (requests.RequestException, ValueError):
        # 息知密钥位于请求地址中，网络异常详情可能包含密钥，不能回显。
        raise RuntimeError("息知网络请求失败或响应无法解析；未自动重试，请先检查微信或息知记录。") from None
    if not isinstance(result, dict) or type(result.get('code')) is not int or result['code'] != 200:
        code = result.get('code') if isinstance(result, dict) else None
        code_info = str(code) if type(code) is int else "未知"
        raise RuntimeError(f"息知未接受请求，返回码：{code_info}；请检查XZKEY和息知配置。")
    print('息知请求已接收，请以微信实际收到消息或息知记录为准。')

def pushplus_bot(title, content):
    """发送一次PushPlus请求；失败时交给上层通知器记录，不自动重发。"""
    if not PUSH_PLUS_TOKEN:
        raise RuntimeError("未配置PUSH_PLUS_TOKEN，请在当前仓库的Actions Secrets中添加。")

    print("PushPlus服务启动")
    url = 'https://www.pushplus.plus/send'
    data = {
        "token": PUSH_PLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "txt",
        "channel": "wechat"
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(
            url, json=data, headers=headers, timeout=20, allow_redirects=False
        )
        if response.status_code != 200:
            raise RuntimeError(f"PushPlus请求失败，HTTP状态码：{response.status_code}；未自动重试。")
        result = response.json()
    except (requests.RequestException, ValueError):
        # 不回显异常详情或响应正文，避免第三方错误信息包含Token。
        raise RuntimeError("PushPlus网络请求失败或响应无法解析；未自动重试，请先检查微信或推送记录。") from None
    if not isinstance(result, dict) or type(result.get('code')) is not int or result['code'] != 200:
        code = result.get('code') if isinstance(result, dict) else None
        code_info = str(code) if type(code) is int else "未知"
        raise RuntimeError(f"PushPlus未接受请求，返回码：{code_info}；请检查Token、实名状态和额度。")
    print('PushPlus请求已接收，请以微信实际收到消息或平台推送记录为准。')

def send(title, content):
    """
    发送通知
    :param title: 通知标题
    :param content: 通知内容
    """
    # 记录日志
    print(f"通知标题: {title}")
    print(f"通知内容:\n{content}")
    
    # 依次尝试三种通知方式
    if SCKEY:
        serverJ(title, content)
    
    if XZKEY:
        xizhi(title, content)
    
    if PUSH_PLUS_TOKEN:
        pushplus_bot(title, content)
    
    # 如果没有设置任何通知方式
    if not SCKEY and not XZKEY and not PUSH_PLUS_TOKEN:
        print("未配置任何通知方式，跳过通知发送")

if __name__ == '__main__':
    # 测试通知
    send("测试通知", "这是一条测试通知消息")
