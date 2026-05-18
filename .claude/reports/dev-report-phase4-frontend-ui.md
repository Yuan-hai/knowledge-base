# Dev Report: Phase 4 -- Frontend UI Components

**Date**: 2026-05-18
**Status**: All 18 components created, Vite build passes (112 modules, 0 errors)

---

## Design Summary

Warm minimalist design using Tailwind CSS utility classes exclusively:
- **Color palette**: Off-white backgrounds (`stone-50`), warm gray text (`stone-700`/`stone-800`), dark accent (`stone-800`) for user bubbles and primary buttons
- **Typography**: System font stack with `Inter` as preferred, antialiased rendering
- **Layout**: Two-panel -- 280px left sidebar (documents) + fluid main chat area
- **Animations**: Subtle transitions on hover states, slide-in settings panel, toast enter/leave

---

## Files Created (18 total)

### Composables (4) -- `src/composables/`

| # | File | Purpose |
|---|------|---------|
| 1 | `useSettings.ts` | Fetches `/api/settings` on mount, exposes `selectedModel`, `uploadFolder`, `availableModels`, `updateSettings()` |
| 2 | `useDocuments.ts` | Document CRUD: `fetchDocuments()`, `uploadDocument(file)` with progress tracking, `deleteDocument(id)` |
| 3 | `useRagContext.ts` | Manages `Set<string>` of selected document IDs for RAG mode, with `toggleDocument()`, `isSelected()`, `getSelectedIds()` |
| 4 | `useChat.ts` | Full SSE streaming for both `/api/chat` and `/api/rag/query`. Parses `data:` lines, handles `<!--SOURCES:...-->` marker. Stores parsed sources in reactive `messageSources` map. |

### Shared Components (2) -- `src/components/shared/`

| # | File | Purpose |
|---|------|---------|
| 5 | `LoadingSpinner.vue` | SVG spinner with `sm`/`md`/`lg` sizes, `role="status"` for accessibility |
| 6 | `Toast.vue` | Teleported notification with enter/leave transitions. Supports `success`/`error`/`info` types with color-coded icons. Auto-dismiss after configurable duration. |

### Settings Components (2) -- `src/components/settings/`

| # | File | Purpose |
|---|------|---------|
| 7 | `ModelSelector.vue` | Styled `<select>` bound to `modelValue` with `update:modelValue` emit. Renders options from `ModelInfo[]`. |
| 8 | `SettingsPanel.vue` | Slide-in panel (300ms transition from right). Contains ModelSelector + upload folder text input + save button. Teleported with backdrop overlay. |

### Document Components (3) -- `src/components/document/`

| # | File | Purpose |
|---|------|---------|
| 9 | `DocumentItem.vue` | Single document row: filename, formatted date, chunk count, RAG checkbox (conditional), delete button (hover-revealed) |
| 10 | `DocumentUpload.vue` | Drag-and-drop zone with file input fallback. Shows upload progress bar during upload. Filters to `.pdf`, `.docx`, `.txt`, `.md`. |
| 11 | `DocumentList.vue` | Scrollable list container. Shows loading spinner, empty state with icon, or rendered DocumentItem list. Displays document count in header. |

### Chat Components (4) -- `src/components/chat/`

| # | File | Purpose |
|---|------|---------|
| 12 | `ChatMessage.vue` | Message bubble: user (right-aligned, `stone-800` bg, white text) vs assistant (left-aligned, `stone-50` bg, bordered). Expandable sources section for RAG citations. |
| 13 | `ChatInput.vue` | Auto-resizing textarea + send button. Enter to send, Shift+Enter for newline. Disabled while streaming. |
| 14 | `ChatModeToggle.vue` | Pill-style toggle between "Chat" and "RAG" modes. RAG button shows badge with selected document count. |
| 15 | `ChatPanel.vue` | Main chat container: scrollable message list (auto-scrolls on new content), empty state with guidance text, typing indicator (bouncing dots), ChatInput at bottom. |

### Layout Components (2) -- `src/components/layout/`

| # | File | Purpose |
|---|------|---------|
| 16 | `AppHeader.vue` | Top bar: "Library" branding with book icon, current model name chip (hidden on mobile), settings gear button |
| 17 | `AppSidebar.vue` | 280px left panel: DocumentUpload at top, DocumentList filling remaining space, folder path display in footer |

### Pages (1) -- `src/pages/`

| # | File | Purpose |
|---|------|---------|
| 18 | `HomePage.vue` | Full app layout orchestrator. Initializes all composables, wires up events between sidebar/chat/settings/toast. Handles send/upload/delete/save workflows. |

---

## Base Styles Updates

- `src/style.css`: Added Tailwind base layer with font smoothing, custom selection colors, styled scrollbars (6px, rounded thumb).
- `index.html`: Title changed to "Library -- Knowledge Base".

---

## Key Architectural Decisions

1. **Composables pattern**: All state is managed in composables, keeping components purely presentational. HomePage.vue is the sole orchestrator that wires composables to component props/events.

2. **SSE with fetch()**: The `useChat` composable uses native `fetch()` with `ReadableStream` instead of Axios, since Axios does not support streaming response bodies.

3. **RAG sources**: Parsed from `<!--SOURCES:{json}-->` markers in the SSE stream and stored in a reactive `Record<number, string[]>` map keyed by message index. ChatPanel passes the appropriate sources to each ChatMessage.

4. **Reactive Set for selections**: `useRagContext` uses `ref<Set<string>>` and replaces the entire Set on mutation to trigger Vue reactivity (Vue 3 does not deeply track Set/Map mutations).

5. **Toast via Teleport**: Rendered at `<body>` level with absolute positioning to avoid z-index issues. Uses Vue `<Transition>` for enter/leave animations.

---

## Build Verification

```
vite v4.5.14 building for production...
112 modules transformed.
dist/index.html            0.46 kB
dist/assets/index-**.css  19.77 kB (gzip: 4.24 kB)
dist/assets/index-**.js   172.93 kB (gzip: 64.68 kB)
built in 2.66s
```

Zero TypeScript errors, zero build warnings.
