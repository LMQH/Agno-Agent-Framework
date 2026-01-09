#!/usr/bin/env python3
"""
创建环境配置文件脚本
从 env.template 创建 .env.dev, .env.show, .env.prod 文件
"""

import shutil
from pathlib import Path

def create_env_files():
    """创建环境配置文件"""
    project_root = Path(__file__).parent.parent
    template_file = project_root / "env.template"
    
    if not template_file.exists():
        print(f"错误: 未找到模板文件 {template_file}")
        return False
    
    env_files = {
        ".env.dev": "开发环境",
        ".env.show": "展示环境",
        ".env.prod": "生产环境"
    }
    
    created = []
    skipped = []
    
    for env_file, description in env_files.items():
        target_file = project_root / env_file
        
        if target_file.exists():
            print(f"跳过: {env_file} 已存在 ({description})")
            skipped.append(env_file)
        else:
            try:
                shutil.copy(template_file, target_file)
                print(f"创建: {env_file} ({description})")
                created.append(env_file)
            except Exception as e:
                print(f"错误: 创建 {env_file} 失败: {e}")
                return False
    
    print("\n" + "="*50)
    print("环境文件创建完成！")
    print("="*50)
    
    if created:
        print(f"\n已创建 {len(created)} 个文件:")
        for f in created:
            print(f"  - {f}")
        print("\n请编辑这些文件，设置正确的配置值。")
    
    if skipped:
        print(f"\n已跳过 {len(skipped)} 个已存在的文件:")
        for f in skipped:
            print(f"  - {f}")
    
    print("\n提示:")
    print("  - 这些文件可以提交到版本控制系统")
    print("  - 使用 'python main.py dev/show/prod' 切换环境")
    print("  - 详细说明请参考 document/ENV_SETUP.md")
    
    return True

if __name__ == "__main__":
    create_env_files()
