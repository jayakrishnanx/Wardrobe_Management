# 🚂 Railway Deployment Guide

Follow these steps to host your **Wardrobe Management** system on Railway.app.

## 1. Prepare Your Repository
1. Ensure all your code is pushed to **GitHub**.
2. Make sure you've included the `Procfile`, `runtime.txt`, and updated `requirements.txt` (which I've already added for you).

## 2. Deploy on Railway
1. Go to [Railway.app](https://railway.app/) and log in with GitHub.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your `Wardrobe_Management` repository.
4. Click **Deploy Now**.

## 3. Add a Database
1. Once the project is created, click the **+ Add** button in the Railway dashboard.
2. Select **Database** -> **Add PostgreSQL**.
3. Railway will automatically link this database to your Django app using the `DATABASE_URL` environment variable I configured in your settings.

## 4. Set Environment Variables
Go to the **Variables** tab of your service in Railway and add the following:
- `DJANGO_SECRET_KEY`: (Any random string)
- `DJANGO_DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app-name.railway.app`
- `CSRF_TRUSTED_ORIGINS`: `https://your-app-name.railway.app`
- `EMAIL_HOST_USER`: (Your email)
- `EMAIL_HOST_PASSWORD`: (Your app password)
- `GROQ_API_KEY`: (Your Groq key)
- `GOOGLE_API_KEY`: (Your Gemini key)

## 5. Final Setup
Railway will automatically detect your `Procfile` and start the server. To run migrations and collect static files, you can add these to a "Post-Deploy" script or simply run them via the Railway CLI or a temporary command:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

---
**Done!** Your site will be live at the domain Railway provides you (you can find this under the **Settings** tab in Railway).
