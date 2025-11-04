# Solution Summary: Subroutine HTML Issues

## Problem Statement
1. No graphs showing in any sections in subroutine HTMLs
2. "Called from" section showing "N/A" for all subroutines
3. `!!` comments not showing in the control flow section

## Root Causes Identified

### Issue 1 & 2: Missing Graphs
**Root Cause:** The graphviz system package was not installed. While the Python `graphviz` package was installed via pip, it requires the actual graphviz system binaries (`dot`, etc.) to generate graphs.

**Evidence:**
- When running FORD without graphviz installed: `Warning: Will not be able to generate graphs. Graphviz not installed.`
- The `CalledByGraph`, `CallsGraph`, and control flow graphs are all generated using graphviz
- Template already handles missing graphs gracefully with `{% if procedure.calledbygraph %}`

**Solution:** Install graphviz system package:
- Ubuntu/Debian: `sudo apt-get install graphviz`
- macOS: `brew install graphviz`
- Windows: Download from https://graphviz.org/download/

### Issue 3: Missing `!!` Comments
**Root Cause:** The `LogicBlockExtractor` in `ford/control_flow.py` was skipping ALL comments, including `!!` documentation comments.

**Evidence:**
```python
# Old code at line 698-700:
if not line_stripped or line_stripped.startswith("!"):
    i += 1
    continue
```
This skipped both single `!` comments (which should be ignored) and `!!` documentation comments (which should be preserved).

**Solution:** Modified the logic to:
1. Capture `!!` comments separately from single `!` comments
2. Associate comments with their corresponding blocks/statements
3. Pass comments through the entire processing pipeline
4. Render comments in the HTML template

## Changes Made

### 1. ford/control_flow.py
Added comment handling throughout the control flow extraction:

**LogicBlock dataclass** (lines 494-541):
- Added `comments: List[str]` field
- Added `comment_lines: List[int]` field

**Extract method** (lines 678-1037):
- Differentiate between `!!` (documentation) and `!` (regular) comments
- Track comments in `current_comments` and `current_comment_lines`
- Associate comments with blocks when creating them
- Add comments to stack alongside statements
- Properly handle comments for nested blocks

Key changes:
```python
# Collect documentation comments (!! comments)
if line_stripped.startswith("!!"):
    comment_text = line_stripped[2:].strip()
    current_comments.append(comment_text)
    current_comment_lines.append(line_num)
    i += 1
    continue

# Skip empty lines and other comments (single !)
if not line_stripped or (line_stripped.startswith("!") and not line_stripped.startswith("!!")):
    i += 1
    continue
```

### 2. ford/templates/proc_page.html
Added comment rendering for all logic block types:

**For collapsible blocks** (IF, ELSEIF, ELSE, DO, SELECT, CASE):
```html
{% if block.comments %}
  {% for comment in block.comments %}
    <div class="text-muted mb-1">
      <i class="fa fa-comment me-1"></i><em>{{ comment }}</em>
      {% if block.comment_lines and loop.index0 < block.comment_lines|length %}
        <span class="text-muted small">(line {{ block.comment_lines[loop.index0] }})</span>
      {% endif %}
    </div>
  {% endfor %}
{% endif %}
```

**For statement blocks**:
Updated to show comments even when there are no statements.

## Testing Performed

### Test 1: Graphviz Installation
```bash
# Before: Warning about missing graphviz
Warning: Will not be able to generate graphs. Graphviz not installed.

# After installing graphviz
sudo apt-get install graphviz
ford example-project-file.md
# Success: Generating graphs ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 33/33
```

### Test 2: Comment Extraction
Test file with `!!` comments:
```fortran
subroutine test_sub(x, y)
    integer, intent(in) :: x
    integer, intent(out) :: y
    integer :: i
    
    !! Initialize result
    y = 0
    
    !! Loop through and add
    do i = 1, x
      !! Add i to y
      y = y + i
    end do
end subroutine test_sub
```

**Result:** All three comments appear in the generated HTML:
1. "Initialize result" (before y = 0)
2. "Loop through and add" (before DO loop)
3. "Add i to y" (inside DO loop)

### Test 3: Graph Verification
Checked `doc/proc/increment.html` and confirmed presence of:
1. CalledByGraph SVG (Called From section)
2. CallsGraph SVG (Calls section)
3. Control Flow Graph SVG (Control Flow section)
4. Graph legends/help text

## Impact

### User Impact
- Users now see all graphs when graphviz is installed
- Documentation comments (`!!`) appear in control flow section
- Better code documentation and understanding

### Code Quality
- No breaking changes
- Minimal modifications to existing code
- Backward compatible (gracefully handles missing comments)

## Documentation Updates Needed

### User Guide
Should add note about graphviz system dependency:

> **Note:** Graph generation requires the graphviz system package to be installed. Install it using:
> - Ubuntu/Debian: `sudo apt-get install graphviz`
> - macOS: `brew install graphviz`  
> - Windows: Download from https://graphviz.org/download/
>
> The Python `graphviz` package alone is not sufficient.

### Control Flow Documentation
Should document the `!!` comment feature:

> Documentation comments (lines starting with `!!`) are preserved and displayed in the logic blocks section, providing inline explanations of the code's behavior.

## Verification Steps

To verify the fix works:

1. **Install graphviz system package**
   ```bash
   sudo apt-get install graphviz  # or equivalent for your OS
   ```

2. **Generate documentation**
   ```bash
   ford your-project-file.md
   ```

3. **Verify graphs appear**
   - Open any subroutine HTML page
   - Check "Called From" section - should show graph if there are callers
   - Check "Calls" section - should show graph if procedure calls others
   - Check "Control Flow" section - should show control flow graph

4. **Verify comments appear**
   - Look at "Control Flow" > "Logic Blocks"
   - Comments should appear with italicized text and line numbers
   - Comments should appear in the appropriate blocks (IF, DO, etc.)

## Related Files Modified
- `ford/control_flow.py` - Comment extraction logic
- `ford/templates/proc_page.html` - Comment rendering in HTML

## No Changes Required
- Graph generation code (already working when graphviz is installed)
- Template conditional logic (already handles missing graphs gracefully)
- Other documentation sections (functioning correctly)
