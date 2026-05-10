import { getCollection, type CollectionEntry } from 'astro:content';
import { CATEGORIES, type CategorySlug } from '../config';

export type Post = CollectionEntry<'posts'>;

const isProd = import.meta.env.PROD;

export async function getAllPosts(): Promise<Post[]> {
  const posts = await getCollection('posts', ({ data }) =>
    isProd ? !data.draft && !data.unlisted : true
  );
  return posts.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );
}

export async function getPostsByCategory(slug: CategorySlug): Promise<Post[]> {
  const all = await getAllPosts();
  return all.filter((p) => p.data.category === slug);
}

export async function getAllTags(): Promise<Map<string, number>> {
  const all = await getAllPosts();
  const counts = new Map<string, number>();
  for (const p of all) {
    for (const t of p.data.tags) {
      counts.set(t, (counts.get(t) ?? 0) + 1);
    }
  }
  return counts;
}

export async function getPostsByTag(tag: string): Promise<Post[]> {
  const all = await getAllPosts();
  return all.filter((p) => p.data.tags.includes(tag));
}

export function getCategoryMeta(slug: string) {
  return CATEGORIES.find((c) => c.slug === slug);
}

export function tagSlug(tag: string): string {
  return tag
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\u4e00-\u9fff]+/g, '-')
    .replace(/^-|-$/g, '');
}

export function tagFromSlug(slug: string, tags: string[]): string | undefined {
  return tags.find((t) => tagSlug(t) === slug);
}

// Reading-time estimate: 250 words/min English, 500 chars/min Chinese.
// Rough heuristic — good enough for a kicker.
export function readingTime(body: string): number {
  const chinese = (body.match(/[\u4e00-\u9fff]/g) ?? []).length;
  const englishWords = body
    .replace(/[\u4e00-\u9fff]/g, ' ')
    .split(/\s+/)
    .filter(Boolean).length;
  const minutes = chinese / 500 + englishWords / 250;
  return Math.max(1, Math.round(minutes));
}

export function formatDate(d: Date, locale = 'en-US'): string {
  return d.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function formatDateShort(d: Date, locale = 'en-US'): string {
  return d.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function groupByYearMonth(posts: Post[]) {
  const groups = new Map<number, Map<number, Post[]>>();
  for (const p of posts) {
    const y = p.data.pubDate.getUTCFullYear();
    const m = p.data.pubDate.getUTCMonth();
    if (!groups.has(y)) groups.set(y, new Map());
    const byMonth = groups.get(y)!;
    if (!byMonth.has(m)) byMonth.set(m, []);
    byMonth.get(m)!.push(p);
  }
  return groups;
}

// Scrape the first image URL from a post's raw body. Used as a hero
// fallback when a post has no explicit `cover` in its frontmatter.
// Matches both Markdown (`![alt](url)`) and HTML `<img src="url">` forms.
export function extractFirstImage(body: string): string | undefined {
  if (!body) return undefined;
  const md = body.match(/!\[[^\]]*\]\(([^)\s]+)(?:\s+["'][^"']*["'])?\)/);
  if (md) return md[1];
  const html = body.match(/<img[^>]+src=["']([^"']+)["']/i);
  if (html) return html[1];
  return undefined;
}

export async function getAdjacentPosts(current: Post) {
  const all = await getAllPosts();
  const idx = all.findIndex((p) => p.id === current.id);
  return {
    newer: idx > 0 ? all[idx - 1] : undefined,
    older: idx >= 0 && idx < all.length - 1 ? all[idx + 1] : undefined,
  };
}
