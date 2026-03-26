# Security — AutoGPS by Bonn

This document describes the security measures implemented in the app. Each technical section includes a plain-language explanation for readers without an IT background.

---

## 1. On-device data encryption

**Technology:** AES-256-GCM + AES-256-SIV via `EncryptedSharedPreferences` (AndroidX Security)

All sensitive data saved by the app is encrypted with 256-bit AES encryption, the same standard used by banks and governments. Protected data includes:

| Data | Why it's sensitive |
|------|-------------------|
| Emergency contact names and numbers | Personal information (PII) |
| Bluetooth device MAC addresses | Unique device identifiers |
| Last parking coordinates | User's physical location |

The encryption key is stored in the **Android Keystore**, a hardware-protected area of the phone that even other apps with root permissions cannot directly access.

If the device does not support hardware encryption (rare, on some very old models or with custom firmware), the app still works with standard Android protections (`MODE_PRIVATE`).

> **For the user:** Think of your data as locked inside a digital safe within the phone. Even if someone managed to copy the app's files, they would only see incomprehensible data. Without the key (which is physically tied to your phone) they cannot read anything.

---

## 2. No servers, no tracking

The app **does not communicate with any server** for its core features. There are no analytics, trackers, telemetry, or data collection of any kind.

The only two network connections are:

| Connection | Destination | Purpose | Frequency |
|------------|-------------|---------|-----------|
| Update check | `raw.githubusercontent.com` (GitHub) | Check if a newer version exists | Max once every 24 hours |
| Parking map | `tile.openstreetmap.org` | Download the map tile for the widget | Only when you park |

Both use **HTTPS** (encrypted connection). No personal data is sent — the app only downloads public information (the available version and a map image).

> **For the user:** The app works entirely on your phone. There is no "our server" receiving your data. Where you park, who your emergency contacts are, which Bluetooth devices you use — everything stays exclusively on your phone.

---

## 3. Secure updates

When the app checks for a newer version, it applies four layers of protection:

1. **Mandatory HTTPS** — The connection is encrypted. Any unencrypted response is rejected.
2. **Domain whitelist** — The download URL is accepted only if it points to `github.com` or `raw.githubusercontent.com`. A URL pointing to any other site is silently rejected, even if the format is correct.
3. **SHA-256 integrity verification** — If the version file contains a SHA-256 hash, the app validates it (it must be exactly 64 hexadecimal characters) and displays it in the update dialog. The user can compare the hash with the one published on GitHub to verify the downloaded file has not been tampered with.
4. **Network timeout** — If the server does not respond within 5 seconds, the request is automatically cancelled to prevent hangs.

The update dialog is **dismissible**: you can always ignore the update by pressing "Not now" or the back button.

> **For the user:** When the app tells you there's an update, it verifies the file actually comes from GitHub (where the code is published). If someone tried to tamper with the update check, the app would refuse to download from an unknown site. Additionally, if available, the app shows a "fingerprint" of the file (SHA-256) that you can compare with the one published on GitHub to make sure the file is authentic. And if you don't want to update, you can simply dismiss the notice.

---

## 4. Verified emergency SMS

When you press "YES, alert emergency contacts" after a detected accident, the app:

1. **Sends SMS in the background** without blocking the screen
2. **Verifies the delivery of each individual part** of the message (long SMS are automatically split)
3. **Waits for network confirmation** that each part was delivered to the message center
4. **Shows the actual result**: "SMS sent to 3 contacts" or "SMS sent to 2/3 contacts" if some fail

If an SMS fails (no signal, insufficient credit), the app reports it explicitly instead of pretending everything went fine.

The emergency contact list is also protected against **partial data corruption**: if a single contact is unreadable (for example after a system crash), the other valid contacts are still loaded and used for sending. The app never loses the entire emergency contact list because of a single corrupted entry.

The coordinates sent in the SMS are the actual ones detected by GPS. If GPS is unavailable (tunnel, underground parking), the SMS clearly states "LOCATION NOT AVAILABLE" instead of sending a wrong position.

After pressing "YES", the buttons are **immediately disabled** to prevent an accidental second tap (due to stress or the vehicle moving) from sending the SMS twice.

> **For the user:** In an emergency situation, it's crucial to know whether your contacts were actually alerted. The app doesn't tell you "done!" if something actually went wrong. And if the phone can't determine where you are, it tells your contacts clearly, instead of sending them to the wrong place.

---

## 5. Concurrency error protection

The accident detection system handles events from multiple sources simultaneously (motion sensor, timers, GPS). Critical operations use **atomic primitives** (`AtomicBoolean`, `AtomicInteger`) that guarantee:

- A single impact generates **one alarm only**, never two overlapping ones
- Bluetooth device checks at startup don't lose data even if two devices respond at the same instant
- SMS sending cannot be triggered twice for the same accident
- The **emergency screen cannot be accidentally dismissed**: the back button is blocked — the user must explicitly press "YES" or "NO"

> **For the user:** If you have an accident, the app shows you a single emergency screen (not two overlapping ones) and sends SMS only once (no duplicates). The screen won't close by accident if you press the back button — you must make an explicit choice. Everything works predictably even in chaotic situations.

---

## 6. Limited GPS permission

The app uses the `WRITE_SECURE_SETTINGS` permission (granted via ADB during installation) to control GPS. This permission is powerful — in theory it could modify many system settings.

To limit risk, the app uses a **whitelisted helper** that:

- Accepts **only** the command to change GPS mode
- Allows **only** three values: off (0), battery saving (2), high accuracy (3)
- **Rejects** any other value or setting with an explicit error

In practice, even if a bug in the app tried to use the permission for something else, the helper would block it.

> **For the user:** The app has the "power" to turn GPS on and off — that's its main function. But we've put an internal lock that prevents it from doing anything else with that power. It can only touch GPS, nothing else.

---

## 7. Protection against unauthorized backup

| Measure | Detail |
|---------|--------|
| `allowBackup=false` | Android's automatic backups (Google One, local backup) **do not include** the app's data |
| `dataExtractionRules` | SharedPreferences are excluded from both cloud backup and device-to-device transfer |
| `FLAG_IMMUTABLE` | All PendingIntents use the immutable flag to prevent manipulation by other apps |
| `VISIBILITY_PRIVATE` | App notifications do not show sensitive content on the lock screen |
| Debug-only logging | In production the app does not write any log containing personal data — no phone number, name, or coordinate ends up in system files |

> **For the user:** If someone connects your phone to a computer and tries to back up app data, AutoGPS data will not be copied. App notifications don't show private information on the lock screen. And the app leaves no traces in system logs.

---

## 8. Automated tests

The app includes **78 automated tests** that verify the correct behavior of critical components:

- Post-impact movement threshold calculation (physics formula)
- Emergency SMS content (text, coordinates, edge cases)
- Emergency contact management (add, remove, resilience to corrupted data)
- GPS settings whitelist (allowed and rejected values)
- Bluetooth device state (connection, disconnection, concurrency)

Tests are run automatically with every code change to ensure no update introduces regressions.

> **For the user:** Every time we update the app, 78 automated checks verify that everything works correctly — especially the parts that concern your safety in case of an accident. It's like a factory test that's repeated with every update.

---

## Summary

| Area | Protection |
|------|-----------|
| Data at rest | AES-256 encryption with hardware key |
| Data in transit | HTTPS for all connections |
| Updates | HTTPS + domain whitelist + SHA-256 + timeout |
| Emergency SMS | Delivery verification + real coordinates or "not available" + double-send block + corrupted data resilience |
| Emergency screen | Cannot be accidentally dismissed — explicit choice required |
| Concurrency | Atomic operations — no double alarms |
| GPS permission | Value whitelist — no misuse possible |
| Backup | Disabled — data not extractable |
| Privacy | Zero servers, zero tracking, zero analytics |
| Quality | 78 automated tests on critical components |

---

*Last updated: March 2026 — version 2.1.2*
