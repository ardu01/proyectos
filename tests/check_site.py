#!/usr/bin/env python3
"""Comprueba el catálogo. La web de Zalmann OS vive en ardu01/zalmann-os-web.

No arranca navegador. Los enlaces internos se resuelven en disco.
"""

from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
WEB = "https://ardu01.github.io/zalmann-os-web/"

ARTICLE_IDS = [
    "sopa-ia",
    "jerry",
    "zalmann-os",
    "avatar-engine",
    "cad",
    "os-apple",
    "orbit-terminal",
    "orbit-os",
    "sopa-web",
    "orbit-web",
    "fairway",
    "tower-defense",
    "clash-progreso",
    "monitor-msi",
    "rea-codex",
    "motor-ligero",
    "axiom-lab",
    "android-deck",
]

REQUIRED_HREFS = [
    "https://ardu01.github.io/sopa-web/",
    "https://ardu01.github.io/jerry-web/",
    "https://ardu01.github.io/SopaCad-web/",
    "https://ardu01.github.io/orbit-web/",
    "https://ardu01.github.io/app-golf/",
    "https://github.com/ardu01/app-golf",
    "https://github.com/ardu01/app-golf/releases/tag/v5.1.6",
    "https://ardu01.github.io/Tower-defense/",
    "https://github.com/ardu01/Tower-defense",
    "https://ardu01.github.io/clash-progreso/",
    "https://github.com/ardu01/clash-progreso",
    "https://ardu01.github.io/axiom-lab/",
    "https://github.com/ardu01/axiom-lab",
    "https://github.com/ardu01/Control-deck",
    "https://github.com/ardu01/Control-deck/tree/HEAD/software/interface",
    "https://github.com/ardu01/sopa-web",
    "https://github.com/ardu01/orbit-web",
    "#prioritario",
    "#secundario",
    "#terminado",
    "#aparcado",
    "https://ardu01.github.io/zalmann-os-web/",
]

KEPT_SNIPPETS = [
    "OS estilo Apple Pi",
    "Entorno Linux para Raspberry Pi inspirado en macOS.",
    "Guardado en local · Próximamente en GitHub",
    "Avatar Engine",
    "SopaCAD",
    "SOPA IA",
    "Jerry",
    "min-width:1124px",
    "--accent:#0071e3",
]

PRIVATE_REPO = "github.com/" + "ardu01/" + "zalmann-os"
SECRET_PATTERNS = [
    re.compile(r"mailto:", re.I),
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    re.compile(r"/home/|/Users/|[A-Za-z]:\\\\"),
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: list[str] = []
        self.h1 = 0
        self.images = 0
        self.skip = False
        self.main = False
        self.lang = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {k: v for k, v in attrs}
        if tag == "html":
            self.lang = data.get("lang") or ""
        if tag == "a":
            href = data.get("href")
            if href:
                self.hrefs.append(href)
            if "skip" in (data.get("class") or "").split():
                self.skip = True
        if tag == "img":
            self.images += 1
        if data.get("id"):
            self.ids.append(data["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.main = True


def parse(path: Path) -> tuple[str, LinkParser]:
    text = path.read_text(encoding="utf-8")
    parser = LinkParser()
    parser.feed(text)
    return text, parser


def resolve(page: Path, href: str) -> tuple[Path, str] | None:
    if re.match(r"^[a-z]+:", href):
        return None
    path, _, frag = href.partition("#")
    if path in ("",):
        target = page
    else:
        target = (page.parent / path).resolve()
        if target.is_dir():
            target = target / "index.html"
    return target, frag


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index_text, cls.index = parse(INDEX)

    def test_catalog_counts_and_order(self) -> None:
        ids = re.findall(r'<article class="card reveal" id="([^"]+)">', self.index_text)
        self.assertEqual(ids, ARTICLE_IDS)
        self.assertEqual(len(ids), 18)
        self.assertIn(">18</b>proyectos", self.index_text)
        self.assertIn(">3</b><span class=\"dot hi\"></span>prioritarios", self.index_text)
        self.assertIn(">3</b><span class=\"dot dev\"></span>secundarios", self.index_text)
        self.assertIn(">9</b><span class=\"dot ok\"></span>terminados", self.index_text)
        self.assertIn(">3</b><span class=\"dot idea\"></span>aparcados", self.index_text)
        priority = self.index_text.split('id="prioritario"', 1)[1].split('id="secundario"', 1)[0]
        self.assertIn('<span class="count">3</span>', priority)
        self.assertLess(priority.index("sopa-ia"), priority.index("jerry"))
        self.assertLess(priority.index("jerry"), priority.index("zalmann-os"))
        secondary = self.index_text.split('id="secundario"', 1)[1].split('id="terminado"', 1)[0]
        self.assertIn('<span class="count">3</span>', secondary)
        for name in ("avatar-engine", "cad", "os-apple"):
            self.assertIn(name, secondary)

    def test_existing_links_and_cards_remain(self) -> None:
        for href in REQUIRED_HREFS:
            self.assertIn(f'href="{href}"', self.index_text)
        for snippet in KEPT_SNIPPETS:
            self.assertIn(snippet, self.index_text)
        card = self.index_text.split('id="zalmann-os"', 1)[1].split("</article>", 1)[0]
        self.assertIn("Escritorio Ubuntu XFCE de inspiración Tahoe.", card)
        self.assertIn("Dock magnificador renderizado por software.", card)
        self.assertIn("Python", card)
        self.assertIn("En desarrollo", card)
        self.assertIn(
            f'href="{WEB}" target="_blank" rel="noopener"',
            card,
        )
        self.assertNotIn('href="zalmann-os/"', self.index_text)
        self.assertIn("Repositorio privado", card)
        self.assertNotIn(PRIVATE_REPO, card)
        self.assertFalse((ROOT / "zalmann-os").exists())

    def test_internal_links_resolve(self) -> None:
        for page, parser in ((INDEX, self.index),):
            for href in parser.hrefs:
                resolved = resolve(page, href)
                if resolved is None:
                    continue
                target, frag = resolved
                self.assertTrue(target.is_file(), f"{href} desde {page.name} no existe ({target})")
                if frag:
                    text = target.read_text(encoding="utf-8")
                    self.assertRegex(text, rf'id="{re.escape(frag)}"')

    def test_no_private_repo_link_secrets_or_invented_claims(self) -> None:
        pages = [INDEX, ROOT / "README.md"]
        for page in pages:
            text = page.read_text(encoding="utf-8")
            self.assertNotIn(PRIVATE_REPO, text, page.name)
            for pattern in SECRET_PATTERNS:
                self.assertIsNone(pattern.search(text), f"{pattern.pattern} en {page.name}")
            self.assertIsNone(re.search(r"github\.com/ardu01/zalmann-os(?!-web)", text), page.name)


if __name__ == "__main__":
    unittest.main()
