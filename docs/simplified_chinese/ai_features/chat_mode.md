# 对话模式

针对圣经相关问题的对话式助手：涵盖经文、历史背景、专题探讨等丰富内容。

## 开启

- **AI** 菜单 → `对话模式`
- 右键点击经文或章节 → `问 BibleMate`（[指南](ask_biblemate.md)），即可自动预填您的问题。

## 使用方法

1. 在文本框中输入您的需求。
2. 点击 **发送** 或按下 **Ctrl+S**（macOS 为 **Cmd+S**）。
3. 回答会以格式化文本的形式实时流式显示。系统会记录每个回合的对话，方便您提出后续问题。
4. 当任务运行时，发送按钮会变为 **停止**；确认后即可取消运行。

## 处理流程

根据输入框下方的复选框设置，每个请求会依序经过：

1. [优化用户要求](prompt_engineering.md)（`优化`）– 选填
2. [选择工具](chat_tool_selection.md)（`工具`）– 选填
3. 回复生成，可选配[代理](chat_agent_option.md)选项
4. [审查](chat_review.md)节点 – 选填

## 控件

| 控件 | 用途 |
|---|---|
| 自动滚动 | 随着流式输出自动向下滚动 (`auto_scroll`) |
| 优化 | `prompt_engineering`（默认开启） |
| 代理 | `use_agent`（默认开启） |
| 工具 | `auto_tool_selection`（默认关闭） |
| 审查 | `chat_mode_review`（默认关闭） |

复选框的状态会保存于您的偏好设定中。

## 其他操作

[复制、下载、编辑与导出](export_edit_responses.md)。欢迎消息底部的按钮可切换至[伙伴模式](partner_mode.md)或[代理模式](agent_mode.md)。

## 必要条件

使用您所配置的 [AI 后端](ai_backends.md)。
