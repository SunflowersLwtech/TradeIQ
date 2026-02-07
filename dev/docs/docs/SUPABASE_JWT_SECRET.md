# SUPABASE_JWT_SECRET Configuration Guide

## 🔑 What is SUPABASE_JWT_SECRET?

`SUPABASE_JWT_SECRET` is the secret key used to **verify JWT tokens issued by Supabase**.

### Purpose

In your project, it is used for:

1. **JWT Verification** - Verify Supabase Auth tokens sent from the frontend
2. **User Authentication** - Verify user identity through `SupabaseJWTAuthentication` middleware
3. **Automatic User Creation** - Automatically create/lookup `UserProfile` based on email in JWT

### Usage in Code

```python
# backend/tradeiq/middleware/supabase_auth.py
# Verify JWT using HS256 algorithm
payload = jwt.decode(
    token,
    secret,  # This is SUPABASE_JWT_SECRET
    algorithms=["HS256"],
    ...
)
```

## 📍 How to Get SUPABASE_JWT_SECRET?

### Method 1: Supabase Dashboard (Recommended)

1. Log in to Supabase Dashboard
2. Go to your project
3. Navigate to: **Settings → API → JWT Settings**
4. Find **"JWT Secret"** or **"Legacy JWT Secret"**
5. Copy the secret value

**Path:**
```
https://supabase.com/dashboard/project/[YOUR-PROJECT-ID]/settings/api
```

### Method 2: JWT Keys Page

1. Navigate to: **Settings → JWT Keys**
2. If using legacy (HS256):
   - View **"Legacy JWT Secret"** tab
   - Copy the displayed secret
3. If using new version (ES256):
   - Need to configure code to use public key verification (current code uses HS256)

## ⚠️ Important Notes

### Current Code Uses HS256 (Symmetric Encryption)

Your code uses **HS256** algorithm, which is **symmetric encryption** and requires:
- ✅ **JWT Secret** (a string secret)
- ❌ Not Public Key

### Information in Images

The images you see show:
- **Public Key (JWK format)** - This is a **public key** (for ES256 asymmetric encryption)
- **Algorithm: ES256** - Asymmetric encryption algorithm

**However:**
- Your code uses **HS256** (symmetric encryption)
- Requires **JWT Secret** (string), not public key

### Supabase Secret Types

Supabase supports two JWT signing methods:

| Type | Algorithm | Key Format | Purpose |
|------|-----------|------------|---------|
| **Legacy** | HS256 | String secret | Symmetric encryption, requires JWT Secret |
| **New** | ES256 | Public/Private key pair | Asymmetric encryption, requires Public Key |

**Your project uses Legacy HS256**, so you need the JWT Secret string.

## 🔧 Configuration Steps

### 1. Get JWT Secret

In Supabase Dashboard:
1. Settings → API
2. Find **"JWT Secret"** or **"Legacy JWT Secret"**
3. Click "Reveal" or "Show" to display the secret
4. Copy the complete secret string

### 2. Add to .env

```bash
# Supabase Auth (Phase 6) - Get from Supabase Dashboard -> Settings -> API -> JWT Secret
SUPABASE_JWT_SECRET=your-jwt-secret-string-here
SUPABASE_URL=https://omwlpupmmdgppvsmhugl.supabase.co
```

### 3. Verify Configuration

```bash
cd backend
python manage.py shell
```

```python
from django.conf import settings
print(settings.SUPABASE_JWT_SECRET)  # Should display your secret
```

## 🎯 Do You Need to Configure This?

### ✅ Configuration Required

- Frontend uses Supabase Auth (Google Sign-In, etc.)
- API needs to verify JWT tokens
- User authentication functionality needed

### ❌ Configuration Not Required

- Demo only, no real user authentication needed
- Using mock data, not connecting to frontend
- Testing backend functionality only

## 📝 Notes

1. **Security**:
   - JWT Secret is sensitive information, do not commit to Git
   - `.env` file is already ignored in `.gitignore`

2. **Secret Format**:
   - JWT Secret is a **long string** (usually 32+ characters)
   - Not JSON format
   - Not Public Key

3. **Algorithm Matching**:
   - Ensure Supabase project uses HS256 (Legacy)
   - If project has been upgraded to ES256, code needs to be modified to use public key verification

## 🔍 How to Confirm Which Algorithm Your Project Uses?

In Supabase Dashboard:
1. Settings → JWT Keys
2. Check the displayed key type:
   - If you see "Legacy JWT Secret" → Using HS256 ✅
   - If you only see Public Key (JWK) → Using ES256 ⚠️

## 💡 If Project Uses ES256 (New Version)

If your Supabase project has been upgraded to ES256, you need to modify the code:

1. Use Public Key instead of Secret
2. Change algorithm to ES256
3. Use JWKS URL to fetch public key

But this requires code modifications, and the current code is designed for HS256.

## ✅ Summary

- **SUPABASE_JWT_SECRET** = Supabase Dashboard → Settings → API → JWT Secret
- It is a **string secret** (not public key)
- Used to verify JWT tokens issued by Supabase
- Can be temporarily skipped if user authentication is not needed
