# Guide d'installation - Intégration PSA Car Controller

## 📁 Structure complète des fichiers

Voici la structure exacte que vous devez avoir dans votre dossier Home Assistant :

```
config/
└── custom_components/
    └── psacc/
        ├── __init__.py
        ├── manifest.json
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── api.py
        ├── sensor.py
        ├── binary_sensor.py
        ├── device_tracker.py
        ├── switch.py
        ├── button.py
        ├── number.py
        ├── select.py
        ├── strings.json
        ├── services.yaml
        └── translations/
            ├── en.json
            └── fr.json
```

## 🚀 Installation étape par étape

### Étape 1 : Créer la structure de dossiers

Connectez-vous à votre Home Assistant via SSH ou File Editor et créez la structure :

```bash
mkdir -p config/custom_components/psacc/translations
```

### Étape 2 : Copier tous les fichiers

Copiez tous les fichiers fournis dans le dossier `custom_components/psacc/` en respectant la structure ci-dessus.

**Liste des fichiers à copier :**

#### Fichiers racine du module (dans `psacc/`)
1. ✅ `__init__.py` - Point d'entrée de l'intégration
2. ✅ `manifest.json` - Métadonnées
3. ✅ `config_flow.py` - Interface de configuration
4. ✅ `const.py` - Constantes
5. ✅ `coordinator.py` - Coordinateur de données
6. ✅ `api.py` - Client API
7. ✅ `sensor.py` - Capteurs (10 entités)
8. ✅ `binary_sensor.py` - Capteurs binaires (10 entités)
9. ✅ `device_tracker.py` - Suivi GPS
10. ✅ `switch.py` - Interrupteurs (2 entités)
11. ✅ `button.py` - Boutons (6 entités)
12. ✅ `number.py` - Curseurs numériques (2 entités)
13. ✅ `select.py` - Sélecteurs (1 entité)
14. ✅ `strings.json` - Traductions par défaut
15. ✅ `services.yaml` - Définition des services

#### Fichiers de traduction (dans `psacc/translations/`)
16. ✅ `en.json` - Traduction anglaise
17. ✅ `fr.json` - Traduction française

### Étape 3 : Vérifier les permissions

Assurez-vous que tous les fichiers ont les bonnes permissions :

```bash
chmod 644 config/custom_components/psacc/*.py
chmod 644 config/custom_components/psacc/*.json
chmod 644 config/custom_components/psacc/*.yaml
chmod 644 config/custom_components/psacc/translations/*.json
```

### Étape 4 : Redémarrer Home Assistant

Redémarrez complètement Home Assistant (pas seulement recharger la configuration).

**Via l'interface :**
1. Allez dans **Paramètres** → **Système**
2. Cliquez sur **Redémarrer**
3. Attendez que Home Assistant redémarre complètement

**Via CLI :**
```bash
ha core restart
```

### Étape 5 : Vérifier l'installation

Après le redémarrage, vérifiez que l'intégration est bien reconnue :

1. Allez dans **Paramètres** → **Appareils et Services**
2. Cliquez sur **+ Ajouter une intégration**
3. Recherchez "**PSA Car Controller**"
4. Si elle apparaît, l'installation est réussie ✅

## ⚙️ Configuration initiale

### 1. Préparer votre Docker PSA Car Controller

Avant de configurer l'intégration, assurez-vous que :

- ✅ Votre Docker PSA Car Controller est installé et démarré
- ✅ Il est accessible depuis Home Assistant
- ✅ Vous connaissez son URL (exemple : `http://192.168.1.100:5000`)

**Test de l'API :**
```bash
curl http://VOTRE_IP:5000/vehicles
```

Vous devriez recevoir une liste de vos véhicules en JSON.

### 2. Ajouter l'intégration

1. **Paramètres** → **Appareils et Services**
2. **+ Ajouter une intégration**
3. Recherchez "**PSA Car Controller**"
4. Remplissez le formulaire :

   **URL de l'API :**
   - Format local : `http://192.168.1.100:5000`
   - Format distant : `https://psacc.example.com`
   - ⚠️ Ne pas mettre de `/` à la fin
   
   **Intervalle de mise à jour :**
   - Recommandé : 5 minutes
   - Minimum : 1 minute
   - Maximum : 60 minutes

5. Cliquez sur **Soumettre**

### 3. Vérification

Si la connexion réussit, vous verrez :
- ✅ Un message de succès
- ✅ Vos véhicules apparaissent dans **Appareils et Services**
- ✅ Toutes les entités sont créées automatiquement

## 🔍 Résolution des problèmes

### Problème : "L'intégration n'apparaît pas dans la liste"

**Solutions :**
1. Vérifiez que tous les fichiers sont bien présents
2. Vérifiez le fichier `manifest.json` (pas d'erreur de syntaxe)
3. Consultez les logs : **Paramètres** → **Système** → **Logs**
4. Redémarrez Home Assistant complètement
5. Videz le cache du navigateur (Ctrl + F5)

### Problème : "Cannot connect to API"

**Solutions :**
1. Vérifiez l'URL (pas de `/` à la fin)
2. Testez avec curl : `curl http://VOTRE_IP:5000/vehicles`
3. Vérifiez que le Docker est bien démarré
4. Vérifiez le pare-feu et les règles réseau
5. Essayez depuis un navigateur : `http://VOTRE_IP:5000/vehicles`

### Problème : "Intégration installée mais aucune entité"

**Solutions :**
1. Vérifiez les logs pour voir les erreurs
2. Vérifiez que votre Docker PSA Car Controller a bien des véhicules configurés
3. Actualisez manuellement : cliquez sur le bouton **Actualiser**
4. Attendez l'intervalle de mise à jour (5 minutes par défaut)

### Problème : "Les données ne se mettent pas à jour"

**Solutions :**
1. Vérifiez que le Docker PSA Car Controller reçoit bien les données de PSA
2. Utilisez le bouton **Actualiser** dans le tableau de bord
3. Vérifiez l'intervalle de mise à jour dans les options
4. Consultez les logs du Docker PSA Car Controller

## 📝 Vérification des logs

Pour voir les logs de l'intégration :

1. **Paramètres** → **Système** → **Logs**
2. Recherchez "psacc" dans la barre de recherche
3. Les logs vous indiqueront toute erreur

**Activer les logs détaillés** (optionnel) :

Ajoutez dans votre `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.psacc: debug
```

Puis redémarrez Home Assistant.

## 🎯 Prochaines étapes

Une fois l'installation réussie :

1. ✅ Consultez toutes vos entités dans **Appareils et Services** → **PSA Car Controller**
2. ✅ Créez votre premier tableau de bord avec les cartes Lovelace
3. ✅ Configurez vos premières automatisations
4. ✅ Testez les services personnalisés

## 📚 Ressources supplémentaires

- [README.md](README.md) - Documentation complète
- [Exemples d'automatisations](README.md#automatisations-exemples)
- [Exemples de cartes Lovelace](README.md#carte-lovelace-exemple)
- [Guide des services](README.md#utilisation-des-services)

## 💡 Conseils

- **Fréquence de mise à jour** : Ne descendez pas en dessous de 5 minutes pour éviter de surcharger l'API PSA
- **Sécurité** : Si votre API est accessible depuis Internet, pensez à la sécuriser (HTTPS, authentification)
- **Sauvegarde** : Sauvegardez votre configuration avant toute modification importante
- **Tests** : Testez d'abord les commandes manuellement avant de créer des automatisations

## ❓ Besoin d'aide ?

Si vous rencontrez des problèmes :

1. Consultez les logs détaillés
2. Vérifiez que votre Docker PSA Car Controller fonctionne
3. Testez l'API manuellement avec curl
4. Créez une issue sur GitHub avec :
   - Version de Home Assistant
   - Version du Docker PSA Car Controller
   - Les logs d'erreur
   - Les étapes pour reproduire le problème

---

**Bonne utilisation ! 🚗⚡**
