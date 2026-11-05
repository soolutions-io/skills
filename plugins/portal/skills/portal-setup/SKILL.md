---
name: portal-setup
description: >
  Setup guidato del gestionale Soolutions su questo computer: installa la CLI
  `portal`, collega il token personale, riconosce il ruolo (partner, cliente,
  staff) e prepara le skill giuste. Usala quando l'utente chiede di installare,
  configurare o collegare il portale/gestionale Soolutions, quando `portal` non
  è installato o risponde «token mancante/non valido», o al primo uso del plugin.
  Trigger: "configura il portale", "installa portal", "collega il gestionale",
  "setup Soolutions", "onboarding", "primo accesso", "token CLI",
  "customers.soolutions.io".
---

# Setup del gestionale Soolutions

Obiettivo: in pochi minuti l'utente ha la CLI `portal` funzionante, collegata al
suo account, e sa cosa chiederti. Procedi un passo alla volta, verifica ogni passo
prima del successivo, e spiega in una riga cosa stai facendo.

Istanza di produzione: `https://customers.soolutions.io` (salvo indicazione diversa
dell'utente).

## 1 · La CLI c'è?

```
portal --version
```

- Risponde con una versione → vai al passo 2 (se è vecchia: `portal update`).
- Comando non trovato → serve installarla. **Chiedi conferma** prima di eseguire,
  e dì cosa farai: scaricare la CLI dal portale Soolutions in `~/.local/bin`.
  - macOS / Linux: `curl -fsSL https://customers.soolutions.io/install.sh | sh`
  - Windows (PowerShell): `irm https://customers.soolutions.io/install.ps1 | iex`

  Richiede Node.js ≥ 20: se manca, l'installer lo dice; guida l'utente a
  installarlo (macOS: `brew install node`, altrimenti https://nodejs.org) e riprova.
  Se l'installer avvisa che `~/.local/bin` non è nel PATH, aggiungilo al profilo
  della shell come indicato e usa il percorso completo finché non riapre il terminale.

## 2 · Il token personale

Il token si crea dal sito, e lo deve fare l'utente: è una credenziale sua.

1. Chiedigli di aprire https://customers.soolutions.io → **Account** → **Token CLI**
   → «Crea token» (un nome qualunque, es. il computer che sta usando).
   Se non riesce ad entrare: il primo accesso arriva per email («Imposta la
   password»); se il link è scaduto c'è «Password dimenticata?» sulla pagina di
   accesso, oppure lo rimanda chi lo ha invitato.
2. Fagli eseguire **nel suo terminale** (non qui in chat):
   ```
   portal configure
   ```
   e incollare il token lì. Così il token non passa da questa conversazione.
   Se l'utente te lo incolla comunque in chat, non ripeterlo nelle risposte e
   suggerisci di revocarlo e crearne uno nuovo a setup finito.
3. Verifica:
   ```
   portal me --json
   ```

Errori comuni:
- `ENROLLMENT_REQUIRED` → l'account deve prima completare la verifica in due
  passaggi dal sito (app di autenticazione). È obbligatoria: fallo accedere al sito,
  seguire la procedura, poi riprova `portal me`.
- `401` / token non valido → token copiato male o revocato: rifare il punto 2.

## 3 · Chi è l'utente (campo `role` di `portal me`)

| Ruolo | Cosa fa col portale | Skill da usare |
|---|---|---|
| `partner` | Ticket dei suoi clienti finali, SLA, proposte di commessa, prezzo di vendita | `portal-partner` |
| `customer` | Avanzamento delle sue commesse, ticket di supporto | `portal-cli` |
| `admin` · `manager` · `developer` | Staff Soolutions: commesse, task, agenti | `portal-cli` (+ strumenti interni, sotto) |

Le skill sono già in questo plugin: non serve installare altro. Riassumi
all'utente in 2-3 righe cosa può chiederti, con esempi concreti per il suo ruolo
(partner: «quali ticket stanno per scadere?», «rispondi al ticket T-… di Rossi»;
cliente: «a che punto è la mia commessa?»; staff: «qual è la prossima task?»).

## 4 · Un progetto in questa cartella? (solo staff, facoltativo)

Se la cartella corrente è il repository di un progetto e l'utente è staff:
`portal context --json`. Se `bound: false`, proponi di collegarlo a una commessa
seguendo la sezione «Onboarding di un progetto» della skill `portal-cli`
(chiedi SEMPRE quale commessa e quale modalità: non sceglierle da solo).

Partner e clienti non ne hanno bisogno: lavorano su tutte le loro commesse da
qualunque cartella.

## 5 · Solo per lo staff Soolutions: gli strumenti interni

Chi scrive il software ha anche un marketplace privato (deploy, DNS, convenzioni).
Serve l'accesso al repository GitHub, che concede Simone. Con l'accesso:

```
claude plugin marketplace add montaofficial/claude-skills
claude plugin install soolutions-dev@soolutions-skills
```

Poi la skill `soolutions-dev` completa il setup della macchina di sviluppo.
Non proporlo a partner e clienti: non ne hanno l'accesso e non serve loro.

## Fine

Chiudi con: ruolo riconosciuto, versione della CLI, cosa può chiederti adesso.
Aggiornamenti futuri: `portal update` per la CLI,
`claude plugin marketplace update soolutions` per le skill.
