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

OPUS_ARTICLES = {
 "books": [
  {
   "title": "《稀缺：我们是如何陷入贫穷与忙碌的》26",
   "url": "https://www.bilibili.com/read/cv44869278",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/5e76fcb41533a6fc67779808fe8cfbda1156356486.jpg",
   "date": "2026-01-17",
   "views": 46,
   "likes": 0,
   "words": 11926,
   "desc": "《稀缺：我们是如何陷入贫穷与忙碌的》 一、稀缺的核心定义：稀缺俘获大脑 稀缺造成的后果不仅仅是因为我们会因拥有的太少而感到不悦，而是因为它会改变我们的思维方式，会强行侵入我们的思想之中。 稀缺会俘获大脑。就像饥饿的研究对",
   "is_book": True
  },
  {
   "title": "《一人企业》25",
   "url": "https://www.bilibili.com/read/cv44040961",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/508196a609816ef7393132b53fea24301156356486.jpg",
   "date": "2025-12-06",
   "views": 29,
   "likes": 0,
   "words": 15418,
   "desc": "一人企业是一种新颖的经营方法，专注于变得更好而不是更大，维持小规模进而带来自由。每个人都应该成为自己的CEO，一人企业是每个人在新的科技条件下的商业新模式。选好自己的商业模式，一个人负责。保持小规模，保持变好，而非盲目扩",
   "is_book": True
  },
  {
   "title": "《Ego Is The Enemy》25",
   "url": "https://www.bilibili.com/read/cv42959095",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/590ccd0b206d851d005f97bd8689943d1156356486.jpg",
   "date": "2025-09-07",
   "views": 48,
   "likes": 0,
   "words": 5661,
   "desc": "一般常说的自我，意义则更浅显：对自己价值的盲信。盲目的自大，自私的野心。本书所探讨的自我，就将使用这一定义。 如果自我像一个缠绕在耳边的声音，不断让我们相信自己比现实更优秀，那它也就使我们和真正的成就背道而驰了，因为它阻",
   "is_book": True
  },
  {
   "title": "《极早退休》25",
   "url": "https://www.bilibili.com/read/cv42013924",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/a07572a37b41d053e238efdca17d150d1156356486.jpg",
   "date": "2025-06-15",
   "views": 52,
   "likes": 2,
   "words": 14957,
   "desc": "我在这里要描述的是另一种生活，一个独立的、富有的和拥有广泛技能的人的生活——一个现代文艺复兴人。 我们当前的世界 对“系统”或“那些人”的失望的抱怨不断。“系统”是比喻那些在奴隶后面走来走去的人，他们让奴隶们继续前进。然",
   "is_book": True
  },
  {
   "title": "《拉新：快速实现用户增长》25",
   "url": "https://www.bilibili.com/read/cv41859043",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/031ad3ad60935e4d7bd75f96a013c4241156356486.jpg",
   "date": "2025-05-31",
   "views": 62,
   "likes": 0,
   "words": 25115,
   "desc": "第1 部分 运营的基础是用户持续增长 对用户增长的追求是运营的核心目标。从投入运营的初期阶段到快速成长期，再到稳定的成熟阶段，拉新贯穿了产品的整个生命周期。拉新做不好，产品就缺乏用户；没有用户，再精致完美的产品都毫无意义",
   "is_book": True
  },
  {
   "title": "《5000天后的世界》25",
   "url": "https://www.bilibili.com/read/cv41795970",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/478ba0c66848ac13f164229598c853f11156356486.jpg",
   "date": "2025-05-25",
   "views": 40,
   "likes": 0,
   "words": 15350,
   "desc": "镜像世界带来的大变革：数百万人一起工作的未来 在未来的 50 年里，AI 将成为可以与自动化和产业革命相提并论的，不，应该是影响更为深远的趋势。 受益于 AI 这类科技的高度发展，未来人们的工作方式势必出现巨大的变化。在",
   "is_book": True
  },
  {
   "title": "《如何开发一个好产品》25",
   "url": "https://www.bilibili.com/read/cv41781754",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/8cae4c2e402321c574a6574d0c411c041156356486.jpg",
   "date": "2025-05-23",
   "views": 43,
   "likes": 0,
   "words": 17213,
   "desc": "我发现遭遇失败的产品有一个普遍模式，而导致产品失败的根本原因就是它们无法比其他替代品更好地满足客户所需。这就是 “产品 - 市场适配性”（Product-Market Fit）这一概念的精髓。 我所说的产品 - 市场适配",
   "is_book": True
  },
  {
   "title": "《模块时代》25",
   "url": "https://www.bilibili.com/read/cv41707711",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/f2363e8921048f5f248a0d6ecc20d3ab1156356486.jpg",
   "date": "2025-05-17",
   "views": 48,
   "likes": 0,
   "words": 9350,
   "desc": "一、基础信息库（元数据整理） 1. 作者档案 青木昌彦（Masahiko Aoki） 学术背景：斯坦福大学经济学教授、日本经济产业研究所（RIETI）创始人，日本学士院会员。研究领域涵盖比较制度分析、信息经济学与产业组织",
   "is_book": True
  },
  {
   "title": "《史记的读法》25",
   "url": "https://www.bilibili.com/read/cv41628484",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/f7dbfdf5dad101db997d914a0ff0b3101156356486.jpg",
   "date": "2025-05-11",
   "views": 49,
   "likes": 1,
   "words": 3706,
   "desc": "司马迁的历史态度 我们今天要读《史记》，首先会遇到两个问题：为什么读？用什么方式读？ 和所有中国传统经典一样，《史记》是在与我们不一样的环境及时代中产生的。经典最简单的定义是 “经过时间淘洗后存留下来的古书”，久远之前的",
   "is_book": True
  },
  {
   "title": "从0到1",
   "url": "https://www.bilibili.com/read/cv41250794",
   "pic": "https://i0.hdslb.com/bfs/article/c44f5938e14215d07611045935d436311156356486.jpg",
   "date": "2025-04-06",
   "views": 42,
   "likes": 0,
   "words": 7925,
   "desc": "未来只是还没有到来的时刻的集合。但是真正使未来如此独特和重要的并非因为未来没有发生，而是未来的世界会与此刻不同。这样看来，如果我们的社会在之后 100 年都没有发生变化，那未来就在 100 多年之后。如果在之后 10 年",
   "is_book": True
  },
  {
   "title": "零售的哲学",
   "url": "https://www.bilibili.com/read/cv41250782",
   "pic": "https://i0.hdslb.com/bfs/article/33e76f725e80e934cd27009929d820ce1156356486.jpg",
   "date": "2025-04-06",
   "views": 31,
   "likes": 0,
   "words": 1566,
   "desc": "关键点在于从变化预测未来，环环相扣地思索应对变化的方法，如此循环往复才会萌发新的商机。 从变化中读懂 “未来”，建立 “假设” 然后 “执行”，再对结果进行 “验证”。这一过程有助于优化工作模式 —— 如果在平日的工作中",
   "is_book": True
  },
  {
   "title": "《启示录：打造用户喜爱的产品》25",
   "url": "https://www.bilibili.com/read/cv41099491",
   "pic": "https://i0.hdslb.com/bfs/article/af22b74c0e2a298c826e65ab6f4163c41156356486.jpg",
   "date": "2025-03-23",
   "views": 134,
   "likes": 0,
   "words": 19709,
   "desc": "我们汲取了深刻教训：如果开发的产品没有市场价值，那么无论开发团队多么优秀也无济于事。不仅如此，我们认识到仅仅做出产品并不够，还要确认产品是有价值的、可用的、可行的。 从担任网景高级产品经理开始，我的日常工作明确分为三块：",
   "is_book": True
  },
  {
   "title": "《精益创业实战第2版》25",
   "url": "https://www.bilibili.com/read/cv40934341",
   "pic": "https://i0.hdslb.com/bfs/article/92d932c55f75b73dfad566fdfc0e00e41156356486.jpg",
   "date": "2025-03-08",
   "views": 35,
   "likes": 0,
   "words": 5859,
   "desc": "我们要解决的主要问题就不是 “能不能把产品做出来”，而是 “该不该把产品做出来”。 一家创业公司之所以能成功，并不一定是因为最初的方案（我们称之为 A 计划）制订得好，更重要的是在资源耗尽之前找到了一个真正可行的方案。 ",
   "is_book": True
  },
  {
   "title": "精益创业：新创企业的成长思维",
   "url": "https://www.bilibili.com/read/cv40868577",
   "pic": "https://i0.hdslb.com/bfs/article/66551a3b2e9e6765009b5357c59ce8231156356486.jpg",
   "date": "2025-03-02",
   "views": 62,
   "likes": 0,
   "words": 14849,
   "desc": "埃里克的《精益创业》作了一个优秀的提炼：目标顾客 — 小范围实验 — 反馈修改 — 产品迭代 — 获得核心认知 — 高速增长。 创业的第一阶段是把想法变成产品。这时开发的产品是精简的原型，投入最少的金钱和精力开发出体现核",
   "is_book": True
  },
  {
   "title": "《以终为始：诱发行为改变的产品设计》25",
   "url": "https://www.bilibili.com/read/cv40797735",
   "pic": "https://i0.hdslb.com/bfs/article/068a0bd071697e7e89ab935d0a6851801156356486.jpg",
   "date": "2025-02-23",
   "views": 32,
   "likes": 0,
   "words": 8830,
   "desc": " [图片] 人是天生的行为科学家。从第一声啼哭开始，我们就能通过施加压力来影响他人的行为了——婴儿大哭，人们就会喂他吃东西；婴儿哼哼，人们就会抱着他哄。我们也会受到影响来自他人的压力的影响。通过与他人、与环境的无数次微妙",
   "is_book": True
  },
  {
   "title": "《重来：更为简单有效的商业思维》25",
   "url": "https://www.bilibili.com/read/cv40715364",
   "pic": "https://i0.hdslb.com/bfs/article/8edb1830cd41b2d6733a3181dc6babdb1156356486.jpg",
   "date": "2025-02-15",
   "views": 48,
   "likes": 0,
   "words": 7959,
   "desc": "我们刻意把自己做成一家小公司，只为小企业和小团队开发软件，帮助他们更轻松地完成工作。 卸下负担 哪来的从错误中学习？ 相比之下，你更应该从成功中汲取养分。成功才是真正靠得住的教材。做成一件事后，你会知道这条路行得通 ——",
   "is_book": True
  },
  {
   "title": "《不会被机器替代的人》25",
   "url": "https://www.bilibili.com/read/cv40670068",
   "pic": "https://i0.hdslb.com/bfs/article/a21faf89fbb46ba1468e0d0634a938851156356486.jpg",
   "date": "2025-02-11",
   "views": 24,
   "likes": 1,
   "words": 6146,
   "desc": "我们将会寻找什么样的工作 计算机的发展不同于世界上任何其他事物，超越了自然成长速度。 两百多年来，科技一直在改变劳动的性质和特定技能的价值。到目前为止，故事中仅有三个大的转折点。 最初，工业革命的崛起使完全凭手艺制作产品",
   "is_book": True
  },
  {
   "title": "《我看见的世界》25",
   "url": "https://www.bilibili.com/read/cv40657619",
   "pic": "https://i0.hdslb.com/bfs/article/d62412b705d8f134755ac9522c440dea1156356486.jpg",
   "date": "2025-02-10",
   "views": 47,
   "likes": 1,
   "words": 5654,
   "desc": " 《我看见的世界》既是李飞飞的个人史，也是一部波澜壮阔、跌宕起伏的人工智能发展史。 以人文本的人工智能 在科学和工业领域，推动人工智能发展的动机是什么，这个问题非常重要。我认为这个动机必须明确地以人为本。 我相信人类文明",
   "is_book": True
  },
  {
   "title": "《How Big Things Get Done》",
   "url": "https://www.bilibili.com/read/cv40624809",
   "pic": "https://i0.hdslb.com/bfs/article/af0fda04bd1c6b5889b479c207afb64a1156356486.jpg",
   "date": "2025-02-07",
   "views": 51,
   "likes": 1,
   "words": 9931,
   "desc": "成功的项目都是相似的，失败的项目也都是相似的。这里面有规律。 谋定而后动 傅以斌总结失败项目的一般规律是“快思考，慢行动”。项目刚上马的时候大家都兴高采烈，一旦做起来才发现遇到各种没想到的问题，进展很慢；然后因为进展慢，",
   "is_book": True
  },
  {
   "title": "《英伟达之道》",
   "url": "https://www.bilibili.com/read/cv40614603",
   "pic": "https://i0.hdslb.com/bfs/article/7a7cb11b7def4cff36f50fffc3a3c5031156356486.jpg",
   "date": "2025-02-06",
   "views": 119,
   "likes": 1,
   "words": 5790,
   "desc": "1.“第二名就是第一个失败者”，传达出公司目标和期待是每次都要赢，体现了强烈的竞争意识和追求卓越、争第一的理念。 2.“快速迭代，更大视野”，强调优先处理可操作事项，尽最大努力完成最重要的第一项任务，突出了高效执行和聚焦",
   "is_book": True
  }
 ],
 "techs": [
  {
   "title": "为即将消失的世界培养人—— 学校正在被两头拆开",
   "url": "https://www.bilibili.com/read/cv53183201",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/c8738c1deb2dd787b9945b47318705cb1156356486.png",
   "date": "2026-09-26",
   "views": 21,
   "likes": 0,
   "words": 6632,
   "desc": "[图片] \"Everything that we've built to train you was built for a world that is soon to no longer exist.\" —— Ben ",
   "is_book": False
  },
  {
   "title": "手工编程的黄昏：从“手艺人”到“代理人”的范式转移",
   "url": "https://www.bilibili.com/read/cv52719086",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/dd31c127b9dccaaeacb3cf4028ce68481156356486.png",
   "date": "2026-08-28",
   "views": 15,
   "likes": 0,
   "words": 2409,
   "desc": "当一位拥有25年经验、曾痴迷于优美代码的顶级程序员，宣布自己已三个月没写过一行代码，并宣称手工编程的经济价值即将归零时，我们听到的，不是一个预言，而是一声宣判。 在《Lex Fridman Podcast》第501期中，",
   "is_book": False
  },
  {
   "title": "半导体与工业视觉图像异常检测研究综述",
   "url": "https://www.bilibili.com/read/cv52688520",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/aa07badaefafb6aeab4c290968646f111156356486.png",
   "date": "2026-08-27",
   "views": 5,
   "likes": 0,
   "words": 10453,
   "desc": "整理日期：2026-08-27 [图片] 随着集成电路（IC）制造工艺节点持续微缩、产线自动化程度不断提高，自动缺陷检测与分类（Automatic Defect Classification, ADC）已成为保证良率的关",
   "is_book": False
  },
  {
   "title": "独舞者的重工业：AI时代“一人公司”的幻象与真实",
   "url": "https://www.bilibili.com/read/cv44920299",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/7f4aad6261857b24a619fdaf64e7263c1156356486.jpg",
   "date": "2026-01-20",
   "views": 79,
   "likes": 0,
   "words": 3249,
   "desc": "独舞者的重工业：AI时代“一人公司”的幻象与真实 清晨六点，上海的SoloNest共享办公空间里已亮起几盏灯。年轻的创业者们对着屏幕，低声与AI智能体进行着当日工作的第一轮对话。隔壁工位，一位独立设计师正指挥着“赛博团队",
   "is_book": False
  },
  {
   "title": "工业AI应用与挑战2025",
   "url": "https://www.bilibili.com/read/cv41969089",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/f99e0bc70dc89932a7a064049b1edf121156356486.jpg",
   "date": "2025-06-11",
   "views": 110,
   "likes": 0,
   "words": 4895,
   "desc": "工业 AI，是 AI 技术在工业领域的应用，它通过机器学习、深度学习、计算机视觉等先进的计算智能方法，实现对工业生产过程的优化和智能化，最终帮助企业提高生产效率、降低成本、提升产品质量，实现数字化转型。 Gartner ",
   "is_book": False
  },
  {
   "title": "Mary Meeker 2025 年 AI 趋势报告深度总结：浪潮之下的机遇与挑",
   "url": "https://www.bilibili.com/read/cv41937245",
   "pic": "https://i0.hdslb.com/bfs/new_dyn/731d83f6638b3506d1d547a8f2b9e54b1156356486.jpg",
   "date": "2025-06-08",
   "views": 50,
   "likes": 0,
   "words": 2956,
   "desc": "Mary Meeker 2025 年 AI 趋势报告深度总结：浪潮之下的机遇与挑战 一、AI 主流化加速：从技术前沿到社会核心的颠覆性渗透 用户与市场的爆发式增长 ChatGPT 现象级扩张：作为 AI 普及的 “风向标",
   "is_book": False
  },
  {
   "title": "人工智能在制造业中的现状、机遇与挑战",
   "url": "https://www.bilibili.com/read/cv40822600",
   "pic": "https://i0.hdslb.com/bfs/article/7e2d1477910d62326339a4fd6899e9f31156356486.jpg",
   "date": "2025-02-25",
   "views": 63,
   "likes": 0,
   "words": 2491,
   "desc": "一、引言 制造业作为国民经济的支柱产业，正处于转型升级的关键时期。人工智能技术的快速发展为制造业带来了新的契机，二者的融合已成为推动制造业高质量发展的重要力量。深入探究人工智能在制造业中的现状、机遇与挑战，对推动制造业智",
   "is_book": False
  },
  {
   "title": "工业大模型的机遇与挑战",
   "url": "https://www.bilibili.com/read/cv40612290",
   "pic": "https://i0.hdslb.com/bfs/article/0eb5c41d388c08e02a1a0f03c171e2461156356486.jpg",
   "date": "2025-02-06",
   "views": 71,
   "likes": 2,
   "words": 7203,
   "desc": "工业大模型应用趋势 当前，新型工业化基础设施正发生深刻变革，在工业领域加快大模型技术应用与落地，将充分激活新连接与新算力底座能力，升级智能化全栈能力新平台，为做强做优做大新型工业化、建设现代化产业体系提供核心助力。 在工",
   "is_book": False
  }
 ]
}


GROUP_RULES = [  # (sub_id, name, 匹配正则, 组名(从标题中剔除))
    ("part1", "Part1: 概述",       r"【[^】]*】L1-", None),
    ("part2", "Part2: 检测软件",   r"【[^】]*】L2-", "质检生产软件"),
    ("part3", "Part3: AI软件",     r"【[^】]*】L3-", "质检AI软件"),
    ("part4", "Part4: 交付作业流程", r"【[^】]*】L4-", "交付作业流程"),
    ("part5", "Part5: 智能照明",   r"【[^】]*】L5-", "智能照明"),
    ("part6", "Part6: 质检套件",   r"【[^】]*】L6-", "质检套件"),
    ("cases", "Part7: 实战案例",       r"【[^】]*】案例", None),
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
        def lesson_key(a):
            t = a["title"]
            m = re.search(r"L(\d+)-(\d+)", t)
            if m:
                return (int(m.group(1)), int(m.group(2)), t)
            m = re.search(r"案例(\d+)", t)
            if m:
                return (100, int(m.group(1)), t)
            return (200, 0, t)
        arr.sort(key=lesson_key)
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
lines.append('      id: "ai-vision", name: "AI工业视觉感知",')
lines.append("      subs: [")
lines.append("        " + subs_js)
lines.append("      ],")
lines.append("    },")
for sid, name in [("ai-productivity", "AI&生产力"), ("vlog", "浮生闲趣"), ("reading", "读书笔记"), ("tech-blog", "科技博文")]:
    lines.append(f'    {{ id: "{sid}", name: "{name}" }},')
lines.append("  ],")
lines.append("")
lines.append("  cards: [")


def article_card_js(a):
    return ("    {\n"
            f"      section: \"{a['section']}\", type: \"article\",\n"
            f"      title: {jstr(a['title'])},\n"
            f"      url: \"{a['url']}\",\n"
            + (f"      pic: \"{a['pic']}\",\n" if a.get("pic") else "")
            + (f"      desc: {jstr(a['desc'])},\n" if a.get("desc") else "")
            + f"      words: {a.get('words',0)}, views: {a.get('views',0)}, likes: {a.get('likes',0)}, date: \"{a['date']}\",\n"
            "    },")

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
lines.append("    // ===== 读书笔记（B站图文） =====")
for a in OPUS_ARTICLES["books"]:
    lines.append(article_card_js({**a, "section": "reading"}))
lines.append("")
lines.append("    // ===== 科技博文（B站图文） =====")
for a in OPUS_ARTICLES["techs"]:
    lines.append(article_card_js({**a, "section": "tech-blog"}))
lines.append("  ],")
lines.append("};")

open("content.js", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"生成完成: ai-vision {len(cards)} 个视频, 分组: {[s['name'] for s in ai_subs]}")
