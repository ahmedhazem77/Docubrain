import DOMPurify from 'dompurify';
import { marked } from 'marked';

marked.setOptions({
    gfm: true,
    breaks: true,
});

export function renderAssistantMarkdown(content) {
    if (!content) {
        return '';
    }

    const html = marked.parse(content, { async: false });

    return DOMPurify.sanitize(html, {
        USE_PROFILES: { html: true },
    });
}
