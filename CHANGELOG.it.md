# Changelog

[English](CHANGELOG.md) | **Italiano**

## v3.1.0 (27 ottobre 2026)

- Android Auto viene ora rilevato con l'API ufficiale di connessione all'auto: basta attivare "Usa Android Auto", non c'è più nessun servizio di accessibilità da abilitare
- Schermata di emergenza: nuovo pulsante "Chiama il 112"
- SMS di emergenza: la schermata ti dice quando i telefoni dei contatti hanno confermato la consegna, non solo quando il messaggio è partito
- Il GPS viene spento solo se è stato AutoGPS ad accenderlo
- Parcheggio: la posizione si salva solo da un rilevamento recente e preciso, e un breve calo del Bluetooth non spegne più il GPS
- Il rilevamento incidenti arma il sensore d'urto solo mentre l'auto è in movimento
- ZTL: le zone con orari non verificati sono etichettate e si possono nascondere; i controlli GPS rallentano quando sei lontano da ogni zona, risparmiando batteria
- Correzione: l'app non va più in crash se avviata senza il permesso di posizione
- Correzione: controllo del download degli aggiornamenti e migrazione delle impostazioni più sicuri

## v3.0.0 (26 ottobre 2026)

- Interfaccia rifatta: guida al primo avvio, checklist di configurazione, interruttore generale per mettere in pausa AutoGPS, ogni funzione spiegata in parole semplici
- Avviso ZTL solo quando ti stai davvero avvicinando a una zona (entro 200 m e in direzione della zona), non più ogni volta che le passi vicino
- Rilevamento incidenti: sensibilità Bassa/Media/Alta, prova di emergenza simulata, schermata di emergenza con conto alla rovescia grande e pulsanti chiari
- Correzione: una ZTL notturna che finisce dopo mezzanotte viene ora conteggiata sul giorno successivo
- Correzione: l'allarme di emergenza non viene mai perso né inviato due volte, e la prova simulata non può più nascondere un incidente reale

## v2.4.0 (21 giugno 2026)

- Timer parcheggio: un secondo promemoria suona 30 minuti prima della scadenza, oltre a quello dei 15 minuti
- Gli avvisi del parcheggio suonano anche in modalità silenziosa e Non disturbare

## v2.3.0 (21 giugno 2026)

- Timer parcheggio: imposta una durata personalizzata con conto alla rovescia e avviso sonoro prima della scadenza
- Selezione ZTL: campo di ricerca per filtrare rapidamente l'elenco delle zone
- Dataset ZTL esteso a 302 zone in tutta Italia, con avvisi basati sui varchi

## v2.2.0 (20 giugno 2026)

- Avvisi ZTL: schermata a tutto schermo prima di entrare in una zona a traffico limitato attiva (Italia)
- Dataset ZTL italiano incluso, aggiornato automaticamente; funziona offline
- Escludi le ZTL per cui sei autorizzato così non ti avvisano

## v2.1.2 (25 marzo 2026)

- SMS di emergenza inviati automaticamente dopo 60 secondi di allarme senza risposta (protegge l'utente incosciente)
- Allarme sonoro forzato sullo speaker del telefono, mai dal Bluetooth
- La musica si mette in pausa automaticamente durante l'allarme di emergenza
- Tutte le costanti di timing del rilevamento incidente centralizzate in un unico file di configurazione

## v2.1.1 (24 marzo 2026)

- Supporto lingua inglese con toggle in-app (IT/EN)
- La preferenza lingua resta attiva anche dopo il riavvio dell'app

## v2.1.0 (23 marzo 2026)

- Widget parcheggio per home screen: indirizzo, tempo relativo, tap per navigare direttamente all'auto
- Indicatore stato GPS nel widget (pallino verde/grigio)
- Supporto dark mode per il widget
- Rilevamento turbolenza post-impatto: l'app riconosce se l'auto sta rotolando dopo un colpo e aspetta che si fermi prima di valutare se è un incidente
- Soglia GPS dinamica basata sulla velocità: a 30 km/h bastano 18 metri per considerare l'auto ferma, a 130 km/h servono 333 metri
- Consiglio in-app per preferire il trigger Bluetooth rispetto ad Android Auto

## v2.0.0 (22 marzo 2026)

- Rilevamento incidente automatico durante la guida (accelerometro + verifica GPS fermo)
- Schermata di emergenza rossa fullscreen visibile anche a schermo bloccato
- Allarme sonoro a volume crescente se non si risponde entro 60 secondi
- Invio SMS di emergenza con posizione Google Maps ai contatti configurati
- Gestione contatti di emergenza (importazione da rubrica o inserimento manuale)
- Soglia sensibilità impatto configurabile (1.5G-5.0G)
- Banner guida per permesso overlay

## v1.1.0 (21 marzo 2026)

- Feature "Ultimo parcheggio": quando il GPS si spegne l'app salva la posizione attuale
- Mappa nella schermata principale con pin sull'ultimo parcheggio
- Indirizzo testuale e indicazione "parcheggiato N minuti fa"
- Tocco sulla mappa per aprire Google Maps; pulsante "Naviga qui" per la navigazione a piedi verso la macchina

## v1.0.0 (18 marzo 2026)

- Prima release
- Trigger Bluetooth multi-dispositivo
- Trigger Android Auto
- Sopravvivenza al riavvio
- Compatibilità Android 8.0-16

---

[Torna al README](README.it.md)
