#!/usr/bin/env python3
"""从 B 站合集生成 content.js（站点内容数据文件）。
用法: python3 gen_content.py
可配置: MID(UP主), SECTIONS(栏目→合集映射)
"""
import urllib.request, json, time, re

MID = "1156356486"

# 栏目定义: section_id -> (二级分组规则, 对应合集 season_id 或 None)
# 二级分组规则: (sub_id, sub_name, 标题前缀正则)
SEASONS = {
    "ai-vision": 4040679,        # 10分钟交付AI工业表面质检
}
FIXED_CARDS = []  # 非合集内容手动维护

GROUP_RULES = [  # (sub_id, name, 匹配正则, 组名(从标题中剔除))
    ("part1", "Part1: 概述",       r"【[^】]*】L1-", None),
    ("part2", "Part2: 检测软件",   r"【[^】]*】L2-", "质检生产软件"),
    ("part3", "Part3: AI软件",     r"【[^】]*】L3-", "质检AI软件"),
    ("part4", "Part4: 交付作业流程", r"【[^】]*】L4-", "交付作业流程"),
    ("part5", "Part5: 智能照明",   r"【[^】]*】L5-", "智能照明"),
    ("part6", "Part6: 质检套件",   r"【[^】]*】L6-", "质检套件"),
    ("cases", "实战案例",          r"【[^】]*】案例", None),
]

def api(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0",
        "Referer": "https://space.bilibili.com/"})
    return json.load(urllib.request.urlopen(req))

def fetch_season(season_id):
    out, pn = [], 1
    while True:
        d = api(f"https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid={MID}&season_id={season_id}&page_num={pn}&page_size=50")
        if d["code"] != 0:
            raise RuntimeError(f"API error {d['code']}: {d['message']}")
        out += d["data"]["archives"]
        if len(out) >= d["data"]["meta"]["total"]:
            return out
        pn += 1

def clean_title(t, group_name):
    t = re.sub(r"^【[^】]*】", "", t).strip()
    if group_name:
        t = t.replace(f"{group_name} - ", "").replace(f"{group_name}-", "").replace(group_name, "", 1)
    return t.strip(" -")

def jstr(s):
    return json.dumps(s, ensure_ascii=False)

# ---- 抓取并生成卡片 ----
cards = []
section_names = {}
subs_by_section = {}

for section_id, season_id in SEASONS.items():
    archives = fetch_season(season_id)
    sub_cards = {sid: [] for sid, *_ in GROUP_RULES}
    for a in archives:
        for sid, name, pat, gname in GROUP_RULES:
            if re.match(pat, a["title"]):
                sub_cards[sid].append(a)
                break
    used_subs = []
    for sid, name, pat, gname in GROUP_RULES:
        arr = sub_cards[sid]
        if not arr:
            continue
        used_subs.append({"id": sid, "name": name})
        arr.sort(key=lambda a: a["title"])
        for a in arr:
            cards.append({
                "section": section_id, "sub": sid, "type": "video",
                "bvid": a["bvid"], "title": clean_title(a["title"], gname),
                "pic": a["pic"].replace("http://", "https://"),
                "duration": a["duration"], "views": a["stat"]["view"],
                "date": time.strftime("%Y-%m-%d", time.localtime(a["pubdate"])),
            })
    subs_by_section[section_id] = used_subs

# ---- 拼装 JS ----
lines = []
lines.append("// ===== 站点内容数据（由 gen_content.py 自动生成，也可手动编辑） =====")
lines.append("const SITE_DATA = {")
lines.append(f"  owner: {{ name: \"ErnestCCC\", mid: {MID} }},")
lines.append("")
lines.append("  sections: [")

# ai-vision: 带二级分组
ai_subs = subs_by_section.get("ai-vision", [])
subs_js = ",\n        ".join(f'{{ id: "{s["id"]}", name: "{s["name"]}" }}' for s in ai_subs)
lines.append("    {")
lines.append('      id: "ai-vision", name: "AI工业视觉检测",')
lines.append("      subs: [")
lines.append("        " + subs_js)
lines.append("      ],")
lines.append("    },")
for sid, name in [("ai-productivity", "AI&生产力"), ("vlog", "生活VLOG"), ("reading", "读书笔记"), ("tech-blog", "科技博文")]:
    lines.append(f'    {{ id: "{sid}", name: "{name}" }},')
lines.append("  ],")
lines.append("")
lines.append("  cards: [")

def card_js(c):
    return ("    {\n"
            f"      section: \"{c['section']}\","
            + (f" sub: \"{c['sub']}\"," if c.get("sub") else "") + " type: \"video\",\n"
            f"      bvid: \"{c['bvid']}\",\n"
            f"      title: {jstr(c['title'])},\n"
            + (f"      desc: {jstr(c['desc'])},\n" if c.get("desc") else "")
            + f"      pic: \"{c['pic']}\",\n"
            f"      duration: {c['duration']}, views: {c['views']}, date: \"{c['date']}\",\n"
            "    },")

# AI&生产力 5 个（手动数据，保留）
AI_PRODUCTIVITY = [
    ("BV1Ebsb6VEad", "Harness 工程：Agent 优先世界的开发实践", "OpenAI 2026 年 2 月发布的《Harness engineering》解读：三人团队五个月写出约 100 万行代码，人工手写 0 行——当 agent 能写所有代码时，工程师干什么？", "https://i2.hdslb.com/bfs/archive/b9d9f205d04a0c7ed39704a7966160d219811a65.jpg", 799, 133, "2026-11-19"),
    ("BV1Wqsz6mEVv", "Anthropic Claude Code 初创公司指南", "基于 Anthropic 2026 年 8 月发布的《The Claude Code guide for startups》实践指南。", "https://i2.hdslb.com/bfs/archive/87253e952674ba4026cd810097885719479b1050.jpg", 438, 96, "2026-11-17"),
    ("BV193sA6fEbi", "AI 原生软件开发生命周期手册——ANTHROPIC官方手册", "《The AI-native SDLC playbook》解读：当 AI 写代码的速度不可思议，为什么交付还是那么慢？", "https://i2.hdslb.com/bfs/archive/9739e4c3aace68666bb5610771c7e77d0e859071.jpg", 506, 22, "2026-11-16"),
    ("BV1ycsn68EkP", "Anthropic 7x24在线Agent架构设计解析", "《Building Always-On Agents》架构解析：如何设计 7x24 小时在线的 Agent 系统。", "https://i0.hdslb.com/bfs/archive/23b15b1976642e96ee5105f40c243b20d558d501.jpg", 470, 138, "2026-11-15"),
    ("BV1Df9FBnEUF", "AI编程实践", "AI 编程实践分享，完整实录。", "https://i1.hdslb.com/bfs/archive/d0952aba281162116bde92db61758dea092cbc4e.jpg", 3924, 141, "2026-04-02"),
]
VLOG = [
    ("BV1vbpc6QENh", "秋季.山峦/索道.YORI.Lofi", "秋季：山峦与索道，配上 YORI 的 Lofi。", "https://i1.hdslb.com/bfs/archive/063414db79c2935cc56eb2bc7ecdf1a46449ecef.jpg", 441, 14, "2026-10-06"),
    ("BV1vCus6pEUk", "立秋.花花/果实.YURI.Lofi", "四季：从立夏到立秋。", "https://i0.hdslb.com/bfs/archive/34a17e3b3e3666dc6e1692eac999fda0857ec14e.jpg", 102, 15, "2026-08-07"),
    ("BV1oSRMBpEeq", "立夏.灰色/绿色.YURI.Lofi", "灰色退去，绿色登场～", "https://i2.hdslb.com/bfs/archive/c878aa1bdd0f60a63ec6749c2c3d959831ea24c7.jpg", 70, 22, "2026-05-05"),
    ("BV125BMBbEZm", "冬至·下雪·白噪音·鲁宾斯坦·夜曲", "黏黏乎乎的雨夹雪～", "https://i0.hdslb.com/bfs/archive/154816328368de30b09444784122af6eb44d6261.jpg", 186, 158, "2025-12-23"),
]
lines.append("    // ===== AI工业视觉检测（合集：10分钟交付AI工业表面质检） =====")
for c in cards:
    lines.append(card_js(c))
lines.append("")
lines.append("    // ===== AI&生产力 =====")
for bv, t, d, p, dur, v, date in AI_PRODUCTIVITY:
    lines.append(card_js({"section": "ai-productivity", "type": "video", "bvid": bv, "title": t, "desc": d, "pic": p, "duration": dur, "views": v, "date": date}))
lines.append("")
lines.append("    // ===== 生活VLOG（B站合集「四季」） =====")
for bv, t, d, p, dur, v, date in VLOG:
    lines.append(card_js({"section": "vlog", "type": "video", "bvid": bv, "title": t, "desc": d, "pic": p, "duration": dur, "views": v, "date": date}))
lines.append("")
lines.append("    // ===== 待填充：reading / tech-blog =====")
lines.append("  ],")
lines.append("};")

open("content.js", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"生成完成: ai-vision {len(cards)} 个视频, 分组: {[s['name'] for s in ai_subs]}")
