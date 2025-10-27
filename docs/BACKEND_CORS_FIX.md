# Backend CORS Configuration - Implementation Guide

## Executive Summary

The frontend is working correctly but cannot communicate with the backend because the backend is rejecting cross-origin requests. You need to add **CORS (Cross-Origin Resource Sharing) middleware** to your FastAPI backend to allow the frontend to make requests.

**Status**: Frontend ready, backend needs CORS configuration
**Time to Fix**: 2 minutes
**Difficulty**: Easy

---

## Why This Is Needed

### The Problem

The frontend (running on `http://127.0.0.1:5173`) is trying to communicate with the backend (running on `http://localhost:8000`). Even though both are on the same machine, the browser treats them as **different origins** because they use different ports.

For security reasons, modern browsers **block cross-origin requests** unless the backend explicitly allows them.

### Current Error

```
Access to XMLHttpRequest at 'http://localhost:8000/attack-path/main' 
from origin 'http://127.0.0.1:5173' has been blocked by CORS policy
```

The browser is preventing the request because the backend didn't send the required permission headers.

### The Backend Logs Show

```
INFO: 127.0.0.1:53388 - "OPTIONS /attack-path/main HTTP/1.1" 405 Method Not Allowed
```

The browser is sending an **OPTIONS preflight request** to check permissions, and your backend is responding with **405 (Method Not Allowed)** because it doesn't have CORS middleware configured.

---

## What CORS Does

CORS middleware adds special response headers that tell the browser:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, *
```

**Translation**: "It's OK for any frontend to make any type of request to me."

---

## Implementation Steps

### Step 1: Import CORS Middleware

Add this import at the **top** of your FastAPI application file:

```python
from fastapi.middleware.cors import CORSMiddleware
```

### Step 2: Create FastAPI App Instance

You should already have this, but verify it exists:

```python
from fastapi import FastAPI

app = FastAPI()
```

### Step 3: Add CORS Middleware (CRITICAL)

**Add these lines RIGHT AFTER creating your FastAPI app**, but BEFORE any route definitions:

```python
# Add CORS middleware - MUST be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allow all origins
    allow_credentials=True,         # Allow cookies/credentials
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"],           # Allow all headers
)
```

### Step 4: Restart Backend

Stop and restart your backend server for changes to take effect:

```bash
# Stop the current process (Ctrl+C)
# Then restart
python main.py  # or your startup command
```

### Step 5: Refresh Frontend

Refresh your browser (http://localhost:5173) and click the button again.

---

## Complete Example

Here's what your main FastAPI file should look like:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create app
app = FastAPI()

# Add CORS middleware BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Now define your routes
@app.post("/attack-path/main")
async def attack_path_main(request: dict):
    # Your existing code here
    pass

@app.get("/health")
async def health():
    return {"status": "ok"}

# ... rest of your routes ...
```

---

## Production Configuration (Optional)

For production, restrict CORS to specific domains instead of allowing all (`"*"`):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",        # Local development
        "http://127.0.0.1:5173",        # Alternative localhost
        "https://yourdomain.com",       # Production domain
        "https://www.yourdomain.com",   # Production with www
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

## Verification

After implementing, you should see this in your backend logs:

```
INFO: 127.0.0.1:xxxxx - "OPTIONS /attack-path/main HTTP/1.1" 200 OK
INFO: 127.0.0.1:xxxxx - "POST /attack-path/main HTTP/1.1" 200 OK
```

The status changed from **405 (Method Not Allowed)** to **200 (OK)** ✅

---

## What Each Parameter Does

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `allow_origins` | `["*"]` | Allow requests from ANY origin |
| `allow_credentials` | `True` | Allow requests with cookies/auth tokens |
| `allow_methods` | `["*"]` | Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc) |
| `allow_headers` | `["*"]` | Allow any headers in the request |

---

## Common Issues

### Issue: Still getting CORS error after restart

**Solution**: 
- Make sure CORS middleware is added BEFORE route definitions
- Make sure you restarted the backend (not just refreshed code)
- Check that no other middleware is blocking CORS

### Issue: 405 Method Not Allowed still appearing

**Solution**:
- The backend process didn't restart properly
- Kill the process completely and start fresh
- Verify the CORS code was added to the right file

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**:
- FastAPI should already be installed if your backend is running
- Run: `pip install fastapi`

---

## How to Tell It's Working

1. **Backend logs show OPTIONS with 200**: `"OPTIONS /attack-path/main HTTP/1.1" 200 OK`
2. **Frontend button works**: Clicking generates the attack path
3. **Stage cards display**: All 7 attack stages render on the page
4. **No CORS errors in browser console**: Developer Tools → Console shows no errors

---

## Next Steps After Fix

1. Add CORS middleware to FastAPI
2. Restart backend
3. Refresh frontend
4. Click "Generate Attack Path" button
5. Verify attack stages display correctly
6. If issues persist, check browser console for error messages

---

## Support

If you still have issues after implementing CORS:

1. Check backend logs for actual errors
2. Verify backend is responding to: `curl -X POST http://localhost:8000/attack-path/main`
3. Open browser DevTools (F12) and check the Network tab for response details
4. Make sure the endpoint `/attack-path/main` exists on your backend

---

**Remember**: This is a **backend configuration issue**, not a frontend issue. The frontend code is already correct and ready to communicate once CORS is enabled.
