# Intégration PSA Car Controller pour Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/YOUR_USERNAME/psacc-ha.svg)](https://github.com/YOUR_USERNAME/psacc-ha/releases)

Intégration Home Assistant custom pour contrôler votre véhicule PSA (Peugeot, Citroën, Opel, DS, Vauxhall) via l'API Docker [PSA Car Controller](https://github.com/flobz/psa_car_controller).

## 🚗 Fonctionnalités

### Capteurs (Sensors)
- ✅ Niveau de batterie (%)
- ✅ Autonomie électrique (km)
- ✅ Autonomie totale (km)
- ✅ Kilométrage (km)
- ✅ Puissance de charge (kW)
- ✅ Temps de charge restant (min)
- ✅ Consommation moyenne (kWh/100km)
- ✅ Température extérieure (°C)
- ✅ Seuil de charge configuré (%)
- ✅ Dernière mise à jour

### Capteurs binaires (Binary Sensors)
- ✅ Charge en cours
- ✅ Branché
- ✅ Portes verrouillées
- ✅ Porte conducteur
- ✅ Porte passager
- ✅ Portes arrière (gauche/droite)
- ✅ Capot
- ✅ Coffre
- ✅ Climatisation active

### Suivi GPS (Device Tracker)
- ✅ Position GPS du véhicule
- ✅ Altitude, cap et qualité du signal

### Interrupteurs (Switches)
- ✅ Démarrer/Arrêter la charge
- ✅ Activer/Désactiver la climatisation

### Boutons (Buttons)
- ✅ Verrouiller les portes
- ✅ Déverrouiller les portes
- ✅ Klaxonner
- ✅ Clignoter les lumières
- ✅ Réveiller le véhicule
- ✅ Actualiser les données

### Curseurs (Numbers)
- ✅ Seuil de charge maximum (50-100%)
- ✅ Température de climatisation (16-28°C)

### Services personnalisés
- ✅ `psacc.set_charge_threshold` - Définir le seuil de charge
- ✅ `psacc.set_charge_schedule` - Configurer un horaire de charge
- ✅ `psacc.start_climate` - Démarrer la climatisation
- ✅ `psacc.stop_climate` - Arrêter la climatisation
- ✅ `psacc.horn` - Klaxonner
- ✅ `psacc.lights` - Clignoter les lumières
- ✅ `psacc.wakeup` - Réveiller le véhicule

## 📋 Prérequis

1. **PSA Car Controller Docker** doit être installé et fonctionnel
   - Guide d'installation: https://github.com/flobz/psa_car_controller
   - L'API doit être accessible depuis Home Assistant

2. **Home Assistant** version 2023.1 ou supérieure

## 🔧 Installation

### Méthode 1: Installation manuelle

1. Téléchargez le dossier `custom_components/psacc/`
2. Copiez-le dans le dossier `custom_components` de votre installation Home Assistant
   ```
   /config/custom_components/psacc/
   ```
3. Redémarrez Home Assistant

### Méthode 2: Via HACS (recommandé)

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur les 3 points en haut à droite et sélectionnez "Dépôts personnalisés"
3. Ajoutez l'URL de ce repository
4. Recherchez "PSA Car Controller"
5. Cliquez sur "Installer"
6. Redémarrez Home Assistant

## ⚙️ Configuration

### Configuration via l'interface

1. Allez dans **Paramètres** → **Appareils et Services**
2. Cliquez sur **+ Ajouter une intégration**
3. Recherchez **PSA Car Controller**
4. Entrez les informations :
   - **URL de l'API** : L'adresse de votre Docker PSA Car Controller
     - Exemple local : `http://192.168.1.100:5000`
     - Exemple distant : `https://psacc.example.com`
   - **Intervalle de mise à jour** : En minutes (défaut: 5)
5. Cliquez sur **Soumettre**

### Vérification de la connexion

L'intégration testera automatiquement la connexion à votre API. En cas d'échec :
- Vérifiez que l'URL est correcte
- Vérifiez que le Docker est bien démarré
- Vérifiez que l'API est accessible depuis Home Assistant
- Vérifiez les logs : **Paramètres** → **Système** → **Logs**

## 📱 Utilisation

### Carte Lovelace exemple

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Ma Peugeot e-208
    entities:
      - entity: sensor.ma_voiture_battery_level
        name: Batterie
      - entity: sensor.ma_voiture_range_electric
        name: Autonomie
      - entity: binary_sensor.ma_voiture_charging
        name: En charge
      - entity: sensor.ma_voiture_charging_power
        name: Puissance
      - entity: device_tracker.ma_voiture_location
        name: Position
        
  - type: horizontal-stack
    cards:
      - type: button
        entity: switch.ma_voiture_charging
        name: Charge
        icon: mdi:battery-charging
        tap_action:
          action: toggle
      - type: button
        entity: switch.ma_voiture_climate
        name: Clim
        icon: mdi:air-conditioner
        tap_action:
          action: toggle
      - type: button
        entity: button.ma_voiture_lock_doors
        name: Verrouiller
        icon: mdi:lock
        tap_action:
          action: call-service
          service: button.press
          
  - type: gauge
    entity: sensor.ma_voiture_battery_level
    min: 0
    max: 100
    needle: true
    severity:
      green: 50
      yellow: 30
      red: 0
```

### Automatisations exemples

#### Notification fin de charge
```yaml
automation:
  - alias: "Voiture chargée"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ma_voiture_battery_level
        above: 79
    condition:
      - condition: state
        entity_id: binary_sensor.ma_voiture_charging
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "🔋 Charge terminée"
          message: "Votre voiture est chargée à {{ states('sensor.ma_voiture_battery_level') }}%"
```

#### Charge automatique en heures creuses
```yaml
automation:
  - alias: "Démarrage charge heures creuses"
    trigger:
      - platform: time
        at: "23:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.ma_voiture_plugged
        state: "on"
      - condition: numeric_state
        entity_id: sensor.ma_voiture_battery_level
        below: 80
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ma_voiture_charging
          
  - alias: "Arrêt charge fin heures creuses"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.ma_voiture_charging
```

#### Préchauffage avant départ
```yaml
automation:
  - alias: "Préchauffage matin"
    trigger:
      - platform: time
        at: "07:30:00"
    condition:
      - condition: state
        entity_id: binary_sensor.ma_voiture_plugged
        state: "on"
      - condition: numeric_state
        entity_id: sensor.ma_voiture_temperature_exterior
        below: 10
    action:
      - service: psacc.start_climate
        data:
          vin: "VF3XXXXXXXXXXXXXXX"
          temperature: 21
```

#### Alerte portes non verrouillées
```yaml
automation:
  - alias: "Alerte portes ouvertes"
    trigger:
      - platform: state
        entity_id: binary_sensor.ma_voiture_doors_locked
        to: "off"
        for:
          minutes: 5
    condition:
      - condition: numeric_state
        entity_id: distance.home
        above: 0.1  # À plus de 100m de la maison
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Portes non verrouillées"
          message: "Votre voiture n'est pas verrouillée"
          data:
            actions:
              - action: "LOCK_CAR"
                title: "Verrouiller"
```

### Utilisation des services

#### Définir un seuil de charge
```yaml
service: psacc.set_charge_threshold
data:
  vin: "VF3XXXXXXXXXXXXXXX"
  threshold: 80
```

#### Programmer une charge
```yaml
service: psacc.set_charge_schedule
data:
  vin: "VF3XXXXXXXXXXXXXXX"
  start_time: "23:00"
  end_time: "07:00"
```

#### Démarrer la climatisation
```yaml
service: psacc.start_climate
data:
  vin: "VF3XXXXXXXXXXXXXXX"
  temperature: 21
```

## 🔍 Dépannage

### L'intégration ne trouve pas mon véhicule

1. Vérifiez que votre Docker PSA Car Controller est bien configuré
2. Vérifiez que vous pouvez accéder à l'API manuellement : `http://VOTRE_IP:5000/vehicles`
3. Consultez les logs de Home Assistant
4. Vérifiez que votre véhicule est bien enregistré dans PSA Car Controller

### Les données ne se mettent pas à jour

1. Vérifiez l'intervalle de mise à jour dans les options de l'intégration
2. Cliquez sur le bouton "Actualiser" dans le tableau de bord
3. Vérifiez que le Docker PSA Car Controller reçoit bien les données de PSA
4. Consultez les logs pour détecter d'éventuelles erreurs API

### Erreur "Cannot connect"

1. Vérifiez que l'URL de l'API est correcte
2. Vérifiez que Home Assistant peut accéder au réseau où se trouve le Docker
3. Testez la connexion avec `curl` ou depuis un navigateur
4. Vérifiez les pare-feu et règles réseau

## 📝 Notes importantes

- ⚠️ **Fréquence de mise à jour** : Ne pas définir un intervalle trop court (< 5 min) pour éviter de surcharger l'API PSA
- 🔋 **Consommation batterie** : Les commandes fréquentes (klaxon, lumières) peuvent solliciter la batterie du véhicule
- 🔐 **Sécurité** : Assurez-vous que votre API PSA Car Controller est sécurisée, surtout si accessible depuis Internet
- 📱 **VIN** : Pour utiliser les services, vous aurez besoin du VIN (numéro d'identification) de votre véhicule

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Soumettre des Pull Requests
- Améliorer la documentation

## 📄 Licence

Cette intégration est sous licence GPL-3.0, comme le projet PSA Car Controller original.

## 🙏 Remerciements

- [@flobz](https://github.com/flobz) pour le projet PSA Car Controller
- La communauté Home Assistant
- Tous les contributeurs

## 🔗 Liens utiles

- [PSA Car Controller](https://github.com/flobz/psa_car_controller)
- [Documentation PSA Car Controller](https://github.com/flobz/psa_car_controller/tree/master/docs)
- [Home Assistant](https://www.home-assistant.io/)
- [Forum Home Assistant](https://community.home-assistant.io/)

---

**Note** : Cette intégration n'est pas affiliée à PSA/Stellantis. Utilisez-la à vos propres risques.
