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
    "#inicio",
    "#contenido",
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
        self.assertFalse((ROOT / "red-casa").exists())
        self.assertFalse((ROOT / "storage-hub").exists())

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

    def test_counters_match_articles(self) -> None:
        sections = ["prioritario", "secundario", "terminado", "aparcado"]
        labels = {
            "prioritario": "prioritarios",
            "secundario": "secundarios",
            "terminado": "terminados",
            "aparcado": "aparcados",
        }
        total = 0
        for index, section in enumerate(sections):
            start = self.index_text.index(f'id="{section}"')
            end = (
                self.index_text.index(f'id="{sections[index + 1]}"')
                if index + 1 < len(sections)
                else self.index_text.index("</main>")
            )
            chunk = self.index_text[start:end]
            ids = re.findall(r'<article class="card reveal" id="([^"]+)">', chunk)
            shown = int(re.search(r'<span class="count">(\d+)</span>', chunk).group(1))
            self.assertEqual(shown, len(ids), section)
            header = re.search(
                rf'<b>(\d+)</b><span class="dot [^"]+"></span>{labels[section]}',
                self.index_text,
            )
            self.assertIsNotNone(header, labels[section])
            self.assertEqual(int(header.group(1)), len(ids), labels[section])
            total += len(ids)
        total_shown = int(
            re.search(r'class="stat total"><b>(\d+)</b>proyectos', self.index_text).group(1)
        )
        self.assertEqual(total_shown, total)
        self.assertEqual(total, len(ARTICLE_IDS))
        self.assertIn("Fuente de verdad del catálogo: este index.html.", self.index_text)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("fuente de verdad", readme)
        self.assertIn("no debe regenerar", readme)

    def test_sopacad_tests_stop_at_0_41(self) -> None:
        card = self.index_text.split('id="cad"', 1)[1].split("</article>", 1)[0]
        self.assertIn("Antes «CAD Libre»", card)
        self.assertIn("Bocetos, extrusión y operaciones de sólidos (B-rep).", card)
        self.assertIn(
            "Las 431 pruebas automáticas corresponden a las versiones hasta la 0.41.",
            card,
        )
        self.assertIn("La 0.42 es la primera con el nombre SopaCAD", card)
        self.assertIn("su validación no está documentada en esta ficha.", card)
        self.assertNotIn("431 pruebas automáticas superadas. Última versión: 0.42", card)
        self.assertNotIn("0.42, con 431", card)

    def test_accessibility_contract(self) -> None:
        self.assertIn('lang="es"', self.index_text)
        self.assertIn('name="viewport" content="width=1124, viewport-fit=cover"', self.index_text)
        self.assertIn('name="color-scheme" content="light dark"', self.index_text)
        self.assertIn("prefers-color-scheme:dark", self.index_text)
        self.assertIn("prefers-reduced-motion:reduce", self.index_text)
        self.assertIn("forced-colors:active", self.index_text)
        self.assertIn('class="skip" href="#contenido"', self.index_text)
        self.assertIn('id="contenido"', self.index_text)
        self.assertIn('id="inicio"', self.index_text)
        self.assertIn("a:focus-visible", self.index_text)
        self.assertIn('aria-label="Secciones del catálogo"', self.index_text)
        external = re.findall(r"<a\b[^>]*target=\"_blank\"[^>]*>", self.index_text)
        self.assertGreaterEqual(len(external), 18)
        for tag in external:
            self.assertIn("aria-label=", tag, tag)
            self.assertIn("pestaña nueva", tag, tag)
            self.assertIn('rel="noopener"', tag, tag)

    def test_no_private_repo_link_secrets_or_invented_claims(self) -> None:
        pages = [INDEX, ROOT / "README.md"]
        banned = [
            "github.com/" + "ardu01/" + "red-casa",
            "github.com/" + "ardu01/" + "storage-hub",
            "192.168.",
            "BEGIN OPENSSH PRIVATE KEY",
        ]
        mac = re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")
        for page in pages:
            text = page.read_text(encoding="utf-8")
            self.assertNotIn(PRIVATE_REPO, text, page.name)
            for pattern in SECRET_PATTERNS:
                self.assertIsNone(pattern.search(text), f"{pattern.pattern} en {page.name}")
            self.assertIsNone(re.search(r"github\.com/ardu01/zalmann-os(?!-web)", text), page.name)
            self.assertIsNone(mac.search(text), page.name)
            for item in banned:
                self.assertNotIn(item, text, page.name)


if __name__ == "__main__":
    unittest.main()
