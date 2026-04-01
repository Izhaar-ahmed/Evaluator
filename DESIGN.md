# Design System: Evaluator 2.0
**Project ID:** 13021156780421303809

## 1. Visual Theme & Atmosphere
A sophisticated, modern, and dark-mode-first aesthetic that bridges the gap between a robust developer tool and an approachable academic workspace. The mood is "Clean & Cyber-Academic": highly legible, sharp, and trusting, using deep backgrounds with neon-like high-contrast accents to draw attention to critical evaluation functionality. Generous whitespace inside components juxtaposes the density of technical code evaluation data.

## 2. Color Palette & Roles
*   **Deep Obsidian (#0F172A):** Main page background. Sets the dark, immersive tone.
*   **Midnight Slate (#1E293B):** Surface background for cards, modals, and input forms. Creates soft elevation on the backdrop.
*   **Electric Indigo (#6366F1):** Primary action color. Used for key CTAs like "Evaluate", important links, and active states.
*   **Emerald Trust (#10B981):** Success indicator. Used for high scores, positive AI feedback, and system "ready" states.
*   **Neon Coral (#F43F5E):** Warning/Failure indicator. Used for strict relevance failures or plagiarism flags.
*   **Frost White (#F8FAFC):** Primary text for headers and vital stats.
*   **Muted Steel (#94A3B8):** Secondary text for helper descriptions and subtle UI boundaries.

## 3. Typography Rules
*   **Font Family:** Inter (or similar modern sans-serif like Roboto/Outfit).
*   **Headers:** Bold (700) and Semi-bold (600) with tight letter spacing (-0.02em) to appear crisp and engineered.
*   **Body:** Regular (400) with higher line height (1.6) for readability.
*   **Monospace (Code blocks):** Fira Code or jetbrains mono for any snippet display.

## 4. Component Stylings
*   **Buttons:** Gently rounded corners (pill-shaped or `rounded-full`), Electric Indigo background, Frost White text, with a subtle glow shadow on hover (`shadow-indigo-500/50`).
*   **Cards/Containers:** Subtly rounded corners (`rounded-2xl`), Midnight Slate background, with a very faint, 1px bright upper border (`border-t border-slate-700`) to create a glass-like edge definition.
*   **Inputs/Forms:** Dark backgrounds (`#0F172A`) deeply inset inside Midnight Slate cards, with Muted Steel pill-shaped borders that glow Electric Indigo on focus.

## 5. Layout Principles
*   Generous padding within components (e.g., 24px or 32px standard margins).
*   A clear, structured grid layout. A large hero section commanding the upper fold, leading down into segmented feature cards for the core AI capabilities (Code Analysis, Content Analysis, Plagiarism).
