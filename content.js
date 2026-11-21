// ===== 站点内容数据（发内容只改这个文件） =====
// 卡片类型：video（B站视频）。以后可扩展：article / book / project 等。
// section: 对应导航栏目 id；sub: AI工业视觉检测下的 Part 分组（可选）
const SITE_DATA = {
  owner: { name: "ErnestCCC", mid: 1156356486 },

  sections: [
    {
      id: "ai-vision", name: "AI工业视觉检测",
      subs: [
        { id: "part1", name: "Part1: 概述" },
        { id: "part2", name: "Part2: 检测软件" },
        { id: "part3", name: "Part3: AI软件" },
      ],
    },
    { id: "ai-productivity", name: "AI&生产力" },
    { id: "vlog", name: "生活VLOG" },
    { id: "reading", name: "读书笔记" },
    { id: "tech-blog", name: "科技博文" },
  ],

  cards: [
    // ===== AI&生产力 =====
    {
      section: "ai-productivity", type: "video",
      bvid: "BV1Ebsb6VEad",
      title: "Harness 工程：Agent 优先世界的开发实践",
      desc: "OpenAI 2026 年 2 月发布的《Harness engineering: leveraging Codex in an agent-first world》解读：三名工程师从空仓库起步，五个月写出约 100 万行代码，人工手写 0 行——当 agent 能写所有代码时，工程师干什么？",
      pic: "https://i2.hdslb.com/bfs/archive/b9d9f205d04a0c7ed39704a7966160d219811a65.jpg",
      duration: 799, views: 133, date: "2026-11-19",
    },
    {
      section: "ai-productivity", type: "video",
      bvid: "BV1Wqsz6mEVv",
      title: "Anthropic Claude Code 初创公司指南",
      desc: "基于 Anthropic 2026 年 8 月发布的《The Claude Code guide for startups》：采访十几家高速增长的初创公司后的实践指南。",
      pic: "https://i2.hdslb.com/bfs/archive/87253e952674ba4026cd810097885719479b1050.jpg",
      duration: 438, views: 96, date: "2026-11-17",
    },
    {
      section: "ai-productivity", type: "video",
      bvid: "BV193sA6fEbi",
      title: "AI 原生软件开发生命周期手册——ANTHROPIC官方手册",
      desc: "《The AI-native SDLC playbook》解读：当 AI 写代码的速度不可思议，为什么交付还是那么慢？瓶颈早已不在写代码，而在代码周围的人类环节。",
      pic: "https://i2.hdslb.com/bfs/archive/9739e4c3aace68666bb5610771c7e77d0e859071.jpg",
      duration: 506, views: 22, date: "2026-11-16",
    },
    {
      section: "ai-productivity", type: "video",
      bvid: "BV1ycsn68EkP",
      title: "Anthropic 7x24在线Agent架构设计解析",
      desc: "《Building Always-On Agents》架构解析：如何设计 7x24 小时在线的 Agent 系统。",
      pic: "https://i0.hdslb.com/bfs/archive/23b15b1976642e96ee5105f40c243b20d558d501.jpg",
      duration: 470, views: 138, date: "2026-11-15",
    },
    {
      section: "ai-productivity", type: "video",
      bvid: "BV1Df9FBnEUF",
      title: "AI编程实践",
      desc: "AI 编程实践分享，完整实录。",
      pic: "https://i1.hdslb.com/bfs/archive/d0952aba281162116bde92db61758dea092cbc4e.jpg",
      duration: 3924, views: 141, date: "2026-04-02",
    },

    // ===== 其他栏目：待填充（content 就绪后在此追加，section 对应导航 id） =====
  ],
};
