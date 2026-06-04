# 响应式设计规范

> 雪桥AI 前端响应式自适应系统规范 — 支持桌面端、平板端、移动端。

---

## 断点系统

| 断点 | 宽度范围 | 目标设备 |
|------|----------|----------|
| `--bp-desktop` | > 1024px | 桌面显示器 |
| `--bp-tablet` | 768px - 1024px | iPad / 平板横屏 |
| `--bp-mobile` | < 768px | 手机竖屏/横屏 |

```css
/* 移动端优先的媒体查询写法 */
@media (max-width: 767px) { /* 手机端样式 */ }
@media (min-width: 768px) and (max-width: 1023px) { /* 平板端样式 */ }
@media (min-width: 1024px) { /* 桌面端增强 */ }
```

## 布局模式

### 侧边栏

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| **expanded** | 桌面端默认 | 完整侧边栏，232px 宽，显示图标+文字 |
| **collapsed** | 平板端自动 / 桌面端手动 | 仅显示图标，68px 宽 |
| **overlay** | 移动端 | 隐藏，汉堡按钮触发覆盖层，带半透明遮罩 |

### 内容区

- 桌面端：`padding: 28px`，左侧留出侧边栏宽度
- 平板端：`padding: 20px`
- 移动端：`padding: 16px`，全宽，侧边栏为 overlay

### 表单布局

- 桌面端：多列 `el-row` + `el-col`
- 平板端：2列或自适应
- 移动端：单列堆叠，`el-col` 默认 `span="24"`

## CSS 变量（响应式覆盖）

```css
:root {
  --sidebar-width: 232px;
  --sidebar-collapsed: 68px;
  --content-padding: 28px;
  --content-padding-tablet: 20px;
  --content-padding-mobile: 16px;
}

@media (max-width: 1023px) {
  :root {
    --sidebar-width: 68px;  /* 平板自动折叠 */
    --content-padding: 20px;
  }
}

@media (max-width: 767px) {
  :root {
    --sidebar-width: 0;     /* 移动端隐藏 */
    --content-padding: 16px;
  }
}
```

## 移动端导航

- 汉堡按钮位于 header 左侧（仅移动端显示）
- 点击展开侧边栏 overlay，带 `position: fixed` + `z-index: 200`
- 遮罩层 `z-index: 190`，点击关闭侧边栏
- 侧边栏展开时禁止 body 滚动

## 组件响应式规则

### 表格 / 列表
- 移动端：表格横向滚动或卡片化
- `el-table` 添加 `:scrollable` 或使用 CSS `overflow-x: auto`

### 弹窗
- 移动端：`width: 90vw`，最大高度 80vh 可滚动
- `el-dialog` 使用百分比宽度

### 图片网格
- 桌面端：3-4 列
- 平板端：2-3 列
- 移动端：1-2 列

## 触摸优化

- 所有可点击元素最小触摸区域 44x44px
- 按钮间距在移动端增加至 12px
- 表单输入框在移动端使用 `size="large"`

## 实现清单

| 文件 | 改动内容 |
|------|----------|
| `styles/global.css` | 添加响应式变量、工具类、动画 |
| `layouts/MainLayout.vue` | 汉堡菜单、overlay侧边栏、响应式header |
| `stores/app.ts` | isMobile, isTablet, sidebarMode 状态 |
| `views/*.vue` (12个) | 响应式样式适配 |
| `components/*.vue` (8个) | 弹窗/卡片响应式 |
