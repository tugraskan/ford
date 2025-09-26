import re
import os

# 1) single-! comment on a VAR decl
VAR_COMMENT_RE = re.compile(
    r'^(?P<indent>\s*)'
    r'(?P<type>integer|real|double\s+precision|logical|character\s*\(.*?\)|complex)'
    r'(?=\s|::)'
    r'(?P<body>[^!\n]*::[^!\n]*?)'
    r'!(?!\!)'                  # one bang, not a “!!”
    r'(?P<comment>.*)$',
    re.IGNORECASE
)

# 2) VAR decl with assignment but no !
VAR_NO_COMMENT_RE = re.compile(
    r'^(?P<indent>\s*)'
    r'(?P<type>integer|real|double\s+precision|logical|character\s*\(.*?\)|complex)'
    r'(?=\s|::)'
    r'(?P<body>[^!\n]*::[^!\n]*?)'
    r'\s*(?P<rest>=\s*[^!\n]+?)\s*$',
    re.IGNORECASE
)

# 3) any top-level decl with no ! at all
TOP_VAR_RE = re.compile(
    r'^(?P<indent>\s*)'
    r'(?P<type>integer|real|double\s+precision|logical|character\s*\(.*?\)|complex)'
    r'(?=\s|::)'
    r'.*::',
    re.IGNORECASE
)

# 4) continuation lines starting with single !
CONT_RE = re.compile(r'^(?P<indent>\s*)!(?!\!)(?P<rest>.*)$')

def bump_declaration_comments(filepath):
    """
    In-place:
    - bump single-! → !! on top-level decls
    - add blank !! if no comment or assignment
    - convert continuation ! lines in var blocks to !!
    """
    lines = open(filepath).read().splitlines(keepends=True)
    out = []
    in_var_block = False

    for line in lines:
        # 1) bump single-! on decl
        m = VAR_COMMENT_RE.match(line)
        if m:
            out.append(f"{m.group('indent')}{m.group('type')}{m.group('body')}!!{m.group('comment')}\n")
            in_var_block = True
            continue

        # 2) assignment with no comment
        m2 = VAR_NO_COMMENT_RE.match(line)
        if m2:
            out.append(f"{m2.group('indent')}{m2.group('type')}{m2.group('body')}{m2.group('rest')} !!\n")
            in_var_block = True
            continue

        # 3) any decl with no !
        tv = TOP_VAR_RE.match(line)
        if tv and '!' not in line:
            out.append(line.rstrip('\n') + ' !!\n')
            in_var_block = True
            continue

        # 4) continuation of var-block comment
        if in_var_block:
            mc = CONT_RE.match(line)
            if mc:
                out.append(f"{mc.group('indent')}!!{mc.group('rest')}\n")
                continue
            # reset when leaving block
            if not line.lstrip().startswith('!'):
                in_var_block = False

        # 5) leave others
        out.append(line)

    with open(filepath, 'w') as f:
        f.writelines(out)


def bump_folder(folder):
    """
    Walk folder for .f90 files and apply the bump
    """
    for root, _, files in os.walk(folder):
        for fn in files:
            if fn.lower().endswith('.f90'):
                bump_declaration_comments(os.path.join(root, fn))




if __name__ == '__main__':
    folder = r'C:\Users\taci.ugraskan\source\repos\swatplus_ug\src'
    bump_folder(folder)