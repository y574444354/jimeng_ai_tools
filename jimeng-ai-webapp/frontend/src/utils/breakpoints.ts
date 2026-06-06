/**
 * 断点常量系统
 *
 * 与 src/styles/global.css 中的 @media 查询保持严格同步。
 * CSS 端无法引用 JS 常量（纯 CSS 方案的限制），采用"文档注释 + 人工同步"策略：
 *   - 本文件是断点值的唯一权威来源（Single Source of Truth）
 *   - global.css 中每个 @media 断点处标注对应的常量名
 *   - 修改断点时，必须同时修改本文件和 global.css
 *
 * 断点策略：以 max-width 上限值为标准（参考 ADR-002）
 */

/** 像素断点值（max-width 上限值策略） */
export const BREAKPOINTS = {
  /** 移动端最大宽度（≤ 此值视为移动端） */
  MOBILE: 767,
  /** 平板端起始宽度 */
  TABLET_MIN: 768,
  /** 平板端结束宽度 */
  TABLET: 1023,
} as const

/** 预编译的 CSS media query 字符串，供 useMediaQuery 使用 */
export const MEDIA_QUERIES = {
  /** 匹配移动端：max-width: 767px */
  MOBILE: `(max-width: ${BREAKPOINTS.MOBILE}px)`,
  /** 匹配平板端：768px ≤ width ≤ 1023px */
  TABLET: `(min-width: ${BREAKPOINTS.TABLET_MIN}px) and (max-width: ${BREAKPOINTS.TABLET}px)`,
  /** 匹配桌面端：width ≥ 1024px */
  DESKTOP: `(min-width: ${BREAKPOINTS.TABLET + 1}px)`,
  /** 匹配平板及以下：width ≤ 1023px */
  TABLET_DOWN: `(max-width: ${BREAKPOINTS.TABLET}px)`,
} as const

export type BreakpointName = 'mobile' | 'tablet' | 'desktop'
