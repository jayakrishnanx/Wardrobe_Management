# 🚀 Render Deployment Guide

Follow these steps to host your **Wardrobe Management** system on Render.com.

## 1. Prepare Your Repository
1. Ensure all your code is pushed to **GitHub**.
2. Make sure you have the `build.sh` and `runtime.txt` files (I've already added these for you).

## 2. Create a Web Service on Render
1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following configurations:
   - **Name**: `wardrobe-manager` (or any name you like)
   - **Environment**: `Python 3`
   - **Region**: (Choose the one closest to you)
   - **Branch**: `main`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn main.wsgi:application`

## 3. Connect a Database
1. Click **New** -> **PostgreSQL**.
2. Give it a name (e.g., `wardrobe-db`).
3. Once created, copy the **Internal Database URL**.
4. Go back to your Web Service -> **Environment** tab.
5. Add a new variable: `DATABASE_URL` and paste the value you just copied.

## 4. Environment Variables
In the **Environment** tab of your Web Service, add the following variables:
- `DJANGO_SECRET_KEY`: (Any random string)
- `DJANGO_DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app-name.onrender.com`
- `CSRF_TRUSTED_ORIGINS`: `https://your-app-name.onrender.com`
- `EMAIL_HOST_USER`: (Your email)
- `EMAIL_HOST_PASSWORD`: (Your app password)
- `GROQ_API_KEY`: (Your Groq key)
- `GOOGLE_API_KEY`: (Your Gemini key)

## 5. Deployment
Render will automatically start the build process using the `build.sh` script. You can watch the progress in the **Events** or **Logs** tab.

---
**Done!** Your site will be live at the `.onrender.com` URL provided by Render.
