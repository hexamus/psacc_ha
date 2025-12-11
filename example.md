# Exemples de configuration - PSA Car Controller

Collection complète d'exemples de cartes Lovelace, automatisations et scripts pour l'intégration PSA Car Controller.

---

## 📱 Cartes Lovelace

### 1. Carte complète du véhicule

```yaml
type: vertical-stack
cards:
  # En-tête avec image
  - type: picture-entity
    entity: device_tracker.ma_voiture_location
    name: Ma Peugeot e-208
    show_state: false
    camera_image: camera.map_ma_voiture
    
  # État général
  - type: glance
    entities:
      - entity: sensor.ma_voiture_battery_level
        name: Batterie
      - entity: sensor.ma_voiture_range_electric
        name: Autonomie
      - entity: sensor.ma_voiture_mileage
        name: Kilométrage
      - entity: binary_sensor.ma_voiture_charging
        name: Charge
    
  # Contrôles rapides
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
      - type: button
        entity: button.ma_voiture_horn
        name: Klaxon
        icon: mdi:bugle
        
  # Jauge batterie
  - type: gauge
    entity: sensor.ma_voiture_battery_level
    name: Niveau de batterie
    min: 0
    max: 100
    needle: true
    severity:
      green: 50
      yellow: 30
      red: 0
      
  # Détails
  - type: entities
    title: Détails du véhicule
    show_header_toggle: false
    entities:
      - entity: sensor.ma_voiture_charging_power
        name: Puissance de charge
      - entity: sensor.ma_voiture_charging_time
        name: Temps restant
      - entity: sensor.ma_voiture_temperature_exterior
        name: Température ext.
      - entity: sensor.ma_voiture_consumption
        name: Consommation moy.
      - type: divider
      - entity: binary_sensor.ma_voiture_doors_locked
        name: Portes verrouillées
      - entity: binary_sensor.ma_voiture_plugged
        name: Branché
      - entity: sensor.ma_voiture_last_update
        name: Dernière MAJ
```

### 2. Carte minimaliste

```yaml
type: vertical-stack
cards:
  - type: custom:mini-graph-card
    entities:
      - entity: sensor.ma_voiture_battery_level
        name: Batterie
    hours_to_show: 24
    line_color: '#00ff00'
    line_width: 3
    font_size: 75
    
  - type: entities
    entities:
      - entity: sensor.ma_voiture_range_electric
        icon: mdi:road-variant
      - entity: sensor.ma_voiture_mileage
        icon: mdi:counter
      - entity: switch.ma_voiture_charging
      - entity: switch.ma_voiture_climate
```

### 3. Carte avec map

```yaml
type: vertical-stack
cards:
  - type: map
    entities:
      - entity: device_tracker.ma_voiture_location
    default_zoom: 15
    aspect_ratio: '16:9'
    
  - type: glance
    entities:
      - entity: sensor.ma_voiture_battery_level
      - entity: binary_sensor.ma_voiture_charging
      - entity: binary_sensor.ma_voiture_doors_locked
```

### 4. Carte de contrôle charge

```yaml
type: entities
title: Gestion de la charge
entities:
  - entity: switch.ma_voiture_charging
    name: Charge
  - entity: number.ma_voiture_charge_threshold
    name: Seuil de charge
  - entity: select.ma_voiture_charge_mode
    name: Mode de charge
  - entity: sensor.ma_voiture_charging_power
    name: Puissance
  - entity: sensor.ma_voiture_charging_time
    name: Temps restant
  - type: divider
  - type: button
    name: Définir charge à 80%
    icon: mdi:battery-80
    tap_action:
      action: call-service
      service: psacc.set_charge_threshold
      service_data:
        vin: VF3XXXXXXXXXXXXXXX
        threshold: 80
```

---

## 🤖 Automatisations

### 1. Notification fin de charge

```yaml
automation:
  - alias: "🔋 Notification fin de charge"
    description: "Notifie quand la charge est terminée"
    trigger:
      - platform: state
        entity_id: binary_sensor.ma_voiture_charging
        from: "on"
        to: "off"
    condition:
      - condition: numeric_state
        entity_id: sensor.ma_voiture_battery_level
        above: 75
    action:
      - service: notify.mobile_app
        data:
          title: "🔋 Charge terminée"
          message: >
            Votre e-208 est chargée à {{ states('sensor.ma_voiture_battery_level') }}%
            Autonomie: {{ states('sensor.ma_voiture_range_electric') }} km
          data:
            tag: "car_charged"
            group: "car"
            notification_icon: "mdi:car-electric"
```

### 2. Charge automatique heures creuses

```yaml
automation:
  - alias: "⚡ Démarrage charge heures creuses"
    description: "Démarre la charge en heures creuses"
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
      - service: notify.mobile_app
        data:
          title: "⚡ Charge démarrée"
          message: "Charge en heures creuses activée"
  
  - alias: "⚡ Arrêt charge fin heures creuses"
    description: "Arrête la charge à la fin des heures creuses"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.ma_voiture_charging
        state: "on"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.ma_voiture_charging
      - service: notify.mobile_app
        data:
          title: "⚡ Charge arrêtée"
          message: >
            Batterie: {{ states('sensor.ma_voiture_battery_level') }}%
```

### 3. Préchauffage intelligent

```yaml
automation:
  - alias: "❄️ Préchauffage matin"
    description: "Préchauffe la voiture avant le départ"
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
      - condition: state
        entity_id: binary_sensor.workday_sensor
        state: "on"
    action:
      - service: psacc.start_climate
        data:
          vin: VF3XXXXXXXXXXXXXXX
          temperature: 21
      - service: notify.mobile_app
        data:
          title: "❄️ Préchauffage activé"
          message: "Votre voiture sera prête dans 15 minutes"
```

### 4. Alerte portes non verrouillées

```yaml
automation:
  - alias: "🔓 Alerte portes non verrouillées"
    description: "Alerte si les portes ne sont pas verrouillées"
    trigger:
      - platform: state
        entity_id: binary_sensor.ma_voiture_doors_locked
        to: "off"
        for:
          minutes: 10
    condition:
      - condition: zone
        entity_id: device_tracker.ma_voiture_location
        zone: zone.home
        state: "not_home"
    action:
      - service: notify.mobile_app
        data:
          title: "🔓 Portes non verrouillées"
          message: "Votre voiture n'est pas verrouillée"
          data:
            tag: "car_unlocked"
            actions:
              - action: "LOCK_CAR"
                title: "Verrouiller maintenant"
                
  # Réponse à l'action
  - alias: "🔒 Verrouillage depuis notification"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "LOCK_CAR"
    action:
      - service: button.press
        target:
          entity_id: button.ma_voiture_lock_doors
      - service: notify.mobile_app
        data:
          title: "🔒 Verrouillage effectué"
          message: "Votre voiture est maintenant verrouillée"
```

### 5. Optimisation charge selon tarif électricité

```yaml
automation:
  - alias: "💰 Charge optimisée tarif"
    description: "Charge uniquement pendant les heures les moins chères"
    trigger:
      - platform: time_pattern
        minutes: "/30"  # Vérifie toutes les 30 minutes
    condition:
      - condition: state
        entity_id: binary_sensor.ma_voiture_plugged
        state: "on"
      - condition: numeric_state
        entity_id: sensor.ma_voiture_battery_level
        below: 80
    action:
      - choose:
          # Heures super creuses (2h-6h) - Charge rapide
          - conditions:
              - condition: time
                after: "02:00:00"
                before: "06:00:00"
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.ma_voiture_charging
              - service: number.set_value
                target:
                  entity_id: number.ma_voiture_charge_threshold
                data:
                  value: 100
          
          # Heures creuses (23h-2h et 6h-7h) - Charge normale
          - conditions:
              - condition: or
                conditions:
                  - condition: time
                    after: "23:00:00"
                    before: "02:00:00"
                  - condition: time
                    after: "06:00:00"
                    before: "07:00:00"
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.ma_voiture_charging
              - service: number.set_value
                target:
                  entity_id: number.ma_voiture_charge_threshold
                data:
                  value: 80
        
        # Par défaut - Arrêt charge
        default:
          - service: switch.turn_off
            target:
              entity_id: switch.ma_voiture_charging
```

### 6. Suivi des déplacements

```yaml
automation:
  - alias: "🚗 Départ domicile"
    trigger:
      - platform: state
        entity_id: device_tracker.ma_voiture_location
        from: "home"
    action:
      - service: notify.mobile_app
        data:
          title: "🚗 Départ"
          message: >
            Batterie: {{ states('sensor.ma_voiture_battery_level') }}%
            Autonomie: {{ states('sensor.ma_voiture_range_electric') }} km
  
  - alias: "🏠 Retour domicile"
    trigger:
      - platform: state
        entity_id: device_tracker.ma_voiture_location
        to: "home"
    action:
      - service: notify.mobile_app
        data:
          title: "🏠 Arrivée"
          message: >
            Vous êtes arrivé
            Batterie restante: {{ states('sensor.ma_voiture_battery_level') }}%
```

---

## 📊 Scripts

### 1. Préparer la voiture pour un départ

```yaml
script:
  prepare_car:
    alias: "Préparer la voiture"
    icon: mdi:car-electric
    sequence:
      # Réveiller le véhicule
      - service: psacc.wakeup
        data:
          vin: VF3XXXXXXXXXXXXXXX
      
      # Attendre 30 secondes
      - delay: "00:00:30"
      
      # Démarrer la climatisation
      - service: psacc.start_climate
        data:
          vin: VF3XXXXXXXXXXXXXXX
          temperature: 21
      
      # Notification
      - service: notify.mobile_app
        data:
          title: "🚗 Préparation en cours"
          message: "Votre voiture sera prête dans 10 minutes"
      
      # Attendre 10 minutes
      - delay: "00:10:00"
      
      # Notification finale
      - service: notify.mobile_app
        data:
          title: "✅ Voiture prête"
          message: >
            Température: {{ states('sensor.ma_voiture_temperature_exterior') }}°C
            Batterie: {{ states('sensor.ma_voiture_battery_level') }}%
            Autonomie: {{ states('sensor.ma_voiture_range_electric') }} km
```

### 2. Charge d'urgence

```yaml
script:
  emergency_charge:
    alias: "Charge d'urgence"
    icon: mdi:battery-alert
    sequence:
      # Vérifier si branché
      - condition: state
        entity_id: binary_sensor.ma_voiture_plugged
        state: "on"
      
      # Définir seuil à 100%
      - service: number.set_value
        target:
          entity_id: number.ma_voiture_charge_threshold
        data:
          value: 100
      
      # Démarrer charge
      - service: switch.turn_on
        target:
          entity_id: switch.ma_voiture_charging
      
      # Notification
      - service: notify.mobile_app
        data:
          title: "⚡ Charge d'urgence activée"
          message: "Charge à 100% démarrée"
```

### 3. Localiser la voiture

```yaml
script:
  find_car:
    alias: "Localiser la voiture"
    icon: mdi:map-marker
    sequence:
      # Klaxonner
      - service: psacc.horn
        data:
          vin: VF3XXXXXXXXXXXXXXX
          count: 2
      
      # Clignoter
      - delay: "00:00:02"
      - service: psacc.lights
        data:
          vin: VF3XXXXXXXXXXXXXXX
          count: 3
      
      # Notification avec carte
      - service: notify.mobile_app
        data:
          title: "📍 Voiture localisée"
          message: >
            Votre voiture se trouve à proximité
            Batterie: {{ states('sensor.ma_voiture_battery_level') }}%
          data:
            tag: "car_location"
            group: "car"
```

---

## 🎨 Templates utiles

### Calcul autonomie réelle

```yaml
sensor:
  - platform: template
    sensors:
      ma_voiture_real_range:
        friendly_name: "Autonomie réelle"
        unit_of_measurement: "km"
        value_template: >
          {% set battery = states('sensor.ma_voiture_battery_level')|float %}
          {% set consumption = states('sensor.ma_voiture_consumption')|float %}
          {% if consumption > 0 %}
            {{ ((battery / 100) * 50 / consumption * 100) | round(0) }}
          {% else %}
            {{ states('sensor.ma_voiture_range_electric') }}
          {% endif %}
```

### Temps avant charge complète

```yaml
sensor:
  - platform: template
    sensors:
      ma_voiture_charge_end_time:
        friendly_name: "Fin de charge estimée"
        device_class: timestamp
        value_template: >
          {% if is_state('binary_sensor.ma_voiture_charging', 'on') %}
            {% set minutes = states('sensor.ma_voiture_charging_time')|int %}
            {{ (now() + timedelta(minutes=minutes)).isoformat() }}
          {% else %}
            {{ 'unknown' }}
          {% endif %}
```

---

## 📱 Widgets iOS/Android

### Widget batterie (via Home Assistant App)

```yaml
type: glance
entities:
  - entity: sensor.ma_voiture_battery_level
    name: Batterie
    icon: mdi:battery-80
  - entity: sensor.ma_voiture_range_electric
    name: Autonomie
  - entity: binary_sensor.ma_voiture_charging
    name: Charge
show_name: true
show_icon: true
show_state: true
```

---

**Note** : Remplacez `VF3XXXXXXXXXXXXXXX` par le VIN réel de votre véhicule et `ma_voiture` par le nom de votre entité.
