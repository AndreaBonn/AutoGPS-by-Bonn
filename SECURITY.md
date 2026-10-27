# Security - AutoGPS by Bonn

**English** | [Italiano](SECURITY.it.md)

This document lists the security and privacy measures implemented in the app and explains how to report a vulnerability. Each section ends with a short explanation for readers without a technical background.

## Supported Versions

| Version | Supported |
|---|---|
| 3.1.x (latest release) | Yes |
| Earlier versions | No, update to the [latest release](https://github.com/AndreaBonn/AutoGPS-by-Bonn/releases/latest) |

## Reporting a Vulnerability

Write to [andreabonacci95@protonmail.com](mailto:andreabonacci95@protonmail.com) with "AutoGPS security" in the subject. Do not open a public issue for a vulnerability.

Please include:

- the app version and the phone model with its Android version
- a description of the problem and the steps to reproduce it
- what an attacker could achieve

<!-- TODO: add response times once decided; no default SLA is stated here -->

Public disclosure is coordinated after a fixed version is released.

## Security Measures Implemented

### 1. Encrypted storage on the device

Emergency contacts, the MAC addresses of your car devices and the last parking position are stored with `EncryptedSharedPreferences` (AndroidX Security): keys encrypted with AES-256-SIV, values with AES-256-GCM. The master key lives in the Android Keystore.

If the device cannot create the encrypted store (rare, on some old or customized firmware), the app falls back to Android's standard private app storage (`MODE_PRIVATE`), so it keeps working. Data stored before encryption was available is migrated, and the migration can be retried safely if it is interrupted.

> **For the user:** your contacts and the places you park are kept in an encrypted safe inside the phone. Someone who copied the app's files would see unreadable data.

### 2. No servers, no tracking

The app has no account, no analytics, no telemetry and no tracker. It makes only these network connections, all over HTTPS, and sends no personal data in any of them:

| Connection | Destination | Purpose | Frequency |
|---|---|---|---|
| Update check | `raw.githubusercontent.com` | Download `version.json` to see if a new version exists | At most once every 24 hours |
| ZTL list | `raw.githubusercontent.com` | Download the public ZTL dataset (`data/ztl_italia.json` in this repository) | At most once every 24 hours, or when you tap "Update now" |
| Map tiles | `tile.openstreetmap.org` | Draw the parking map in the app and in the widget | When a parking map is shown |

The map tile requests reveal the area being displayed to the OpenStreetMap tile server, as with any map. A downloaded ZTL list replaces the current one only if it parses correctly and contains at least one zone; otherwise the app keeps the version it has.

> **For the user:** there is no "AutoGPS server" receiving your data. Where you park, who your contacts are and which car you use stay on your phone.

### 3. Update checks

When the app checks for a new version:

1. **HTTPS only**: the download link is accepted only if it uses HTTPS.
2. **Allowed hosts and path**: the link must point to `github.com` or `raw.githubusercontent.com` and to this repository's path; paths containing `.` or `..` segments are rejected.
3. **SHA-256 shown for comparison**: if `version.json` contains a SHA-256 hash, the app accepts it only as 64 hexadecimal characters and shows it in the update dialog, so you can compare it with the one published in the release. The app does not compute the hash of the downloaded file itself.
4. **Timeout**: connection and read are cancelled after 5 seconds.

The update notice can always be dismissed. The app never installs anything by itself: the APK is installed by you.

> **For the user:** the app only offers updates that come from this GitHub repository, and shows a fingerprint you can check against the one on the release page.

### 4. Emergency SMS

When the emergency SMS is sent:

1. **Each part is tracked**: long messages are split, and the app waits for the network to accept each part.
2. **Delivery reports**: the app also listens for the delivery report from the recipient's network and tells you how many contacts' phones confirmed delivery. The report receivers are private to the app (not exported) and the report intents are addressed only to the app's own package.
3. **Honest result**: the screen shows "SMS sent to 2/3 contacts" or "SMS not sent" when something fails, instead of a generic success.
4. **No wrong position**: if GPS has no position, the SMS says "LOCATION NOT AVAILABLE".
5. **No double send**: after the first choice the buttons are disabled, and one accident produces one alarm and one SMS round. An emergency alert is never lost or repeated, and the rehearsal mode cannot swallow a real alert.
6. **Corrupted contact data**: if one saved contact cannot be read, the others are still loaded and used.

The emergency screen cannot be closed with the back button: you must choose "Get help", "I'm OK" or "Call 112". "Call 112" opens the dialer and does not place the call by itself.

> **For the user:** in an emergency the app tells you what actually happened to the messages, and never sends your contacts to a wrong place.

### 5. Limited use of the system permission

The `WRITE_SECURE_SETTINGS` permission, granted once via ADB, could in principle change many system settings. The app uses it through a single helper that accepts only the location mode and only three values: off (0), battery saving (2) and high accuracy (3). Any other value is rejected with an error.

AutoGPS also records whether it was the one that turned GPS on, and turns it off only in that case. If you switched GPS on by hand, the app leaves it on.

> **For the user:** the app has the power to switch GPS on and off, and an internal lock stops it from touching anything else.

### 6. Backup, notifications and logs

| Measure | Detail |
|---|---|
| `allowBackup="false"` | Android backups (cloud or local) do not include the app's data |
| `dataExtractionRules` | Preferences are excluded from cloud backup and device-to-device transfer |
| Immutable `PendingIntent`s | All `PendingIntent`s are immutable, except the SMS sent and delivery reports, which Android must fill in; those are addressed only to the app itself |
| Lock screen | Ordinary notifications are private on the lock screen; only the emergency alarm and the ZTL alert are public, because they must be readable without unlocking |
| Logs | Addresses, coordinates and other personal data are written to the system log only in debug builds, not in the released app |

> **For the user:** copying or backing up the phone does not take AutoGPS data with it, and the app leaves no personal traces in system logs.

### 7. Automated tests

The app is checked by 720 automated tests (715 run on every build, 5 are developer tools that are skipped). They cover, among other things, the impact and stillness logic, the emergency SMS content and delivery tracking, the emergency contacts, the GPS permission whitelist, the GPS ownership rule, the parking policy, the update link checks and the ZTL alert logic.

> **For the user:** every version goes through hundreds of automatic checks, with particular attention to the parts that matter in an accident.

## Out of Scope

The following are not considered vulnerabilities of AutoGPS:

- attacks that need physical access to an unlocked phone, or a rooted phone
- the content of the public ZTL dataset (report wrong zones as feedback, see [FEEDBACK.md](FEEDBACK.md))
- SMS delivery failures caused by the mobile network or the SIM
- vulnerabilities in Android, Google Maps or third-party libraries that are already public (report them to their maintainers)

---

[Back to README](README.md)
