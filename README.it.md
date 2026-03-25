<p align="center">
  <img src="AutoGPS-icon.png" alt="AutoGPS icon" width="150">
</p>

# AutoGPS by Bonn

> **[English](README.md)** | Italiano

**Versione attuale: 2.1.2**

Ogni volta che sali in macchina devi ricordarti di accendere il GPS. Ogni volta che scendi devi ricordarti di spegnerlo per non massacrare la batteria. AutoGPS lo fa al posto tuo.

L'app rileva quando il telefono si connette al Bluetooth dell'auto (o quando parte Android Auto) e accende il GPS automaticamente. Quando ti disconnetti, lo spegne. Ricorda anche dove hai parcheggiato, così puoi ritrovare la macchina senza pensarci. E se dovesse succedere qualcosa di brutto durante il viaggio, rileva l'incidente e avvisa i tuoi contatti di emergenza con la tua posizione.

---

## Come funziona

AutoGPS resta in ascolto in background e reagisce a due tipi di eventi:

**Bluetooth** — Configuri uno o più dispositivi (vivavoce, autoradio, adattatore OBD). Quando almeno uno si connette, il GPS si accende. Quando tutti si disconnettono, si spegne.

**Android Auto** — Se usi Android Auto, l'app lo rileva automaticamente e gestisce il GPS indipendentemente dal Bluetooth.

I due trigger lavorano in OR: basta che uno dei due sia attivo perché il GPS resti acceso. Si spegne solo quando nessuno dei due è attivo.

**Ultimo parcheggio** — Ogni volta che lasci l'auto, l'app salva la posizione e te la mostra sulla mappa con l'indirizzo e da quanto tempo sei parcheggiato. Toccando la mappa si apre Google Maps; il pulsante "Naviga qui" avvia la navigazione a piedi verso la macchina. Tutto rimane sul tuo dispositivo, nessun dato viene inviato a server.

**Rilevamento incidente** — Se durante il viaggio il telefono rileva un colpo forte (tramite l'accelerometro del telefono), aspetta qualche secondo e poi controlla se l'auto si è fermata. Se resta ferma per 3 minuti, mostra una schermata rossa di emergenza — visibile anche a schermo bloccato — con due pulsanti grandi: "SÌ, avvisa contatti di emergenza" e "NO, è un falso allarme". Se premi SÌ, l'app invia un SMS con la tua posizione esatta (link Google Maps) ai contatti di emergenza che hai configurato. Se non tocchi nessun pulsante entro un minuto, l'app suona un allarme a volume crescente per attirare l'attenzione. Se ancora non rispondi dopo un altro minuto, l'SMS viene inviato automaticamente — così anche se sei privo di sensi, i tuoi contatti verranno avvisati. L'allarme esce sempre dallo speaker del telefono (mai dal Bluetooth) e mette in pausa la musica in riproduzione per farsi sentire chiaramente. Il rilevamento funziona solo durante la guida (Bluetooth connesso o Android Auto attivo) e non interferisce con il funzionamento normale dell'app. Puoi regolare la sensibilità e scegliere i contatti dalla schermata principale.

**Widget parcheggio** — Puoi aggiungere un widget alla schermata home del telefono che mostra sempre l'indirizzo dell'ultimo parcheggio e da quanto tempo sei parcheggiato. Toccando il widget si apre direttamente la navigazione verso l'auto, senza passare dall'app. Un pallino verde o grigio indica se il GPS è attivo. Il widget si aggiorna automaticamente ogni volta che parcheggi.

**Lingua** — L'app è disponibile in italiano e inglese. Puoi cambiare lingua in qualsiasi momento dal toggle in alto a destra nella schermata principale. La scelta resta attiva anche dopo il riavvio dell'app.

L'app sopravvive al riavvio del telefono, funziona con lo schermo spento, e ha un consumo di batteria trascurabile.

---

## Requisiti

- **Telefono Android 8.0 o superiore** (Android 9, 10, 11, 12, 13, 14, 15, 16 — tutti compatibili). Testata su Pixel 8 Pro.
- **Un computer** (Windows, Mac o Linux) con una porta USB libera — serve solo per la configurazione iniziale, una volta sola. Dopo di che puoi dimenticartene.

---

## Guida all'installazione

La guida è divisa in 9 fasi. Le fasi 2-7 si fanno una sola volta. Ci vogliono circa 15-20 minuti la prima volta.

---

## FASE 1 — Scaricare l'APK

Un APK è il file di installazione delle app Android, lo stesso che usa il Play Store internamente. AutoGPS non è sul Play Store, quindi lo scarichi direttamente da qui.

**Clicca su questo link:**

**[AutoGPS-by-Bonn-v2.1.2.apk](AutoGPS-by-Bonn-v2.1.2.apk)** (9 MB)

> **Hai dubbi sulla sicurezza?** Leggi il documento [Sicurezza e Privacy](SECURITY.md) per sapere nel dettaglio come l'app protegge i tuoi dati: crittografia AES-256, zero tracciamento, zero server, SMS verificati.

Cliccando sul link verrai portato a una pagina di GitHub che mostra il file. Non vedrai niente di scaricato — quella è solo la pagina di "anteprima" del file su GitHub. Per scaricare effettivamente il file devi:

- Cliccare sull'**icona con i tre puntini** (⋮) in alto a destra della pagina, oppure
- Cliccare sul pulsante con la **freccia verso il basso** ("Download raw file")

Il file verrà salvato nella cartella **Download**.

Dopo il download, **torna su questa pagina** per seguire i passi successivi.

---

## FASE 2 — Preparare il computer

Per concedere ad AutoGPS il permesso speciale di cui ha bisogno, devi usare uno strumento chiamato **ADB** (Android Debug Bridge). In parole semplici: è un programma che permette al computer di "parlare" con il telefono Android tramite cavo USB e dare istruzioni che normalmente non si possono dare dall'interfaccia grafica.

**Buona notizia:** non devi installare niente di complicato. ADB è un semplice file eseguibile che scarichi, estrai e usi.

**Non serve Android Studio** — è un programma enorme da diversi gigabyte pensato per chi sviluppa app. Per i nostri scopi basta scaricare solo ADB.

### Scaricare ADB

Vai su questa pagina ufficiale di Google:
**https://developer.android.com/tools/releases/platform-tools**

Scorri verso il basso fino alla sezione "Downloads" e scarica la versione per il tuo sistema operativo:

**Windows:**

1. **Clicca su "Download SDK Platform-Tools for Windows"**
2. Accetta i termini e clicca su "Download"
3. Verrà scaricato uno zip — aprilo e trascina la cartella `platform-tools` nella tua cartella **Download** (o dove preferisci, ma ricorda dove la metti)

**Mac:**

1. **Clicca su "Download SDK Platform-Tools for Mac"**
2. Accetta i termini e clicca su "Download"
3. Verrà scaricato uno zip — aprilo e trascina la cartella `platform-tools` nella tua cartella **Download**
4. In alternativa, se hai Homebrew installato, puoi aprire il Terminale e scrivere: `brew install android-platform-tools`

**Linux (Ubuntu/Debian):**

1. **Clicca su "Download SDK Platform-Tools for Linux"**, scarica e decomprimi, oppure

2. Apri il terminale e scrivi:
   
   ```
   sudo apt install adb
   ```

---

## FASE 3 — Attivare le Opzioni sviluppatore sul telefono

Il telefono nasconde alcune funzioni avanzate per evitare che gli utenti le tocchino per errore. Per usare ADB devi prima "sbloccare" queste funzioni con un piccolo trucco.

**Passo per passo:**

1. **Apri l'app Impostazioni** sul telefono (la rotella dentata)

2. **Scorri in fondo e cerca "Info telefono"** — potrebbe chiamarsi anche "Informazioni sul telefono", "Informazioni sul dispositivo" o simile. Il nome varia a seconda del produttore.

3. **Entra in "Info telefono"** e cerca la voce **"Numero build"**. Su alcuni telefoni è nascosta dentro "Informazioni software" o "Informazioni sulla versione". Guardati attorno — c'è.

4. **Tocca "Numero build" 7 volte di fila, velocemente.** Non è uno scherzo — è davvero così che funziona.
   
   - Dopo il terzo o quarto tocco comparirà un messaggio tipo: *"Sei a 3 passi dall'essere uno sviluppatore"*
   - Continua a toccare
   - Al settimo tocco comparirà: *"Ora sei uno sviluppatore!"* (o un messaggio simile)
   - Se il telefono ha un PIN, potrebbe chiederti di inserirlo

5. **Premi il tasto Indietro** fino a tornare alla schermata principale delle Impostazioni.

6. **Ora troverai una nuova voce: "Opzioni sviluppatore"** — potrebbe trovarsi direttamente nell'elenco principale, oppure dentro **Sistema** > **Avanzate** > **Opzioni sviluppatore**. Dipende dal produttore.

---

## FASE 4 — Attivare il Debug USB

Il Debug USB è la funzione che permette ad ADB di comunicare con il telefono.

1. **Apri "Opzioni sviluppatore"** (che hai appena sbloccato nella Fase 3)

2. **Scorri verso il basso** fino a trovare la voce **"Debug USB"** — su alcuni telefoni si chiama "Debug Android"

3. **Attiva l'interruttore** spostandolo verso destra (diventa colorato)

4. Comparirà una finestra di avviso che dice che questa funzione è pensata per lo sviluppo. **Tocca "OK"** per confermare.

---

## FASE 5 — Collegare il telefono al computer

1. **Collega il telefono al computer con un cavo USB.** Se possibile usa il cavo originale del telefono — alcuni cavi economici sono "solo ricarica" e non trasmettono dati.

2. **Sul telefono potrebbe comparire una notifica** tipo "Seleziona modalità USB" o "Opzioni USB". Se compare, **seleziona "Trasferimento file"** (o "MTP"). NON scegliere "Solo ricarica" — con quella opzione il computer non riesce a comunicare con il telefono.

3. **Comparirà una finestra sul telefono** con scritto qualcosa tipo: **"Consenti debug USB?"** e un codice chiamato "impronta RSA". Questo è normale — il sistema vuole confermare che sei tu ad aver autorizzato il computer.
   
   - **Tocca "Consenti"**
   - Puoi anche spuntare la casella "Consenti sempre da questo computer" così non te lo chiede di nuovo

**Se la finestra non compare:**

- Stacca il cavo USB e riattaccalo
- Oppure torna in Opzioni sviluppatore, disattiva Debug USB, riattivalo, poi riattacca il cavo
- Assicurati di aver scelto "Trasferimento file" e non "Solo ricarica"

---

## FASE 6 — Aprire il terminale sul computer

Il terminale (detto anche "prompt dei comandi" su Windows) è una finestra dove scrivi comandi testuali. Sembra complicato ma userai solo 3 comandi copiati da questa guida.

**Windows:**

1. Premi il **tasto Windows + R** sulla tastiera (tasto con il logo di Windows, tenuto premuto, poi R)
2. Nella piccola finestra che compare, scrivi **`cmd`** e premi Invio
3. Si apre una finestra nera — è il Prompt dei comandi
4. In alternativa: cerca **"cmd"** o **"Prompt dei comandi"** nella barra di ricerca di Windows

**Mac:**

1. Premi **Cmd + Spazio** per aprire Spotlight
2. Scrivi **"Terminale"** e premi Invio
3. In alternativa: vai in Applicazioni > Utility > Terminale

**Linux:**

1. Cerca **"Terminale"** nel menu delle applicazioni
2. Oppure premi **Ctrl + Alt + T** (funziona su molte distribuzioni)

---

## FASE 7 — Installare l'APK e concedere il permesso

Ora che hai il terminale aperto e il telefono collegato, puoi fare tutto in pochi comandi.

### Navigare nella cartella platform-tools

Prima devi dire al terminale di "entrare" nella cartella `platform-tools` che hai scaricato nella Fase 2.

**Windows** (se hai messo platform-tools nella cartella Download):

```
cd %USERPROFILE%\Downloads\platform-tools
```

**Mac/Linux** (se hai messo platform-tools nella cartella Download):

```
cd ~/Downloads/platform-tools
```

Se hai messo la cartella altrove, adatta il percorso di conseguenza.

### Verificare che il telefono sia riconosciuto

**Copia e incolla questo comando, poi premi Invio:**

```
adb devices
```

Dovresti vedere un output simile a questo:

```
List of devices attached
XXXXXXXX    device
```

La parola `device` (o una serie di numeri/lettere) indica che il telefono è riconosciuto. **Se vedi `unauthorized`**, torna al telefono: dovrebbe esserci una notifica "Consenti debug USB?" in attesa — tocca "Consenti".

Se non vedi nessun dispositivo, controlla che il cavo sia ben inserito e che tu abbia selezionato "Trasferimento file" nella Fase 5.

### Installare l'APK

**Windows** — se l'APK è nella cartella Download:

```
adb install "%USERPROFILE%\Downloads\AutoGPS-by-Bonn-v2.1.2.apk"
```

**Mac/Linux** — se l'APK è nella cartella Download:

```
adb install ~/Downloads/AutoGPS-by-Bonn-v2.1.2.apk
```

Se l'APK si trova in un'altra cartella, sostituisci il percorso con quello corretto. Al termine dovresti vedere `Success`.

**Alternativa senza ADB per l'installazione:** puoi anche trasferire l'APK sul telefono (via cavo, WhatsApp, email, Google Drive...) e installarlo aprendo il file dal gestore file del telefono. Android ti chiederà di abilitare l'installazione da "origini sconosciute" — conferma. Anche in questo caso dovrai comunque eseguire il comando del permesso qui sotto.

### Concedere il permesso speciale

Questo è il passaggio fondamentale. Senza di esso l'app non può controllare il GPS.

**Copia e incolla esattamente questo comando, poi premi Invio:**

```
adb shell pm grant com.autogps.app android.permission.WRITE_SECURE_SETTINGS
```

Se il comando va a buon fine **non compare nessun messaggio** — il cursore torna semplicemente a capo. Silenzio = successo. Se invece compare un messaggio di errore, leggi la sezione "Risoluzione problemi" in fondo a questa guida.

---

## FASE 8 — Configurare l'app

Apri AutoGPS sul telefono. La prima volta ti verrà chiesto di concedere alcuni permessi.

### Permessi runtime

Quando l'app te li chiede, **concedili tutti:**

- **Bluetooth** — necessario per rilevare quando ti connetti all'auto
- **Posizione** — richiesta dal sistema Android per qualsiasi app che usa il Bluetooth
- **Posizione in background** — quando ti viene chiesto, seleziona **"Consenti sempre"** e non "Solo durante l'uso". Senza questa opzione l'app non funziona con lo schermo spento.
- **Notifiche** — necessaria per la notifica che conferma che il servizio è attivo in background
- **SMS** — necessario se vuoi che l'app possa inviare messaggi di emergenza in caso di incidente
- **Overlay (visualizzazione sopra altre app)** — se l'app mostra un banner arancione con scritto "Permesso overlay mancante", toccalo per aprire le impostazioni e concedere il permesso. Serve per mostrare la schermata di emergenza anche quando il telefono è bloccato.

### Aggiungere i dispositivi Bluetooth

Nella sezione **"Trigger Bluetooth"** tocca **"Aggiungi dispositivo"** e seleziona dalla lista il Bluetooth della tua auto (vivavoce, autoradio, o qualsiasi dispositivo Bluetooth a bordo). Puoi aggiungerne quanti ne vuoi.

### Android Auto (opzionale)

Se vuoi che l'app funzioni anche con Android Auto, nella sezione dedicata tocca **"Apri impostazioni accessibilità"** e abilita il servizio AutoGPS nell'elenco. Non è obbligatorio — se non usi Android Auto, salta questo passaggio.

### Ottimizzazione batteria

Se nella schermata principale vedi un **banner arancione**, toccalo e segui le istruzioni per escludere AutoGPS dall'ottimizzazione batteria. Questa ottimizzazione è una funzione di Android che "sospende" le app in background per risparmiare energia — ma per AutoGPS è un problema perché deve sempre restare in ascolto.

### Contatti di emergenza (opzionale)

Se vuoi usare la funzione di rilevamento incidente, nella sezione "Rilevamento Incidente" della schermata principale tocca "Contatti di emergenza". Da qui puoi:

- **Importare un contatto dalla rubrica** del telefono
- **Inserire un contatto manualmente** con nome e numero di telefono

Aggiungi almeno un contatto — in caso di incidente, l'app invierà un SMS a tutti i contatti in lista con un link alla tua posizione su Google Maps. Puoi aggiungere, modificare o eliminare i contatti in qualsiasi momento.

Con lo **slider "Soglia rilevamento impatto"** puoi regolare quanto l'app deve essere sensibile: un valore basso rileva anche urti lievi (ma può dare falsi allarmi), un valore alto rileva solo urti molto forti. Il valore predefinito (2.8G) è un buon compromesso per la maggior parte delle situazioni.

---

## FASE 9 — Verifica che tutto funzioni

Questo test richiede 5 minuti ed è il modo migliore per confermare che la configurazione è riuscita.

1. **Assicurati che il GPS sia spento** (puoi verificarlo aprendo Google Maps — se non trova la posizione, è spento)
2. **Connetti il Bluetooth dell'auto** dal telefono (come faresti normalmente)
3. **Controlla che il GPS si sia acceso da solo** — dovrebbe succedere entro pochi secondi
4. **Disconnetti il Bluetooth**
5. **Controlla che il GPS si spenga** — potrebbero volerci fino a 5 minuti, è normale

Se GPS si accende ma non si spegne, attendi qualche minuto — il servizio ha un ritardo intenzionale per evitare accensioni/spegnimenti rapidi.

---

## Risoluzione problemi

**"Il telefono non viene riconosciuto dal computer" (adb devices non mostra niente)**

- Controlla che il cavo USB sia ben inserito da entrambe le parti
- Prova una porta USB diversa del computer
- Assicurati di aver scelto "Trasferimento file" sul telefono (non "Solo ricarica")
- Su Windows: potrebbe servire installare i driver USB del produttore del telefono. Cerca su Google "driver USB [nome del tuo telefono]"

**"adb devices mostra 'unauthorized'"**

- Guarda il telefono: dovrebbe essere comparsa una notifica "Consenti debug USB?" — toccala e scegli "Consenti"
- Se la notifica non appare: stacca il cavo, disattiva e riattiva Debug USB nelle Opzioni sviluppatore, poi riattacca il cavo

**"Il comando adb non viene trovato" (errore tipo "adb is not recognized")**

- Sei sicuro di essere entrato nella cartella `platform-tools` con il comando `cd`? Prova a rifarlo.
- Su Windows: assicurati di aver estratto il file zip e di essere dentro la cartella `platform-tools`, non fuori
- Puoi anche provare a trascinare la finestra del terminale dentro la cartella `platform-tools` in Explorer — su alcune versioni di Windows questo apre il terminale già posizionato nella cartella giusta

**"L'app non accende il GPS dopo la configurazione"**

- Verifica che il permesso speciale sia stato concesso correttamente: riapri il terminale, rientra nella cartella platform-tools, e riesegui il comando `adb shell pm grant com.autogps.app android.permission.WRITE_SECURE_SETTINGS`
- Controlla che il GPS sul telefono sia completamente spento prima del test (non in modalità "risparmio")
- Se hai un telefono Xiaomi, Samsung, Huawei o Oppo, leggi la sezione "Limitazioni note" qui sotto

**"L'app smette di funzionare dopo qualche giorno"**

- Alcuni produttori (soprattutto Xiaomi, Huawei, Oppo) hanno sistemi aggressivi di risparmio batteria che "uccidono" le app in background. Vai su [dontkillmyapp.com](https://dontkillmyapp.com), cerca il tuo telefono e segui le istruzioni specifiche per il tuo modello.
- Assicurati di aver tolto AutoGPS dall'ottimizzazione batteria (Fase 8, ultimo punto)

---

## Aggiornamento

Quando esce una nuova versione, scarica il nuovo APK e installalo con:

```
adb install -r AutoGPS-by-Bonn-vX.Y.Z.apk
```

Il flag `-r` significa "reinstalla mantenendo i dati". Le impostazioni vengono conservate e **non serve riconcedere il permesso ADB** — rimane valido anche dopo l'aggiornamento.

In alternativa, puoi installarlo direttamente dal telefono (senza il comando `adb install`) — anche in questo caso le impostazioni e il permesso vengono mantenuti.

---

## Comportamento spegnimento GPS

Dall'app puoi scegliere cosa succede quando tutti i trigger si disattivano:

- **Disattiva GPS completamente** — il GPS si spegne del tutto (impostazione predefinita)
- **Modalità risparmio batteria** — il GPS resta attivo ma usa solo rete e Wi-Fi, senza il chip GPS (consuma meno ma ti localizza in modo meno preciso)

---

## Limitazioni note

- Il controllo del GPS funziona perfettamente su Pixel e dispositivi con Android "puro" (stock). Su telefoni con interfacce molto personalizzate (Xiaomi MIUI/HyperOS, Samsung One UI) il comportamento potrebbe variare a seconda della versione del sistema.
- Alcuni produttori (Xiaomi, Huawei, Oppo) hanno ottimizzazioni batteria aggressive che possono sospendere il servizio. Su questi dispositivi potrebbe servire una configurazione aggiuntiva — vedi [dontkillmyapp.com](https://dontkillmyapp.com) per istruzioni specifiche per il tuo modello.
- Il servizio di accessibilità per Android Auto può essere disabilitato automaticamente dal sistema dopo gli aggiornamenti del telefono. Se smette di funzionare, verifica che sia ancora attivo in Impostazioni > Accessibilità.
- Il rilevamento incidente usa l'accelerometro del telefono. La soglia di default (2.8G) è calibrata per distinguere un incidente da una frenata brusca, ma su strade molto dissestate potrebbe generare falsi allarmi. La soglia è configurabile dall'app.
- L'invio SMS di emergenza richiede una SIM attiva con credito sufficiente. Su telefoni senza SIM l'SMS non verrà inviato.

---

## Privacy e Sicurezza

L'app non comunica con nessun server, non raccoglie dati, non contiene analytics o tracker di nessun tipo. La posizione dell'ultimo parcheggio viene salvata solo sul tuo dispositivo, cifrata con crittografia AES-256. Tutto rimane sul tuo telefono.

In caso di incidente confermato dall'utente, l'app invia un SMS con la posizione ai soli contatti di emergenza configurati manualmente dall'utente. Nessun dato viene condiviso automaticamente e nessun server è coinvolto — l'SMS parte direttamente dal telefono.

Per tutti i dettagli tecnici sulle misure di sicurezza implementate, consulta il documento **[Sicurezza e Privacy](SECURITY.md)**.

---

## Changelog

### v2.1.2 — 25 marzo 2026

- SMS di emergenza inviati automaticamente dopo 60 secondi di allarme senza risposta (protegge l'utente incosciente)
- Allarme sonoro forzato sullo speaker del telefono, mai dal Bluetooth
- La musica si mette in pausa automaticamente durante l'allarme di emergenza
- Tutte le costanti di timing del rilevamento incidente centralizzate in un unico file di configurazione

### v2.1.1 — 24 marzo 2026

- Supporto lingua inglese con toggle in-app (IT/EN)
- La preferenza lingua resta attiva anche dopo il riavvio dell'app

### v2.1.0 — 23 marzo 2026

- Widget parcheggio per home screen: indirizzo, tempo relativo, tap per navigare direttamente all'auto
- Indicatore stato GPS nel widget (pallino verde/grigio)
- Supporto dark mode per il widget
- Rilevamento turbolenza post-impatto: l'app riconosce se l'auto sta rotolando dopo un colpo e aspetta che si fermi prima di valutare se è un incidente
- Soglia GPS dinamica basata sulla velocità: a 30 km/h bastano 18 metri per considerare l'auto ferma, a 130 km/h servono 333 metri
- Consiglio in-app per preferire il trigger Bluetooth rispetto ad Android Auto

### v2.0.0 — 22 marzo 2026

- Rilevamento incidente automatico durante la guida (accelerometro + verifica GPS fermo)
- Schermata di emergenza rossa fullscreen visibile anche a schermo bloccato
- Allarme sonoro a volume crescente se non si risponde entro 60 secondi
- Invio SMS di emergenza con posizione Google Maps ai contatti configurati
- Gestione contatti di emergenza (importazione da rubrica o inserimento manuale)
- Soglia sensibilità impatto configurabile (1.5G — 5.0G)
- Banner guida per permesso overlay

### v1.1.0 — 21 marzo 2026

- Feature "Ultimo parcheggio": quando il GPS si spegne l'app salva la posizione attuale
- Mappa nella schermata principale con pin sull'ultimo parcheggio
- Indirizzo testuale e indicazione "parcheggiato N minuti fa"
- Tocco sulla mappa per aprire Google Maps; pulsante "Naviga qui" per la navigazione a piedi verso la macchina

### v1.0.0 — 18 marzo 2026

- Prima release
- Trigger Bluetooth multi-dispositivo
- Trigger Android Auto
- Sopravvivenza al riavvio
- Compatibilità Android 8.0 — 16

---

## Ti è utile?

Se AutoGPS ti semplifica la vita, lascia una ⭐ al repository — è il modo più semplice per supportare il progetto.

## Autore e licenza

Sviluppato da [Andrea Bonacci](https://github.com/AndreaBonn).

Il codice sorgente è privato. L'uso dell'applicazione è libero e gratuito.
