# BYOK - 自備金鑰 (Bring Your Own Key)

**BibleMate AI** 支援「自備金鑰」（BYOK）模式，允許您使用個人 API 金鑰。此方式帶來了多項核心優勢：

- **模型彈性**：您不再受限於管理員設定的預設 AI 後端。您可以切換至偏好的提供商，或選擇符合您需求的特定模型。

- **繞過速率限制**：管理員通常會對佔用較多資源的功能（如代理模式或夥伴模式）設定每日用量限制。透過使用您自己的金鑰，您可以解除這些限制，並根據所選提供商的配額與計費方式使用。

- **個人化自主掌控**：您可以直接在 AI 提供商處管理自己的用量與費用。

# 如何設定您的 API 金鑰

大部分提供商的設定流程大致相似。

註冊：在您選擇的 AI 提供商註冊帳戶。

生成金鑰：在帳戶控制台中找到 API 區塊並建立新的 API 金鑰。

設定 BibleMate：在 BibleMate AI 網頁介面中，前往「偏好設定」（Preferences）。輸入 AI 後端提供商、您的 API 金鑰以及您希望使用的具體模型名稱。

## 範例 - 申請免費的 Google Gemini API 金鑰 (FREE)

以下是使用 Google AI Studio 的範例：

1. 開啟網站 https://aistudio.google.com ，點選 `Get Started`，並使用您的個人 Google 帳戶登入。
<img width="1281" height="461" alt="Image" src="https://github.com/user-attachments/assets/e9a54d02-c245-4331-9de2-0764e94bc561" />

2. 在左側選單中，點選 `Get API Key`，然後在右上角點選 `Create API Key`。
<img width="1617" height="1056" alt="Image" src="https://github.com/user-attachments/assets/63d5f1ab-9ba1-4eee-a213-af58ccf73541" />

3. 首先點選 `Create Project`，例如輸入：BibleMate。
<img width="512" height="329" alt="Image" src="https://github.com/user-attachments/assets/97d677d5-22c5-42b2-b9e7-f7106efcb09c" />

4. 輸入 API 名稱以供日後辨識，例如輸入：BibleMate。
<img width="511" height="283" alt="Image" src="https://github.com/user-attachments/assets/9ceb7476-c56c-4459-90bd-69c4b168fceb" />

5. 複製新建立的 API Key，並以您偏好的方式妥善保存。在第三個步驟中會用到它。請勿將此 API Key 與他人共享。
<img width="1043" height="263" alt="Image" src="https://github.com/user-attachments/assets/6373d1ce-f4f6-4529-899a-3d535a513f4a" />

注意事項：
* 您可以忽略 Billing（帳單設定），因為 Google 提供免費額度（Free tier）。
* 免費額度在高用量時有請求速率限制。如果是家庭共同使用，建議使用不同家庭成員的 Google 帳戶申請多個 API Key。

## 在 BibleMate AI 偏好設定中輸入您的 API 金鑰

<img width="1312" height="1344" alt="Image" src="https://github.com/user-attachments/assets/4d41ffb9-bb4b-4941-a8f6-c5a65b6b7557" />

1. 選擇 `googleai` 作為 AI 後端
2. 輸入 `gemini-2.5-flash` 作為 AI 模型（可依需求修改）
3. 輸入您的 API Key

完成！
