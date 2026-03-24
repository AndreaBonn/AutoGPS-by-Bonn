# Sicurezza — AutoGPS by Bonn

Questo documento descrive le misure di sicurezza implementate nell'app. Ogni sezione tecnica include una spiegazione in linguaggio naturale per chi non ha un background informatico.

---

## 1. Crittografia dei dati sul dispositivo

**Tecnologia:** AES-256-GCM + AES-256-SIV tramite `EncryptedSharedPreferences` (AndroidX Security)

Tutti i dati sensibili salvati dall'app sono cifrati con crittografia AES a 256 bit, lo stesso standard usato da banche e governi. I dati protetti includono:

| Dato | Perche' e' sensibile |
|------|---------------------|
| Nomi e numeri dei contatti di emergenza | Informazioni personali (PII) |
| Indirizzi MAC dei dispositivi Bluetooth | Identificatori univoci del dispositivo |
| Coordinate dell'ultimo parcheggio | Posizione fisica dell'utente |

La chiave di crittografia e' custodita nel **Android Keystore**, un'area hardware protetta del telefono a cui nemmeno altre app con permessi di root possono accedere direttamente.

Se il dispositivo non supporta la crittografia hardware (raro, su alcuni modelli molto vecchi o con firmware personalizzati), l'app funziona comunque con le protezioni standard di Android (`MODE_PRIVATE`).

> **Per l'utente:** Immagina che i tuoi dati siano chiusi in una cassaforte digitale all'interno del telefono. Anche se qualcuno riuscisse a copiare i file dell'app, vedrebbe solo dati incomprensibili. Senza la chiave (che e' legata fisicamente al tuo telefono) non possono leggere nulla.

---

## 2. Nessun server, nessun tracciamento

L'app **non comunica con nessun server** per le sue funzionalita' principali. Non ci sono analytics, tracker, telemetria, o raccolta dati di alcun tipo.

Le uniche due connessioni di rete sono:

| Connessione | Destinazione | Scopo | Frequenza |
|-------------|-------------|-------|-----------|
| Controllo aggiornamenti | `raw.githubusercontent.com` (GitHub) | Verificare se esiste una versione piu' recente | Max 1 volta ogni 24 ore |
| Mappa parcheggio | `tile.openstreetmap.org` | Scaricare il tassello di mappa per il widget | Solo quando parcheggi |

Entrambe avvengono su **HTTPS** (connessione cifrata). Nessun dato personale viene inviato — l'app scarica solo informazioni pubbliche (la versione disponibile e un'immagine della mappa).

> **Per l'utente:** L'app funziona interamente sul tuo telefono. Non esiste un "nostro server" che riceve i tuoi dati. Dove parcheggi, chi sono i tuoi contatti di emergenza, quali dispositivi Bluetooth usi — tutto resta esclusivamente nel tuo telefono.

---

## 3. Aggiornamenti sicuri

Quando l'app verifica se esiste una versione piu' recente, applica tre livelli di protezione:

1. **HTTPS obbligatorio** — La connessione e' cifrata. Rifiuta qualsiasi risposta non cifrata.
2. **Whitelist dei domini** — L'URL di download viene accettato solo se punta a `github.com` o `raw.githubusercontent.com`. Un URL che punta a qualsiasi altro sito viene rifiutato silenziosamente, anche se il formato e' corretto.
3. **Timeout di rete** — Se il server non risponde entro 5 secondi, la richiesta viene annullata automaticamente per evitare blocchi.

Il dialogo di aggiornamento e' **dismissibile**: puoi sempre ignorare l'aggiornamento premendo "Non ora" o il tasto indietro.

> **Per l'utente:** Quando l'app ti dice che c'e' un aggiornamento, verifica che il file provenga davvero da GitHub (dove il codice e' pubblicato). Se qualcuno provasse a manomettere il controllo aggiornamenti, l'app si rifiuterebbe di scaricare da un sito sconosciuto. E se non vuoi aggiornare, puoi semplicemente chiudere l'avviso.

---

## 4. SMS di emergenza verificati

Quando premi "SI', avvisa contatti di emergenza" dopo un incidente rilevato, l'app:

1. **Invia gli SMS in background** senza bloccare lo schermo
2. **Verifica l'invio di ogni singola parte** del messaggio (gli SMS lunghi vengono divisi automaticamente)
3. **Attende conferma dalla rete** che ogni parte sia stata consegnata al centro messaggi
4. **Mostra il risultato reale**: "SMS inviati a 3 contatti" oppure "SMS inviati a 2/3 contatti" se qualcuno fallisce

Se un SMS non riesce (mancanza di segnale, credito esaurito), l'app lo segnala esplicitamente invece di far credere che sia andato tutto bene.

Le coordinate inviate nell'SMS sono quelle reali rilevate dal GPS. Se il GPS non e' disponibile (tunnel, parcheggio sotterraneo), l'SMS indica chiaramente "POSIZIONE NON DISPONIBILE" invece di inviare una posizione sbagliata.

Dopo aver premuto "SI'", i pulsanti vengono **immediatamente disabilitati** per evitare che un secondo tocco accidentale (dovuto a stress o al veicolo in movimento) invii gli SMS due volte.

> **Per l'utente:** In una situazione di emergenza, e' fondamentale sapere se i tuoi contatti sono stati realmente avvisati. L'app non ti dice "fatto!" se in realta' qualcosa e' andato storto. E se il telefono non riesce a determinare dove ti trovi, lo dice chiaramente ai tuoi contatti, invece di mandarli nel posto sbagliato.

---

## 5. Protezione da errori di concorrenza

Il sistema di rilevamento incidenti gestisce eventi da piu' fonti contemporaneamente (sensore di movimento, timer, GPS). Le operazioni critiche usano **primitive atomiche** (`AtomicBoolean`, `AtomicInteger`) che garantiscono che:

- Un singolo impatto genera **un solo allarme**, mai due sovrapposti
- La verifica dei dispositivi Bluetooth all'avvio non perde dati anche se due dispositivi rispondono nello stesso istante
- L'invio SMS non puo' essere attivato due volte per lo stesso incidente
- La **schermata di emergenza non puo' essere chiusa accidentalmente**: il tasto indietro e' bloccato — l'utente deve premere esplicitamente "SI'" o "NO"

> **Per l'utente:** Se hai un incidente, l'app ti mostra una sola schermata di emergenza (non due sovrapposte) e invia gli SMS una sola volta (non duplicati). La schermata non si chiude per sbaglio se premi il tasto indietro — devi fare una scelta esplicita. Tutto funziona in modo prevedibile anche in situazioni caotiche.

---

## 6. Permesso GPS limitato

L'app utilizza il permesso `WRITE_SECURE_SETTINGS` (concesso via ADB durante l'installazione) per controllare il GPS. Questo permesso e' potente — in teoria permetterebbe di modificare molte impostazioni di sistema.

Per limitare il rischio, l'app usa un **helper con whitelist** che:

- Accetta **solo** il comando per cambiare la modalita' GPS
- Ammette **solo** tre valori: spento (0), risparmio batteria (2), alta precisione (3)
- **Rifiuta** qualsiasi altro valore o impostazione con un errore esplicito

In pratica, anche se un bug nell'app tentasse di usare il permesso per qualcos'altro, il helper lo bloccherebbe.

> **Per l'utente:** L'app ha il "potere" di accendere e spegnere il GPS — e' la sua funzione principale. Ma abbiamo messo un lucchetto interno che le impedisce di fare qualsiasi altra cosa con quel potere. Puo' solo toccare il GPS, nient'altro.

---

## 7. Protezione contro il backup non autorizzato

| Misura | Dettaglio |
|--------|-----------|
| `allowBackup=false` | I backup automatici di Android (Google One, backup locale) **non includono** i dati dell'app |
| `dataExtractionRules` | Le SharedPreferences sono escluse sia dal backup cloud che dal trasferimento tra dispositivi |
| `FLAG_IMMUTABLE` | Tutti i PendingIntent usano il flag immutabile per prevenire manipolazioni da altre app |
| `VISIBILITY_PRIVATE` | Le notifiche dell'app non mostrano contenuto sensibile sulla schermata di blocco |
| Log solo in debug | In produzione l'app non scrive nessun log — nessun dato finisce nei file di sistema |

> **Per l'utente:** Se qualcuno collega il tuo telefono a un computer e prova a fare un backup dei dati delle app, i dati di AutoGPS non verranno copiati. Le notifiche dell'app non mostrano informazioni private sulla schermata di blocco. E l'app non lascia tracce nei log di sistema.

---

## 8. Test automatici

L'app include **78 test automatici** che verificano il corretto funzionamento dei componenti critici:

- Calcolo della soglia di movimento post-impatto (formula fisica)
- Contenuto degli SMS di emergenza (testo, coordinate, casi limite)
- Gestione contatti di emergenza (aggiunta, rimozione, resilienza a dati corrotti)
- Whitelist delle impostazioni GPS (valori ammessi e rifiutati)
- Stato dei dispositivi Bluetooth (connessione, disconnessione, concorrenza)

I test vengono eseguiti automaticamente ad ogni modifica del codice per garantire che nessun aggiornamento introduca regressioni.

> **Per l'utente:** Ogni volta che aggiorniamo l'app, 78 controlli automatici verificano che tutto funzioni correttamente — specialmente le parti che riguardano la tua sicurezza in caso di incidente. E' come un collaudo di fabbrica che viene ripetuto ad ogni aggiornamento.

---

## Riepilogo

| Area | Protezione |
|------|-----------|
| Dati a riposo | Crittografia AES-256 con chiave hardware |
| Dati in transito | HTTPS per tutte le connessioni |
| Aggiornamenti | HTTPS + whitelist domini + timeout |
| SMS emergenza | Verifica invio + coordinate reali o "non disponibile" + blocco doppio invio |
| Schermata emergenza | Non chiudibile accidentalmente — scelta esplicita obbligatoria |
| Concorrenza | Operazioni atomiche — nessun doppio allarme |
| Permesso GPS | Whitelist valori — nessun uso improprio |
| Backup | Disabilitato — dati non estraibili |
| Privacy | Zero server, zero tracciamento, zero analytics |
| Qualita' | 78 test automatici sui componenti critici |

---

*Ultimo aggiornamento: marzo 2026 — versione 2.1.0*
