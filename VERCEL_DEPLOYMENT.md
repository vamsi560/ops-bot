# 🚀 Vercel Deployment Guide for Operations Bot

## 📋 Overview

This guide will help you deploy your Operations Bot to Vercel as a **single monorepo deployment** with both backend (FastAPI) and frontend (React) components.

## 🏗️ Architecture

- **Backend**: Deployed as Vercel Serverless Functions at `/api/*` routes
- **Frontend**: Deployed as a static React app at root routes
- **Single Domain**: Everything runs on one Vercel domain
- **Database**: Uses environment variables for configuration

## 📁 Project Structure

```
Ops/
├── vercel.json             # Unified Vercel configuration
├── backend/                # FastAPI Backend
│   ├── requirements-vercel.txt  # Python dependencies
│   ├── main.py             # FastAPI app with /api/* routes
│   └── ...                 # Other backend files
├── frontend/               # React Frontend
│   ├── env.example         # Environment variables template
│   └── ...                 # React app files
└── VERCEL_DEPLOYMENT.md    # This guide
```

## 🔧 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Vercel CLI** (optional): `npm i -g vercel`

## 🚀 Deployment Steps

### Single Deployment Process

1. **Go to Vercel Dashboard**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"

2. **Import Repository**
   - Select your GitHub repository
   - **Root Directory**: Leave as root (don't select a subfolder)
   - Framework Preset: **Other** (Vercel will auto-detect)

3. **Configure Environment Variables**
   ```
   ONEDRIVE_ACCESS_TOKEN=your_onedrive_token
   ONEDRIVE_BASE_FOLDER=your_sharepoint_site_id
   LLM_PROVIDER=gemini
   LLM_API_KEY=your_gemini_api_key
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Get your single deployment URL (e.g., `https://your-ops-bot.vercel.app`)

### 🎯 Result

After deployment, you'll have:
- **Frontend**: `https://your-ops-bot.vercel.app/` (React app)
- **Backend API**: `https://your-ops-bot.vercel.app/api/` (FastAPI endpoints)
- **Bot Endpoints**: `https://your-ops-bot.vercel.app/api/bot/*` (Bot functionality)

## 🔐 Environment Variables Setup

### Environment Variables (in Vercel Dashboard)

| Variable | Value | Description |
|----------|-------|-------------|
| `ONEDRIVE_ACCESS_TOKEN` | `eyJ0eXAiOiJKV1QiLCJub25jZSI6...` | Your SharePoint access token |
| `ONEDRIVE_BASE_FOLDER` | `vmivsp.sharepoint.com,40b61c06-2f8a-49ff-b7b9-a83d5e10baa2,cbad67fe-664d-41db-98d2-725081a62e57` | Your SharePoint site ID |
| `LLM_PROVIDER` | `gemini` | LLM provider (gemini/huggingface/openai) |
| `LLM_API_KEY` | `AIzaSyA5_KnR58T2MTG4oOvBeAqbd8idJCdOlRA` | Your Gemini API key |
| `HUGGINGFACE_API_KEY` | `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` | Your Hugging Face API key |

**Note**: No `REACT_APP_API_URL` needed! The frontend automatically uses `/api` in production.

## 🧪 Testing Deployment

### Test Backend
```bash
curl https://your-ops-bot.vercel.app/api/
```

### Test Frontend
- Visit your deployment URL: `https://your-ops-bot.vercel.app/`
- Open the QA Assistant
- Ask a question to test the connection

## 🔄 Continuous Deployment

Once deployed, Vercel will automatically redeploy when you push changes to your GitHub repository.

## 🛠️ Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend CORS settings include your Vercel domain
   - Check that `REACT_APP_API_URL` is correctly set

2. **Environment Variables Not Loading**
   - Verify variables are set in Vercel dashboard
   - Redeploy after adding new variables

3. **Build Failures**
   - Check `requirements-vercel.txt` for missing dependencies
   - Verify Python version compatibility

4. **API Connection Issues**
   - Test backend endpoints directly
   - Check network tab in browser dev tools

### Debug Commands

```bash
# Test backend locally
cd backend
python main.py

# Test frontend locally
cd frontend
npm start
```

## 📊 Monitoring

- **Vercel Dashboard**: Monitor deployments and performance
- **Function Logs**: View serverless function logs
- **Analytics**: Track usage and performance metrics

## 🔒 Security Notes

- Never commit `.env` files to Git
- Use Vercel's environment variables for sensitive data
- Regularly rotate API keys and tokens
- Monitor usage to prevent abuse

## 🎯 Next Steps

1. Set up custom domains (optional)
2. Configure monitoring and alerts
3. Set up automated backups
4. Implement rate limiting
5. Add authentication if needed

## 📞 Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **React Docs**: [reactjs.org](https://reactjs.org)
