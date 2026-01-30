# 🌐 Web-to-Mockup GIF Generator

Un outil d’automatisation puissant qui transforme n’importe quelle page web en un **GIF animé de défilement (scrolling)**, intégré directement dans des **mockups MacBook et iPhone**.

---

## ✨ Fonctionnalités

- 📸 **Capture d’écran intelligente**  
  Utilise **Playwright** pour capturer l’intégralité d’une page web, quelle que soit sa hauteur.

- 🍪 **Gestion automatique des cookies**  
  Détecte et tente d’accepter automatiquement les bannières de cookies courantes pour un rendu propre.

- 📐 **Perspective Mapping**  
  Injection réaliste des captures dans les écrans des mockups grâce à des **transformations homographiques** (*numpy*).

- 📱 **Multi-Device**  
  Génération de mockups :
  - MacBook
  - iPhone
  - Vue combinée côte à côte

- 🧹 **Nettoyage automatique**  
  Suppression des fichiers temporaires (screenshots, frames) après génération du GIF final.

---

## 🚀 Installation

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/JbMp6/auto_mockup_webpage.git
cd auto_mockup_webpage
```

### 2️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3️⃣ Préparer les assets

```
overlay/
├── mac.png
└── iphone.png
```

---

## 🛠️ Utilisation

```bash
python main.py
```

Le script te demandera :
- URL du site
- Nombre de frames
- Durée du GIF

---

## 📂 Structure du projet

```
auto_mockup_webpage/
├── main.py
├── overlay/
├── screen/
├── frames/
├── requirements.txt
└── README.md
```

---

## 📄 Licence

MIT
