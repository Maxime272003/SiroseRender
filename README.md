# SiroseRender – Automatisation de Rendus Maya/Arnold & Husk/Karma

SiroseRender est une application graphique qui facilite et automatise les rendus avec Maya/Arnold et Husk/Karma. Elle propose une interface moderne pour configurer vos rendus, les ajouter à une file d’attente, et exécuter plusieurs rendus en séquence, que ce soit pour Maya ou Houdini.

---

## 📥 Télécharger l'exécutable
**Téléchargez la dernière version ici** :  
[📥 Télécharger maintenant](https://github.com/Maxime272003/SiroseRender/releases/latest/download/SiroseRender.exe)

---

## Fonctionnalités principales

- **Rendu Maya/Arnold** :  
  - Rendu complet ou rapide (FML) sur une plage de frames.
  - Gestion des layers, du répertoire de sortie, et de la résolution.
  - Configuration dynamique des chemins Maya et plugins Qt.

- **Rendu Husk/Karma** :  
  - Rendu Full Sequence ou FML (première, milieu, dernière frame).
  - Choix rapide entre Karma et KarmaXPU.
  - Aperçu de la commande Husk générée.

- **File d’attente** :  
  - Ajoutez plusieurs configurations de rendu à une file d’attente et exécutez-les en séquence.
  - Gestion et suppression des rendus dans la file.

- **Historique** :  
  - Visualisez l’historique des rendus précédents.

- **Thème clair/sombre** :  
  - Basculez entre les modes Light et Dark.

---

## Prérequis

### Logiciels nécessaires
- **Maya** (pour les rendus Maya/Arnold)
- **Arnold** (plugin activé dans Maya)
- **Husk** (pour les rendus Houdini/Karma)
- **Karma/KarmaXPU** (moteurs de rendu pour Husk)

### Dépendances Python
- **PyQt5**  
  Installez avec :
  ```bash
  pip install PyQt5
  ```

---

## Installation et utilisation

### Option 1 : Utilisation de l’exécutable
1. Téléchargez le fichier `.exe` depuis la section releases.
2. Exécutez le fichier pour lancer l’application.

### Option 2 : Depuis le code source
1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/Maxime272003/SiroseRender.git
   cd SiroseRender
   ```
2. Installez les dépendances :
   ```bash
   pip install PyQt5
   ```
3. Lancez l’application :
   ```bash
   python SiroseRender.py
   ```
4. (Optionnel) Générez un exécutable avec PyInstaller :
   ```bash
   pyinstaller --onefile ./SiroseRender.py
   ```

---

## Configuration des paramètres

Avant de lancer un rendu, configurez les chemins nécessaires :

- **Pour Maya/Arnold** :  
  Cliquez sur le bouton **Paramètres** de l’onglet Maya/Arnold et renseignez :
  - Chemin Maya (bin) : ex : `C:\Program Files\Autodesk\Maya2024\bin`
  - Chemin Qt Plugins : ex : `C:\Program Files\Autodesk\Maya2024\plugins`

- **Pour Husk/Karma** :  
  Cliquez sur le bouton **Paramètres** de l’onglet Husk/Karma et renseignez :
  - Chemin Husk (bin) : ex : `C:\Program Files\Side Effects Software\Houdini 20.5.487\bin`

Les chemins sont sauvegardés dans `config.ini` et rechargés automatiquement.

---

## Utilisation

### Rendu Maya/Arnold
1. Remplissez les champs (scène, frames, output, etc.).
2. Choisissez le type de rendu (Complet ou FML).
3. Cliquez sur **Lancer** ou ajoutez à la file d’attente.

### Rendu Husk/Karma
1. Remplissez les champs (scène USD, frames, moteur, etc.).
2. Choisissez le type de rendu (Full Sequence ou FML).
3. Cliquez sur **Lancer** ou ajoutez à la file d’attente.

### File d’attente
- Ajoutez plusieurs rendus, puis cliquez sur **Lancer** pour exécuter toute la file.
- Supprimez un rendu de la file via le bouton dédié.

### Historique
- Consultez l’historique des rendus via le bouton dédié dans la barre d’outils.

---

## Logs et diagnostics

Les logs des commandes et erreurs sont affichés dans la section dédiée de chaque onglet. Utilisez-les pour diagnostiquer d’éventuels problèmes.

---

## Contribution

Les contributions sont les bienvenues !  
N’hésitez pas à ouvrir une issue ou une pull request.

---

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus d’informations.