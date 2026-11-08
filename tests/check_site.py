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
    "red-casa",
    "storage-hub",
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
    "red-casa/",
    "storage-hub/",
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
        self.assertEqual(len(ids), 20)
        self.assertIn(">20</b>proyectos", self.index_text)
        self.assertIn(">3</b><span class=\"dot hi\"></span>prioritarios", self.index_text)
        self.assertIn(">5</b><span class=\"dot dev\"></span>secundarios", self.index_text)
        self.assertIn(">9</b><span class=\"dot ok\"></span>terminados", self.index_text)
        self.assertIn(">3</b><span class=\"dot idea\"></span>aparcados", self.index_text)
        priority = self.index_text.split('id="prioritario"', 1)[1].split('id="secundario"', 1)[0]
        self.assertIn('<span class="count">3</span>', priority)
        self.assertLess(priority.index("sopa-ia"), priority.index("jerry"))
        self.assertLess(priority.index("jerry"), priority.index("zalmann-os"))
        secondary = self.index_text.split('id="secundario"', 1)[1].split('id="terminado"', 1)[0]
        self.assertIn('<span class="count">5</span>', secondary)
        for name in ("avatar-engine", "cad", "os-apple", "red-casa", "storage-hub"):
            self.assertIn(name, secondary)
        self.assertLess(secondary.index("os-apple"), secondary.index("red-casa"))
        self.assertLess(secondary.index("red-casa"), secondary.index("storage-hub"))

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
        self.assertTrue((ROOT / "red-casa" / "index.html").is_file())
        self.assertTrue((ROOT / "storage-hub" / "index.html").is_file())

    def test_internal_links_resolve(self) -> None:
        pages = sorted(ROOT.rglob("*.html"))
        self.assertGreaterEqual(len(pages), 3)
        for page in pages:
            _text, parser = parse(page)
            for href in parser.hrefs:
                resolved = resolve(page, href)
                if resolved is None:
                    continue
                target, frag = resolved
                self.assertTrue(target.is_file(), f"{href} desde {page} no existe ({target})")
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

    def test_lan_pages_follow_the_documentation(self) -> None:
        red_card = self.index_text.split('id="red-casa"', 1)[1].split("</article>", 1)[0]
        hub_card = self.index_text.split('id="storage-hub"', 1)[1].split("</article>", 1)[0]
        self.assertIn('href="red-casa/"', red_card)
        self.assertIn('href="storage-hub/"', hub_card)
        self.assertNotIn("target=", red_card)
        self.assertNotIn("target=", hub_card)
        self.assertIn("En desarrollo", red_card)
        self.assertIn("En desarrollo", hub_card)
        self.assertIn("Según la documentación", red_card)
        self.assertIn("La documentación de estado indica la versión 4.1.0.", hub_card)
        self.assertNotIn("github.com", red_card)
        self.assertNotIn("github.com", hub_card)
        for label in ("desplegado", "instalado en casa", "prueba superada"):
            self.assertNotIn(label, red_card)
            self.assertNotIn(label, hub_card)

        red = (ROOT / "red-casa" / "index.html").read_text(encoding="utf-8")
        hub = (ROOT / "storage-hub" / "index.html").read_text(encoding="utf-8")
        for page, name in ((red, "red-casa"), (hub, "storage-hub")):
            self.assertEqual(page.count("<img "), 1, name)
            self.assertNotIn("galería", page.lower(), name)
            self.assertNotIn("mockup", page.lower(), name)
            self.assertNotIn("seguridad absoluta", page.lower(), name)
            self.assertIn('id="demostracion"', page, name)
            self.assertIn("En desarrollo", page, name)
            self.assertIn('name="viewport" content="width=1124, viewport-fit=cover"', page, name)
            self.assertIn("prefers-color-scheme:dark", page, name)
            self.assertIn('class="skip" href="#contenido"', page, name)
        red_caption = "Interfaz real en modo demostración, con dispositivos ficticios y sin sondeo de red."
        hub_caption = "Interfaz real en demostración aislada con datos ficticios; no muestra equipos ni discos reales."
        self.assertIn(f'alt="{red_caption}"', red)
        self.assertIn(f"<figcaption>{red_caption}</figcaption>", red)
        self.assertIn('src="../assets/red-casa-demo.png"', red)
        self.assertIn(f'alt="{hub_caption}"', hub)
        self.assertIn(f"<figcaption>{hub_caption}</figcaption>", hub)
        self.assertIn('src="../assets/storage-hub-demo.png"', hub)
        self.assertIn("no la muestra como disponible", hub)
        for name, filename in (
            ("red-casa-demo.png", ROOT / "assets" / "red-casa-demo.png"),
            ("storage-hub-demo.png", ROOT / "assets" / "storage-hub-demo.png"),
        ):
            data = filename.read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"), name)
            self.assertNotIn(b"Exif", data, name)
            self.assertGreater(len(data), 1000, name)
        self.assertIn("servicio público", red)
        self.assertIn("desactivados por defecto", red)
        self.assertIn("Funciona por HTTP.", red)
        self.assertIn("no usa UPnP", red)
        self.assertIn("/24", red)
        self.assertIn("MAC privada", red)
        self.assertIn('href="../#red-casa"', red)
        self.assertIn('href="../storage-hub/"', red)
        self.assertIn("La documentación de estado indica la versión 4.1.0.", hub)
        self.assertIn("no lo da por instalado en los equipos de casa", hub)
        self.assertIn("SHA-256", hub)
        self.assertIn("solo lectura", hub)
        self.assertIn("No admite IPv6.", hub)
        self.assertIn("Esta web no ha ejecutado esas pruebas", hub)
        self.assertIn('href="../#storage-hub"', hub)
        self.assertIn('href="../red-casa/"', hub)
        self.assertNotIn("github.com", red)
        self.assertNotIn("github.com", hub)

    def test_no_private_repo_link_secrets_or_invented_claims(self) -> None:
        pages = [INDEX, ROOT / "README.md", *sorted(ROOT.rglob("*.html"))]
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
