---
name: portal-partner
description: >
  Assisti un PARTNER del gestionale Soolutions tramite la CLI `portal`:
  ticket di supporto dei suoi clienti finali, tempi di risposta SLA, stato delle
  commesse e prezzo di vendita. Usala quando l'utente è un partner (ruolo
  `partner`) e deve: vedere i ticket in scadenza, rispondere ai propri clienti,
  aprire una segnalazione verso Soolutions, controllare l'avanzamento dei lavori
  o il proprio contratto di supporto. Trigger: "partner", "rivenditore", "mio
  cliente", "ticket", "SLA", "in scadenza", "segnalazione", "supporto",
  "prezzo di vendita", "markup".
---

# Portal — assistente del partner

Il partner compra da Soolutions e rivende ai suoi clienti finali. Nel gestionale
è **primo livello di supporto**: la sua risposta pubblica su un ticket di un suo
cliente FERMA il cronometro SLA. Questa skill serve a farlo bene, dal terminale.

## 1 · Identità: verifica prima di agire

Primo comando, sempre:

```
portal me --json
```

Deve restituire `"role": "partner"`. Se il ruolo è diverso, **FERMATI** e dillo
all'utente: con un altro ruolo questa skill dà istruzioni sbagliate (usa
`portal-cli`, la skill di progetto). Se manca il token: `portal configure`, oppure
chiedilo all'utente — MAI inventarlo, mai usare quello di un altro.

Nessun binding di progetto serve: il partner lavora su più clienti e spesso
senza checkout. La skill si installa globale
(`portal skill install --variant partner --global`).

## 2 · Perimetro: cosa vedi e cosa no

Vedi, e solo per i TUOI clienti finali (e per te stesso):

- commesse e loro avanzamento (`portal commesse list|get`);
- ticket di supporto (`portal ticket …`);
- anagrafica dei tuoi clienti (`portal clients list|create`);
- i tuoi contratti di supporto (`portal support contracts`);
- il prezzo di VENDITA che hai fissato (`portal commesse sale`).

**Puoi PROPORRE** (non decidere): aprire una commessa in bozza per un tuo cliente
finale, duplicare la versione corrente per proporre modifiche ai requisiti, al
nome della commessa e alla proposta economica, e inviarla in approvazione. Diventa
il contratto **solo quando Soolutions la approva**: quello resta un gesto nostro.

NON esiste per te: la chat interna di commessa, il prezzo che Soolutions applica a
te quando non è condiviso, la flotta di agenti e l'orchestratore, i piani/contratti
di altri clienti, e l'APPROVAZIONE delle proposte (anche delle tue). Un **404 fuori
perimetro è normale**, non un errore da aggirare: non riprovare con altri id e non
cambiare ambiente.

## 3 · Loop quotidiano

```
portal notifications list --unread        # cosa è successo per te (parti da qui)
portal ticket list --json                 # tutti i tuoi ticket
portal ticket list --sla breached         # prima i violati
```

Le notifiche dicono COSA è successo e DOVE (nuovo ticket di un tuo cliente,
risposta nostra, esito di una proposta), mai il testo: aprile con `portal ticket get`
o `portal commesse get`, poi `portal notifications read <id…>` (o `--all`). Se una
resta non letta qualche minuto, all'utente arriva un riepilogo email.

Ordine di lavoro:

1. **SLA violati**, poi quelli più vicini alla scadenza (`sla.responseRemainingMs`).
2. **Rispondi ai ticket dei tuoi clienti**: la tua risposta pubblica ferma il timer
   (sei il primo livello). `portal ticket reply <id|codice> "testo"`.
3. **Controlla l'avanzamento** di ciò che hai venduto: `portal commesse get <id>`
   (requisiti soddisfatti = barra di progresso del cliente), `portal task list
   --commessa <id>` in sola lettura.

## 4 · Aprire un ticket verso Soolutions

```
portal ticket create "Checkout in errore 500" --commessa <id|.> \
  --severity critical|high|medium|low \
  --description "versione, come si riproduce, servizi coinvolti, da quando"
```

L'origine `partner` è dedotta dalla tua identità: i tuoi ticket arrivano marcati
come segnalazioni del partner e valgono quasi come segnalazioni tecniche.
Ricambia la fiducia: scrivi TU la diagnosi di primo livello (cosa hai già escluso),
non girare il messaggio del cliente così com'è.

## 5 · Audience: il thread è il canale

Le tue risposte sono **sempre pubbliche** (le legge anche il cliente finale): è il
sistema a imporlo, non serve alcun flag. Soolutions può scriverti in un canale
riservato («partner + noi»): quelle righe il tuo cliente non le vede.

Non promettere tempi che non controlli: se il ticket non ha contratto
(`sla.planName` null) NON esiste alcuno SLA da citare.

**Allegati**: log e screenshot si allegano al ticket, scegliendo chi li vede —
`portal task attach <ticketId> <file> --audience public|partner` (senza
`--audience` un file dello staff resta interno). Un file «partner» lo vedi tu e
Soolutions, non il tuo cliente.

**Ho scritto la cosa sbagliata.** Ogni messaggio si ritira entro 60 secondi:
`portal comment retract <commentId>` (l'id lo stampa la reply). Dopo il ritiro il
messaggio non è più visibile a nessuno tranne Soolutions, che lo vede segnato come
ritirato. Attenzione a cosa NON promette: se il cliente aveva la pagina aperta,
l'ha già letto — il ritiro chiude la porta, non riavvolge il tempo. Se sono passati
più di 60 secondi, chiedi a noi: admin e manager ritirano senza finestra.

## 6 · Stati del ticket

Puoi: `waiting-customer` (aspetti il tuo cliente), `resolved`, `closed`,
`reopen` (entro 30 giorni dalla risoluzione).

Su un ticket **risolto** rispondere e riaprire sono due gesti diversi: una
risposta normale lascia il ticket risolto (un «grazie» non riapre nulla), mentre
`portal ticket reply <id> "…" --reopen` lo riapre e riavvia il termine di
risoluzione. Su un ticket **chiuso** la risposta semplice è rifiutata: serve la
riapertura. Un risolto senza riscontro si chiude da sé dopo 7 giorni — ma non se
tu o il tuo cliente avete scritto nel frattempo.

La **gravità** non è tua (la cambia Soolutions) e non si cambia su un ticket
concluso.

```
portal ticket state <id> waiting-customer --note "in attesa dei log"
portal ticket resolve <id> --note "risolto: cache invalidata"
```

NON puoi mettere `waiting-partner`: quello lo mette Soolutions quando aspetta TE —
rispondi sul thread e si sblocca da solo. Le transizioni non previste sono
rifiutate: leggi `allowedStates` nel JSON del ticket invece di indovinare.

## 7 · Escalation a Soolutions

Non esiste un pulsante «escalation»: si dichiara nel thread, che è auditabile e
cronometrato.

```
portal ticket reply <id> "ESCALATION a Soolutions: riprodotto su 2 clienti, log allegati, serve intervento infrastrutturale"
```

Il triage di Soolutions pesca i ticket per urgenza SLA; il primo che risponde lato
Soolutions ferma il timer. Se il problema sembra infrastrutturale, dillo: il
supporto vede lo stato dei servizi e sa distinguere «era già giù prima» da
«è caduto dopo».

## 8 · Contratti e cronometro

```
portal support contracts --json
portal support contracts --client <clientId>
```

Il countdown ti è visibile solo se il contratto ha visibilità `partner` o
`client`: se non lo vedi, i tempi esistono comunque e li presidia Soolutions —
chiedi, non stimare.

## 9 · Prezzo di vendita: affare tuo

```
portal commesse sale <id|.> <importo in eur> [--share|--no-share] [--clear]
```

Il prezzo che fai al tuo cliente lo decidi tu. `--share` lo rende visibile a
Soolutions (utile quando volete ragionare insieme sul margine), `--no-share` lo
tiene riservato: nessuna delle due scelte cambia ciò che paghi a noi.

Divieti, in breve: mai token di altri; mai toccare task che non sono ticket; mai
insistere su un 404; mai APPROVARE una versione di commessa (nemmeno la propria);
mai promettere tempi fuori contratto.

## 9-bis · Proporre una commessa o una modifica

Il ciclo è sempre lo stesso: **bozza → invio → nostra approvazione**.

```
portal commesse create --name "Nome proposto" --client <clientId>   # nuova, in bozza
portal commesse duplicate <versionId>          # proponi modifiche alla corrente
portal commesse add-req <versionId> "Requisito" [--kind mandatory|optional]
portal commesse edit <versionId> [--name <nome>] [--description] [--budget <eur>]
portal commesse edit-req <versionId> REQ-n [--name] [--description] [--kind] [--group]
portal commesse rm-req <versionId> REQ-n       # soft-delete: le task collegate restano
portal commesse submit <versionId>             # in approvazione
portal commesse withdraw <versionId>           # ritira: torna un lavoro in corso
```

Cose da sapere prima di usarli:

- il **nome** che scrivi è una PROPOSTA: la commessa prende quel nome quando
  approviamo. Il **codice** (`C-2026-0007`) non cambia mai. Su una bozza già
  aperta il nome si propone (o si corregge) con `commesse edit <versionId>
  --name "…"`; `--name ""` ritira la proposta di rinomina;
- una proposta **senza requisiti** non si invia: aggiungine almeno uno;
- puoi editare la bozza anche dopo l'invio (chi revisiona vede sempre l'ultima
  versione), e **ritirarla** senza perdere niente;
- se la rifiutiamo, la nota spiega perché: `commesse duplicate <versionId>` della
  versione rifiutata riprende tutto — requisiti, prezzi, nome — e si riparte da lì;
- editi solo le bozze che hai scritto TU: quelle dei colleghi si leggono.

**Conferma con l'utente prima di inviare o ritirare**: un invio mette in moto una
nostra revisione, un ritiro la ferma.

### La trattativa è privata (e questo ti conviene)

Una tua proposta nasce **«partner + noi»**: la vediamo noi e la vedi tu, **il tuo
cliente finale non la vede** — non compare nel suo elenco versioni, non ha un
badge «proposta in corso», e l'URL diretto gli risponde «non trovata». Quindi
puoi chiederci uno sconto, discutere margini e cambiare idea senza che il tuo
cliente assista alla contrattazione. Anche la nostra **nota di rifiuto** segue la
stessa regola: la leggi tu, non lui.

```
portal commesse review <versionId>                    la conversazione sulla proposta
portal commesse review-comment <versionId> "testo" [--audience partner|public]
portal commesse share <versionId>                     mostrala al tuo cliente (IRREVERSIBILE)
portal comment retract <commentId> --review           ritira un messaggio (60s)
```

- sul thread di una proposta puoi scrivere a **due** livelli: `partner` (io e
  Soolutions — è il default) oppure `public` (anche il cliente finale). Il livello
  è stampato accanto a ogni messaggio: `[noi+partner]`, `[tutti]`;
- `[solo noi]` sono note interne di Soolutions: quelle non le vedi mai, ed è
  normale che nel thread ci siano righe che non ti riguardano;
- **`share` è irreversibile e alza solo la PROPOSTA**, non la conversazione: il
  cliente inizia a vedere i requisiti e i numeri che hai scritto, non lo scambio
  che c'è stato con noi. Chiedi conferma all'utente prima di usarlo;
- quando **approviamo**, la versione diventa pubblica per definizione: è il
  contratto, e il cliente deve poterlo leggere.

Se è il **cliente** ad aprire una modifica, il suo testo è pubblico: noi e te ne
discutiamo con messaggi `partner` (che lui non vede) e gli rispondiamo in `public`
solo quando siamo allineati. Non rispondere al cliente prima di aver sentito noi.

## 10 · Comandi e riferimenti

Ogni comando accetta `--env <nome>` e `--json` — in fondo, o subito dopo
`portal` (`portal --json ticket list`). In automazione usa sempre `--json`.

```
portal me [--json]                             identità e ruolo
portal ticket list [--state] [--sla breached|warning|ok|none] [--json]
portal ticket get <id|codice> [--json]         stato SLA + conversazione
portal ticket create <titolo...> --commessa <id> [--severity] [--description]
portal ticket reply <id> "testo" [--reopen]   la riapertura è esplicita
portal ticket state <id> <stato> · resolve|close|reopen <id>
portal task attach <id> <file> --audience public|partner   log e screenshot
portal support contracts [--client <id>]       i tuoi contratti e i tempi
portal commesse list|get [id] · commesse sale <id|.> <eur> [--share|--no-share]
portal commesse create --name <nome> --client <id>   apri una bozza (proposta)
portal commesse propose <id> · duplicate <vid>       proponi modifiche alla corrente
portal commesse add-req <vid> <nome> · edit-req <vid> REQ-n · rm-req <vid> REQ-n
portal commesse edit <vid> [--name] [--budget <eur>] · submit|withdraw <vid>
portal commesse review <vid> · review-comment <vid> "testo" [--audience partner|public]
portal commesse share <vid>                    mostra la proposta al cliente (irreversibile)
portal comment retract <commentId> [--review]  ritira un messaggio (entro 60s)
portal clients list|create <nome>              i tuoi clienti finali
portal task list --commessa <id>               avanzamento (sola lettura)
portal skill update --variant partner --global aggiorna QUESTA skill
```

Contratti JSON completi e protocollo di supporto: `<istanza>/llms.txt`.
Guida CLI stampabile: `<istanza>/downloads/portal-cli.pdf`. Manuale del partner
(perimetro, onboarding clienti, prezzi, ticket, con un protocollo per te in
appendice): `<istanza>/downloads/manuale-partner.pdf`.
Conferma con l'utente ogni scrittura che non ha chiesto esplicitamente; i comandi
read-only sono sempre sicuri.
