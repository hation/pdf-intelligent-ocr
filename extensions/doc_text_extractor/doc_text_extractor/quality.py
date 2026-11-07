"""文本质量评分：评估提取文本的可用性，过滤乱码/内容过少的结果。"""

import os
import re

# 通用领域关键词（文档类内容的常见词），可被调用方覆盖
DEFAULT_KEYWORDS = [
    "公司", "产品", "市场", "行业", "数据", "分析", "服务", "用户",
    "系统", "项目", "技术", "内容", "研究", "报告", "问题", "需求",
    "方案", "业务", "团队", "计划", "结果", "时间", "工作", "信息",
    "the", "and", "of", "for", "with", "data", "report", "system",
]

# 乱码检测：5+ 个连续短字母词（如 "HHS ie ae ere CBE"），避免误伤英文正常句子
NOISE_PATTERN = re.compile(r"[A-Za-z]{1,4}(?:\s+[A-Za-z]{1,4}){4,}")
CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")
ALNUM_PATTERN = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]")


def _safe_basename(path):
    return os.path.splitext(os.path.basename(path))[0]


def score_text_quality(text, path=None, keywords=None):
    """对提取文本打分（0-100），越高表示内容越可信。

    参数：
        text: 待评估文本
        path: 源文件路径（可选，用于文件名关键词匹配加分）
        keywords: 领域关键词列表；None 用通用默认词表，[] 表示不启用关键词加分

    返回：
        dict: score / total_len / chinese_ratio / alnum_ratio / noise_ratio
              / keyword_hits / title_hits / line_count / avg_line_len
    """
    stripped = (text or "").strip()
    total_len = len(stripped)
    chinese_count = len(CHINESE_PATTERN.findall(stripped))
    alnum_count = len(ALNUM_PATTERN.findall(stripped))
    chinese_ratio = chinese_count / total_len if total_len else 0
    alnum_ratio = alnum_count / total_len if total_len else 0
    noise_matches = NOISE_PATTERN.findall(stripped)
    noise_len = sum(len(match) for match in noise_matches)
    noise_ratio = noise_len / total_len if total_len else 0

    kw = DEFAULT_KEYWORDS if keywords is None else keywords
    keyword_hits = sum(1 for word in kw if word.lower() in stripped.lower()) if kw else 0

    line_count = len([line for line in stripped.splitlines() if line.strip()])
    avg_line_len = total_len / line_count if line_count else 0

    title_hits = 0
    if path:
        title_tokens = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{2,}", _safe_basename(path))
        important_tokens = [token for token in title_tokens if len(token) >= 2]
        title_hits = sum(1 for token in important_tokens[:12] if token.lower() in stripped.lower())

    score = 0

    if total_len >= 1500:
        score += 25
    elif total_len >= 800:
        score += 20
    elif total_len >= 400:
        score += 12
    elif total_len >= 150:
        score += 5

    if chinese_ratio >= 0.45:
        score += 25
    elif chinese_ratio >= 0.3:
        score += 18
    elif chinese_ratio >= 0.18:
        score += 10
    elif chinese_ratio >= 0.08:
        score += 4

    if keyword_hits >= 8:
        score += 25
    elif keyword_hits >= 5:
        score += 18
    elif keyword_hits >= 3:
        score += 10
    elif keyword_hits >= 1:
        score += 4

    if title_hits >= 4:
        score += 15
    elif title_hits >= 2:
        score += 10
    elif title_hits >= 1:
        score += 5

    if alnum_ratio >= 0.55:
        score += 5

    if 12 <= avg_line_len <= 120:
        score += 5

    if noise_ratio > 0.3:
        score -= 25
    elif noise_ratio > 0.18:
        score -= 15
    elif noise_ratio > 0.1:
        score -= 8

    if total_len < 120:
        score -= 20

    score = max(0, min(100, score))

    return {
        "score": score,
        "total_len": total_len,
        "chinese_ratio": round(chinese_ratio, 4),
        "alnum_ratio": round(alnum_ratio, 4),
        "noise_ratio": round(noise_ratio, 4),
        "keyword_hits": keyword_hits,
        "title_hits": title_hits,
        "line_count": line_count,
        "avg_line_len": round(avg_line_len, 2),
    }
