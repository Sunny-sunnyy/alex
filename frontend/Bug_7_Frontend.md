# Bug 7 Frontend: `next dev` / `next build` crash trên WSL2

## Mục tiêu của tài liệu này

File này là handoff note cho một session mới, ghi lại đầy đủ bug đã gặp ở **Guide 7 - Frontend & API**, những gì đã được chẩn đoán, những thay đổi đã áp dụng vào repo, trạng thái hiện tại, và các bước tiếp theo nên làm.

Source of truth của tài liệu này là:

- code hiện tại trong repo
- log thực tế từ terminal của người dùng
- các thay đổi đã được áp dụng trong session hiện tại

Region chính đang dùng cho môi trường này: **`ap-southeast-1`**

---

## 1. Bối cảnh

Người dùng đang ở **Guide 7** và muốn chạy local stack bằng:

```bash
cd scripts
uv run run_local.py
```

Stack mong muốn:

- backend local: `backend/api` trên `http://localhost:8000`
- frontend local: `frontend` trên `http://localhost:3000`

---

## 2. Triệu chứng ban đầu

Khi chạy:

```bash
cd scripts
uv run run_local.py
```

backend lên được, nhưng frontend crash gần như ngay lập tức:

```text
> frontend@0.1.0 dev
> next dev

Bus error (core dumped)
```

Trong lần đầu, `run_local.py` còn báo sai là frontend đã chạy:

```text
✅ Frontend running at http://localhost:3000
```

rồi sau đó mới phát hiện process đã chết:

```text
⚠️  A process has stopped unexpectedly!
```

---

## 3. Cách tái hiện bug

Bug không chỉ xảy ra qua script, mà tái hiện trực tiếp trong `frontend`:

```bash
cd frontend
npm run dev
```

và:

```bash
npm run build
```

Cả hai đều chết với:

```text
Bus error (core dumped)
```

Điều này chứng minh bug **không nằm ở `run_local.py` trước tiên**.

---

## 4. Chẩn đoán đã thực hiện

### 4.1. Kiểm tra xem lỗi có nằm ở `run_local.py` không

Kết quả: **không**

Lý do:

- chạy trực tiếp `npm run dev` trong `frontend` cũng crash
- chạy `npm run build` trong `frontend` cũng crash

### 4.2. Kiểm tra native module của Next

Đã chạy kiểm tra load trực tiếp native binary của Next SWC:

```bash
node -e "require('./node_modules/@next/swc-linux-x64-gnu/next-swc.linux-x64-gnu.node')"
```

Kết quả:

- process chết với exit code `135`
- tương đương với `Bus error`

Điều này là bằng chứng mạnh cho thấy crash xảy ra ở lớp:

- **native `next-swc` binding**
- không phải do code React page, không phải do route app

### 4.3. Kiểm tra version Node

Máy người dùng ban đầu đang dùng:

- `node v24.17.0`
- `npm 11.13.0`

Đã kiểm tra trong máy có sẵn `nvm` và các version:

- `v22.19.0`
- `v24.17.0`

Đã thử chuyển sang Node 22:

```bash
source ~/.nvm/nvm.sh
nvm use 22
npm run dev
npm run build
```

Kết quả:

- vẫn crash với `Bus error`

=> Kết luận: **không phải chỉ do Node 24**

### 4.4. Điều tra fallback wasm của Next

Đã đọc mã trong:

```text
frontend/node_modules/next/dist/build/swc/index.js
```

Phát hiện các cơ chế liên quan:

- `NEXT_TEST_WASM=1`
- `NEXT_TEST_WASM_DIR=<path>`
- package fallback:
  - `@next/swc-wasm-nodejs`
  - `@next/swc-wasm-web`

### 4.5. Cài package wasm fallback

Đã yêu cầu user chạy:

```bash
cd frontend
npm install @next/swc-wasm-nodejs@15.5.3
```

Kết quả:

- package được cài thành công
- `package.json` đã có thêm:

```json
"@next/swc-wasm-nodejs": "^15.5.3"
```

- `node_modules/@next/swc-wasm-nodejs` tồn tại
- `require.resolve('@next/swc-wasm-nodejs')` hoạt động

### 4.6. Kiểm tra biến môi trường `NEXT_TEST_WASM`

Khi chạy:

```bash
NEXT_TEST_WASM=1 npm run dev
```

hoặc:

```bash
NEXT_TEST_WASM=1 npm run build
```

Next vẫn fail và log:

```text
Attempted to load @next/swc-wasm-nodejs, but it was not installed
Attempted to load @next/swc-wasm-web, but it was not installed
cannot run loadNative when `NEXT_TEST_WASM` is set
Failed to load SWC binary for linux/x64
```

### 4.7. Tìm ra workaround đúng

Đã thử ép thẳng biến:

```bash
NEXT_TEST_WASM=1 NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs npm run dev
```

và:

```bash
NEXT_TEST_WASM=1 NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs npm run build
```

Kết quả quan trọng:

- **không còn `Bus error`**
- SWC native crash đã được bypass thành công

Kết quả cụ thể:

#### `npm run dev`

Không còn `Bus error`, nhưng trong sandbox của agent bị chặn bind port:

```text
Error: listen EPERM: operation not permitted 0.0.0.0:3000
```

Lỗi này là do môi trường sandbox của agent, **không phải bug frontend của user**.

#### `npm run build`

Build chạy qua được SWC/lint/type-check, và tiến xa hơn nhiều. Output dừng ở:

```text
Linting and checking validity of types ...
./components/ErrorBoundary.tsx
2:8  Warning: 'Link' is defined but never used.
...
Next.js build worker exited with code: 1 and signal: null
```

Điểm quan trọng:

- đây **không còn là `Bus error`**
- tức là workaround wasm đã thực sự có hiệu lực

---

## 5. Root cause hiện tại

### Root cause đã được chứng minh

Frontend local bị crash vì:

- **native `next-swc` binary trên WSL2 của máy này bị crash**
- cụ thể là binary:

```text
node_modules/@next/swc-linux-x64-gnu/next-swc.linux-x64-gnu.node
```

### Điều đã được chứng minh bằng log

1. `next dev` crash
2. `next build` crash
3. load trực tiếp native SWC binary cũng crash
4. ép dùng wasm qua `NEXT_TEST_WASM` + `NEXT_TEST_WASM_DIR` thì không còn `Bus error`

### Root cause chưa khẳng định ở mức sâu hơn

Chưa chứng minh được native SWC crash là do:

- WSL2 kernel / CPU instruction incompatibility
- glibc / native ABI
- bug riêng của Next 15.5.3 trên máy này
- hoặc tương tác với Node version / sandbox / platform

Nhưng với mục tiêu đưa project chạy được, điều đó **chưa cần thiết ngay** vì đã có workaround.

---

## 6. Các thay đổi đã áp dụng trong repo

### 6.1. `scripts/run_local.py`

File đã sửa:

- [scripts/run_local.py](../scripts/run_local.py)

#### Thay đổi 1: sửa bug báo thành công giả

Trước đây:

- frontend crash nhưng script vẫn có thể in `✅ Frontend running`

Bây giờ:

- nếu process frontend/backend chết sớm, script in:
  - exit code
  - log gần nhất

#### Thay đổi 2: tránh `uv sync` thừa cho backend

Script không còn sync lại backend dependencies một cách thừa nếu workspace env đã tồn tại.

#### Thay đổi 3: thêm workaround wasm cho frontend

Script giờ tự set:

```python
NEXT_TEST_WASM=1
NEXT_TEST_WASM_DIR=<frontend>/node_modules/@next/swc-wasm-nodejs
```

và tự tạo:

```text
~/.cache/next-swc
```

#### Thay đổi 4: fail sớm nếu thiếu package wasm

Nếu thiếu:

```text
frontend/node_modules/@next/swc-wasm-nodejs/wasm.js
```

script sẽ báo lỗi rõ ràng và dừng.

---

### 6.2. `scripts/deploy.py`

File đã sửa:

- [scripts/deploy.py](../scripts/deploy.py)

#### Thay đổi:

Khi build frontend production, script giờ cũng set:

```python
NEXT_TEST_WASM=1
NEXT_TEST_WASM_DIR=<frontend>/node_modules/@next/swc-wasm-nodejs
```

và kiểm tra package wasm fallback tồn tại trước khi chạy `npm run build`.

Mục tiêu:

- để production build không chết vì native `next-swc` giống local

---

### 6.3. `frontend/next.config.ts`

File đã sửa rồi sửa lại:

- [frontend/next.config.ts](./next.config.ts)

#### Trạng thái cuối cùng

Đã **bỏ** phần:

```ts
experimental: {
  useWasmBinary: true
}
```

Lý do:

- trên `linux/x64`, Next chỉ warning:

```text
experimental.useWasmBinary is not an option for supported platform linux/x64 and will be ignored
```

- không giải quyết được vấn đề
- workaround thực sự là `NEXT_TEST_WASM` + `NEXT_TEST_WASM_DIR`

---

## 7. Các lệnh đã dùng và kết quả

### 7.1. Tái hiện bug gốc

```bash
cd frontend
npm run dev
```

Kết quả:

```text
Bus error (core dumped)
```

```bash
npm run build
```

Kết quả:

```text
Bus error (core dumped)
```

### 7.2. Chứng minh native SWC crash

```bash
node -e "require('./node_modules/@next/swc-linux-x64-gnu/next-swc.linux-x64-gnu.node')"
```

Kết quả:

- exit code `135`

### 7.3. Cài wasm fallback

```bash
cd frontend
npm install @next/swc-wasm-nodejs@15.5.3
```

Kết quả:

- package được cài

### 7.4. Workaround đúng

```bash
cd frontend
NEXT_TEST_WASM=1 NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs npm run dev
```

Kết quả:

- không còn `Bus error`

```bash
NEXT_TEST_WASM=1 NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs npm run build
```

Kết quả:

- không còn `Bus error`
- build đi xa hơn, dừng ở stage khác

---

## 8. Trạng thái hiện tại (updated 2026-07-09)

### Đã xử lý xong

- xác định được bug không nằm ở app pages trước tiên
- xác định được native `next-swc` là điểm crash
- xác định được workaround wasm hoạt động
- đã tích hợp workaround đó vào `scripts/run_local.py`
- đã tích hợp workaround đó vào `scripts/deploy.py`
- đã sửa bug báo sai trạng thái frontend trong `run_local.py`

### DA XAC MINH END-TO-END (2026-07-09)

Build production (`npm run build`) da chay thanh cong voi workaround wasm:

- **KHONG con `Bus error`** — workaround wasm hoat dong hoan toan
- `next build` hoan tat: 9 pages exported thanh cong
- Phat hien va fix 2 loi app-level (truoc day bi SWC crash che khuat):
  1. `ErrorBoundary.tsx` — xoa unused `Link` import
  2. `@clerk/nextjs` type declarations — `node_modules` can duoc cai lai bang `npm install --legacy-peer-deps` tren WSL2

### Loi app-level da fix trong session nay

#### Fix 1: ErrorBoundary.tsx — unused Link import

```diff
 import React, { Component, ErrorInfo, ReactNode } from 'react';
-import Link from 'next/link';
```

#### Fix 2: node_modules corruption

`@clerk/nextjs/dist/types/index.d.ts` bi thieu — can cai lai dependencies:
```bash
cd frontend
rm -rf node_modules package-lock.json
git checkout -- package-lock.json
npm install --legacy-peer-deps
```

Sau khi cai lai, ca `@clerk/nextjs` types va `@next/swc-wasm-nodejs` deu day du.

---

## 9. Bước tiếp theo đề xuất cho session mới

### Bước 1

Yêu cầu user chạy:

```bash
cd ~/AiProduction_t6_2026_wsl/projects/alex/scripts
UV_CACHE_DIR=/tmp/uv-cache uv run run_local.py
```

### Bước 2

Nếu frontend còn fail, kiểm tra log mới:

- còn `Bus error` không?
- hay đã chuyển sang lỗi app-level khác?

### Bước 3

Nếu frontend đã dùng wasm fallback và không còn `Bus error`, nhưng `npm run build` vẫn fail:

- debug lỗi build thật sự tiếp theo
- khả năng cao lúc này là lỗi code/config bình thường, không còn là bug nền tảng SWC

### Bước 4

Nếu cần chạy production build qua script:

```bash
cd scripts
uv run deploy.py
```

và xác minh `deploy.py` đã dùng `NEXT_TEST_WASM_DIR` đúng.

---

## 10. Tóm tắt cho session mới

Bug chính:

- `frontend` crash với `Bus error` khi `next dev` / `next build`

Root cause đã chứng minh:

- native `next-swc` binary crash trên WSL2

Workaround đúng (DA VERIFIED 2026-07-09):

```bash
NEXT_TEST_WASM=1
NEXT_TEST_WASM_DIR=$PWD/node_modules/@next/swc-wasm-nodejs
```

**BUILD DA PASS:** `npm run build` chay thanh cong — 9 pages exported, khong con `Bus error`.

Đã patch workaround vào:

- [scripts/run_local.py](../scripts/run_local.py)
- [scripts/deploy.py](../scripts/deploy.py)

Fix them:

- [frontend/components/ErrorBoundary.tsx](./components/ErrorBoundary.tsx) — xoa unused `Link` import
- `frontend/node_modules` — can `npm install --legacy-peer-deps` tren WSL2

Trạng thái hiện tại:

- `npm run build` PASS (da verify)
- Con `npm run dev` / `run_local.py` can user chay verify tren may that (khong the test trong sandbox vi port bind)

