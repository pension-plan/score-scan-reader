# UI references from 21st.dev

Retrieved 2026-11-08 with the 21st.dev Magic MCP. These are React/shadcn components; the app is plain JS with no build step, so port the **patterns**, not the code. The wireframe these fit into is `docs/ui-refs/ui-mock.excalidraw-elements.json` (Excalidraw elements; also rendered on the plan page).

## 1. Upload dropzone: "Upload Dropzone Empty State" (arihantcodes, id 29988)
https://21st.dev/@arihantcodes_1f7b8c4d/components/upload-empty
Patterns to port:
- **Drag depth counter**: `dragenter` fires for every child crossed, so keep `depth++` on dragenter, `depth--` on dragleave, and clear the "over" state only at 0. Reset to 0 on drop. (v1 flickers without this.)
- Title changes with state: idle ("Drop a scanned PDF or image") → over ("Drop it here") → done ("<file> converted").
- Hidden `<input type=file class=sr-only>` triggered by a visible button; reset `value = ""` after change so the same file can be chosen twice.
- One `aria-live="polite"` sr-only line announcing "Release to convert".
- Per-file row: name (truncate) + size (mono, tabular-nums) + thin progress meter while working, tick icon when done.
- Respect `prefers-reduced-motion` (faster, no movement).

## 2. Pipeline progress: "Stepper" (kevingirelli, id 35237)
https://21st.dev/@kevingirelli/components/stepper
Patterns to port (use it for the conversion stages: Render, Clean up, Staves, Notes, Lyrics, Parts, MusicXML):
- `<nav aria-label="Conversion progress"><ol>` so screen readers announce step count.
- Each `<li data-state="complete|current|upcoming">`; current step carries `aria-current="step"`.
- Indicator: number in a circle, check mark when complete, and an sr-only ", Completed / Current / Upcoming" after the number (colour and check are not read aloud).
- Separator line between steps, coloured once the step before is complete; `aria-hidden`.
- On narrow screens (<640px) only the current step shows its title; the rest are sr-only. This keeps the row within 400px.
- Colour transitions off under reduced motion.

## 3. MusicXML output: "Code Block" (kvnkld, id 23586)
https://21st.dev/@kvnkld/components/code-block
Patterns to port:
- Header bar: file label ("score.musicxml", language "MusicXML 4.0") on the left, Copy button on the right with icon + text that flips to "Copied" for ~1.2 s.
- Body with line numbers in a gutter (`user-select: none`) and code lines; horizontal scroll inside the block only.
- Keep v1's clipboard fallback: if `navigator.clipboard.writeText` rejects, select the text and show "Press Ctrl/Cmd+C". For very long output render a capped number of lines and keep the full text in a hidden textarea for copying.

Other candidates found (not retrieved): UploadThing Dropzone (18847), joyco File Dropzone (19201), originui Stepper (769), shadcnspace Animated Progress Stepper (28558), 0xuser64bit Code Block (35773).
