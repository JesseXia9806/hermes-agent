#!/usr/bin/env python3
"""
eHR系统浏览器自动化脚本
用于自动登录和审批单据
作者: Jesse Xia
创建日期: 2026-08-04
"""

import json
import sys
import os
from datetime import datetime

def log_message(message):
    """记录日志到文件"""
    log_file = os.path.expanduser("~/.hermes/logs/ehr_browser_automation.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def read_config(config_file):
    """读取配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_message(f"读取配置文件失败: {e}")
        return None

def perform_browser_automation(config):
    """执行浏览器自动化操作"""
    try:
        # 导入Hermes工具
        from hermes_tools import browser_navigate, browser_snapshot, browser_click, browser_type
        
        username = config['username']
        password = config['password']
        ehr_url = config['ehr_url']
        approve_url = config['approve_url']
        
        log_message("开始浏览器自动化操作...")
        
        # 步骤1: 导航到登录页面
        log_message(f"导航到登录页面: {ehr_url}")
        browser_navigate(ehr_url)
        
        # 等待页面加载
        import time
        time.sleep(3)
        
        # 步骤2: 输入用户名
        log_message(f"输入用户名: {username}")
        browser_type("e10", username)
        time.sleep(1)
        
        # 步骤3: 输入密码
        log_message("输入密码")
        browser_type("e11", password)
        time.sleep(1)
        
        # 步骤4: 点击登录按钮
        log_message("点击登录按钮")
        browser_click("e9")
        
        # 等待登录完成
        time.sleep(5)
        
        # 步骤5: 验证登录状态
        log_message("验证登录状态")
        browser_snapshot()
        
        # 步骤6: 进入审批页面
        log_message(f"进入审批页面: {approve_url}")
        browser_navigate(approve_url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 步骤7: 获取页面快照
        browser_snapshot()
        
        # 步骤8: 选择所有单据
        log_message("选择待审批单据...")
        forms_selected = 0
        
        # 尝试选择单据复选框 (ref从e44开始)
        for i in range(44, 50):
            ref = f"e{i}"
            try:
                browser_click(ref)
                forms_selected += 1
                log_message(f"已选择单据 {forms_selected}")
                time.sleep(0.5)
            except Exception as e:
                log_message(f"无法点击 {ref}: {e}")
                continue
        
        log_message(f"总共选择了 {forms_selected} 个单据")
        
        # 步骤9: 批量审批
        if forms_selected > 0:
            log_message("开始批量审批...")
            browser_click("e32")
            
            # 等待审批完成
            time.sleep(3)
            
            # 检查审批结果
            browser_snapshot()
            log_message("✅ 批量审批完成")
        else:
            log_message("ℹ️ 没有找到需要审批的单据")
        
        log_message("✅ 浏览器自动化操作完成")
        return True
        
    except Exception as e:
        log_message(f"❌ 浏览器自动化失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python3 ehr_browser_automation.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    log_message("========== 开始eHR浏览器自动化任务 ==========")
    
    # 读取配置
    config = read_config(config_file)
    if not config:
        log_message("无法读取配置，任务终止")
        sys.exit(1)
    
    log_message(f"配置加载成功: 用户名 {config['username']}")
    
    # 执行浏览器自动化
    success = perform_browser_automation(config)
    
    if success:
        log_message("========== eHR浏览器自动化任务完成 ==========")
        sys.exit(0)
    else:
        log_message("========== eHR浏览器自动化任务失败 ==========")
        sys.exit(1)

if __name__ == "__main__":
    main()