#!/usr/bin/env node
/**
 * Recorre el catálogo con Chrome headless.
 * La landing está en ardu01.github.io/zalmann-os-web y aquí solo se comprueba el enlace.
 */
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { setTimeout as delay } from "node:timers/promises";

const PORT = 9334;
const WEB = 8765;
const OUT = "/tmp/zalmann-shots";
mkdirSync(OUT, { recursive: true });

const chrome = spawn("google-chrome", [
  "--headless=new",
  "--no-sandbox",
  "--disable-dev-shm-usage",
  "--disable-gpu",
  "--hide-scrollbars",
  "--remote-debugging-port=" + PORT,
  "--user-data-dir=/tmp/chrome-zalmann-profile",
  "--no-first-run",
  "about:blank",
], { stdio: "ignore" });

const server = spawn("python3", ["-m", "http.server", String(WEB), "--bind", "127.0.0.1"], {
  cwd: new URL("..", import.meta.url).pathname,
  stdio: "ignore",
});

function stop() {
  chrome.kill("SIGTERM");
  server.kill("SIGTERM");
}

class CDP {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id && this.pending.has(msg.id)) {
        const job = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) job.reject(new Error(JSON.stringify(msg.error)));
        else job.resolve(msg.result);
      }
    });
  }
  send(method, params = {}, timeout = 15000) {
    const id = ++this.id;
    const packet = JSON.stringify({ id, method, params });
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error("timeout " + method));
      }, timeout);
      this.pending.set(id, {
        resolve: (v) => { clearTimeout(timer); resolve(v); },
        reject: (e) => { clearTimeout(timer); reject(e); },
      });
      this.ws.send(packet);
    });
  }
}

async function waitOk(url, asJson) {
  for (let i = 0; i < 50; i++) {
    try {
      const res = await fetch(url);
      if (res.ok) return asJson ? res.json() : true;
    } catch { /* el servicio aún arranca */ }
    await delay(200);
  }
  throw new Error("sin respuesta de " + url);
}

async function openPage(url) {
  const created = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
  if (!created.ok) throw new Error("json/new " + created.status);
  const tab = await created.json();
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve);
    ws.addEventListener("error", reject);
  });
  const cdp = new CDP(ws);
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: 1280, height: 900, deviceScaleFactor: 1, mobile: false,
  });
  return { cdp, ws, tab };
}

async function settle(cdp) {
  await cdp.send("Runtime.evaluate", {
    expression: `new Promise((resolve) => {
      if (document.readyState === "complete") resolve(true);
      else addEventListener("load", () => resolve(true), { once: true });
    })`,
    awaitPromise: true,
  });
  await delay(150);
}

async function shot(cdp, name, full = false) {
  const { data } = await cdp.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: full,
  });
  const file = `${OUT}/${name}.png`;
  writeFileSync(file, Buffer.from(data, "base64"));
  return file;
}

async function metrics(cdp) {
  const { result } = await cdp.send("Runtime.evaluate", {
    expression: `(() => {
      const doc = document.documentElement;
      const small = [...document.querySelectorAll("a, button")].filter((el) => {
        if (el.classList.contains("skip")) return false;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return false;
        return r.width < 24 || r.height < 24;
      }).map((el) => el.textContent.trim());
      const cs = getComputedStyle(document.body);
      return {
        overflow: doc.scrollWidth > doc.clientWidth + 1,
        scrollWidth: doc.scrollWidth,
        clientWidth: doc.clientWidth,
        h1: document.querySelectorAll("h1").length,
        title: document.title,
        bg: cs.backgroundColor,
        color: cs.color,
        small,
        url: location.href,
      };
    })()`,
    returnByValue: true,
  });
  return result.value;
}

async function setView(cdp, width, height, scheme, mobile) {
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width, height, deviceScaleFactor: 1, mobile,
  });
  await cdp.send("Emulation.setEmulatedMedia", {
    features: [{ name: "prefers-color-scheme", value: scheme }],
  });
  await delay(80);
}

const failures = [];
function check(cond, message) {
  if (!cond) failures.push(message);
}

try {
  await waitOk(`http://127.0.0.1:${PORT}/json/version`, true);
  await waitOk(`http://127.0.0.1:${WEB}/`, false);
  const { cdp, ws } = await openPage(`http://127.0.0.1:${WEB}/`);
  await settle(cdp);

  const wide = [[1280, 900], [1440, 900]];
  for (const scheme of ["light", "dark"]) {
    for (const [w, h] of wide) {
      await setView(cdp, w, h, scheme, false);
      const m = await metrics(cdp);
      check(!m.overflow, `índice desborda en ${scheme} ${w}px (${m.scrollWidth}/${m.clientWidth})`);
    }
  }

  await setView(cdp, 1440, 900, "light", false);
  await cdp.send("Runtime.evaluate", {
    expression: `new Promise((resolve) => {
      const el = document.querySelector("#zalmann-os");
      el.scrollIntoView({ block: "center" });
      const tick = () => el.classList.contains("in") ? resolve(true) : setTimeout(tick, 40);
      setTimeout(() => resolve(false), 2000);
      tick();
    })`,
    awaitPromise: true,
  });
  await delay(1000);
  const indexShot = await shot(cdp, "index-prioritario-desktop-light");
  const indexInfo = await cdp.send("Runtime.evaluate", {
    expression: `(() => {
      const card = document.querySelector("#zalmann-os");
      const link = card.querySelector("a.btn.primary");
      const priority = document.querySelectorAll("#prioritario article").length;
      return { text: card.innerText, href: link.getAttribute("href"), priority, revealed: card.classList.contains("in") };
    })()`,
    returnByValue: true,
  });
  const info = indexInfo.result.value;
  const linkInfo = await cdp.send("Runtime.evaluate", {
    expression: `(() => {
      const link = document.querySelector("#zalmann-os a.btn.primary");
      return { target: link.getAttribute("target"), rel: link.getAttribute("rel") };
    })()`,
    returnByValue: true,
  });
  const link = linkInfo.result.value;
  check(info.priority === 3, "la sección Prioritario no tiene 3 fichas");
  check(info.href === "https://ardu01.github.io/zalmann-os-web/", "la ficha no enlaza la web independiente");
  check(link.target === "_blank" && link.rel === "noopener", "Ver web no abre como enlace externo");
  check(info.text.includes("Zalmann OS"), "no se ve el título de la ficha");
  check(info.revealed, "la ficha no entra en pantalla");
  check(!info.text.includes("github.com"), "la ficha no debe mostrar un enlace a GitHub");

  const sopa = await cdp.send("Runtime.evaluate", {
    expression: `document.querySelector("#cad").innerText`,
    returnByValue: true,
  });
  const sopaText = sopa.result.value;
  check(sopaText.includes("Las 431 pruebas automáticas corresponden a las versiones hasta la 0.41."), "SopaCAD no acota las 431 pruebas a la 0.41");
  check(sopaText.includes("La 0.42 es la primera con el nombre SopaCAD"), "SopaCAD no identifica la 0.42");
  check(sopaText.includes("su validación no está documentada en esta ficha."), "falta el matiz de la 0.42");
  check(!sopaText.includes("Última versión: 0.42"), "sigue el texto que junta las 431 pruebas con la 0.42");

  await setView(cdp, 1440, 900, "dark", false);
  const darkM = await metrics(cdp);
  await setView(cdp, 1440, 900, "light", false);
  const lightM = await metrics(cdp);
  check(darkM.bg !== lightM.bg, "claro y oscuro comparten fondo");
  check(lightM.bg === "rgb(251, 251, 253)", "fondo claro inesperado: " + lightM.bg);
  check(darkM.bg === "rgb(0, 0, 0)", "fondo oscuro inesperado: " + darkM.bg);

  await cdp.send("Runtime.evaluate", {
    expression: `window.scrollTo(0, 0)`,
  });
  await delay(200);
  const countersShot = await shot(cdp, "index-contadores-light");

  await setView(cdp, 1440, 900, "dark", false);
  await cdp.send("Runtime.evaluate", { expression: `window.scrollTo(0, 0)` });
  await delay(200);
  const darkShot = await shot(cdp, "index-contadores-dark");

  await setView(cdp, 1440, 900, "light", false);
  await cdp.send("Runtime.evaluate", { expression: `window.scrollTo(0, 0)` });
  await delay(100);
  const skip = await cdp.send("Runtime.evaluate", {
    expression: `(() => {
      const link = document.querySelector("a.skip");
      const hidden = link.getBoundingClientRect();
      link.focus();
      const shown = link.getBoundingClientRect();
      return {
        href: link.getAttribute("href"),
        hiddenTop: hidden.top,
        top: shown.top,
        width: shown.width,
        height: shown.height,
      };
    })()`,
    returnByValue: true,
  });
  const skipInfo = skip.result.value;
  check(skipInfo.href === "#contenido", "el salto no apunta al contenido");
  check(skipInfo.hiddenTop < 0, "el salto se ve antes de recibir el foco: " + JSON.stringify(skipInfo));
  check(skipInfo.top >= 0 && skipInfo.top < 80 && skipInfo.width >= 24 && skipInfo.height >= 24, "el salto no queda visible al foco: " + JSON.stringify(skipInfo));
  await cdp.send("Runtime.evaluate", {
    expression: `document.querySelector("a.skip").blur(); true`,
    returnByValue: true,
  });

  await cdp.send("Runtime.evaluate", {
    expression: `new Promise((resolve) => {
      const el = document.querySelector("#cad");
      el.scrollIntoView({ block: "center" });
      const tick = () => el.classList.contains("in") ? resolve(true) : setTimeout(tick, 40);
      setTimeout(() => resolve(false), 2000);
      tick();
    })`,
    awaitPromise: true,
  });
  await delay(900);
  const sopaShot = await shot(cdp, "index-sopacad-light");

  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: 390, height: 844, deviceScaleFactor: 3, mobile: true,
  });
  await cdp.send("Runtime.evaluate", { expression: `window.scrollTo(0, 0)` });
  await delay(250);
  const phoneEval = await cdp.send("Runtime.evaluate", {
    expression: `(() => {
      const doc = document.documentElement;
      return {
        clientWidth: doc.clientWidth,
        scrollWidth: doc.scrollWidth,
        innerWidth: window.innerWidth,
        scale: window.visualViewport ? window.visualViewport.scale : null,
        viewport: document.querySelector('meta[name="viewport"]').content,
        minWidth: getComputedStyle(doc).minWidth,
      };
    })()`,
    returnByValue: true,
  });
  const phone = phoneEval.result.value;
  check(String(phone.viewport).includes("width=1124"), "el viewport no fija el lienzo de 1124");
  check(phone.scrollWidth <= phone.clientWidth + 1, `el iPhone desborda (${phone.scrollWidth}/${phone.clientWidth}, escala ${phone.scale})`);
  check(
    phone.clientWidth >= 1100 || (typeof phone.scale === "number" && phone.scale < 0.6),
    "el iPhone no escala el lienzo de escritorio: " + JSON.stringify(phone),
  );
  const phoneShot = await shot(cdp, "index-iphone-light");

  const census = await cdp.send("Runtime.evaluate", {
    expression: `(() => ({
      total: document.querySelector(".stat.total b").textContent,
      priority: document.querySelectorAll("#prioritario article").length,
      secondary: document.querySelectorAll("#secundario article").length,
      done: document.querySelectorAll("#terminado article").length,
      parked: document.querySelectorAll("#aparcado article").length,
      red: document.querySelector("#red-casa a.btn.primary").getAttribute("href"),
      hub: document.querySelector("#storage-hub a.btn.primary").getAttribute("href"),
    }))()`,
    returnByValue: true,
  });
  const counts = census.result.value;
  check(counts.total === "20", "el total no es 20: " + counts.total);
  check(counts.priority === 3 && counts.secondary === 3 && counts.done === 11 && counts.parked === 3, "los grupos no cuadran: " + JSON.stringify(counts));

  function contrastOf(fg, bg) {
    const lin = (v) => {
      const c = v / 255;
      return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    };
    const L = (c) => 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b);
    const a = (L(fg) + 0.05) / (L(bg) + 0.05);
    return a >= 1 ? a : 1 / a;
  }
  async function labelReport() {
    const evaluated = await cdp.send("Runtime.evaluate", {
      expression: `(() => {
        const parse = (s) => {
          const m = String(s).match(/rgba?\\(([^)]+)\\)/);
          if (!m) return null;
          const p = m[1].split(",").map((n) => Number(n.trim()));
          return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
        };
        const composite = (fg, bg) => ({
          r: fg.r * fg.a + bg.r * (1 - fg.a),
          g: fg.g * fg.a + bg.g * (1 - fg.a),
          b: fg.b * fg.a + bg.b * (1 - fg.a),
        });
        const read = (el) => {
          const cs = getComputedStyle(el);
          const card = getComputedStyle(el.closest(".card") || el.parentElement);
          let bg = parse(cs.backgroundColor);
          const base = parse(card.backgroundColor);
          if (bg && bg.a < 1 && base) bg = { ...composite(bg, base), a: 1 };
          return { text: el.textContent.trim(), cls: el.className, color: parse(cs.color), bg };
        };
        return {
          done: [...document.querySelectorAll("#terminado article .pill.ok")].map(read),
          dev: [...document.querySelectorAll("#prioritario article .pill.dev, #secundario article .pill.dev")].map(read),
          pause: document.querySelector("#aparcado h2").childNodes[0].textContent.trim(),
          nav: document.querySelector('a[href="#aparcado"]').textContent.trim(),
        };
      })()`,
      returnByValue: true,
    });
    return evaluated.result.value;
  }
  await setView(cdp, 1440, 900, "light", false);
  await cdp.send("Runtime.evaluate", { expression: `document.querySelector("#terminado").scrollIntoView({block:"start"})` });
  await delay(200);
  const lightLabels = await labelReport();
  check(lightLabels.done.length === 11, "en claro no hay 11 etiquetas verdes");
  check(lightLabels.dev.length === 4, "en claro no hay 4 etiquetas En desarrollo");
  check(lightLabels.pause.startsWith("En pausa") && lightLabels.nav === "En pausa", "el texto visible no es En pausa");
  for (const pill of lightLabels.done) {
    check(pill.text === "Terminado / mantener", "etiqueta verde distinta: " + pill.text);
    check(contrastOf(pill.color, pill.bg) >= 4.5, "contraste verde claro " + contrastOf(pill.color, pill.bg).toFixed(2));
    check(pill.color.g > pill.color.r && pill.color.g > pill.color.b, "la etiqueta de terminado no es verde");
  }
  for (const pill of lightLabels.dev) {
    check(pill.text === "En desarrollo", "etiqueta de desarrollo distinta");
    check(contrastOf(pill.color, pill.bg) >= 4.5, "contraste naranja claro " + contrastOf(pill.color, pill.bg).toFixed(2));
    check(pill.color.r > pill.color.g, "En desarrollo no es naranja");
  }
  const lightDone = await shot(cdp, "etiquetas-terminado-claro");
  await cdp.send("Runtime.evaluate", { expression: `document.querySelector("#sopa-ia").scrollIntoView({block:"center"})` });
  await delay(150);
  const lightDev = await shot(cdp, "etiquetas-prioritario-claro");
  await cdp.send("Runtime.evaluate", { expression: `document.querySelector("#cad").scrollIntoView({block:"center"})` });
  await delay(150);
  const lightCad = await shot(cdp, "etiquetas-sopacad-claro");
  await setView(cdp, 1440, 900, "dark", false);
  await cdp.send("Runtime.evaluate", { expression: `document.querySelector("#terminado").scrollIntoView({block:"start"})` });
  await delay(200);
  const darkLabels = await labelReport();
  check(darkLabels.done.length === 11 && darkLabels.dev.length === 4, "en oscuro faltan etiquetas");
  for (const pill of darkLabels.done) {
    check(contrastOf(pill.color, pill.bg) >= 4.5, "contraste verde oscuro " + contrastOf(pill.color, pill.bg).toFixed(2));
    check(pill.color.g > pill.color.r, "en oscuro la etiqueta de terminado no es verde");
  }
  for (const pill of darkLabels.dev) {
    check(contrastOf(pill.color, pill.bg) >= 4.5, "contraste naranja oscuro " + contrastOf(pill.color, pill.bg).toFixed(2));
    check(pill.color.r > pill.color.b, "en oscuro En desarrollo no es naranja");
  }
  const darkDone = await shot(cdp, "etiquetas-terminado-oscuro");
  await cdp.send("Runtime.evaluate", { expression: `document.querySelector("#sopa-ia").scrollIntoView({block:"center"})` });
  await delay(150);
  const darkDev = await shot(cdp, "etiquetas-prioritario-oscuro");
  check(counts.red === "red-casa/" && counts.hub === "storage-hub/", "las fichas nuevas no enlazan sus páginas");

  const pageShots = [];
  for (const spec of [
    { path: "red-casa/", title: "Red Casa", asset: "red-casa-demo.png", caption: "Interfaz real en modo demostración, con dispositivos ficticios y sin sondeo de red.", light: "vista-web-red-casa-demo", darkShot: "vista-web-red-casa-oscuro", phoneShot: "vista-web-red-casa-iphone" },
    { path: "storage-hub/", title: "Storage Hub", asset: "storage-hub-demo.png", caption: "Interfaz real en demostración aislada con datos ficticios; no muestra equipos ni discos reales.", light: "vista-web-storage-hub-demo", darkShot: "", phoneShot: "vista-web-storage-hub-iphone" },
  ]) {
    const assetRes = await fetch(`http://127.0.0.1:${WEB}/assets/${spec.asset}`);
    check(assetRes.status === 200, `${spec.asset} HTTP ${assetRes.status}`);
    const assetBytes = await assetRes.arrayBuffer();
    check(assetBytes.byteLength > 1000, `${spec.asset} vacío`);
    const opened = await openPage(`http://127.0.0.1:${WEB}/${spec.path}`);
    await settle(opened.cdp);
    await setView(opened.cdp, 1440, 900, "light", false);
    await opened.cdp.send("Runtime.evaluate", {
      expression: `Promise.all([...document.images].map((img) => img.complete && img.naturalWidth > 0 ? true : new Promise((resolve) => { img.addEventListener("load", () => resolve(true), { once: true }); img.addEventListener("error", () => resolve(false), { once: true }); })))`,
      awaitPromise: true,
    });
    await opened.cdp.send("Runtime.evaluate", {
      expression: `document.querySelector("#demostracion").scrollIntoView({ block: "start" })`,
    });
    await delay(200);
    const info = await opened.cdp.send("Runtime.evaluate", {
      expression: `(() => {
        const doc = document.documentElement;
        const back = document.querySelector("a.btn.primary");
        const img = document.querySelector("#demostracion img");
        const caption = document.querySelector("#demostracion figcaption");
        return {
          h1: document.querySelector("h1").textContent,
          imgs: document.images.length,
          naturalWidth: img ? img.naturalWidth : 0,
          naturalHeight: img ? img.naturalHeight : 0,
          alt: img ? img.alt : "",
          caption: caption ? caption.textContent : "",
          label: document.querySelector("#demostracion h2")?.textContent || "",
          github: document.body.innerText.toLowerCase().includes("github.com"),
          overflow: doc.scrollWidth > doc.clientWidth + 1,
          bg: getComputedStyle(document.body).backgroundColor,
          back: back ? back.getAttribute("href") : "",
          displayedWidth: img ? img.getBoundingClientRect().width : 0,
        };
      })()`,
      returnByValue: true,
    });
    const page = info.result.value;
    check(page.h1 === spec.title, `${spec.path} título inesperado: ${page.h1}`);
    check(page.imgs === 1, `${spec.path} imágenes: ${page.imgs}`);
    check(page.naturalWidth > 0 && page.naturalHeight > 0, `${spec.path} naturalWidth ${page.naturalWidth}`);
    check(page.alt === spec.caption, `${spec.path} alt distinto`);
    check(page.caption === spec.caption, `${spec.path} pie distinto`);
    check(page.label === "Demostración", `${spec.path} sin etiqueta visible`);
    check(page.displayedWidth >= 200 && page.displayedWidth <= 1080, `${spec.path} ancho mostrado ${page.displayedWidth}`);
    check(!page.github, `${spec.path} muestra un enlace de GitHub`);
    check(!page.overflow, `${spec.path} desborda en claro`);
    check(page.bg === "rgb(251, 251, 253)", `${spec.path} fondo claro: ${page.bg}`);
    check(page.back.startsWith("../#"), `${spec.path} no vuelve a su ficha: ${page.back}`);
    pageShots.push(await shot(opened.cdp, spec.light));
    await setView(opened.cdp, 1440, 900, "dark", false);
    const darkPage = await opened.cdp.send("Runtime.evaluate", {
      expression: `(() => {
        const doc = document.documentElement;
        return {
          bg: getComputedStyle(document.body).backgroundColor,
          overflow: doc.scrollWidth > doc.clientWidth + 1,
        };
      })()`,
      returnByValue: true,
    });
    check(darkPage.result.value.bg === "rgb(0, 0, 0)", `${spec.path} fondo oscuro: ${darkPage.result.value.bg}`);
    check(!darkPage.result.value.overflow, `${spec.path} desborda en oscuro`);
    if (spec.darkShot) pageShots.push(await shot(opened.cdp, spec.darkShot));
    await opened.cdp.send("Emulation.setDeviceMetricsOverride", {
      width: 390, height: 844, deviceScaleFactor: 3, mobile: true,
    });
    await opened.cdp.send("Runtime.evaluate", {
      expression: `document.querySelector("#demostracion").scrollIntoView({ block: "start" })`,
    });
    await delay(250);
    const phonePage = await opened.cdp.send("Runtime.evaluate", {
      expression: `(() => {
        const doc = document.documentElement;
        return {
          clientWidth: doc.clientWidth,
          scrollWidth: doc.scrollWidth,
          scale: window.visualViewport ? window.visualViewport.scale : null,
        };
      })()`,
      returnByValue: true,
    });
    const phoneView = phonePage.result.value;
    check(phoneView.scrollWidth <= phoneView.clientWidth + 1, `${spec.path} desborda en el iPhone`);
    check(phoneView.clientWidth >= 1100 && phoneView.scale < 0.6, `${spec.path} no escala el lienzo: ${JSON.stringify(phoneView)}`);
    if (spec.phoneShot) pageShots.push(await shot(opened.cdp, spec.phoneShot));
    opened.ws.close();
  }

  ws.close();
  const report = {
    ok: failures.length === 0,
    failures,
    phone,
    counts,
    theme: { light: lightM.bg, dark: darkM.bg },
    shots: [indexShot, countersShot, darkShot, sopaShot, phoneShot, lightDone, lightDev, lightCad, darkDone, darkDev, ...pageShots],
  };
  writeFileSync(`${OUT}/report.json`, JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  stop();
  process.exit(failures.length ? 1 : 0);
} catch (error) {
  console.error(error);
  stop();
  process.exit(1);
}
