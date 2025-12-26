# Google Drive MCP Setup Guide

To use the Google Drive MCP integration, you need to provide Google Cloud credentials. We recommend using a **Service Account** for backend API usage.

## Prerequisites

1.  **Google Cloud Project**: You need a project in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Enable Drive API**:
    *   Go to **APIs & Services > Library**.
    *   Search for **Google Drive API**.
    *   Click **Enable**.

## Option 1: Service Account (Recommended)

This method allows your application to act as a distinct identity (`your-sa@project-id.iam.gserviceaccount.com`).

1.  **Create Service Account**:
    *   Go to **IAM & Admin > Service Accounts**.
    *   Click **Create Service Account**.
    *   Name it (e.g., `docustream-drive-agent`).
    *   Skip role assignment for now (unless you need domain-wide delegation).

2.  **Generate Key**:
    *   Click on the newly created service account.
    *   Go to the **Keys** tab.
    *   Click **Add Key > Create new key**.
    *   Select **JSON**.
    *   The file will download automatically (e.g., `project-id-12345.json`).

3.  **Configure Environment**:
    *   Place the JSON file in your project (e.g., in `secrets/` or root). **Do not commit this file to git!**
    *   Set the environment variable:
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key-file.json"
        ```

4.  **Share Files (CRITICAL STEP)**:
    *   **Concept**: A Service Account is treated as a **completely separate user** with its own empty Google Drive. It **does NOT** automatically have access to your personal files.
    *   **Action**: You MUST go to your Google Drive, right-click the folder or file you want the API to access, click **Share**, and paste the **Service Account Email** (e.g., `docustream-drive-agent@project-id.iam.gserviceaccount.com`).
    *   *Without this step, the agent will see an empty drive.*

    > **Note on Domain-Wide Delegation**: If you are a Google Workspace Administrator, you can set up "Domain-Wide Delegation" to allow the Service Account to impersonate you and access *all* your files without manual sharing. This requires advanced setup in the Google Admin Console.


If you need to access your personal drive without sharing files manually, you typically use User OAuth.
The `npx @modelcontextprotocol/server-google-drive` tool may support an interactive login flow or require an OAuth Client Secret file mapped to `GOOGLE_DRIVE_OAUTH_CREDENTIALS`.
*Refer to the [official MCP server documentation](https://github.com/modelcontextprotocol/servers) for advanced OAuth setup.*
