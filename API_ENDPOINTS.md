# Documentation des endpoints API - PSA Car Controller

Ce document liste tous les endpoints utilisés par l'intégration Home Assistant.

## 🔗 Configuration de base

**URL de base** : Configurée lors de l'installation (ex: `http://192.168.1.100:5000`)

**Headers requis** : Aucun (pas d'authentification pour le moment)

**Format de réponse** : JSON

---

## 📍 Endpoints disponibles

### 1. Liste des véhicules

**Endpoint** : `GET /vehicles`

**Description** : Récupère la liste de tous les véhicules configurés

**Réponse attendue** :
```json
[
  {
    "vin": "VF3XXXXXXXXXXXXXXX",
    "brand": "Peugeot",
    "model": "e-208",
    "label": "Ma e-208"
  }
]
```

**Utilisation dans l'intégration** :
- Au démarrage pour découvrir les véhicules
- Dans le coordinateur pour initialiser la liste

---

### 2. Statut du véhicule

**Endpoint** : `GET /get_vehicleinfo/{vin}`

**Description** : Récupère toutes les informations d'un véhicule

**Paramètres** :
- `{vin}` : Numéro VIN du véhicule

**Réponse attendue** :
```json
{
  "energy": [
    {
      "level": 85,
      "autonomy": 320,
      "charging": {
        "status": "InProgress",
        "plugged": true,
        "rate": 7.4,
        "remaining_time": 45,
        "charge_threshold": 80
      }
    }
  ],
  "position": {
    "geometry": {
      "coordinates": [6.1234, 48.5678]
    },
    "properties": {
      "altitude": 250,
      "heading": 180,
      "updatedAt": "2024-01-15T10:30:00Z",
      "signalQuality": "Good"
    }
  },
  "odometer": {
    "mileage": 15420
  },
  "doors": {
    "driver": "Closed",
    "passenger": "Closed",
    "rear_left": "Closed",
    "rear_right": "Closed",
    "hood": "Closed",
    "trunk": "Closed"
  },
  "preconditionning": {
    "airConditioning": {
      "status": "Disabled",
      "temperature": 21.0
    }
  },
  "environment": {
    "temperature": 12.5,
    "consumption": 18.4
  },
  "updatedAt": "2024-01-15T10:35:00Z"
}
```

**Utilisation dans l'intégration** :
- Mise à jour périodique de toutes les entités
- Appelé par le coordinateur

---

### 3. Démarrer/Arrêter la charge

**Endpoint** : `POST /charge_now/{vin}/{charge}`

**Description** : Démarre ou arrête la charge

**Paramètres** :
- `{vin}` : Numéro VIN du véhicule
- `{charge}` : `1` pour démarrer, `0` pour arrêter

**Exemples** :
```
POST /charge_now/VF3XXXXXXXXXXXXXXX/1  # Démarrer
POST /charge_now/VF3XXXXXXXXXXXXXXX/0  # Arrêter
```

**Utilisation dans l'intégration** :
- Switch "Charging"
- Service `switch.turn_on` / `switch.turn_off`

---

### 4. Définir le seuil de charge

**Endpoint** : `POST /charge_control`

**Description** : Configure le seuil de charge maximum

**Body (JSON)** :
```json
{
  "vin": "VF3XXXXXXXXXXXXXXX",
  "percentage": 80
}
```

**Utilisation dans l'intégration** :
- Number entity "Charge threshold"
- Service `psacc.set_charge_threshold`

---

### 5. Programmer la charge

**Endpoint** : `POST /charge_control`

**Description** : Configure un horaire de charge

**Body (JSON)** :
```json
{
  "vin": "VF3XXXXXXXXXXXXXXX",
  "start": "23:00",
  "end": "07:00"
}
```

**Utilisation dans l'intégration** :
- Service `psacc.set_charge_schedule`

---

### 6. Démarrer la climatisation

**Endpoint** : `POST /climate/{vin}/{temperature}`

**Description** : Démarre la climatisation avec une température

**Paramètres** :
- `{vin}` : Numéro VIN du véhicule
- `{temperature}` : Température cible (16-28)

**Exemple** :
```
POST /climate/VF3XXXXXXXXXXXXXXX/21
```

**Utilisation dans l'intégration** :
- Switch "Climate" (turn_on)
- Number "Climate temperature"
- Service `psacc.start_climate`

---

### 7. Arrêter la climatisation

**Endpoint** : `POST /climate/{vin}/0`

**Description** : Arrête la climatisation

**Exemple** :
```
POST /climate/VF3XXXXXXXXXXXXXXX/0
```

**Utilisation dans l'intégration** :
- Switch "Climate" (turn_off)
- Service `psacc.stop_climate`

---

### 8. Réveiller le véhicule

**Endpoint** : `POST /wakeup/{vin}`

**Description** : Réveille le véhicule pour actualiser les données

**Paramètres** :
- `{vin}` : Numéro VIN du véhicule

**Exemple** :
```
POST /wakeup/VF3XXXXXXXXXXXXXXX
```

**Utilisation dans l'intégration** :
- Button "Wake up"
- Service `psacc.wakeup`

---

### 9. Klaxonner

**Endpoint** : `POST /horn/{vin}/{count}`

**Description** : Fait retentir le klaxon

**Paramètres** :
- `{vin}` : Numéro VIN du véhicule
- `{count}` : Nombre de coups (1-5)

**Exemple** :
```
POST /horn/VF3XXXXXXXXXXXXXXX/1
```

**Utilisation dans l'intégration** :
- Button "Horn"
- Service `psacc.horn`

---

### 10. Clignoter les lumières

**Endpoint** : `POST /lights/{vin}/{count}`

**Description** : Fait clignoter les lumières

**Paramètres** :
- `{vin}` : Numéro VIN du véhicule
- `{count}` : Nombre de clignotements (1-5)

**Exemple** :
```
POST /lights/VF3XXXXXXXXXXXXXXX/1
```

**Utilisation dans l'intégration** :
- Button "Flash lights"
- Service `psacc.lights`

---

### 11. Verrouiller les portes

**Endpoint** : `POST /door_lock/{vin}`

**Description** : Verrouille toutes les portes

**Paramètres** :
- `{vin}` : Numéro VIN du véhicule

**Exemple** :
```
POST /door_lock/VF3XXXXXXXXXXXXXXX
```

**Utilisation dans l'intégration** :
- Button "Lock doors"

---

### 12. Déverrouiller les portes

**Endpoint** : `POST /door_unlock/{vin}`

**Description** : Déverrouille toutes les portes

**Paramètres** :
- `{vin}` : Numéro VIN du véhicule

**Exemple** :
```
POST /door_unlock/VF3XXXXXXXXXXXXXXX
```

**Utilisation dans l'intégration** :
- Button "Unlock doors"

---

## 🧪 Tests manuels

Vous pouvez tester les endpoints avec `curl` :

### Lister les véhicules
```bash
curl http://192.168.1.100:5000/vehicles
```

### Obtenir le statut
```bash
curl http://192.168.1.100:5000/get_vehicleinfo/VF3XXXXXXXXXXXXXXX
```

### Démarrer la charge
```bash
curl -X POST http://192.168.1.100:5000/charge_now/VF3XXXXXXXXXXXXXXX/1
```

### Définir le seuil de charge
```bash
curl -X POST http://192.168.1.100:5000/charge_control \
  -H "Content-Type: application/json" \
  -d '{"vin":"VF3XXXXXXXXXXXXXXX","percentage":80}'
```

### Démarrer la climatisation
```bash
curl -X POST http://192.168.1.100:5000/climate/VF3XXXXXXXXXXXXXXX/21
```

---

## ⚠️ Notes importantes

### Fréquence d'appel
- **GET /vehicles** : Une seule fois au démarrage
- **GET /get_vehicleinfo** : Selon l'intervalle configuré (défaut: 5 min)
- **POST endpoints** : À la demande (actions utilisateur)

### Gestion d'erreurs
L'intégration gère automatiquement :
- ✅ Timeouts (30 secondes)
- ✅ Erreurs réseau
- ✅ Réponses invalides
- ✅ Endpoints indisponibles

### Sécurité
- Aucune authentification requise pour le moment
- À sécuriser si exposé sur Internet
- Considérez l'usage de HTTPS et d'un reverse proxy

---

## 🔄 Synchronisation

**Flux de données** :
```
Home Assistant → API PSACC → PSA Cloud → Véhicule
```

**Délais approximatifs** :
- Lecture de données : < 5 secondes
- Commandes (charge, clim) : 10-30 secondes
- Mise à jour position : Variable selon réveil véhicule

---

## 📝 Format des données

### Coordonnées GPS
Format : `[longitude, latitude]`
```json
"coordinates": [6.1234, 48.5678]
```

### Dates
Format ISO 8601 : `YYYY-MM-DDTHH:MM:SSZ`
```json
"updatedAt": "2024-01-15T10:35:00Z"
```

### Énumérations

**Status de charge** :
- `"InProgress"` : Charge en cours
- `"Disconnected"` : Déconnecté
- `"Failure"` : Erreur

**État des portes** :
- `"Open"` : Ouvert
- `"Closed"` : Fermé

**État climatisation** :
- `"Enabled"` : Activé
- `"Disabled"` : Désactivé
- `"InProgress"` : En cours

---

## 🐛 Debugging

Pour activer les logs d'API dans Home Assistant :

```yaml
logger:
  default: info
  logs:
    custom_components.psacc.api: debug
```

Vous verrez alors :
- Toutes les requêtes HTTP
- Les réponses JSON
- Les erreurs détaillées

---

**Note** : Cette documentation est basée sur l'API PSA Car Controller v3.6+. Consultez la [documentation officielle](https://github.com/flobz/psa_car_controller) pour les dernières mises à jour.
