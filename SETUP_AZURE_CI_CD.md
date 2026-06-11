# Azure CI/CD Setup Instructions

## Overview
This guide will help you set up automatic deployment from GitHub to Azure Web App.

## Prerequisites
1. Azure subscription with Web App `zynch-website-2026`
2. GitHub repository: `https://github.com/CortexFlow-AI/Zynch-new-website-2026`
3. Azure CLI or Azure Portal access

## Step 1: Create Azure Service Principal

Run this command locally (requires Azure CLI with owner/admin permissions):

```bash
# Create a service principal with Contributor role
az ad sp create-for-rbac \
  --name "zynch-github-deploy" \
  --role contributor \
  --scopes /subscriptions/6e13f208-ad46-4e38-8dfc-961fe62197a7/resourceGroups/zynch-rg/providers/Microsoft.Web/sites/zynch-website-2026 \
  --sdk-auth
```

This will output a JSON object like:
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "subscriptionId": "6e13f208-ad46-4e38-8dfc-961fe62197a7",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "...
}
```

## Step 2: Add GitHub Secrets

1. Go to your GitHub repository: https://github.com/CortexFlow-AI/Zynch-new-website-2026
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

### Secret 1: AZURE_CREDENTIALS
- **Name:** `AZURE_CREDENTIALS`
- **Value:** Paste the entire JSON output from Step 1

### Secret 2: AZURE_WEBAPP_NAME
- **Name:** `AZURE_WEBAPP_NAME`
- **Value:** `zynch-website-2026`

## Step 3: Verify the Setup

1. Push any change to the `master` branch
2. Go to the **Actions** tab in your GitHub repository
3. You should see a new workflow run
4. The deployment should complete in ~1-2 minutes

## How It Works

1. **Push to master** → GitHub Actions triggers
2. **Validate** → Checks HTML syntax and file sizes
3. **Package** → Creates deployment.zip with all files
4. **Deploy** → Uses Azure credentials to deploy to Web App
5. **Complete** → Your site is live at https://zynch-website-2026.azurewebsites.net

## Troubleshooting

### Deployment Fails with "Invalid credentials"
- Verify the AZURE_CREDENTIALS secret is correct JSON
- Ensure the service principal has "Contributor" role on the Web App

### Web App shows old content
- Check the "purge" option or ensure "Clean" deployment is enabled
- The workflow uses `--clean` flag in deployment

### Need to redeploy manually
- You can always trigger a manual deployment from GitHub Actions tab

## Alternative: Use Azure Web App Publish Profile

If you prefer, you can use a publish profile instead:

1. Get publish profile from Azure Portal:
   - Go to Web App → Deployment Center → Basic auth credentials
   - Download the publish profile

2. Add as GitHub secret `AZURE_PUBLISH_PROFILE` with the downloaded content

3. Update the workflow to use:
```yaml
- name: Deploy to Azure Web App
  uses: azure/webapps-deploy@v3
  with:
    app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
    publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
    package: './deployment.zip'
```

## Security Notes

- The service principal only has access to the specific Web App resource
- Secrets are encrypted and never exposed in logs
- You can rotate credentials anytime from Azure Portal
- Consider using environments for additional protection

## Questions?

If you need help, check:
- GitHub Actions logs: https://github.com/CortexFlow-AI/Zynch-new-website-2026/actions
- Azure Portal: https://portal.azure.com → App Services → zynch-website-2026