#!/usr/bin/env python3
"""
占位符渲染脚本
读取 placeholder-config.json，批量替换 fragments/ 和 PROJECT.md 中的占位符

用法：
    python3 render-placeholders.py <项目目录>
    python3 render-placeholders.py ./我的新书
"""
import json
import sys
import shutil
from pathlib import Path


def load_config(project_dir):
    """加载 placeholder-config.json，提取占位符映射"""
    config_path = Path(project_dir) / "placeholder-config.json"
    if not config_path.exists():
        print(f"❌ 未找到: {config_path}")
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    mapping = {}

    def extract(obj):
        if not isinstance(obj, dict):
            return
        # 收集 _占位符 字段的所有占位符
        placeholders = obj.get("_占位符", [])
        # 找这个对象里的实际值字段（排除 _开头的元数据）
        value_fields = {k: v for k, v in obj.items() if not k.startswith("_") and isinstance(v, str) and not v.startswith("{")}
        for ph in placeholders:
            if not (isinstance(ph, str) and ph.startswith("{") and ph.endswith("}")):
                continue
            # 优先用对象里第一个非占位符值
            if value_fields:
                mapping[ph] = next(iter(value_fields.values()))
            else:
                # 让用户手动填
                mapping[ph] = input(f"请输入 {ph} 的值: ").strip()
        for k, v in obj.items():
            if k.startswith("_"):
                continue
            extract(v)

    extract(config)
    return mapping


def render_file(file_path, mapping, backup_dir):
    """替换单个文件中的占位符"""
    content = file_path.read_text(encoding="utf-8")
    original = content

    for ph, value in mapping.items():
        content = content.replace(ph, value)

    if content != original:
        backup_path = backup_dir / file_path.name
        shutil.copy2(file_path, backup_path)
        file_path.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    if len(sys.argv) < 2:
        print("用法: python3 render-placeholders.py <项目目录>")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"❌ 项目目录不存在: {project_dir}")
        sys.exit(1)

    print(f"📦 渲染占位符: {project_dir}")

    mapping = load_config(project_dir)
    print(f"   找到 {len(mapping)} 个占位符")

    if not mapping:
        print("   ⚠️  没有占位符需要替换")
        return

    # 显示预览
    print("\n   占位符映射:")
    for ph, value in mapping.items():
        preview = value[:30] + "..." if len(value) > 30 else value
        print(f"     {ph} → {preview}")

    # 备份目录
    backup_dir = project_dir / ".placeholder-backup"
    backup_dir.mkdir(exist_ok=True)

    # 替换 fragments/
    fragments_dir = project_dir / "fragments"
    if fragments_dir.exists():
        for f in fragments_dir.glob("*.html"):
            if render_file(f, mapping, backup_dir):
                print(f"   ✅ {f.name}")

    # 替换 PROJECT.md
    project_md = project_dir / "PROJECT.md"
    if project_md.exists():
        if render_file(project_md, mapping, backup_dir):
            print(f"   ✅ PROJECT.md")

    print(f"\n✅ 完成！备份在 {backup_dir}/")
    print("   如需撤销: cp .placeholder-backup/* fragments/")


if __name__ == "__main__":
    main()
