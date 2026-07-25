# 项目长期记忆 — UL_Portfolio

## 项目核心
申请 **University of Limerick MSc in Interaction and Experience Design** 的作品集项目。

主交付物：**AI Trust Layer** —— 企业 RAG 系统的"信任界面层"，用 Streamlit 实现的可运行原型。
设计定位：让非技术用户看懂、敢信、会用 AI 的回答。
核心差异化：三档置信度标签 + 低置信度警报 + 渐进式呈现 + Admin 监控闭环。

## 用户背景
- fansh，轨道交通弱电系统集成架构设计背景
- 设计偏好：留白克制、信息层级清晰、双语标签、精准小幅修改、强可回滚性
- 沟通风格：渐进式精确调整、低容忍过度解释

## 关键资产状态（截至 2026-07-25）
- ✅ PRD Step 1-6 文档链：完整闭合（见工作空间根目录的 `01_*.md` 到 `06_*.md`，及 `07_PRD_Step6_Portfolio_Scope.md`）
- ✅ 可运行代码：ai_trust_layer/ 全部 9 个模块 + 防弹演示模式（MOCK_LLM_MODE）
- ✅ 截图：10 张关键场景截图（screenshots/）
- ✅ 录屏：3 分钟 demo 视频（videos/）
- ✅ ardot 设计稿：P0 首页引导层 + 低置信度警报横幅重设计（file ID 707535023504113），从默认 Streamlit 升级到浅色 + 深蓝信任色 + Inter/IBM Plex Mono 企业 SaaS 调性
- ✅ P0 全部完成：首页引导层 + 高/中/低置信度结果页 pill/alert + 点击展开渐进式呈现 + Admin Dashboard eyebrow/CSS 圆点；已 git 锚定（`p0-baseline` 指向 `0550713`，P0 完成 `4e58cdf`）。
- ✅ P1 Admin Dashboard 三图完成（trust health trend line + confidence distribution donut + jargon term bar chart），在独立分支 `p1-admin-dashboard` 待用户确认合并；已进一步重设计为「图表 ↔ 原始数据」一一对应布局，并修复标题顶部溢出、趋势/表格上下满宽、章节标题层级、饼图居中、表格底部与饼图图例对齐、Verification 列绿/灰胶囊区分；最新版消除图表与表格冗余：饼图直接显示百分比+中心总数，柱状图保留数值标签，右侧改为 PRD 驱动的「解读/候选词库」卡。

## HCI 理论锚点（叙事必备）
- Progressive Disclosure（Nielsen Heuristic）
- Trust Calibration（Lee & See, 2004）
- Cognitive Load Theory（Sweller）
- Explainable AI（XAI Research）
- Human-in-the-Loop Systems

## Demo 锁定场景
- Scene 1：首页空状态
- Scene 2：高置信度（"What signaling system does Project XX use?"）
- Scene 3：低置信度警报（"What is the construction budget for YY Line?"）
- Scene 4：中置信度渐进式（"What are the technical parameters of ZDJ-200 switch machine?"）
- Scene 5：Admin Dashboard
- Scene 6：收尾

## 用户习惯约定
- 中文回复（默认）
- 增量式精确调整（不喜大批量重写）
- 强可回滚性要求（如"删除文字但保留图片"）
- 视觉稿需双语标注
- 局部微调优先于整体重做（用户在 ardot 编辑器手动微调，助手不主动大改已完成稿）

## 设计审美约束（2026-07-25 用户反馈提炼）
- **排版完整性**：副标题/单行文字避免单词单独成行断行（如 "matters." 单字成行破坏美感），整段需在一行内完整显示
- **对齐一致性**：同层级卡片/组件的边框大小、内边距、间距保持视觉一致
- **色彩克制**：每个页面/场景控制在 3 个颜色范围内；语义色 triplet（如置信度绿/橙/红）可作为功能图标点缀，但单场景主色不超 3 个
- **视觉权重清晰**：警报/提示类组件需有强烈视觉锚（色条/图标），避免像普通系统提示