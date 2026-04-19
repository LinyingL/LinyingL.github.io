# Obsidian + Templater setup

This folder holds the Templater template for creating new blog posts from
inside Obsidian. It is **not** built by Astro — it lives here purely as
reference.

## One-time setup

1. Open the Blog folder as an Obsidian vault.
2. Install the **Templater** community plugin.
   Settings → Community plugins → Browse → search "Templater" → Install → Enable.
3. Configure Templater:
   Settings → Templater →
   - **Template folder location:** `docs/templates`
   - **Trigger Templater on new file creation:** optional, but handy
   - **Folder templates** (optional): set `src/content/posts/` → `docs/templates/new-post.md`
     so any new file created inside the posts folder auto-applies this template.
4. (Recommended) Add a hotkey:
   Settings → Hotkeys → search "Templater: Open insert template modal" → assign `Cmd+T`.

## Recommended Obsidian settings

- Settings → Files & Links → **Use [[Wikilinks]]**: **off** (Astro does not parse them).
- Settings → Files & Links → **Excluded files**: add `node_modules`, `dist`, `.astro`.
- Settings → Files & Links → **Default location for new notes**: `src/content/posts`.

## Workflow for a new post

1. `Cmd+N` to create a new file inside `src/content/posts/`.
   Name it with the slug you want for the URL (e.g. `end-of-the-dollar.md`).
2. `Cmd+T` (or via command palette: "Templater: Insert template") → choose `new-post`.
3. Pick the category from the dropdown; the cursor lands below the frontmatter.
4. Write.
5. When ready to publish, remove `draft: true`.
6. Commit and push with the Obsidian Git plugin
   (`Cmd+P` → "Git: Create backup"), or from the terminal.

## Notes

- `title` is auto-filled from the Obsidian filename.
- `pubDate` is auto-filled with today's date.
- `slug` is implicit: Astro uses the filename (minus `.md`) as the URL segment.
- `description` stays empty — fill it in yourself; it shows up on the homepage
  list and in social share cards.
