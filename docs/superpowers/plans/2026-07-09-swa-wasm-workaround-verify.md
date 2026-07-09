# Verify & Fix next-swc Wasm Workaround for WSL2

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify the `NEXT_TEST_WASM` workaround eliminates the `Bus error` crash on WSL2, and fix any remaining issues so `uv run run_local.py` works end-to-end.

**Architecture:** The workaround forces Next.js to use `@next/swc-wasm-nodejs` (WebAssembly) instead of the native `@next/swc-linux-x64-gnu` binary which crashes on this WSL2. Both `scripts/run_local.py` and `scripts/deploy.py` already set `NEXT_TEST_WASM=1` + `NEXT_TEST_WASM_DIR`. The gap: it has never been verified end-to-end on the user's machine.

**Tech Stack:** Next.js 15.5.3, Node.js, WSL2 (Linux), npm, Python/uv

## Global Constraints

- Use `npm run build` with wasm env vars to verify, NOT `npx next build` directly
- Do NOT modify `frontend/next.config.ts` (already correctly stripped of `experimental.useWasmBinary`)
- Do NOT modify `frontend/package.json` unless adding a convenience script
- All verification commands run in the `frontend/` directory or `scripts/` directory
- Region: `ap-southeast-1` (not relevant for this task but project default)

---

### Task 1: Verify wasm fallback package is installed

**Files:**
- Check: `frontend/node_modules/@next/swc-wasm-nodejs/wasm.js`
- Check: `frontend/package.json` (already has `@next/swc-wasm-nodejs@^15.5.3`)

**Interfaces:**
- Produces: confirmation that wasm package exists on disk

- [ ] **Step 1: Check wasm.js exists on disk**

Run: `ls -la frontend/node_modules/@next/swc-wasm-nodejs/wasm.js`

Expected: File exists with reasonable size (>1MB for wasm binary).

If missing, run:
```bash
cd frontend && npm install @next/swc-wasm-nodejs@15.5.3
```

- [ ] **Step 2: Verify package.json has the dependency**

Run: `grep 'swc-wasm-nodejs' frontend/package.json`

Expected:
```json
"@next/swc-wasm-nodejs": "^15.5.3"
```

---

### Task 2: Verify `npm run build` works with wasm fallback

**Files:**
- Uses: `frontend/node_modules/@next/swc-wasm-nodejs/wasm.js`
- Uses: `frontend/next.config.ts`

**Interfaces:**
- Consumes: wasm package from Task 1
- Produces: successful `next build` output OR error log for diagnosis

- [ ] **Step 1: Clean previous build artifacts**

```bash
cd frontend
rm -rf out .next
```

- [ ] **Step 2: Run production build with wasm env vars**

```bash
cd frontend
NEXT_TEST_WASM=1 NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs npm run build
```

Expected outcomes (check which one you get):

**SUCCESS:** Build completes without `Bus error`. You'll see:
```
✓ Linting and checking validity of types
✓ Creating an optimized production build
✓ Collecting page data
✓ Generating static pages
```

**FAILURE — Still Bus error:** Native SWC still being loaded. Check:
- Is `NEXT_TEST_WASM_DIR` pointing to the right directory?
- Run `ls node_modules/@next/swc-wasm-nodejs/wasm.js` to confirm

**FAILURE — Different error (not Bus error):** This is progress! The wasm workaround is working but there's an app-level issue. The error message will be meaningful (lint error, type error, import error, etc.) rather than `Bus error (core dumped)`. Copy the full error output.

- [ ] **Step 3: Report result**

Based on the output from Step 2, determine which scenario applies:
- Success → proceed to Task 3
- Still Bus error → go to Task 4
- Different error → go to Task 5

---

### Task 3: If build succeeds — verify full stack via run_local.py

**Only execute if Task 2 produced a successful build.**

**Files:**
- Uses: `scripts/run_local.py`
- Uses: `backend/api/main.py`
- Uses: `frontend/` (dev server)

- [ ] **Step 1: Clean up previous dev artifacts**

```bash
cd frontend
rm -rf .next out
```

- [ ] **Step 2: Run full local stack**

```bash
cd scripts
uv run run_local.py
```

Expected:
```
📋 Prerequisites Check:
  ✅ Node.js: vXX.XX.X
  ✅ npm: XX.XX.X
  ✅ uv: X.X.X
✅ Environment files found

🚀 Starting FastAPI backend...
  ✅ Backend running at http://localhost:8000

🚀 Starting NextJS frontend...
  ✅ Frontend running at http://localhost:3000
```

- [ ] **Step 3: Verify frontend responds**

In another terminal:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

Expected: `200`

- [ ] **Step 4: Verify backend health**

```bash
curl -s http://localhost:8000/health
```

Expected: `{"status":"healthy"}`

- [ ] **Step 5: Commit if all passes**

```bash
git add -A
git commit -m "verify: swc wasm workaround confirmed working on WSL2

- Verified next build + next dev work with NEXT_TEST_WASM=1
- Wasm fallback bypasses native SWC Bus error on WSL2
- run_local.py and deploy.py wasm integration confirmed

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: If still Bus error — deep diagnosis

**Only execute if Task 2 still shows `Bus error (core dumped)`.**

- [ ] **Step 1: Double-check env var is actually passed**

```bash
cd frontend
NEXT_TEST_WASM=1 NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs \
  node -e "console.log('WASM:', process.env.NEXT_TEST_WASM); console.log('DIR:', process.env.NEXT_TEST_WASM_DIR)"
```

Expected: Both env vars printed correctly.

- [ ] **Step 2: Check if native binary is still being loaded despite env vars**

```bash
cd frontend
NEXT_TEST_WASM=1 NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs \
  node -e "
process.env.NEXT_TEST_WASM = '1';
process.env.NEXT_TEST_WASM_DIR = process.cwd() + '/node_modules/@next/swc-wasm-nodejs';
try {
  require('@next/swc-wasm-nodejs');
  console.log('wasm package loaded OK');
} catch(e) {
  console.log('wasm load failed:', e.message);
}
"
```

- [ ] **Step 3: Check Next.js version compatibility**

```bash
cd frontend
node -e "console.log(require('next/package.json').version)"
```

Expected: `15.5.3`

The wasm fallback package version MUST match the next version. Verify:
```bash
cd frontend
node -e "console.log(require('@next/swc-wasm-nodejs/package.json').version)"
```

Expected: `15.5.3` (must match next version exactly)

If versions mismatch, reinstall:
```bash
cd frontend
npm install @next/swc-wasm-nodejs@$(node -e "console.log(require('next/package.json').version)")
```

- [ ] **Step 4: Try force-disabling native SWC**

As a last resort, temporarily rename the native binary so Next.js can't find it:
```bash
cd frontend
mv node_modules/@next/swc-linux-x64-gnu/next-swc.linux-x64-gnu.node \
   node_modules/@next/swc-linux-x64-gnu/next-swc.linux-x64-gnu.node.bak
```

Then retry build:
```bash
NEXT_TEST_WASM=1 NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs npm run build
```

If this works, we can add binary rename to the scripts.

**IMPORTANT:** If renaming the binary fixes it, restore it after test:
```bash
mv node_modules/@next/swc-linux-x64-gnu/next-swc.linux-x64-gnu.node.bak \
   node_modules/@next/swc-linux-x64-gnu/next-swc.linux-x64-gnu.node
```

---

### Task 5: If different error (not Bus error) — fix app-level issues

**Only execute if Task 2 produces a non-Bus-error failure.**

Common post-wasm errors and fixes:

- [ ] **Step 1: TypeScript/ESLint errors**

If build fails at `Linting and checking validity of types` stage:
```bash
cd frontend
npx tsc --noEmit 2>&1 | head -30
```

Fix each type error. Common ones from Bug_7_Frontend.md:
- `ErrorBoundary.tsx:2:8 Warning: 'Link' is defined but never used` — remove unused import

- [ ] **Step 2: Import/module resolution errors**

If errors mention missing modules or incorrect imports, check each file in `frontend/pages/` and `frontend/components/` against their imports.

- [ ] **Step 3: Next.js config errors**

If the error references next.config.ts, verify:
```typescript
// frontend/next.config.ts should be:
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: { unoptimized: true },
  trailingSlash: false,
};

export default nextConfig;
```

NO `experimental.useWasmBinary` (already correctly removed).

- [ ] **Step 4: Retry build after each fix**

After each fix:
```bash
cd frontend
NEXT_TEST_WASM=1 NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs npm run build
```

Stop when build succeeds.

---
