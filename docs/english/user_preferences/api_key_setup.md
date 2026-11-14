# BYOK - Bring Your Own Key

**BibleMate AI** supports a "Bring Your Own Key" (BYOK) model, allowing you to use your personal API keys. This approach offers several key advantages:

- **Model Flexibility**: You are not restricted to the default AI backend set by the administrator. You can switch to your preferred providers or specific models that suit your needs.

- **Bypass Rate Limits**: Administrators often impose daily usage limits on resource-intensive features like Agent Mode or Partner. By using your own key, you remove these restrictions and operate according to your own provider's limits and costs.

- **Personalized Control**: You manage your own usage and costs directly with the AI provider.

# How to Set Up Your API Key

The process is similar across most providers.

Register: Create an account with your chosen AI provider.

Generate Key: Locate the API section in your account dashboard and create a new API key.

Configure BibleMate: In the BibleMate AI web interface, navigate to Preferences. Enter the AI backend provider, your API key, and the specific model name you wish to use.

## Example - Apply for Google Gemini API Keys (FREE)

Here is an example using Google AI Studio:

1. Open the website https://aistudio.google.com, select `Get Started`, and log in with your personal Google Account.
<img width="1281" height="461" alt="Image" src="https://github.com/user-attachments/assets/e9a54d02-c245-4331-9de2-0764e94bc561" />

2. In the left menu, select `Get API Key`, and then in the top right corner, select `Create API Key`.
<img width="1617" height="1056" alt="Image" src="https://github.com/user-attachments/assets/63d5f1ab-9ba1-4eee-a213-af58ccf73541" />

3. First, select `Create Project`, for example, enter: BibleMate.
<img width="512" height="329" alt="Image" src="https://github.com/user-attachments/assets/97d677d5-22c5-42b2-b9e7-f7106efcb09c" />

4. Enter an API name for future identification, for example, enter: BibleMate.
<img width="511" height="283" alt="Image" src="https://github.com/user-attachments/assets/9ceb7476-c56c-4459-90bd-69c4b168fceb" />

5. Copy the newly created API Key and save it in your preferred way. It will be useful in the third step. Do not share this API Key with others.
<img width="1043" height="263" alt="Image" src="https://github.com/user-attachments/assets/6373d1ce-f4f6-4529-899a-3d535a513f4a" />

Notes:
* You can ignore Billing, as Google provides a free tier.
* The Free Tier has rate limits with heavy usage. It is recommended that if a family uses it together, they apply for multiple API Keys using different family members' Google Accounts.

## Enter Your API Key in BibleMate AI Preferences

<img width="1312" height="1344" alt="Image" src="https://github.com/user-attachments/assets/4d41ffb9-bb4b-4941-a8f6-c5a65b6b7557" />

1. Select `googleai` as the AI backend
2. Enter `gemini-2.5-flash` as the AI model (modify based on your needs)
3. Enter your API Key

That's it!
