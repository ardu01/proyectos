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

  ws.close();
  const report = { ok: failures.length === 0, failures, shots: [indexShot] };
  writeFileSync(`${OUT}/report.json`, JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  stop();
  process.exit(failures.length ? 1 : 0);
} catch (error) {
  console.error(error);
  stop();
  process.exit(1);
}
