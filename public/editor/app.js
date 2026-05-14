/**
 * Blog Editor — Mobile-first editor for linyingl.github.io
 * Uses the GitHub API to read/write Markdown files directly.
 */

(() => {
  'use strict';

  // ─── Config ────────────────────────────────────────────────────────
  const REPO_OWNER = 'LinyingL';
  const REPO_NAME  = 'LinyingL.github.io';
  const POSTS_PATH = 'src/content/posts';
  const BRANCH     = 'main';
  const API_BASE   = 'https://api.github.com';

  // ─── State ─────────────────────────────────────────────────────────
  let token        = '';
  let posts        = [];          // cached list
  let currentFile  = null;        // { path, sha, name, content }
  let originalContent = '';       // for dirty detection
  let isPreview    = false;

  // ─── DOM refs ──────────────────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const screens     = { login: $('#screen-login'), posts: $('#screen-posts'), editor: $('#screen-editor') };
  const tokenInput  = $('#github-token');
  const loginBtn    = $('#btn-login');
  const loginError  = $('#login-error');
  const postsList   = $('#posts-list');
  const searchInput = $('#search-input');
  const filterTabs  = $('#filter-tabs');
  const editorTA    = $('#editor-textarea');
  const previewPane = $('#preview-pane');
  const previewDiv  = $('#preview-content');
  const btnSave     = $('#btn-save');
  const btnBack     = $('#btn-back');
  const btnPreview  = $('#btn-preview-toggle');
  const editorFname = $('#editor-filename');
  const fmToggleBtn = $('#btn-toggle-fm');
  const fmFields    = $('#fm-fields');
  const commitDialog = $('#commit-dialog');
  const commitMsg   = $('#commit-message');
  const commitErr   = $('#commit-error');
  const newPostDialog = $('#new-post-dialog');
  const newPostSlug = $('#new-post-slug');
  const newPostTitle = $('#new-post-title');
  const slugPreview = $('#slug-preview');
  const toast       = $('#toast');
  const toastMsg    = $('#toast-msg');

  // Frontmatter inputs
  const fm = {
    title:       $('#fm-title'),
    description: $('#fm-description'),
    date:        $('#fm-date'),
    category:    $('#fm-category'),
    tags:        $('#fm-tags'),
    kicker:      $('#fm-kicker'),
    draft:       $('#fm-draft'),
    featured:    $('#fm-featured'),
    unlisted:    $('#fm-unlisted'),
  };

  // ─── Helpers ───────────────────────────────────────────────────────
  function showScreen(name) {
    Object.values(screens).forEach(s => s.classList.remove('active'));
    screens[name].classList.add('active');
  }

  function showToast(msg, duration = 2500) {
    toastMsg.textContent = msg;
    toast.classList.remove('hidden');
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.classList.add('hidden'), 300);
    }, duration);
  }

  function setLoading(btn, loading) {
    const text = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.btn-loader');
    if (!text || !loader) return;
    text.classList.toggle('hidden', loading);
    loader.classList.toggle('hidden', !loading);
    btn.disabled = loading;
  }

  async function apiRequest(endpoint, options = {}) {
    const headers = {
      'Authorization': `token ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      ...options.headers,
    };
    const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `HTTP ${res.status}`);
    }
    return res.json();
  }

  // ─── Frontmatter parsing ──────────────────────────────────────────
  function parseFrontmatter(content) {
    const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
    if (!match) return { frontmatter: {}, body: content };
    const yaml = match[1];
    const body = content.slice(match[0].length);
    const frontmatter = {};
    const lines = yaml.split('\n');
    for (const line of lines) {
      const m = line.match(/^(\w[\w-]*):\s*(.*)$/);
      if (m) {
        let val = m[2].trim();
        // Boolean
        if (val === 'true') val = true;
        else if (val === 'false') val = false;
        // Array (simple inline)
        else if (val.startsWith('[') && val.endsWith(']')) {
          val = val.slice(1, -1).split(',').map(s => s.trim().replace(/^["']|["']$/g, '')).filter(Boolean);
        }
        // Quoted string
        else if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
          val = val.slice(1, -1);
        }
        frontmatter[m[1]] = val;
      }
    }
    return { frontmatter, body };
  }

  function buildFrontmatter(data) {
    const lines = ['---'];
    if (data.title) lines.push(`title: "${data.title}"`);
    if (data.description) lines.push(`description: "${data.description}"`);
    if (data.pubDate) lines.push(`pubDate: ${data.pubDate}`);
    if (data.category) lines.push(`category: ${data.category}`);
    if (data.tags && data.tags.length) lines.push(`tags: [${data.tags.map(t => t.trim()).join(', ')}]`);
    if (data.author) lines.push(`author: "${data.author}"`);
    if (data.kicker) lines.push(`kicker: "${data.kicker}"`);
    if (data.cover) lines.push(`cover: ${data.cover}`);
    if (data.coverAlt) lines.push(`coverAlt: "${data.coverAlt}"`);
    lines.push(`draft: ${!!data.draft}`);
    lines.push(`featured: ${!!data.featured}`);
    if (data.unlisted !== undefined) lines.push(`unlisted: ${!!data.unlisted}`);
    lines.push('---');
    return lines.join('\n');
  }

  function getFullContent() {
    const body = editorTA.value;
    const fmData = {
      title:       fm.title.value,
      description: fm.description.value,
      pubDate:     fm.date.value,
      category:    fm.category.value,
      tags:        fm.tags.value ? fm.tags.value.split(',').map(s => s.trim()).filter(Boolean) : [],
      kicker:      fm.kicker.value,
      draft:       fm.draft.checked,
      featured:    fm.featured.checked,
      unlisted:    fm.unlisted.checked,
      // preserve original fields
      author:      currentFile?._fm?.author || 'Linying Li',
      cover:       currentFile?._fm?.cover || '',
      coverAlt:    currentFile?._fm?.coverAlt || '',
    };
    return buildFrontmatter(fmData) + '\n' + body;
  }

  function isDirty() {
    return getFullContent() !== originalContent;
  }

  // ─── Auth ──────────────────────────────────────────────────────────
  function initAuth() {
    const saved = localStorage.getItem('blog_editor_token');
    if (saved) {
      token = saved;
      verifyToken().then(ok => {
        if (ok) {
          showScreen('posts');
          loadPosts();
        }
      });
    }
  }

  async function verifyToken() {
    try {
      const user = await apiRequest('/user');
      return !!user.login;
    } catch {
      return false;
    }
  }

  // ─── Posts list ────────────────────────────────────────────────────
  async function loadPosts() {
    postsList.innerHTML = `<div class="loading-state"><span class="spinner large"></span><p>加载文章中…</p></div>`;
    try {
      // Get directory listing
      const items = await apiRequest(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${POSTS_PATH}?ref=${BRANCH}`);
      // Filter for directories (each post is a directory) and .md/.mdx files
      const postDirs = items.filter(i => i.type === 'dir');
      const postFiles = items.filter(i => i.type === 'file' && /\.(md|mdx)$/.test(i.name));

      // For directories, look for index.md / index.mdx inside
      const allPosts = [];

      for (const file of postFiles) {
        allPosts.push({
          path: file.path,
          name: file.name,
          sha: file.sha,
          slug: file.name.replace(/\.(md|mdx)$/, ''),
        });
      }

      for (const dir of postDirs) {
        try {
          const dirContents = await apiRequest(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${dir.path}?ref=${BRANCH}`);
          const indexFile = dirContents.find(f => /^index\.(md|mdx)$/.test(f.name));
          if (indexFile) {
            allPosts.push({
              path: indexFile.path,
              name: `${dir.name}/${indexFile.name}`,
              sha: indexFile.sha,
              slug: dir.name,
            });
          }
        } catch { /* skip broken dirs */ }
      }

      // Fetch frontmatter for each to display titles
      const detailed = await Promise.all(allPosts.map(async (p) => {
        try {
          const file = await apiRequest(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${p.path}?ref=${BRANCH}`);
          const content = decodeBase64(file.content);
          const { frontmatter } = parseFrontmatter(content);
          return { ...p, sha: file.sha, fm: frontmatter, content };
        } catch {
          return { ...p, fm: {}, content: '' };
        }
      }));

      // Sort by date descending
      detailed.sort((a, b) => {
        const da = a.fm.pubDate || '';
        const db = b.fm.pubDate || '';
        return db.localeCompare(da);
      });

      posts = detailed;
      renderPosts(posts);
    } catch (err) {
      postsList.innerHTML = `<div class="empty-state"><p>加载失败: ${err.message}</p></div>`;
    }
  }

  function renderPosts(list) {
    if (!list.length) {
      postsList.innerHTML = `<div class="empty-state"><p>没有找到文章</p></div>`;
      return;
    }
    postsList.innerHTML = list.map((p, i) => {
      const title = p.fm.title || p.slug;
      const desc = p.fm.description || '';
      const date = p.fm.pubDate || '';
      const cat = p.fm.category || '';
      const isDraft = p.fm.draft === true;
      const isFeatured = p.fm.featured === true;
      const isUnlisted = p.fm.unlisted === true;
      let badges = '';
      if (isDraft) badges += '<span class="badge badge-draft">草稿</span>';
      else badges += '<span class="badge badge-published">已发布</span>';
      if (isFeatured) badges += '<span class="badge badge-featured">推荐</span>';
      if (isUnlisted) badges += '<span class="badge badge-unlisted">未列出</span>';

      return `
        <div class="post-card" data-index="${i}" style="animation-delay: ${i * 0.05}s">
          <div class="post-card-header">
            <div class="post-card-title">${escapeHtml(title)}</div>
            <div class="post-card-badges">${badges}</div>
          </div>
          ${desc ? `<div class="post-card-desc">${escapeHtml(desc)}</div>` : ''}
          <div class="post-card-meta">
            <span>📅 ${date || '无日期'}</span>
            <span>📁 ${cat || '无分类'}</span>
          </div>
        </div>
      `;
    }).join('');

    // Click to edit
    postsList.querySelectorAll('.post-card').forEach(card => {
      card.addEventListener('click', () => {
        const idx = parseInt(card.dataset.index);
        openEditor(posts[idx]);
      });
    });
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ─── Filtering & Search ────────────────────────────────────────────
  let currentFilter = 'all';

  function applyFilters() {
    const query = searchInput.value.toLowerCase();
    let filtered = posts;

    if (currentFilter === 'published') filtered = filtered.filter(p => !p.fm.draft);
    else if (currentFilter === 'draft') filtered = filtered.filter(p => p.fm.draft === true);
    else if (currentFilter === 'unlisted') filtered = filtered.filter(p => p.fm.unlisted === true);

    if (query) {
      filtered = filtered.filter(p =>
        (p.fm.title || '').toLowerCase().includes(query) ||
        (p.fm.description || '').toLowerCase().includes(query) ||
        p.slug.toLowerCase().includes(query)
      );
    }

    renderPosts(filtered);
  }

  // ─── Editor ────────────────────────────────────────────────────────
  function openEditor(post) {
    currentFile = post;
    const { frontmatter, body } = parseFrontmatter(post.content);
    currentFile._fm = frontmatter;

    // Populate frontmatter fields
    fm.title.value       = frontmatter.title || '';
    fm.description.value = frontmatter.description || '';
    fm.date.value        = frontmatter.pubDate || '';
    fm.category.value    = frontmatter.category || 'economics';
    fm.tags.value        = Array.isArray(frontmatter.tags) ? frontmatter.tags.join(', ') : (frontmatter.tags || '');
    fm.kicker.value      = frontmatter.kicker || '';
    fm.draft.checked     = frontmatter.draft === true;
    fm.featured.checked  = frontmatter.featured === true;
    fm.unlisted.checked  = frontmatter.unlisted === true;

    editorTA.value = body;
    originalContent = getFullContent();
    editorFname.textContent = post.slug;
    btnSave.disabled = true;

    // Close preview if open
    isPreview = false;
    previewPane.classList.add('hidden');

    // Collapse frontmatter
    fmFields.classList.add('collapsed');
    fmToggleBtn.classList.remove('open');

    showScreen('editor');
    editorTA.focus();
  }

  function createNewPost(slug, title) {
    const today = new Date().toISOString().slice(0, 10);
    const content = `---
title: "${title}"
description: ""
pubDate: ${today}
category: economics
tags: []
author: "Linying Li"
draft: true
featured: false
---

Write your article here…
`;
    currentFile = {
      path: `${POSTS_PATH}/${slug}/index.md`,
      name: `${slug}/index.md`,
      slug: slug,
      sha: null,  // new file
      content: content,
      fm: { title, pubDate: today, category: 'economics', draft: true },
      _fm: { author: 'Linying Li' },
    };
    const { frontmatter, body } = parseFrontmatter(content);
    currentFile._fm = frontmatter;

    fm.title.value = title;
    fm.description.value = '';
    fm.date.value = today;
    fm.category.value = 'economics';
    fm.tags.value = '';
    fm.kicker.value = '';
    fm.draft.checked = true;
    fm.featured.checked = false;
    fm.unlisted.checked = false;

    editorTA.value = body;
    originalContent = ''; // always dirty for new
    editorFname.textContent = slug;
    btnSave.disabled = false;

    isPreview = false;
    previewPane.classList.add('hidden');
    fmFields.classList.add('collapsed');
    fmToggleBtn.classList.remove('open');

    showScreen('editor');
    editorTA.focus();
  }

  // ─── Save / Commit ─────────────────────────────────────────────────
  async function commitFile(message) {
    const content = getFullContent();
    const encoded = btoa(unescape(encodeURIComponent(content)));

    const payload = {
      message: message || `Update ${currentFile.slug}`,
      content: encoded,
      branch: BRANCH,
    };
    if (currentFile.sha) {
      payload.sha = currentFile.sha;
    }

    const result = await apiRequest(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${currentFile.path}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    // Update SHA
    currentFile.sha = result.content.sha;
    originalContent = content;
    btnSave.disabled = true;
    return result;
  }

  // ─── Preview ───────────────────────────────────────────────────────
  function togglePreview() {
    isPreview = !isPreview;
    if (isPreview) {
      const md = editorTA.value;
      previewDiv.innerHTML = marked.parse(md, { breaks: true, gfm: true });
      previewPane.classList.remove('hidden');
    } else {
      previewPane.classList.add('hidden');
    }
  }

  // ─── Toolbar actions ──────────────────────────────────────────────
  const toolbarActions = {
    bold:     { before: '**', after: '**', placeholder: '粗体文字' },
    italic:   { before: '*', after: '*', placeholder: '斜体文字' },
    heading:  { before: '## ', after: '', placeholder: '标题', lineStart: true },
    link:     { before: '[', after: '](https://)', placeholder: '链接文字' },
    image:    { before: '![', after: '](./image.jpg)', placeholder: '图片描述' },
    quote:    { before: '> ', after: '', placeholder: '引用文字', lineStart: true },
    code:     { before: '```\n', after: '\n```', placeholder: '代码' },
    'list-ul': { before: '- ', after: '', placeholder: '列表项', lineStart: true },
    'list-ol': { before: '1. ', after: '', placeholder: '列表项', lineStart: true },
    hr:       { before: '\n---\n', after: '', placeholder: '' },
    table:    { before: '\n| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| ', after: ' | | |\n', placeholder: '内容' },
    footnote: { before: '[^', after: ']', placeholder: '1' },
  };

  function applyToolbarAction(action) {
    const config = toolbarActions[action];
    if (!config) return;

    const ta = editorTA;
    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    const text = ta.value;
    const selected = text.substring(start, end);

    let insert;
    if (selected) {
      insert = config.before + selected + config.after;
    } else {
      insert = config.before + config.placeholder + config.after;
    }

    ta.value = text.substring(0, start) + insert + text.substring(end);
    const cursorPos = start + config.before.length + (selected || config.placeholder).length;
    ta.setSelectionRange(
      start + config.before.length,
      cursorPos
    );
    ta.focus();
    checkDirty();
  }

  // ─── Base64 decode (handles Unicode) ──────────────────────────────
  function decodeBase64(str) {
    try {
      const cleaned = str.replace(/\n/g, '');
      return decodeURIComponent(escape(atob(cleaned)));
    } catch {
      // fallback
      return atob(str.replace(/\n/g, ''));
    }
  }

  // ─── Dirty check ──────────────────────────────────────────────────
  function checkDirty() {
    btnSave.disabled = !isDirty();
  }

  // ─── Event Listeners ──────────────────────────────────────────────
  function initEvents() {
    // Login
    $('#login-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      loginError.classList.add('hidden');
      token = tokenInput.value.trim();
      if (!token) return;
      setLoading(loginBtn, true);
      try {
        const ok = await verifyToken();
        if (ok) {
          localStorage.setItem('blog_editor_token', token);
          showScreen('posts');
          loadPosts();
          showToast('✅ 连接成功');
        } else {
          throw new Error('Token 无效或权限不足');
        }
      } catch (err) {
        loginError.textContent = err.message;
        loginError.classList.remove('hidden');
      } finally {
        setLoading(loginBtn, false);
      }
    });

    // Toggle token visibility
    $('#toggle-token-vis').addEventListener('click', () => {
      const isPassword = tokenInput.type === 'password';
      tokenInput.type = isPassword ? 'text' : 'password';
      $('.icon-eye').classList.toggle('hidden', !isPassword);
      $('.icon-eye-off').classList.toggle('hidden', isPassword);
    });

    // Logout
    $('#btn-logout').addEventListener('click', () => {
      if (confirm('确定退出？')) {
        localStorage.removeItem('blog_editor_token');
        token = '';
        tokenInput.value = '';
        showScreen('login');
      }
    });

    // Refresh
    $('#btn-refresh').addEventListener('click', () => {
      loadPosts();
      showToast('🔄 刷新中…');
    });

    // Search
    searchInput.addEventListener('input', applyFilters);

    // Filter tabs
    filterTabs.addEventListener('click', (e) => {
      if (!e.target.matches('.filter-tab')) return;
      filterTabs.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      currentFilter = e.target.dataset.filter;
      applyFilters();
    });

    // New post
    $('#btn-new-post').addEventListener('click', () => {
      newPostSlug.value = '';
      newPostTitle.value = '';
      slugPreview.textContent = 'my-new-article';
      newPostDialog.classList.remove('hidden');
      newPostSlug.focus();
    });

    newPostSlug.addEventListener('input', () => {
      slugPreview.textContent = newPostSlug.value || 'my-new-article';
    });

    $('#btn-cancel-new').addEventListener('click', () => {
      newPostDialog.classList.add('hidden');
    });

    $('#btn-create-post').addEventListener('click', () => {
      const slug = newPostSlug.value.trim().toLowerCase().replace(/[^a-z0-9-]/g, '-');
      const title = newPostTitle.value.trim();
      if (!slug || !title) {
        showToast('⚠️ 请填写 slug 和标题');
        return;
      }
      newPostDialog.classList.add('hidden');
      createNewPost(slug, title);
    });

    // Back from editor
    btnBack.addEventListener('click', () => {
      if (isDirty() && !confirm('有未保存的更改，确定返回？')) return;
      showScreen('posts');
      loadPosts(); // refresh list
    });

    // Preview toggle
    btnPreview.addEventListener('click', togglePreview);

    // Frontmatter toggle
    fmToggleBtn.addEventListener('click', () => {
      fmFields.classList.toggle('collapsed');
      fmToggleBtn.classList.toggle('open');
    });

    // Editor dirty check
    editorTA.addEventListener('input', checkDirty);
    Object.values(fm).forEach(input => {
      input.addEventListener('input', checkDirty);
      input.addEventListener('change', checkDirty);
    });

    // Toolbar
    $('#editor-toolbar').addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-action]');
      if (btn) applyToolbarAction(btn.dataset.action);
    });

    // Save button → open commit dialog
    btnSave.addEventListener('click', () => {
      commitMsg.value = `Update ${currentFile.slug}`;
      commitErr.classList.add('hidden');
      commitDialog.classList.remove('hidden');
      commitMsg.focus();
      commitMsg.select();
    });

    // Cancel commit
    $('#btn-cancel-commit').addEventListener('click', () => {
      commitDialog.classList.add('hidden');
    });

    // Confirm commit
    $('#btn-confirm-commit').addEventListener('click', async () => {
      const msg = commitMsg.value.trim() || `Update ${currentFile.slug}`;
      const btn = $('#btn-confirm-commit');
      setLoading(btn, true);
      commitErr.classList.add('hidden');
      try {
        await commitFile(msg);
        commitDialog.classList.add('hidden');
        showToast('✅ 已提交并推送');
      } catch (err) {
        commitErr.textContent = `提交失败: ${err.message}`;
        commitErr.classList.remove('hidden');
      } finally {
        setLoading(btn, false);
      }
    });

    // Tab key in editor
    editorTA.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = editorTA.selectionStart;
        const end = editorTA.selectionEnd;
        editorTA.value = editorTA.value.substring(0, start) + '  ' + editorTA.value.substring(end);
        editorTA.selectionStart = editorTA.selectionEnd = start + 2;
        checkDirty();
      }
    });

    // Close dialogs on overlay click
    [commitDialog, newPostDialog].forEach(dialog => {
      dialog.addEventListener('click', (e) => {
        if (e.target === dialog) dialog.classList.add('hidden');
      });
    });

    // Keyboard shortcut: Ctrl/Cmd+S to save
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (!btnSave.disabled && screens.editor.classList.contains('active')) {
          btnSave.click();
        }
      }
    });
  }

  // ─── Init ──────────────────────────────────────────────────────────
  function init() {
    initEvents();
    initAuth();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
