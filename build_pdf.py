#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_pdf.py — 把課程 md 生成「學生手冊」「教師手冊」HTML，再用 Chrome 印成 PDF。
（取代原本放 /tmp 會弄丟的版本——這支進 repo，跨機器可重生。）

用法（這台已驗證）：
  uv run --with markdown python build_pdf.py        # 生 HTML
  # 再各跑一次 Chrome headless 印 PDF（兩本手冊各一次）：
  # Windows:
  #   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu --no-pdf-header-footer \
  #     --print-to-pdf="打造你的AI雙人小隊-學生手冊.pdf" "slides/打造你的AI雙人小隊-學生手冊.html"
  #   （教師手冊把上面兩個檔名的「學生」換成「教師」再跑一次）
  # Mac:
  #   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer \
  #     --print-to-pdf="打造你的AI雙人小隊-學生手冊.pdf" "slides/打造你的AI雙人小隊-學生手冊.html"

Windows 字型用「Microsoft JhengHei」；Mac 用「PingFang TC」，字型堆疊都列了。
"""
import re, pathlib, markdown

HERE = pathlib.Path(__file__).parent

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "PingFang TC","Microsoft JhengHei","Heiti TC","Noto Sans TC",sans-serif;
  color:#1A1A1A; line-height:1.75; font-size:11.5pt; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.cover { height: 250mm; display:flex; flex-direction:column; justify-content:center;
  align-items:center; text-align:center; background:#F4ECD8; border-radius:8px; page-break-after:always; }
.cover .drop { font-size:56pt; }
.cover .ct { font-size:34pt; color:#0E7C7B; margin:6pt 0 2pt; border:none; }
.cover .cs { font-size:15pt; color:#1A1A1A; margin:0 0 18pt; }
.cover .cm { font-size:11pt; color:#0E7C7B; }
.cover .cf { font-size:10pt; color:#777; margin-top:30pt; }
.doc { page-break-before: always; }
h1 { font-size:21pt; color:#0E7C7B; border-bottom:3px solid #D9A441; padding-bottom:6px; margin-top:0; }
h2 { font-size:15.5pt; color:#0E7C7B; margin-top:20px; border-left:5px solid #D9A441; padding-left:10px; }
h3 { font-size:13pt; color:#1A1A1A; margin-top:16px; }
p { margin:7px 0; }
a { color:#0E7C7B; text-decoration:none; }
strong { color:#0E7C7B; }
code { background:#f2ede0; padding:1px 5px; border-radius:4px; font-size:10pt;
  font-family:"SF Mono",Menlo,Consolas,monospace; color:#7a4a00; }
pre { background:#1A1A1A; color:#F4ECD8; padding:11px 14px; border-radius:8px;
  overflow-x:auto; page-break-inside:avoid; }
pre code { background:none; color:#F4ECD8; padding:0; font-size:9.5pt; }
blockquote { border-left:4px solid #0E7C7B; background:#f6f1e6; margin:10px 0;
  padding:7px 14px; border-radius:0 6px 6px 0; color:#333; }
table { border-collapse:collapse; width:100%; margin:12px 0; font-size:10pt; page-break-inside:avoid; }
th,td { border:1px solid #d8cdb0; padding:6px 9px; text-align:left; vertical-align:top; }
th { background:#0E7C7B; color:#fff; }
tr:nth-child(even) td { background:#faf6ec; }
hr { border:none; border-top:1px dashed #c9bd9e; margin:18px 0; }
ul,ol { margin:6px 0 6px 4px; padding-left:22px; }
li { margin:3px 0; }
"""

def md_to_html(path):
    text = (HERE / path).read_text(encoding="utf-8")
    # 剝掉內部審稿標記「【洄瀾草稿】…」整行（不進對外 PDF）
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("【洄瀾草稿】"))
    return markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])

def page(title, cover, docs):
    body = [f'<section class="cover">{cover}</section>']
    for d in docs:
        body.append(f'<section class="doc">{md_to_html(d)}</section>')
    html = (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
            f'<title>{title}</title><style>{CSS}</style></head><body>'
            + "\n".join(body) + "</body></html>")
    out = HERE / "slides" / f"{title}.html"
    out.write_text(html, encoding="utf-8")
    print("wrote", out)

STUDENT_COVER = (
    '<div class="drop">💧</div>'
    '<h1 class="ct">打造你的 AI 雙人小隊</h1>'
    '<p class="cs">不用寫程式，學會當 AI 團隊的小隊長</p>'
    '<p class="cm">通識課學生手冊 ｜ 學生講義 ＋ 安裝設定指南 ＋ 給 AI 的指令包</p>'
    '<p class="cf">國立東華大學 洄瀾學院通識教育中心 ｜ 洄瀾鏡像團隊 出品</p>'
)
TEACHER_COVER = (
    '<div class="drop">📘</div>'
    '<h1 class="ct">打造你的 AI 雙人小隊</h1>'
    '<p class="cs">教師手冊 ｜ 帶通識生組一支會合作的 AI 小隊</p>'
    '<p class="cm">教學目標 ＋ 課前準備 ＋ 課堂流程 ＋ 評量 ＋ 現場處理</p>'
    '<p class="cf">國立東華大學 洄瀾學院通識教育中心 ｜ 洄瀾鏡像團隊 出品</p>'
)

page("打造你的AI雙人小隊-學生手冊", STUDENT_COVER, ["01_學生講義.md", "02_安裝設定指南.md", "04_給AI的指令包.md"])
page("打造你的AI雙人小隊-教師手冊", TEACHER_COVER, ["03_教師手冊.md"])
