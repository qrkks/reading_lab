# Reading Lab

这里收集了一些数学与统计学读书笔记。仓库推送到 `main` 后，GitHub Actions 会自动运行 Quarto，把各本书渲染成 HTML 并发布到 GitHub Pages。

在线入口：

- [Reading Lab 首页](https://qrkks.github.io/reading_lab/)

GitHub Pages 的 HTML 默认参数放在 `_quarto-html.yml`。本地渲染各本书时不会自动读取它；workflow 发布网页时会把它临时作为 `_metadata.yml` 注入到每本书的渲染目录。

如果这些链接暂时打不开，需要先在 GitHub 仓库的 `Settings -> Pages` 里把发布源设为 `GitHub Actions`，然后等待一次 workflow 跑完。
