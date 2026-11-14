# BYOK - 自带密钥 (Bring Your Own Key)

**BibleMate AI** 支持“自带密钥”（BYOK）模式，允许您使用个人 API 密钥。这种方式带来了多项核心优势：

- **模型灵活性**：您不再受限于管理员设置的默认 AI 后端。您可以切换至偏好的提供商，或选择符合您需求的特定模型。

- **绕过速率限制**：管理员通常会对占用较多资源的功能（如代理模式或伙伴模式）设置每日用量限制。通过使用您自己的密钥，您可以解除这些限制，并根据所选提供商的配额与计费方式使用。

- **个性化自主掌控**：您可以直接在 AI 提供商处管理自己的用量与费用。

# 如何设置您的 API 密钥

大部分提供商的设置流程大致相似。

注册：在您选择的 AI 提供商注册账户。

生成密钥：在账户控制面板中找到 API 区域并创建新的 API 密钥。

配置 BibleMate：在 BibleMate AI 网页界面中，前往“偏好设定”（Preferences）。输入 AI 后端提供商、您的 API 密钥以及您希望使用的具体模型名称。

## 示例 - 申请免费的 Google Gemini API 密钥 (FREE)

以下是使用 Google AI Studio 的示例：

1. 打开网站 https://aistudio.google.com ，点击 `Get Started`，并使用您的个人 Google 账户登录。
<img width="1281" height="461" alt="Image" src="https://github.com/user-attachments/assets/e9a54d02-c245-4331-9de2-0764e94bc561" />

2. 在左侧菜单中，点击 `Get API Key`，然后在右上角点击 `Create API Key`。
<img width="1617" height="1056" alt="Image" src="https://github.com/user-attachments/assets/63d5f1ab-9ba1-4eee-a213-af58ccf73541" />

3. 首先点击 `Create Project`，例如输入：BibleMate。
<img width="512" height="329" alt="Image" src="https://github.com/user-attachments/assets/97d677d5-22c5-42b2-b9e7-f7106efcb09c" />

4. 输入 API 名称以供日后识别，例如输入：BibleMate。
<img width="511" height="283" alt="Image" src="https://github.com/user-attachments/assets/9ceb7476-c56c-4459-90bd-69c4b168fceb" />

5. 复制新创建的 API Key，并以您偏好的方式妥善保存。在第三个步骤中会用到它。请勿将此 API Key 与他人共享。
<img width="1043" height="263" alt="Image" src="https://github.com/user-attachments/assets/6373d1ce-f4f6-4529-899a-3d535a513f4a" />

注意事项：
* 您可以忽略 Billing（账单设置），因为 Google 提供免费额度（Free tier）。
* 免费额度在高用量时有请求速率限制。如果是家庭共同使用，建议使用不同家庭成员的 Google 账户申请多个 API Key。

## 在 BibleMate AI 偏好设定中输入您的 API 密钥

<img width="1312" height="1344" alt="Image" src="https://github.com/user-attachments/assets/4d41ffb9-bb4b-4941-a8f6-c5a65b6b7557" />

1. 选择 `googleai` 作为 AI 后端
2. 输入 `gemini-2.5-flash` 作为 AI 模型（可按需修改）
3. 输入您的 API Key

完成！
