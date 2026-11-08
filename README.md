# Ardu Solutions | Portfolio de Proyectos

**Portfolio tecnológico y catálogo centralizado de los proyectos desarrollados por Miguel Rodríguez Saiz.**

[![Website](https://img.shields.io/badge/Website-Online-2563EB?style=flat-square)](https://ardu01.github.io/proyectos/)
![HTML5](https://img.shields.io/badge/HTML5-Web-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Design-1572B6?style=flat-square&logo=css&logoColor=white)
![GitHub Pages](https://img.shields.io/badge/Hosting-GitHub_Pages-222222?style=flat-square&logo=github)
![Status](https://img.shields.io/badge/Status-Active-16A34A?style=flat-square)

---

## Descripción

**Ardu Solutions Projects** es una plataforma web diseñada para reunir, organizar y presentar los proyectos tecnológicos desarrollados por **Miguel Rodríguez Saiz** bajo la identidad de Ardu Solutions.

El catálogo funciona como punto de acceso central a un ecosistema de desarrollos que abarca inteligencia artificial, ingeniería de software, sistemas operativos, aplicaciones de escritorio, electrónica, hardware, herramientas de productividad y videojuegos.

Su objetivo es ofrecer una visión estructurada de cada proyecto, documentar su evolución y facilitar el acceso a sus respectivas páginas web y repositorios públicos.

**Desarrollo:** Miguel Rodríguez Saiz  
**Organización:** Ardu Solutions  
**Categoría:** Desarrollo Web / Portfolio / Gestión de Proyectos  
**Plataforma:** Web  
**Publicación:** GitHub Pages

### Acceder a la plataforma

**[Ver portfolio de proyectos](https://ardu01.github.io/proyectos/)**

## Características principales

### Catálogo centralizado

La plataforma permite consultar los proyectos desde una única interfaz, con información organizada sobre:

- Nombre e identificación del proyecto.
- Descripción y propósito.
- Categoría tecnológica.
- Estado actual de desarrollo.
- Prioridad dentro del ecosistema.
- Enlaces a webs, repositorios y recursos disponibles.
- Información sobre su evolución.

### Organización por estados

Los proyectos se distribuyen en cuatro grupos principales:

| Categoría | Descripción |
|---|---|
| Prioritario | Proyectos estratégicos en desarrollo activo. |
| Secundario | Desarrollos en curso con prioridad intermedia. |
| Terminado | Proyectos finalizados o en mantenimiento. |
| En pausa | Ideas y desarrollos temporalmente detenidos. |

Esta clasificación permite identificar las áreas de trabajo actuales y consultar el histórico de desarrollos.

### Interfaz y experiencia de usuario

La web utiliza un diseño minimalista inspirado en interfaces de software modernas.

Entre sus características se incluyen:

- Diseño de tarjetas para presentar proyectos.
- Interfaz con navegación por categorías.
- Compatibilidad con temas claro y oscuro según el sistema.
- Transiciones y animaciones de interfaz.
- Indicadores visuales de estado y prioridad.
- Contadores de proyectos por categoría.
- Enlaces directos a los recursos publicados.
- Adaptación específica del lienzo de escritorio para su visualización en iPhone.
- Consideraciones de accesibilidad, como navegación mediante teclado y reducción de movimiento.

La plataforma está desarrollada como un sitio estático, sin necesidad de servicios de backend.

## Ecosistema de proyectos

El catálogo reúne desarrollos de diferentes disciplinas tecnológicas.

### Inteligencia artificial

**SOPA IA**

Plataforma de inteligencia artificial local orientada a ejecutar y gestionar modelos de lenguaje en equipos personales.

[Web de SOPA IA](https://ardu01.github.io/sopa-web/)

**Jerry**

Proyecto de asistente de inteligencia artificial para escritorio, con un enfoque en la interacción y la coordinación de agentes.

[Web de Jerry](https://ardu01.github.io/jerry-web/)

### Sistemas operativos

**Zalmann OS**

Entorno de escritorio basado en Ubuntu y XFCE, con personalización visual y componentes propios de interfaz.

[Web de Zalmann OS](https://ardu01.github.io/zalmann-os-web/)

### Ingeniería y desarrollo de software

El catálogo también incorpora iniciativas relacionadas con diseño CAD, herramientas técnicas, desarrollo de aplicaciones y soluciones de ingeniería.

### Hardware y electrónica

Proyectos de diseño y fabricación de componentes, sistemas experimentales y plataformas de control.

### Aplicaciones y entretenimiento

Herramientas de productividad, aplicaciones web, utilidades y videojuegos desarrollados dentro del ecosistema.

> La lista completa, su clasificación y sus estados actualizados se encuentran en el catálogo web.

## Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| HTML5 | Estructura y contenido de la plataforma. |
| CSS3 | Diseño visual, temas y animaciones. |
| JavaScript | Comportamiento e interactividad del sitio. |
| Python | Validación automatizada del catálogo. |
| GitHub | Control de versiones y gestión del código. |
| GitHub Pages | Publicación y alojamiento web. |

El proyecto utiliza una arquitectura estática que evita dependencias de backend y simplifica su distribución y mantenimiento.

## Arquitectura del repositorio

```text
proyectos/
│
├── assets/
│   └── Recursos gráficos del sitio
│
├── red-casa/
│   └── Página dedicada al proyecto Red Casa
│
├── storage-hub/
│   └── Página dedicada al proyecto Storage Hub
│
├── tests/
│   └── check_site.py
│
├── .nojekyll
├── index.html
└── README.md
```

### Componentes principales

**`index.html`**

Archivo principal del portfolio. Contiene la estructura, el diseño y las fichas de proyectos publicadas.

Es la fuente de referencia del catálogo y debe mantenerse directamente.

**`assets/`**

Directorio de recursos gráficos empleados por la web.

**`red-casa/` y `storage-hub/`**

Páginas independientes de proyectos específicos, integradas en el catálogo.

**`tests/check_site.py`**

Conjunto de pruebas automatizadas para comprobar la coherencia y estructura del sitio web.

## Instalación y ejecución local

El portfolio puede ejecutarse localmente sin instalar un framework ni configurar un servidor de aplicaciones.

### Requisitos

- Navegador web moderno.
- Git, para clonar el repositorio.
- Python 3, para ejecutar las pruebas de validación.

### Clonar el proyecto

```bash
git clone https://github.com/ardu01/proyectos.git
```

Acceder al directorio:

```bash
cd proyectos
```

### Ejecutar la web

Abrir el archivo `index.html` en un navegador.

También puede utilizarse un servidor HTTP local:

```bash
python -m http.server 8000
```

Acceder desde el navegador a:

`http://localhost:8000`

## Validación y pruebas

El repositorio incorpora pruebas automatizadas para verificar la integridad del catálogo.

Entre las comprobaciones definidas se encuentran:

- Número de proyectos publicados.
- Orden y clasificación de las fichas.
- Coherencia entre los contadores y los elementos del catálogo.
- Presencia de proyectos y enlaces obligatorios.
- Estructura HTML y navegación.
- Verificación de referencias internas.
- Comprobaciones orientadas a evitar la publicación accidental de información sensible.

### Ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python -m unittest discover -s tests -v
```

Antes de publicar modificaciones, es recomendable ejecutar la validación completa.

## Mantenimiento del catálogo

### Fuente de referencia

El archivo `index.html` constituye la fuente de verdad del catálogo.

No existe un generador de páginas activo dentro del repositorio.

**Importante:** No debe regenerarse el catálogo mediante herramientas externas antiguas, ya que podrían sustituirse fichas y modificaciones realizadas directamente en el documento.

### Añadir un proyecto

Para incorporar un nuevo desarrollo:

1. Abrir `index.html`.
2. Identificar la categoría correspondiente.
3. Añadir la ficha HTML del proyecto.
4. Incorporar su descripción, categoría y estado.
5. Añadir los enlaces públicos pertinentes.
6. Actualizar los contadores de proyectos.
7. Revisar las comprobaciones automatizadas afectadas.
8. Ejecutar las pruebas antes de publicar.

Los contadores del encabezado y de las secciones deben coincidir con el número real de fichas `<article>` correspondientes.

### Repositorios privados

Algunos proyectos del catálogo se desarrollan en repositorios privados.

En estos casos, la plataforma puede mostrar información pública del proyecto sin proporcionar acceso al código fuente.

La publicación de una ficha no implica que su repositorio sea público ni que su software esté disponible para descarga.

## Publicación

La plataforma se distribuye mediante **GitHub Pages**.

| Parámetro | Configuración |
|---|---|
| Repositorio | `ardu01/proyectos` |
| Rama de publicación | `main` |
| Directorio | `/` |
| Archivo principal | `index.html` |
| Hosting | GitHub Pages |
| Dominio | `ardu01.github.io` |

**URL pública:**

https://ardu01.github.io/proyectos/

El repositorio incluye `.nojekyll` para evitar el procesamiento predeterminado de Jekyll.

## Evolución del proyecto

### Funcionalidades implementadas

- [x] Catálogo web de proyectos.
- [x] Clasificación por prioridad y estado.
- [x] Diseño visual basado en tarjetas.
- [x] Modos claro y oscuro.
- [x] Contadores de proyectos por categoría.
- [x] Enlaces a páginas y repositorios públicos.
- [x] Publicación mediante GitHub Pages.
- [x] Páginas dedicadas a proyectos seleccionados.
- [x] Pruebas automatizadas de coherencia.
- [x] Incorporación de recursos visuales reales para determinados proyectos.

### Posibles mejoras futuras

- [ ] Automatización controlada de determinadas tareas de mantenimiento.
- [ ] Incorporación de documentación técnica ampliada.
- [ ] Ampliación de capturas y demostraciones.
- [ ] Mejoras adicionales de navegación y adaptación a dispositivos.
- [ ] Ampliación de las páginas individuales de proyectos.

Estas mejoras son propuestas de evolución, no funcionalidades actualmente disponibles.

## Autor y organización

**Miguel Rodríguez Saiz**

Diseño, desarrollo y mantenimiento del portfolio.

**Ardu Solutions**

Iniciativa tecnológica enfocada en el desarrollo de software, inteligencia artificial, electrónica, sistemas y soluciones de ingeniería.

### Enlaces oficiales

- **Portfolio:** https://ardu01.github.io/proyectos/
- **Ardu Solutions:** https://ardusolutions.pages.dev/
- **GitHub:** https://github.com/ardu01
- **Repositorio:** https://github.com/ardu01/proyectos

## Licencia

El repositorio no dispone actualmente de una licencia de software declarada.

Su disponibilidad pública permite consultar el código, pero no constituye por sí misma una autorización general para copiarlo, modificarlo o redistribuirlo.

Los proyectos enlazados desde el catálogo pueden disponer de sus propias condiciones de licencia y distribución.

---

**© 2026 Miguel Rodríguez Saiz · Ardu Solutions**

*Innovación, ingeniería y desarrollo tecnológico.*
