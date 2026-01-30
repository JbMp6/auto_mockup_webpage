🌐 Web-to-Mockup GIF Generator
Un outil d'automatisation puissant qui transforme n'importe quelle page web en un GIF animé de défilement (scrolling), intégré directement dans des mockups MacBook et iPhone.
✨ Fonctionnalités
 * Capture d'écran intelligente : Utilise Playwright pour capturer l'intégralité d'une page web.
 * Gestion des Cookies : Détecte et accepte automatiquement les bannières de cookies courantes pour un rendu propre.
 * Perspective Mapping : Utilise des transformations matricielles (numpy) pour injecter parfaitement les captures d'écran dans les écrans des mockups, même avec de la perspective.
 * Multi-Device : Génère des rendus pour MacBook, iPhone, ou une vue combinée côte à côte.
 * Nettoyage automatique : Supprime les fichiers temporaires (frames, screenshots) après la génération du GIF final.
🚀 Installation
 * Cloner le projet :
   git clone https://github.com/votre-username/web-to-mockup-gif.git
cd web-to-mockup-gif

 * Installer les dépendances :
   pip install playwright pillow numpy
playwright install chromium

 * Préparer les assets :
   Assurez-vous d'avoir un dossier overlay/ à la racine contenant vos images de base :
   * mac.png
   * iphone.png
🛠️ Utilisation
Lancez simplement le script principal :
python main.py

Le script vous demandera interactivement :
 * L'URL du site à capturer.
 * Le nombre de frames (plus il y en a, plus le scroll sera fluide).
 * La durée totale du GIF en secondes.
Exemple de sortie
Le script génère trois types de fichiers selon la fonction appelée :
 * site_mac_with_overlay.gif
 * site_iphone_with_overlay.gif
 * combined_mockup.gif (Mac et iPhone côte à côte)
🧠 Comment ça marche ?
Le processus suit une pipeline précise pour garantir un rendu professionnel :
 * Headless Browsing : Playwright ouvre le site en arrière-plan, attend que le réseau soit inactif (networkidle) et tente de cliquer sur "Accepter" pour les cookies.
 * Full Page Screenshot : Une capture d'écran de très haute résolution est prise sur toute la hauteur du site.
 * Frame Slicing : La capture est découpée en N segments calculés pour simuler un défilement fluide du haut vers le bas.
 * Perspective Transform :
   Chaque frame subit une transformation homographique pour s'adapter aux coordonnées exactes de l'écran du mockup :
   
   
   Où A représente les points de destination sur le mockup et B les coins de l'image source.
 * GIF Assembly : Les images transformées sont superposées au mockup et assemblées dans un fichier GIF optimisé.
📂 Structure du projet
 * main.py : Le script principal contenant toute la logique.
 * overlay/ : Dossier contenant les templates PNG de vos appareils.
 * screen/ : (Temporaire) Stocke la capture d'écran originale.
 * frames/ : (Temporaire) Stocke les images individuelles avant l'assemblage du GIF.
📝 Configuration des coordonnées
Si vous changez d'image de mockup, vous devrez mettre à jour les coordonnées des coins de l'écran (TL, TR, BL, BR) dans les fonctions :
 * createMacMockup : macbook_screen_size
 * createIphoneMockup : iphone_screen_size
