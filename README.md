# Linying Li — Personal site & blog

An Economist-styled personal homepage and long-form blog, built with
[Astro](https://astro.build) and deployed to GitHub Pages.

## What you get

- **Home page** — Economist-style cover story + latest articles grouped by section
- **Sections** — Economics, Politics, International Relations (edit in `src/config.ts`)
- **Tags** — free-form, one article can have many
- **Archive** — all articles by year and month
- **Search** — built-in, works offline after the page loads (via [Pagefind](https://pagefind.app))
- **About / résumé page** — doubles as your personal homepage (`src/pages/about.astro`)
- **RSS feed** at `/rss.xml`, sitemap at `/sitemap-index.xml`
- **Dark mode** (respects system setting, with a manual toggle)
- **SEO** — Open Graph + Twitter card metadata on every page
- **404 page** — Economist-red and on-brand

Everything is static. No database, no server. Just Markdown files in Git.

## Writing a new article

Create a new `.md` file in `src/content/posts/`. The filename becomes
the URL slug, e.g. `my-new-essay.md` → `/posts/my-new-essay/`.

```markdown
---
title: "Your title here"
description: "One-sentence teaser shown in lists and social cards."
pubDate: 2026-04-19
category: economics              # economics | politics | international-relations
tags: [inflation, central-banks] # free-form; one article can have many
author: "Linying Li"
kicker: "Monetary policy"        # optional — overrides the category label shown above the headline
cover: ./cover.jpg               # optional — put the image next to the markdown file
coverAlt: "A short description for accessibility and captions"
draft: false                     # drafts are hidden from production builds
featured: false                  # set true to promote on the home page
---

Write your article in Markdown. The first paragraph gets a drop cap
automatically. Headings, lists, blockquotes, tables and code blocks
are all styled.

## Subheading

Regular paragraph. You can use **bold**, *italics*, [links](https://example.com),
and standard Markdown.

> Pull-quote. Economist-style red left rule.
```

For rich content (components, custom layouts, JSX), rename to `.mdx`.

### Where to put images

- For a **cover image** — put it next to the Markdown file and reference
  it with a relative path: `cover: ./cover.jpg`. Astro will optimise it
  automatically.
- For **images inside the article** — put them next to the Markdown and
  use `![alt](./image.jpg)`.

## Local development

```bash
npm install
npm run dev         # http://localhost:4321
npm run build       # builds to ./dist and generates the Pagefind index
npm run preview     # preview the production build
```

## Deploying to GitHub Pages

1. Create a new GitHub repository named **`linyingl.github.io`** (this
   name is important — it is what makes the site live at
   `https://linyingl.github.io`).
2. Push this folder to that repo:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin git@github.com:linyingl/linyingl.github.io.git
   git push -u origin main
   ```
3. On GitHub, open **Settings → Pages**, and under "Build and deployment"
   set **Source** to **GitHub Actions**.
4. That's it. Every `git push` to `main` rebuilds and redeploys within a
   minute or two. The workflow lives at `.github/workflows/deploy.yml`.

### Custom domain (optional)

If you later buy a domain (e.g. `linyingli.com`):

1. Add a `CNAME` file in `public/` containing just the domain.
2. Update `site:` in `astro.config.mjs` and `SITE.url` in `src/config.ts`.
3. Point the domain's DNS at GitHub Pages (GitHub's docs have the
   current IPs).

## Customising

- **Site title, author, description, URL** — `src/config.ts`
- **Navigation links** — `src/config.ts` (`NAV`)
- **Categories** — `src/config.ts` (`CATEGORIES`) **and** the enum in
  `src/content.config.ts` (both need to match)
- **Colours, fonts, spacing** — CSS variables at the top of
  `src/styles/global.css`
- **About page** — edit `src/pages/about.astro` directly
- **Homepage "cover story"** — set `SITE.heroSlug` in `src/config.ts`
  to pin a specific article, or leave empty to auto-pick the newest

## Project structure

```
src/
├── config.ts                 # site metadata, categories, nav
├── content.config.ts         # Markdown schema
├── content/
│   └── posts/                # ← your articles go here
├── layouts/
│   ├── BaseLayout.astro      # head, header, footer wrapper
│   └── PostLayout.astro      # single-article layout
├── components/               # Header, Footer, ArticleCard, HeroArticle, …
├── pages/
│   ├── index.astro           # home
│   ├── about.astro           # personal homepage / résumé
│   ├── archive.astro         # by month
│   ├── search.astro          # Pagefind UI
│   ├── 404.astro
│   ├── rss.xml.js
│   ├── posts/                # article routes + paginated list
│   ├── categories/           # section routes
│   └── tags/                 # tag routes
├── styles/global.css         # design tokens
└── utils/posts.ts            # helpers (sorting, tags, reading-time)
```

## Things I deliberately did not include

- **Comments** — GitHub Pages is static, so comments need a third-party
  service. If you want them later, [Giscus](https://giscus.app) uses
  GitHub Issues as the backend and takes about 5 minutes to add.
- **Analytics** — drop in [Plausible](https://plausible.io),
  [Umami](https://umami.is) or Google Analytics via a `<script>` tag in
  `BaseLayout.astro` when you want it.
- **A CMS / admin panel** — by design. The workflow is "write Markdown,
  `git push`, done."

## Licence

Content is yours. The theme scaffolding is free to reuse.
