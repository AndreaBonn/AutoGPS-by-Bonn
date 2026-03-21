# AutoGPS by Bonn

**Versione attuale: 1.1.0**

Ogni volta che sali in macchina devi ricordarti di accendere il GPS. Ogni volta che scendi devi ricordarti di spegnerlo per non massacrare la batteria. AutoGPS lo fa al posto tuo.

L'app rileva quando il telefono si connette al Bluetooth dell'auto (o quando parte Android Auto) e accende il GPS automaticamente. Quando ti disconnetti, lo spegne. Semplice.

## Download

Scarica l'APK dalla cartella di questo repository:

**[AutoGPS-by-Bonn-v1.1.0.apk](AutoGPS-by-Bonn-v1.1.0.apk)** (6 MB)

Compatibile con Android 8.0 e superiori (fino ad Android 16). Testata su Pixel 8 Pro.

## Come funziona

AutoGPS resta in ascolto in background e reagisce a due tipi di eventi:

**Bluetooth** — Configuri uno o più dispositivi (vivavoce, autoradio, adattatore OBD). Quando almeno uno si connette, il GPS si accende. Quando tutti si disconnettono, si spegne.

**Android Auto** — Se usi Android Auto, l'app lo rileva automaticamente e gestisce il GPS indipendentemente dal Bluetooth.

I due trigger lavorano in OR: basta che uno dei due sia attivo perché il GPS resti acceso. Si spegne solo quando nessuno dei due è attivo.

**Ultimo parcheggio** — Ogni volta che lasci l'auto, l'app salva la posizione e te la mostra sulla mappa con l'indirizzo e da quanto tempo sei parcheggiato. Toccando la mappa si apre Google Maps; il pulsante "Naviga qui" avvia la navigazione a piedi verso la macchina. Tutto rimane sul tuo dispositivo, nessun dato viene inviato a server.

L'app sopravvive al riavvio del telefono, funziona con lo schermo spento, e ha un consumo di batteria trascurabile.

## Installazione

### Opzione 1 — Da computer con ADB

```bash
adb install AutoGPS-by-Bonn-v1.1.0.apk
```

### Opzione 2 — Direttamente dal telefono

Scarica l'APK, aprilo dal file manager e conferma l'installazione. Android ti chiederà di abilitare l'installazione da origini sconosciute.

## Configurazione iniziale

Dopo l'installazione ci sono alcuni passaggi da fare una sola volta.

### 1. Concedere il permesso speciale (obbligatorio)

Questo è il passaggio fondamentale. Senza questo permesso l'app non può controllare il GPS.

Collega il telefono al PC via USB con il debug USB attivo e lancia:

```bash
adb shell pm grant com.autogps.app android.permission.WRITE_SECURE_SETTINGS
```

Nessun output = tutto ok.

**Come attivare il debug USB:** Impostazioni > Info telefono > tocca "Numero build" 7 volte > torna in Impostazioni > Sistema > Opzioni sviluppatore > Debug USB.

### 2. Permessi runtime

All'apertura l'app chiede diversi permessi. Concedili tutti:

- **Bluetooth** — per rilevare le connessioni
- **Posizione** — richiesta dal sistema per il Bluetooth
- **Posizione in background** — seleziona "Consenti sempre", non "Solo durante l'uso"
- **Notifiche** — per la notifica del servizio in background

### 3. Aggiungere i dispositivi Bluetooth

Nella sezione "Trigger Bluetooth" tocca "Aggiungi dispositivo" e seleziona il Bluetooth della tua auto dalla lista dei dispositivi accoppiati. Puoi aggiungerne quanti ne vuoi.

### 4. Android Auto (opzionale)

Se vuoi usare anche il trigger Android Auto, nella sezione dedicata tocca "Apri impostazioni accessibilità" e abilita il servizio AutoGPS. Non è obbligatorio.

### 5. Ottimizzazione batteria

Se vedi un banner arancione nella schermata principale, toccalo per disabilitare l'ottimizzazione batteria per AutoGPS.

### 6. Verifica

Spegni il GPS, connetti il Bluetooth dell'auto e controlla che il GPS si riaccenda da solo. Disconnetti e verifica che si spenga (Potrebbe impiegare fino a 5 minuti per lo spegnimento).

## Aggiornamento

Quando esce una nuova versione, scarica il nuovo APK e installalo sopra quello esistente:

```bash
adb install -r AutoGPS-by-Bonn-vX.Y.Z.apk
```

Oppure passati l'APK sul telefono e installalo normalmente. Le impostazioni vengono mantenute e non serve riconcedere il permesso ADB.

## Comportamento spegnimento GPS

Dall'app puoi scegliere cosa succede quando tutti i trigger si disattivano:

- **Disattiva GPS completamente** — il GPS si spegne del tutto (default)
- **Modalità risparmio batteria** — il GPS resta attivo ma usa solo rete e Wi-Fi, senza il chip GPS

## Limitazioni note

- Il controllo del GPS usa `Settings.Secure.LOCATION_MODE`, che funziona su Pixel e dispositivi stock Android. Su dispositivi con interfacce molto personalizzate (Xiaomi MIUI, Samsung One UI) il comportamento potrebbe variare.
- Alcuni produttori (Xiaomi, Huawei, Oppo) hanno ottimizzazioni batteria aggressive che possono terminare il servizio in background. Su questi dispositivi potrebbe servire una configurazione aggiuntiva — vedi [dontkillmyapp.com](https://dontkillmyapp.com) per istruzioni specifiche.
- Il servizio di accessibilità per Android Auto può essere disabilitato dal sistema dopo aggiornamenti. Se smette di funzionare, verifica che sia ancora attivo nelle impostazioni.

## Privacy

L'app non comunica con nessun server, non raccoglie dati, non contiene analytics o tracker. Tutto rimane sul tuo dispositivo.

## Changelog

### v1.1.0 — 21 marzo 2026

- Feature "Ultimo parcheggio": quando il GPS si spegne l'app salva la posizione attuale
- Mappa OSMDroid nella schermata principale con pin sull'ultimo parcheggio
- Indirizzo testuale via geocoding inverso e indicazione "parcheggiato N minuti fa"
- Tocco sulla mappa per aprire Google Maps; pulsante "Naviga qui" per la navigazione a piedi
- Nuova dipendenza: OSMDroid 6.1.20 (mappe OpenStreetMap gratuite, senza API key)
- Nuovi permessi: INTERNET e ACCESS_NETWORK_STATE (per i tile della mappa)

### v1.0.0 — 18 marzo 2026

- Prima release
- Trigger Bluetooth multi-dispositivo
- Trigger Android Auto via AccessibilityService
- UI Material Design 3 con dark mode e edge-to-edge
- Sopravvivenza al riavvio
- Compatibilità Android 8.0 — 16 (API 26-36)

## Ti è utile?

Se AutoGPS ti è piaciuto o ti semplifica la vita, lascia una ⭐ al repository — è il modo più semplice per supportare il progetto.

## Autore e licenza

Sviluppato da [Andrea Bonacci](https://github.com/AndreaBonn).

Il codice sorgente è privato. L'uso dell'applicazione è libero e gratuito.
