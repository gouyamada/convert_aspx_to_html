# pylint: disable=line-too-long
"""
ASPX ファイルを HTML に変換するスクリプト
- 固定の共通 head セクションを使用
- ローカルの CSS/JS アセットを参照
"""
import re
import argparse
from pathlib import Path


# ---------- regex ----------
PAGE_DIRECTIVE_RE = re.compile(r'<%@\s*Page\s+[^%]*%>', re.IGNORECASE | re.DOTALL)
TITLE_RE = re.compile(r'Title\s*=\s*"([^"]+)"', re.IGNORECASE)

ASP_CONTENT_START_RE = re.compile(r'<asp:Content[^>]*>', re.IGNORECASE)
ASP_CONTENT_END_RE = re.compile(r'</asp:Content>', re.IGNORECASE)

THREE_LINE_HEADER_RE = re.compile(
    r'''
    <%\s*[-]{3,}\s*%>\s*
    <%\s*--\s*(.*?)\s*--\s*%>\s*
    <%\s*[-]{3,}\s*%>
    ''',
    re.IGNORECASE | re.DOTALL | re.VERBOSE
)

ASP_COMMENT_RE = re.compile(r'<%--.*?--%>', re.DOTALL)
ASP_SERVER_BLOCK_RE = re.compile(r'<%[^@].*?%>', re.DOTALL)

# ---------- fixed common head ----------
COMMON_HEAD_TEMPLATE = """<head>
    <meta charset="UTF-8">
    <title>{{TITLE}}</title>

    <!-- CSS -->
    <link rel="stylesheet" href="Content/jquery-ui.min.css">
    <link rel="stylesheet" href="Content/tabulator/tabulator.min.css">

    <!-- JS base -->
    <script src="Scripts/jquery-3.7.1.min.js"></script>
    <script src="Scripts/jquery-ui.min.js"></script>

    <!-- FontAwesome -->
    <script src="Scripts/FontAwesome/fontawesome.min.js"></script>
    <script src="Scripts/FontAwesome/solid.min.js"></script>
    <script src="Scripts/FontAwesome/regular.min.js"></script>

    <!-- App common -->
    <script src="Scripts/mvp.js"></script>
</head>
"""

# ---------- conversion ----------


def convert_aspx_to_html(aspx_path: Path, output_dir: Path):
    """
    ASPX ファイルを HTML に変換して出力ディレクトリに保存する関数

    :param aspx_path: 変換する ASPX ファイルが保存されているディレクトリのパス
    :param output_dir: 変換後の HTML ファイルを保存するディレクトリのパス
    """
    text = aspx_path.read_text(encoding="utf-8")

    # Title 取得
    title = "Untitled Page"
    page_match = PAGE_DIRECTIVE_RE.search(text)
    if page_match:
        title_match = TITLE_RE.search(page_match.group(0))
        if title_match:
            title = title_match.group(1)

    # Page ディレクティブ削除
    text = PAGE_DIRECTIVE_RE.sub("", text)

    # 3行コメントを HTML コメントへ
    def header_replacer(m):
        return f"<!-- ----------- {m.group(1).strip()} ----------- -->"

    text = THREE_LINE_HEADER_RE.sub(header_replacer, text)

    # asp:Content 削除
    text = ASP_CONTENT_START_RE.sub("", text)
    text = ASP_CONTENT_END_RE.sub("", text)

    # ASP.NET コメント削除
    text = ASP_COMMENT_RE.sub("", text)
    text = ASP_SERVER_BLOCK_RE.sub("", text)

    body = text.strip()
    head = COMMON_HEAD_TEMPLATE.replace("{{TITLE}}", title)

    html = f"""<!DOCTYPE html>
<html lang="ja">
{head}
<body>

{body}

</body>
</html>
"""

    output_path = output_dir / f"{aspx_path.stem}.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"Converted: {aspx_path.name} -> {output_path.name}")

# ---------- main ----------


def main():
    """
    メイン関数
    """
    parser = argparse.ArgumentParser(
        description="Convert ASPX files to HTML using fixed common <head> (local assets)"
    )
    parser.add_argument("input_dir", help="ASPX ファイルのディレクトリ")
    parser.add_argument("output_dir", help="HTML 出力ディレクトリ")

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists() or not input_dir.is_dir():
        raise ValueError(f"入力ディレクトリが不正です: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    aspx_files = list(input_dir.glob("*.aspx"))
    if not aspx_files:
        print("aspx ファイルが見つかりませんでした。")
        return

    for aspx_file in aspx_files:
        convert_aspx_to_html(aspx_file, output_dir)


if __name__ == "__main__":
    main()
