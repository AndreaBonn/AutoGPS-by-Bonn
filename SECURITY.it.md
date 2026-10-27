# Sicurezza - AutoGPS by Bonn

[English](SECURITY.md) | **Italiano**

Questo documento elenca le misure di sicurezza e privacy implementate nell'app e spiega come segnalare una vulnerabilità. Ogni sezione si chiude con una breve spiegazione per chi non ha una formazione tecnica.

## Versioni supportate

| Versione | Supportata |
|---|---|
| 3.1.x (ultima release) | Sì |
| Versioni precedenti | No, aggiorna all'[ultima release](https://github.com/AndreaBonn/AutoGPS-by-Bonn/releases/latest) |

## Segnalare una vulnerabilità

Scrivi a [andreabonacci95@protonmail.com](mailto:andreabonacci95@protonmail.com) con "AutoGPS security" nell'oggetto. Non aprire una issue pubblica per una vulnerabilità.

Indica:

- la versione dell'app, il modello del telefono e la versione di Android
- una descrizione del problema e i passi per riprodurlo
- cosa potrebbe ottenere un attaccante

<!-- TODO: aggiungere i tempi di risposta quando decisi; qui non è dichiarato nessuno SLA predefinito -->

La divulgazione pubblica è coordinata dopo il rilascio di una versione corretta.

## Misure di sicurezza implementate

### 1. Archiviazione cifrata sul dispositivo

Contatti di emergenza, indirizzi MAC dei dispositivi dell'auto e posizione dell'ultimo parcheggio sono salvati con `EncryptedSharedPreferences` (AndroidX Security): chiavi cifrate con AES-256-SIV, valori con AES-256-GCM. La chiave principale è custodita nell'Android Keystore.

Se il dispositivo non riesce a creare l'archivio cifrato (raro, su alcuni firmware vecchi o personalizzati), l'app ripiega sull'archiviazione privata standard di Android (`MODE_PRIVATE`) e continua a funzionare. I dati salvati prima che la cifratura fosse disponibile vengono migrati, e la migrazione si può ripetere senza danni se viene interrotta.

> **Per l'utente:** i tuoi contatti e i luoghi in cui parcheggi stanno in una cassaforte cifrata dentro il telefono. Chi copiasse i file dell'app vedrebbe solo dati illeggibili.

### 2. Nessun server, nessun tracciamento

L'app non ha account, analytics, telemetria né tracker. Fa solo queste connessioni di rete, tutte in HTTPS, e in nessuna invia dati personali:

| Connessione | Destinazione | Scopo | Frequenza |
|---|---|---|---|
| Controllo aggiornamenti | `raw.githubusercontent.com` | Scaricare `version.json` per sapere se c'è una nuova versione | Al massimo una volta ogni 24 ore |
| Elenco ZTL | `raw.githubusercontent.com` | Scaricare il dataset pubblico delle ZTL (`data/ztl_italia.json` in questo repository) | Al massimo una volta ogni 24 ore, o quando tocchi "Aggiorna ora" |
| Tile della mappa | `tile.openstreetmap.org` | Disegnare la mappa del parcheggio nell'app e nel widget | Quando viene mostrata una mappa del parcheggio |

Le richieste delle tile rivelano al server di OpenStreetMap la zona mostrata, come succede con qualsiasi mappa. Un elenco ZTL scaricato sostituisce quello attuale solo se si legge correttamente e contiene almeno una zona; altrimenti l'app tiene la versione che ha.

> **Per l'utente:** non esiste un "server di AutoGPS" che riceve i tuoi dati. Dove parcheggi, chi sono i tuoi contatti e quale auto usi restano sul tuo telefono.

### 3. Controllo degli aggiornamenti

Quando l'app controlla se c'è una nuova versione:

1. **Solo HTTPS**: il link di download è accettato solo se usa HTTPS.
2. **Host e percorso consentiti**: il link deve puntare a `github.com` o `raw.githubusercontent.com` e al percorso di questo repository; i percorsi con segmenti `.` o `..` vengono rifiutati.
3. **SHA-256 mostrato per il confronto**: se `version.json` contiene un hash SHA-256, l'app lo accetta solo se è di 64 caratteri esadecimali e lo mostra nella finestra di aggiornamento, così puoi confrontarlo con quello pubblicato nella release. L'app non calcola da sola l'hash del file scaricato.
4. **Timeout**: connessione e lettura vengono annullate dopo 5 secondi.

L'avviso di aggiornamento si può sempre ignorare. L'app non installa mai niente da sola: l'APK lo installi tu.

> **Per l'utente:** l'app propone solo aggiornamenti che arrivano da questo repository GitHub, e ti mostra un'impronta da confrontare con quella della pagina della release.

### 4. SMS di emergenza

Quando parte l'SMS di emergenza:

1. **Ogni parte è tracciata**: i messaggi lunghi vengono divisi, e l'app aspetta che la rete accetti ogni parte.
2. **Rapporti di consegna**: l'app ascolta anche il rapporto di consegna della rete del destinatario e ti dice quanti telefoni dei contatti hanno confermato la ricezione. I receiver dei rapporti sono privati dell'app (non esportati) e gli intent dei rapporti sono indirizzati solo al pacchetto dell'app.
3. **Esito onesto**: la schermata mostra "SMS inviati a 2/3 contatti" o "SMS non inviati" quando qualcosa fallisce, invece di un successo generico.
4. **Nessuna posizione sbagliata**: se il GPS non ha una posizione, l'SMS scrive "POSIZIONE NON DISPONIBILE".
5. **Nessun doppio invio**: dopo la prima scelta i pulsanti vengono disattivati, e un incidente produce un solo allarme e un solo giro di SMS. Un allarme di emergenza non va mai perso né ripetuto, e la modalità di prova non può assorbire un allarme vero.
6. **Dati dei contatti corrotti**: se un contatto salvato non si legge, gli altri vengono comunque caricati e usati.

La schermata di emergenza non si chiude con il tasto Indietro: devi scegliere "Chiedi aiuto", "Sto bene" o "Chiama il 112". "Chiama il 112" apre il telefono con il numero composto e non avvia la chiamata da solo.

> **Per l'utente:** in un'emergenza l'app ti dice cosa è successo davvero ai messaggi, e non manda mai i tuoi contatti nel posto sbagliato.

### 5. Uso limitato del permesso di sistema

Il permesso `WRITE_SECURE_SETTINGS`, concesso una volta via ADB, in teoria potrebbe modificare molte impostazioni di sistema. L'app lo usa tramite un unico helper che accetta solo la modalità di localizzazione e solo tre valori: spento (0), risparmio batteria (2) e alta precisione (3). Qualsiasi altro valore viene rifiutato con un errore.

AutoGPS registra anche se è stato lui ad accendere il GPS, e lo spegne solo in quel caso. Se hai acceso il GPS a mano, l'app lo lascia acceso.

> **Per l'utente:** l'app ha il potere di accendere e spegnere il GPS, e un blocco interno le impedisce di toccare qualsiasi altra cosa.

### 6. Backup, notifiche e log

| Misura | Dettaglio |
|---|---|
| `allowBackup="false"` | I backup di Android (cloud o locali) non includono i dati dell'app |
| `dataExtractionRules` | Le preferenze sono escluse dal backup cloud e dal trasferimento tra dispositivi |
| `PendingIntent` immutabili | Tutti i `PendingIntent` sono immutabili, tranne i rapporti di invio e consegna degli SMS, che Android deve compilare; questi sono indirizzati solo all'app stessa |
| Schermata di blocco | Le notifiche ordinarie sono private sulla schermata di blocco; solo l'allarme di emergenza e l'avviso ZTL sono pubblici, perché devono essere leggibili senza sbloccare |
| Log | Indirizzi, coordinate e altri dati personali finiscono nel log di sistema solo nelle build di debug, non nell'app rilasciata |

> **Per l'utente:** copiare o fare il backup del telefono non porta via i dati di AutoGPS, e l'app non lascia tracce personali nei log di sistema.

### 7. Test automatici

L'app è verificata da 720 test automatici (715 eseguiti a ogni build, 5 sono strumenti di sviluppo che vengono saltati). Coprono, tra l'altro, la logica di urto e di immobilità, il contenuto degli SMS di emergenza e il tracciamento della consegna, i contatti di emergenza, la whitelist del permesso GPS, la regola di proprietà del GPS, la politica del parcheggio, i controlli sul link di aggiornamento e la logica degli avvisi ZTL.

> **Per l'utente:** ogni versione passa centinaia di controlli automatici, con particolare attenzione alle parti che contano in caso di incidente.

## Fuori ambito

Non sono considerate vulnerabilità di AutoGPS:

- attacchi che richiedono l'accesso fisico a un telefono sbloccato, o un telefono con root
- il contenuto del dataset pubblico delle ZTL (le zone sbagliate si segnalano come feedback, vedi [FEEDBACK.it.md](FEEDBACK.it.md))
- mancate consegne degli SMS dovute alla rete mobile o alla SIM
- vulnerabilità già pubbliche di Android, Google Maps o librerie di terze parti (vanno segnalate ai rispettivi manutentori)

---

[Torna al README](README.it.md)
