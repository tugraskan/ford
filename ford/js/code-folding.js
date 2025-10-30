/**
 * Code folding functionality for Fortran source code
 * Provides VS Code-style collapsible blocks for do/if/select/etc.
 */

(function() {
    'use strict';

    // Fortran block patterns: [start_regex, end_regex, block_name]
    // Ordered from most specific to least specific
    const BLOCK_PATTERNS = [
        [/^\s*(do)\s+/i, /^\s*end\s+do\b/i, 'do'],
        [/^\s*(if)\s*\(/i, /^\s*end\s+if\b/i, 'if'],
        [/^\s*(select\s+case)\s*\(/i, /^\s*end\s+select\b/i, 'select'],
        [/^\s*(where)\s*\(/i, /^\s*end\s+where\b/i, 'where'],
        [/^\s*(forall)\s*\(/i, /^\s*end\s+forall\b/i, 'forall'],
        [/^\s*(associate)\s*\(/i, /^\s*end\s+associate\b/i, 'associate'],
        [/^\s*(block)(?:\s|$)/i, /^\s*end\s+block\b/i, 'block'],
        [/^\s*(critical)(?:\s|$)/i, /^\s*end\s+critical\b/i, 'critical'],
        [/^\s*(interface)\b/i, /^\s*end\s+interface\b/i, 'interface'],
        [/^\s*(subroutine)\s+\w/i, /^\s*end\s+subroutine\b/i, 'subroutine'],
        [/^\s*(function)\s+\w/i, /^\s*end\s+function\b/i, 'function'],
        [/^\s*(type)(?:\s|,)/i, /^\s*end\s+type\b/i, 'type'],
        [/^\s*(module)\s+\w/i, /^\s*end\s+module\b/i, 'module'],
        [/^\s*(program)\s+\w/i, /^\s*end\s+program\b/i, 'program'],
    ];

    /**
     * Get text content from line including all siblings until next line anchor
     */
    function getFullLineText(lineAnchor) {
        let text = '';
        let node = lineAnchor;
        
        while (node) {
            if (node.nextSibling) {
                node = node.nextSibling;
                if (node.nodeName === 'A' && node.id && node.id.startsWith('ln-')) {
                    break;
                }
                if (node.nodeType === Node.TEXT_NODE) {
                    text += node.textContent;
                } else if (node.nodeName === 'SPAN') {
                    text += node.textContent;
                }
            } else {
                break;
            }
        }
        
        return text;
    }

    /**
     * Find all code blocks and wrap them for folding
     */
    function addCodeFolding() {
        const codeBlocks = document.querySelectorAll('.hl.codehilite pre, .highlight pre');
        
        codeBlocks.forEach(function(pre) {
            // Get all line anchors
            const lines = Array.from(pre.querySelectorAll('a[id^="ln-"]'));
            if (lines.length === 0) return;

            // Build an array of line info
            const lineInfo = lines.map((anchor, idx) => ({
                anchor: anchor,
                idx: idx,
                text: getFullLineText(anchor)
            }));

            let blockIdCounter = 0;

            // Process from first to last, finding ALL blocks (including nested)
            for (let i = 0; i < lineInfo.length; i++) {
                // Skip if this line already has a fold icon (already processed as a start line)
                if (lineInfo[i].anchor.previousSibling && 
                    lineInfo[i].anchor.previousSibling.classList &&
                    lineInfo[i].anchor.previousSibling.classList.contains('code-fold-icon')) {
                    continue;
                }

                const text = lineInfo[i].text;

                // Try each pattern
                for (const [startPattern, endPattern, blockType] of BLOCK_PATTERNS) {
                    if (!startPattern.test(text)) continue;

                    // Find matching end
                    let depth = 1;
                    let endIdx = -1;

                    for (let j = i + 1; j < lineInfo.length; j++) {
                        const jText = lineInfo[j].text;
                        
                        if (startPattern.test(jText)) {
                            depth++;
                        } else if (endPattern.test(jText)) {
                            depth--;
                            if (depth === 0) {
                                endIdx = j;
                                break;
                            }
                        }
                    }

                    if (endIdx === -1) break; // No matching end found

                    // Create fold structure
                    blockIdCounter++;
                    const blockId = `code-fold-${blockIdCounter}`;
                    const endText = lineInfo[endIdx].text.trim();

                    // Wrap this block
                    wrapBlock(lineInfo, i, endIdx, blockId, blockType, endText);

                    break; // Found a match, move to next line
                }
            }
        });
    }

    /**
     * Wrap a block with folding UI
     */
    function wrapBlock(lineInfo, startIdx, endIdx, blockId, blockType, endText) {
        const startAnchor = lineInfo[startIdx].anchor;
        
        // Create wrapper div
        const wrapper = document.createElement('div');
        wrapper.className = 'code-fold-block';
        wrapper.id = blockId;
        wrapper.dataset.blockType = blockType;

        // Create fold icon span (insert before the line anchor)
        const icon = document.createElement('span');
        icon.className = 'code-fold-icon';
        icon.innerHTML = '▼';
        icon.dataset.blockId = blockId;
        icon.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleBlock(blockId);
        };

        // Create preview span (shown when collapsed)
        const preview = document.createElement('span');
        preview.className = 'code-fold-preview';
        preview.dataset.blockId = blockId;
        preview.style.display = 'none';
        preview.innerHTML = ' <span class="ellipsis">…</span> <span class="end-text">' + 
            escapeHtml(endText) + '</span>';

        // Insert icon and preview right before the start line anchor
        startAnchor.parentNode.insertBefore(icon, startAnchor);
        startAnchor.parentNode.insertBefore(preview, startAnchor);

        // Mark the start line
        startAnchor.classList.add('code-fold-start');
        startAnchor.dataset.blockId = blockId;

        // Wrap content lines (between start and end, exclusive)
        if (startIdx + 1 < endIdx) {
            const contentWrapper = document.createElement('span');
            contentWrapper.className = 'code-fold-content';
            contentWrapper.dataset.blockId = blockId;

            // Collect all nodes between start and end anchors
            let currentNode = startAnchor;
            const nodesToWrap = [];
            let foundEnd = false;

            while (currentNode && !foundEnd) {
                currentNode = currentNode.nextSibling;
                if (!currentNode) break;

                if (currentNode === lineInfo[endIdx].anchor) {
                    foundEnd = true;
                    break;
                }

                // Check if we've reached a line in our range
                const isLineInRange = lineInfo.slice(startIdx + 1, endIdx).some(info => 
                    info.anchor === currentNode
                );

                if (isLineInRange || currentNode.nodeType === Node.TEXT_NODE || 
                    currentNode.nodeName === 'SPAN') {
                    nodesToWrap.push(currentNode);
                }
            }

            // Wrap the nodes
            if (nodesToWrap.length > 0) {
                const parent = startAnchor.parentNode;
                parent.insertBefore(contentWrapper, nodesToWrap[0]);
                nodesToWrap.forEach(node => contentWrapper.appendChild(node));
            }
        }

        // Mark the end line
        const endAnchor = lineInfo[endIdx].anchor;
        endAnchor.classList.add('code-fold-end');
        endAnchor.dataset.blockId = blockId;
    }

    /**
     * Toggle fold state
     */
    function toggleBlock(blockId) {
        const icon = document.querySelector(`.code-fold-icon[data-block-id="${blockId}"]`);
        const preview = document.querySelector(`.code-fold-preview[data-block-id="${blockId}"]`);
        const content = document.querySelector(`.code-fold-content[data-block-id="${blockId}"]`);
        const endLine = document.querySelector(`.code-fold-end[data-block-id="${blockId}"]`);

        if (!icon) return;

        const isCollapsed = icon.innerHTML === '▶';

        if (isCollapsed) {
            // Expand
            icon.innerHTML = '▼';
            if (preview) preview.style.display = 'none';
            if (content) content.style.display = '';
            if (endLine) endLine.style.display = '';
        } else {
            // Collapse
            icon.innerHTML = '▶';
            if (preview) preview.style.display = 'inline';
            if (content) content.style.display = 'none';
            if (endLine) endLine.style.display = 'none';
        }
    }

    /**
     * Escape HTML
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addCodeFolding);
    } else {
        addCodeFolding();
    }

})();
