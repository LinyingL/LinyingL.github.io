// Site-wide configuration. Edit these to customize your blog.
export const SITE = {
  title: 'Linying Li',
  description:
    'A data journalism blog on political economy and the institutions that hold states together.',
  author: 'Linying Li',
  authorEmail: 'linyingli_hy@outlook.com',
  githubUser: 'linyingl',
  // Use your github.io URL here. If you buy a custom domain later, change it.
  url: 'https://linyingl.github.io',
  locale: 'en',
  postsPerPage: 8,
  // Pinned article (slug). Leave empty to auto-pick the newest article
  // as the home-page cover story.
  heroSlug: '',
} as const;

// Short homepage intro — sits above the cover story.
// Edit freely. Plain text or inline HTML both work.
export const INTRO = {
  heading: 'Linying Li',
  body: `A data journalism blog on political economy and the institutions
    that hold states together — or fail to. Long, slow pieces, meant to
    still be worth reading a year from now.`,
  aboutLabel: 'More about me',
  aboutHref: '/about/',
} as const;

// Category list — add or rename freely.
// "accent" is a Morandi-palette hex used as the small section label colour.
export const CATEGORIES = [
  { slug: 'economics', name: 'Economics', kicker: 'Economics', accent: '#8DA9BA' },
  { slug: 'politics', name: 'Politics', kicker: 'Politics', accent: '#A5B3A0' },
  {
    slug: 'international-relations',
    name: 'International Relations',
    kicker: 'International Relations',
    accent: '#BFA596',
  },
] as const;

export type CategorySlug = (typeof CATEGORIES)[number]['slug'];

export const NAV = [
  { href: '/', label: 'Home' },
  { href: '/categories/economics/', label: 'Economics' },
  { href: '/categories/politics/', label: 'Politics' },
  { href: '/categories/international-relations/', label: 'International' },
  { href: '/archive/', label: 'Archive' },
  { href: '/about/', label: 'About' },
] as const;
