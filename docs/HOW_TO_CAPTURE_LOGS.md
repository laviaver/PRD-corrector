# How to Capture Logs for Debugging the "Internal server error"

Follow these steps in order. They tell you where logs go and how to save them so we can see the real error.

---

## Step 1: Turn on DEBUG so the API returns the real error

1. Open `backend/.env` in your editor.
2. Add or change this line:
   ```env
   DEBUG=True
   ```
3. Save the file.

When DEBUG is on, the 500 response includes the exception type and message, so you may see the cause directly in the browser or in the Network tab.

---

## Step 2: Decide how you run the app

You can either use **start.sh** (logs go to a file) or **run the backend alone in the terminal** (logs on screen + easy to copy).

---

## Option A – Using start.sh (logs in a file)

### 2A.1 Start the app as usual

```bash
cd /Users/lavia/PRD-corrector
./start.sh
```

### 2A.2 Reproduce the error

1. Open http://localhost:5173 in the browser.
2. Choose your PRD file (e.g. `AI_PRD_Reviewer_PRD.docx`).
3. Click **Upload & Analyze**.
4. Wait until you see **Error: Internal server error** (or the DEBUG message).

### 2A.3 Where the logs are

Backend logs are written to:

```text
/Users/lavia/PRD-corrector/backend.log
```

That file is in the **project root** (same folder as `start.sh`), not inside `backend/`.

### 2A.4 Copy the last part of the log (the useful bit)

In a **new terminal** (leave the app running), run:

```bash
tail -100 /Users/lavia/PRD-corrector/backend.log
```

That prints the last 100 lines. Copy all of that output.

To append the same lines to a file you can share:

```bash
tail -100 /Users/lavia/PRD-corrector/backend.log > ~/Desktop/prd-error-log.txt
```

Then open `~/Desktop/prd-error-log.txt` and copy its contents (or share the file).

---

## Option B – Running the backend in the terminal (recommended for debugging)

This shows logs **in the terminal** and makes it easy to copy them.

### 2B.1 Stop the app if it’s running

- If you started it with `./start.sh`, press **Ctrl+C** in that terminal.
- If you’re not sure, in another terminal run:
  ```bash
  lsof -ti :8000 | xargs kill -9
  lsof -ti :5173 | xargs kill -9
  ```

### 2B.2 Start only the backend (so logs go to the terminal)

In a terminal:

```bash
cd /Users/lavia/PRD-corrector/backend
source venv/bin/activate
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Do **not** put `> ...` or `&` at the end. Leave this terminal open; all backend logs will appear here.

### 2B.3 Start the frontend in another terminal

In a **second** terminal:

```bash
cd /Users/lavia/PRD-corrector/frontend
npm run dev
```

### 2B.4 Reproduce the error

1. Open http://localhost:5173.
2. Select your PRD file.
3. Click **Upload & Analyze**.
4. Watch the **first** terminal (where uvicorn is running). When the error happens, you’ll see the Python traceback and error message there.

### 2B.5 Copy the logs

1. In the backend terminal, scroll up until you see the line with **ERROR** or **Traceback**.
2. Select from that line down to the end of the traceback.
3. Copy (Cmd+C).
4. Paste into a text file (e.g. `prd-error-log.txt`) or into your reply.

To save directly to a file while you reproduce:

1. Before clicking Upload & Analyze, in the backend terminal run:
   ```bash
   # You can't easily do this in the same terminal while uvicorn is running,
   # so use Option B.6 below instead.
   ```
2. Or use the “record” script in Step 3.

---

## Option B.6 – Record backend logs with the helper script (easiest)

From the project root:

```bash
./record-backend-logs.sh
```

This starts **only** the backend and writes all output to `backend-session.log` in the project root (and shows it in the terminal).

Then:

1. In another terminal: `cd frontend && npm run dev`
2. Open http://localhost:5173 and reproduce the error (Upload & Analyze).
3. In the first terminal, press **Ctrl+C** to stop the backend.
4. Open `backend-session.log` — the full session, including the error and traceback, is there. Share the last 50–100 lines (the part with `ERROR` and `Traceback`).

**Or** run with a custom log file:

```bash
./record-backend-logs.sh ~/Desktop/my-debug-log.txt
```

---

## Step 3: What to share

Send:

1. **The last 50–100 lines** of `backend.log` (Option A) or of the backend terminal / `backend-session.log` (Option B), **including**:
   - any line containing `ERROR` or `Traceback`
   - the full traceback (all lines starting with `Traceback`, `File "...", line X`, and the last line with the exception name and message).
2. **If you have DEBUG=True**: the **exact** error text shown in the UI (e.g. “Internal server error: …”) or the “detail” / “error” field from the failed request in the browser **Network** tab.

That’s enough to see why the server is returning 500.

---

## Quick reference

| You want…                          | Do this |
|------------------------------------|--------|
| Logs in a file (use start.sh)      | See Option A; logs are in `backend.log`; use `tail -100 backend.log` or save that to a file. |
| Logs on screen + easy to copy      | See Option B; run backend with `uvicorn` in the foreground in one terminal, frontend in another. |
| Full backend session in a file     | Run backend with `2>&1 \| tee ~/Desktop/backend-session.log` (Option B.6), then reproduce and share that file. |
| Actual error message in the API    | Set `DEBUG=True` in `backend/.env`, restart backend, then check UI or Network tab for the 500 response body. |
