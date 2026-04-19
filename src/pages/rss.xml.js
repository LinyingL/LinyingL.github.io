import rss from '@astrojs/rss';
import { getAllPosts } from '../utils/posts';
import { SITE } from '../config';

export async function GET(context) {
  const posts = await getAllPosts();
  return rss({
    title: SITE.title,
    description: SITE.description,
    site: context.site ?? SITE.url,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description ?? '',
      pubDate: post.data.pubDate,
      link: `/posts/${post.id}/`,
      categories: [post.data.category, ...post.data.tags],
    })),
    customData: `<language>${SITE.locale}</language>`,
  });
}
