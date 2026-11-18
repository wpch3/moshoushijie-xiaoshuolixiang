#!/usr/bin/env python3
"""检查章号、标题、字数、引用角标与出戏词；不代替人工判断文风、戏剧性与连续性。"""
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
BODY = ROOT / "正文"
PATTERN = re.compile(r"^第(\d+)章.*\.md$")
HAN = re.compile(r"[\u4e00-\u9fff]")
CITATION = re.compile(r"\[\d+\]")
BANNED = ("系统提示", "属性面板", "签到", "经验值", "技能冷却", "见资料区", "本章小结")

MIN_HAN = 3800
MAX_HAN = 5200


def main():
    records = []
    issues = []
    for path in sorted(BODY.glob("*.md")):
        match = PATTERN.match(path.name)
        if not match:
            issues.append(f"文件名无法识别：{path.name}")
            continue
        n = int(match.group(1))
        text = path.read_text(encoding="utf-8")
        title, separator, body = text.partition("\n")
        if not separator or not title.startswith(f"# 第{n:03d}章"):
            issues.append(f"标题与文件名不一致：{path.name}")
        citations = CITATION.findall(body)
        if citations:
            issues.append(f"引用角标：第{n:03d}章 {citations}")
        for word in BANNED:
            if word in body:
                issues.append(f"出戏词：第{n:03d}章「{word}」")
        if re.search(r"^#+\s*(本章|写作|备注|进展)", body, flags=re.M):
            issues.append(f"章内出现工作性标题：第{n:03d}章")
        han = len(HAN.findall(body))
        records.append((n, path.name, han))
    if not records:
        print("没有找到正文文件", file=sys.stderr)
        return 1

    records.sort()
    counts = Counter(x[0] for x in records)
    for n in range(1, records[-1][0] + 1):
        if counts[n] != 1:
            issues.append(f"章节编号第{n:03d}章出现 {counts[n]} 次")

    print(f"章节：{len(records)}；范围：001—{records[-1][0]:03d}")
    print(f"正文汉字（不含标题）：{sum(r[2] for r in records):,}")
    short = [r for r in records if r[2] < MIN_HAN]
    long_ = [r for r in records if r[2] > MAX_HAN]
    print(f"不足{MIN_HAN}汉字：{len(short)}章（特殊章节允许较短，需在记忆区注明理由）")
    for n, _, han in short:
        print(f"  第{n:03d}章：{han}汉字")
    if long_:
        print(f"超过{MAX_HAN}汉字：{len(long_)}章（建议拆分或复核节奏）")
        for n, _, han in long_:
            print(f"  第{n:03d}章：{han}汉字")
    print(f"结构/角标/出戏词问题：{len(issues)}")
    for issue in issues:
        print("  " + issue)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
