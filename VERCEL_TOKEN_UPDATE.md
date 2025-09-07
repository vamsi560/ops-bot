# OneDrive Token Setup Guide

## Hardcoded Token Approach (Recommended)

For maximum reliability, we now use a hardcoded token approach. This eliminates the need for constant token updates.

### Step 1: Get Your Token
1. Go to [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
2. Sign in with your Microsoft account
3. In the 'Modify permissions' tab, add these permissions:
   - `Files.ReadWrite.All`
   - `Sites.ReadWrite.All` 
   - `User.Read`
4. Click 'Generate Token'
5. Copy the access token

### Step 2: Set Up Hardcoded Token
Run the setup script to hardcode your token:

```bash
python setup_hardcoded_token.py
```

This script will:
- ✅ Test your token to make sure it works
- ✅ Hardcode it directly in the application code
- ✅ Verify the setup is complete

### Step 3: Deploy to Vercel
- Deploy your app to Vercel as usual
- No environment variables needed for the token
- The app will work reliably without token updates

## Your OneDrive Folder Structure

Based on the image, you have these folders:
- **Account Details** - Account information
- **Bench Report** - Bench resource data  
- **Certification** - Training/certification data
- **GT's Allocation** - Project allocation data
- **RRF** - Resource request forms
- **Utilization** - Resource utilization data

The system will automatically scan these folders and extract data from Excel/Word files.

## Expected Data Mapping

- **Active RRFs**: From RRF folder files
- **Bench Resources**: From Bench Report folder files
- **Active Projects**: From GT's Allocation and Utilization folder files
- **Trainees**: From Certification folder files

## Testing

After updating the token:
1. Visit your Vercel app
2. Check the dashboard - it should show real data from your files
3. Ask the QA bot about your data - it will provide responses based on actual files

## Troubleshooting

If you see zero data:
1. Check if the token is valid (expires every hour)
2. Verify the folder path in environment variables
3. Ensure files are in the correct folders with proper names
4. Check Vercel function logs for errors
