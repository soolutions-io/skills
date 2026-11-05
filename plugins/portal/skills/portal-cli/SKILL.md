---
name: portal-cli
description: >
  Gestisci commesse, requisiti, task, chat di progetto e turni agente sul
  gestionale Soolutions tramite la CLI `portal`. Usala quando devi: fare
  l'onboarding di un progetto (associare la commessa, scegliere la modalità),
  scegliere/lavorare task, spuntare criteri di accettazione, leggere o scrivere
  nella chat di commessa, operare come worker agent o verificare l'avanzamento.
  Trigger: "portal", "gestionale", "commessa", "task", "REQ-", "chat di
  commessa", "menzione", "onboarding", "init", "worker", "agente", "turno",
  "clona il progetto", presenza di `.portal.json` nel repo.
---

# Portal CLI — gestionale Soolutions

Il gestionale (`portal context` mostra l'istanza) è la fonte di verità di requisiti,
task e avanzamento. Il cliente vede la barra di progresso calcolata sui requisiti
soddisfatti: si muove SOLO completando task collegate ai requisiti.

## Primo comando, SEMPRE: `portal context --json`

Ti dice dove sei: progetto, binding commessa, modalità, ambiente risolto, identità.
Da lì decidi:

- **`bound: true`** → il progetto è inizializzato: lavora (sezioni sotto).
- **`bound: false` o nessun progetto** → fai l'ONBOARDING (sezione sotto).
- **CLI assente** → installala: `curl -fsSL <istanza>/install.sh | sh` (Node ≥ 20).

## Onboarding di un progetto (quando manca `.portal.json`)

1. `portal me --json` — serve un token valido (se manca: `portal configure`, o chiedi
   all'utente il token; MAI inventarlo).
2. `portal commesse list --json` → **CHIEDI all'utente** quale commessa associare
   (mostra codice+nome). Non sceglierla mai da solo.
3. **CHIEDI la modalità di lavoro** (spiegala in una riga):
   - `developer` — agisci a nome dell'utente (fine-tuning continuo, pairing);
   - `worker` — personifichi un agente dedicato (task lunghe autonome, protocollo
     turni). Chiedi anche il nome dell'agente (es. «pippo»).
4. Esegui l'init NON interattivo e leggi il JSON:
   `portal init --commessa <id|codice> --mode <developer|worker> [--agent <nome>] --yes --json`
5. Ricorda all'utente di **committare `.portal.json`** (binding condiviso col team).

**Cartella vuota (cold start)**: se l'utente dice «lavoriamo alla commessa X» in una
cartella senza repo, aggiungi `--clone`: la CLI clona il repository collegato alla
commessa (chiede conferma) e inizializza dentro il clone. Se la commessa non ha un
repo collegato, un admin/manager lo imposta con `portal commesse repo <id> <url>`.

**Cambio modalità**: quando l'utente ti dice di cambiare comportamento («ora lavora
come te stesso», «diventa il worker pluto»), riesegui SOLO
`portal init --mode <m> [--agent <nome>] --yes` — aggiorna le preferenze personali
senza toccare `.portal.json`. Cambiare COMMESSA richiede `--force` (avvisa il team).

## Default commessa (dopo l'init)

Nel progetto inizializzato ometti l'id: `task list`, `agent next|wait|status|report`,
`task create`, `chat history|poll|team`, `payments …`, `commesse get|export` usano il
binding. Dove il posizionale è obbligatorio usa `.`: `portal chat send . "testo"`.
ECCEZIONI volute: `chat mentions` (inbox su TUTTE le commesse) e `webhooks add`
(omesso = tutte) non defaultano.

## Modalità developer (agisci come l'utente)

Sei le mani dell'utente: commenti, chat e stati portano il SUO nome.

- Ciclo: `task list` → `task get <id>` → `task status <id> open` → sviluppo →
  `task check <id> <n...>` (SOLO criteri implementati E verificati) → eventuale
  `task comment`. Le subtask sono i criteri di accettazione: tutte spuntate ⇒ task
  done ⇒ requisito Soddisfatto ⇒ avanza la barra del cliente.
- `chat poll .` a inizio sessione: se l'utente è menzionato, digli cosa gli chiedono.
- Claim (`task claim/release`) solo se nel progetto gira anche una flotta: eviti di
  pestare i piedi agli agenti (423 LOCKED = passa oltre, mai forzare claim altrui).

## Modalità worker (personifichi l'agente)

La tua identità è l'env dell'agente (la CLI la usa da sola: `↳ env '<slug>' …` su
stderr; verifica con `portal me`). Il web login degli agenti è bloccato: solo token.

Ciclo del turno (esatto):
1. `portal chat poll . --json` — briefing e ordini PRIMA della coda: se `mentionsMe`
   non è vuoto, gestisci quelle richieste e RISPONDI in chat prima di procedere.
2. `portal agent next --json` — null = fine turno (`agent report`, messaggio di
   chiusura in chat se serve handoff, poi FERMATI). `AGENT_BUSY` = finisci la corrente.
3. `task comments <id>` (riparti dal RIEPILOGO precedente) → `task get <id>` →
   sviluppo (heartbeat tra passi >10 min) → `task check` del verificato →
   `task comment "RIEPILOGO — …"` → `task release --outcome done|partial|blocked`
   (done chiude la task se i criteri sono spuntati o assenti).
4. Handoff: `portal chat send . "RILASCIO — <esito> <taskId> [REQ-n]. @<handle> <azione>"`
   — la @menzione È il trigger (review, deploy, sblocco). `chat team .` per gli handle.
5. Torna al punto 1. In attesa di lavoro: `portal agent wait --json`
   (exit 0 = menzione/task; exit 2 = timeout, chiudi il turno).

Regole flotta: una task in carico alla volta; mai claim altrui; menzionato ⇒ rispondi
SEMPRE in chat (anche solo «visto, non di mia competenza → @altro»); mai spuntare
criteri non verificati; il RIEPILOGO sta sulla task, la chat coordina TRA task.

## Ticket di supporto (se ne incroci uno)

Un ticket è una task con una macchina di supporto: lo STATO non si cambia da
`task status` né trascinandolo sul board, ma con `portal ticket state|resolve`.
Anche il rilascio è diverso: su un ticket `task release --outcome done` libera il
lease e NON lo completa. Rispondendo dal thread della task su un ticket, il
messaggio passa dal supporto: scegli i destinatari (una risposta «per tutti»
ferma il cronometro SLA e la legge il cliente). Le questioni interne su una
commessa altrui si aprono come ticket interni: `portal ticket create "…"
--internal`. Se ne prendi uno che non è per te, `portal ticket requeue <id>
--note "…"` lo restituisce al triage: NON usare `waiting-customer`, che ferma il
cronometro e finisce per sollecitare un cliente che non deve niente. Protocollo
completo del triage: `<istanza>/llms.txt`.

## Flag universali: `--env` e `--json`

OGNI comando che parla con l'API accetta `--env <nome>` (quale ambiente) e
`--json` (output strutturato) — in fondo al comando O subito dopo `portal`:
`portal me --json --env prod` ≡ `portal --env prod --json me`. Un flag sulla
foglia vince sul globale. In automazione preferisci SEMPRE `--json`: l'output
umano può cambiare, il JSON è il contratto. Alternative d'ambiente: la variabile
`PORTAL_ENV=<nome>` (stessa precedenza del flag globale) e `PORTAL_TOKEN` (vince
sul token salvato — per CI). Eccezioni senza `--json`: `commesse export` (ha
`--format csv|md`) e `task download` (scarica un file). Dopo
`commesse create/propose --json` l'id della bozza è `viewing.id` (o `versionId`
nel payload di `propose`).

## Comandi chiave

```
portal context [--json]                stato: progetto, modalità, identità
portal init [--commessa] [--mode] [--agent] [--clone] [--yes] [--json]
portal skill update                    aggiorna QUESTA skill dal server
portal task list|get|create|check|status|claim|release|comments|comment
portal agent next|wait|status|report|register [--json]
portal chat poll .|send . "…"|history|team|mentions [--unread]
portal notifications list [--unread] · read <id…>|--all · settings [--email on|off]
portal ticket list|get|state|resolve|requeue|reply [--audience] [--reopen]  supporto
portal comment retract <cid> [--review] · rescope <cid> --audience …   ritiro silenzioso
portal reviews                         proposte da decidere (admin/manager)
portal commesse list|get|export|repo · review|review-comment|share <vid>   proposte
portal commesse list|get|export|repo · payments list|add · webhooks add|list|test
```

## Regole di sicurezza

- Conferma con l'utente ogni mutazione non richiesta esplicitamente; i comandi
  read-only sono sempre sicuri.
- Rispetta il RBAC: un 404/403 può significare «il tuo ruolo non può» — non aggirare
  cambiando ambiente.
- MAI stampare token per intero; mai committare token o `projects.json`.
- Non creare/approvare versioni di commesse né toccare pagamenti senza istruzione
  esplicita. Protocollo completo per agenti: `<istanza>/llms.txt`.
- **Attento al livello di riservatezza quando scrivi.** Sul thread di una PROPOSTA
  (`commesse review-comment`) il default dello staff è `internal`: se vuoi che il
  partner o il cliente leggano, devi dirlo (`--audience partner|public`). Sui
  TICKET vale l'opposto: il default è pubblico, e una nota interna va chiesta
  (`--audience internal`). Se sbagli, `portal comment retract <id>` ritira il
  messaggio entro 60 secondi — senza lasciare tracce visibili alla controparte, ma
  senza garantire che nessuno l'abbia letto. `commesse share` è IRREVERSIBILE:
  chiedi conferma.
