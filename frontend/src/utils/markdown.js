import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css' // 🏆 推荐使用深色主题，更有科技感

const md = new MarkdownIt({
  html: true, // 允许 HTML 标签
  linkify: true, // 自动将 URL 转为链接
  typographer: true, //排版优化
  highlight: function (str, lang) {
    // 🏆 核心：代码高亮逻辑
    if (lang && hljs.getLanguage(lang)) {
      try {
        return (
          '<pre class="hljs"><code>' +
          hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
          '</code></pre>'
        )
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>'
  },
})

export const renderMarkdown = (content) => {
  return md.render(content || '')
}
