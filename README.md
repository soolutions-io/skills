# Soolutions — skill per Claude Code

Le skill ufficiali per usare i prodotti Soolutions con
[Claude Code](https://claude.com/claude-code). Oggi c'è il plugin **`portal`**: il
gestionale commesse e supporto di [customers.soolutions.io](https://customers.soolutions.io)
dal terminale, con Claude che lo usa per te.

## Installazione (2 minuti)

Nel terminale, con Claude Code già installato:

```bash
claude plugin marketplace add soolutions-io/skills
claude plugin install portal@soolutions
```

Poi apri Claude Code e scrivi **«configura il portale Soolutions»**: la skill
`portal-setup` installa la CLI, ti fa collegare il tuo token personale e riconosce
il tuo ruolo. Ti serve solo l'accesso al portale (l'invito arriva per email).

Dentro Claude Code puoi fare lo stesso con `/plugin marketplace add soolutions-io/skills`
e `/plugin install portal@soolutions`.

## Cosa contiene

| Skill | Per chi | Cosa fa |
|---|---|---|
| `portal-setup` | tutti | Installa la CLI `portal`, collega il token, riconosce il ruolo |
| `portal-partner` | partner | Ticket dei clienti finali e SLA, proposte di commessa, prezzo di vendita |
| `portal-cli` | clienti e staff | Commesse, requisiti, task, chat di progetto, turni degli agenti |

## Aggiornamenti

```bash
claude plugin marketplace update soolutions   # skill
portal update                                 # CLI
```

La versione del plugin segue quella della CLI: le skill descrivono sempre i
comandi della CLI in produzione.

## Sicurezza

- Qui non ci sono credenziali, e non ce ne saranno: il token è personale, si crea
  dal portale e resta sul tuo computer (`portal configure`). Ogni pull request passa
  una scansione automatica dei segreti.
- Cosa puoi vedere e fare lo decidono il tuo account e i suoi permessi sul portale,
  non le skill: una skill spiega a Claude come usare la CLI, non apre accessi.
- Una vulnerabilità? Scrivici, non aprire una issue pubblica: vedi [SECURITY.md](SECURITY.md).

## Per chi mantiene questo repository

Le skill `portal-cli` e `portal-partner` **non si modificano qui**: la fonte è il
repository del gestionale, che le pubblica su `customers.soolutions.io/downloads`
insieme a un manifest con la versione e lo sha256 di ogni file. Per allinearle:

```bash
python3 scripts/sync_from_portal.py          # scarica, verifica gli sha256, aggiorna la versione
python3 scripts/lint.py                      # struttura, frontmatter, niente segreti né path assoluti
```

La CI (`validate`) ripete il lint, cerca segreti con gitleaks e segnala se il
repository è rimasto indietro rispetto al portale. `portal-setup` invece vive qui.
