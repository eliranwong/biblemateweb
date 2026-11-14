# 测试与原型

本项目没有统一的测试运行器。`tests/` 存放了用于原型设计或演示功能的独立脚本（标签页、同步滚动、右键菜单、工具提示、索引、笔记、搜索模式、订阅后端、API 客户端等）。您可以直接运行其中一个脚本：

```bash
python tests/api_client.py
```

其中许多是 NiceGUI 示例：运行脚本并打开输出显示的 URL。`tests/sync_scrolling.md` 说明了同步滚动的架构设计（[用户视角](../integrations/synchronised_windows.md)）。

发布前的手动检查：启动 `biblemateweb`、打开圣经／工具标签页、在每种模式下执行经文搜索、尝试 [API](../integrations/rest_api.md)，并测试移动端版面。
