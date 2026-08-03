# AI Trust Layer 交互原型 — 云端部署指南

> 本原型是**纯静态 HTML**（无后端、无需构建），已内联 CSS 并接入 Tailwind / Lucide CDN。只要上传到任意静态托管服务即可获得可访问的 URL，教授可直接在浏览器中交互。

## 快速交付物

- `pages/`：原始页面文件夹（Trae Design 工作目录使用）。
- `deploy/`：可直接上传的部署包，`index.html` 位于根目录，所有页面相对路径已配置好。
- `ai_trust_layer_web_prototype.design`：设计画布文件，已在 `.design` 中注册 8 个页面与交互连线。

## 推荐部署方式

### 方式一：Netlify Drop（最快，无需命令行）

1. 打开 [https://app.netlify.com/drop](https://app.netlify.com/drop)。
2. 将 `deploy/` 文件夹**整体拖拽**到网页中。
3. 等待几秒，Netlify 会生成一个随机域名（如 `https://illustrious-cupcake-123456.netlify.app`）。
4. 点击域名即可访问；可在 Netlify 后台设置自定义域名。

### 方式二：GitHub Pages（适合已有 GitHub 仓库）

1. 新建 GitHub 仓库，把 `deploy/` 内的所有文件（含 `index.html`）推送到仓库根目录。
2. 进入仓库 **Settings → Pages**。
3. Source 选择 **Deploy from a branch**，Branch 选择 `main / root`，保存。
4. 等待 1–2 分钟，访问 `https://<你的用户名>.github.io/<仓库名>`。

### 方式三：Vercel

1. 打开 [https://vercel.com/new](https://vercel.com/new)，导入 GitHub 仓库。
2. Framework Preset 选择 **Other**。
3. Root Directory 留空（即仓库根目录包含 `index.html`）。
4. 点击 Deploy，完成后复制 `*.vercel.app` 域名。

### 方式四：Cloudflare Pages

1. 打开 [https://dash.cloudflare.com](https://dash.cloudflare.com) → Pages → Create a project。
2. 上传 `deploy/` 文件夹。
3. 部署完成后获得 `*.pages.dev` 域名。

### 方式五：Surge.sh（命令行，适合快速临时链接）

```bash
npm install -g surge
surge deploy/
# 按提示注册/登录，选择域名即可
```

## 本地预览

在 `deploy/` 目录下运行任意静态服务器即可：

```bash
# Python
python -m http.server 8080

# Node.js
npx serve .

# PowerShell
# 用浏览器直接打开 index.html 亦可
```

然后访问 `http://localhost:8080`。

## 页面结构说明

| 页面 | 用途 |
|------|------|
| `index.html` | 项目介绍：问题、设计原则、MVP 功能 |
| `prototype-idle.html` | 交互原型入口 / 空闲态 |
| `prototype-loading.html` | 加载中状态（渐进加载 N1） |
| `prototype-high.html` | 高置信度结果 + PRD 边栏 |
| `prototype-medium.html` | 中置信度结果（来源默认展开） |
| `prototype-low.html` | 低置信度结果 + 非忽略警报 |
| `prototype-document.html` | 模拟文档视图（F1 来源追溯） |
| `prototype-admin.html` | 管理后台（F7 Trust Health） |

所有原型页面左侧为交互界面，右侧为 **PRD 设计理念边栏**，点击边栏卡片可跳转到对应状态页面，实现「设计 rationale + 交互原型」双向链接。

## 注意事项

1. **必须联网**：页面使用 `cdn.jsdelivr.net` 和 `unpkg.com` 加载 Tailwind CSS 与 Lucide 图标，离线环境图标/样式可能无法显示。
2. **无需 API Key**：本原型为纯前端交互演示，不涉及后端 LLM 调用。
3. **部署根目录**：请上传 `deploy/` 文件夹**内的内容**，不要把 `deploy/` 本身作为根目录，否则相对路径会多一层。
4. **自定义域名**：Netlify / Vercel / Cloudflare / GitHub Pages 均支持自定义域名，按各自后台指引设置即可。

## 验证状态

- `validate-design-workspace.mjs`：✅ 通过
- `validate-finish-readiness.mjs --check=all`：✅ 通过
