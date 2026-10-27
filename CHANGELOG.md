# Changelog

**English** | [Italiano](CHANGELOG.it.md)

## v3.1.0 (October 27, 2026)

- Android Auto is now detected through the official car connection API: just turn on "Use Android Auto", there is no accessibility service to enable anymore
- Emergency screen: new "Call 112" button
- Emergency SMS: the screen now tells you when your contacts' phones have confirmed delivery, not only when the message left
- GPS is turned off only if AutoGPS was the one that turned it on
- Parking: the spot is saved only from a fresh, accurate position, and a brief Bluetooth drop no longer switches GPS off
- Accident detection arms the impact sensor only while the car is moving
- ZTL: zones with unverified hours are labelled and can be hidden; GPS checks slow down when you are far from any zone, saving battery
- Fix: the app no longer crashes when started without the location permission
- Fix: safer update download check and settings migration

## v3.0.0 (October 26, 2026)

- Redesigned interface: first-run guide, setup checklist, master switch to pause AutoGPS, every feature explained in plain words
- ZTL alert only when you are actually approaching a zone (within 200 m and heading towards it), no longer every time you drive nearby
- Accident detection: Low/Medium/High sensitivity presets, emergency rehearsal, emergency screen with a big countdown and clear buttons
- Fix: a night-time ZTL window ending after midnight is now counted on the next day
- Fix: an emergency alert is never lost or sent twice, and the rehearsal can no longer swallow a real accident

## v2.4.0 (June 21, 2026)

- Parking timer: a second reminder now sounds 30 minutes before expiry, in addition to the 15-minute one
- Parking alerts play even in silent and Do Not Disturb mode, so an important reminder is never missed

## v2.3.0 (June 21, 2026)

- Parking timer: set a custom duration with a live countdown and an audible alert before it expires
- ZTL zone picker: quickly filter the zone list with a search field
- Expanded ZTL dataset to 302 zones across Italy with gate-based alerts

## v2.2.0 (June 20, 2026)

- ZTL alerts: full-screen warning before entering an active limited traffic zone (Italy)
- Bundled Italian ZTL dataset, refreshed automatically; works offline
- Exclude specific ZTLs you are authorized for so they never alert you

## v2.1.2 (March 25, 2026)

- Emergency SMS auto-sent after 60 seconds of unanswered alarm (protects unconscious users)
- Alarm sound forced to phone's built-in speaker, never Bluetooth
- Music automatically pauses during emergency alarm
- All accident detection timing constants centralized in one config file

## v2.1.1 (March 24, 2026)

- English language support with in-app toggle (IT/EN)
- Language preference persists across app restarts

## v2.1.0 (March 23, 2026)

- Parking widget for home screen: address, relative time, tap to navigate directly to the car
- GPS status indicator in widget (green/gray dot)
- Dark mode support for the widget
- Post-impact turbulence detection: the app recognizes if the car is rolling after an impact and waits for it to stop before evaluating if it's an accident
- Dynamic GPS stillness threshold based on speed: at 30 km/h 18 meters is enough to consider the car stopped, at 130 km/h 333 meters are needed
- In-app tip to prefer Bluetooth trigger over Android Auto

## v2.0.0 (March 22, 2026)

- Automatic accident detection while driving (accelerometer + GPS stillness check)
- Red fullscreen emergency screen visible even on lock screen
- Alarm sound at increasing volume if no response within 60 seconds
- Emergency SMS sending with Google Maps location to configured contacts
- Emergency contacts management (import from phonebook or manual entry)
- Configurable impact sensitivity threshold (1.5G-5.0G)
- Overlay permission guidance banner

## v1.1.0 (March 21, 2026)

- "Last parking" feature: when GPS turns off the app saves the current position
- Map on main screen with pin on last parking
- Text address and "parked N minutes ago" indicator
- Tap on map to open Google Maps; "Navigate here" button for walking navigation to the car

## v1.0.0 (March 18, 2026)

- First release
- Multi-device Bluetooth trigger
- Android Auto trigger
- Survives phone restart
- Android 8.0-16 compatibility

---

[Back to README](README.md)
