# `budy`

An itsy bitsy CLI budgeting assistant.

**Usage**:

```console
$ budy [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `transactions`: Manage transaction history.
* `t`: Manage transaction history.
* `budgets`: Set and manage monthly targets.
* `b`: Set and manage monthly targets.
* `reports`: View financial insights.
* `r`: View financial insights.

## `budy transactions`

Manage transaction history.

**Usage**:

```console
$ budy transactions [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `a`: Add a new transaction to the database.
* `add`: Add a new transaction to the database.
* `ls`: Display transaction history in a table.
* `list`: Display transaction history in a table.
* `i`: Import transactions from a bank CSV file.
* `import`: Import transactions from a bank CSV file.

### `budy transactions a`

Add a new transaction to the database.

**Usage**:

```console
$ budy transactions a [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Set the transaction amount (in dollars/euros).  [0.01&lt;=x&lt;=9999999; required]
* `-d, --date [%Y-%m-%d|%Y/%m/%d]`: Set the transaction date (YYYY-MM-DD).
* `--help`: Show this message and exit.

### `budy transactions add`

Add a new transaction to the database.

**Usage**:

```console
$ budy transactions add [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Set the transaction amount (in dollars/euros).  [0.01&lt;=x&lt;=9999999; required]
* `-d, --date [%Y-%m-%d|%Y/%m/%d]`: Set the transaction date (YYYY-MM-DD).
* `--help`: Show this message and exit.

### `budy transactions ls`

Display transaction history in a table.

**Usage**:

```console
$ budy transactions ls [OPTIONS]
```

**Options**:

* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 7]
* `--help`: Show this message and exit.

### `budy transactions list`

Display transaction history in a table.

**Usage**:

```console
$ budy transactions list [OPTIONS]
```

**Options**:

* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 7]
* `--help`: Show this message and exit.

### `budy transactions i`

Import transactions from a bank CSV file.

**Usage**:

```console
$ budy transactions i [OPTIONS]
```

**Options**:

* `-b, --bank TEXT`: The bank to import from. Options: lhv, seb, swedbank  [required]
* `-f, --file FILE`: Path to the CSV file.  [required]
* `--dry-run`: Parse the file but do not save to the database.
* `--help`: Show this message and exit.

### `budy transactions import`

Import transactions from a bank CSV file.

**Usage**:

```console
$ budy transactions import [OPTIONS]
```

**Options**:

* `-b, --bank TEXT`: The bank to import from. Options: lhv, seb, swedbank  [required]
* `-f, --file FILE`: Path to the CSV file.  [required]
* `--dry-run`: Parse the file but do not save to the database.
* `--help`: Show this message and exit.

## `budy t`

Manage transaction history.

**Usage**:

```console
$ budy t [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `a`: Add a new transaction to the database.
* `add`: Add a new transaction to the database.
* `ls`: Display transaction history in a table.
* `list`: Display transaction history in a table.
* `i`: Import transactions from a bank CSV file.
* `import`: Import transactions from a bank CSV file.

### `budy t a`

Add a new transaction to the database.

**Usage**:

```console
$ budy t a [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Set the transaction amount (in dollars/euros).  [0.01&lt;=x&lt;=9999999; required]
* `-d, --date [%Y-%m-%d|%Y/%m/%d]`: Set the transaction date (YYYY-MM-DD).
* `--help`: Show this message and exit.

### `budy t add`

Add a new transaction to the database.

**Usage**:

```console
$ budy t add [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Set the transaction amount (in dollars/euros).  [0.01&lt;=x&lt;=9999999; required]
* `-d, --date [%Y-%m-%d|%Y/%m/%d]`: Set the transaction date (YYYY-MM-DD).
* `--help`: Show this message and exit.

### `budy t ls`

Display transaction history in a table.

**Usage**:

```console
$ budy t ls [OPTIONS]
```

**Options**:

* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 7]
* `--help`: Show this message and exit.

### `budy t list`

Display transaction history in a table.

**Usage**:

```console
$ budy t list [OPTIONS]
```

**Options**:

* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 7]
* `--help`: Show this message and exit.

### `budy t i`

Import transactions from a bank CSV file.

**Usage**:

```console
$ budy t i [OPTIONS]
```

**Options**:

* `-b, --bank TEXT`: The bank to import from. Options: lhv, seb, swedbank  [required]
* `-f, --file FILE`: Path to the CSV file.  [required]
* `--dry-run`: Parse the file but do not save to the database.
* `--help`: Show this message and exit.

### `budy t import`

Import transactions from a bank CSV file.

**Usage**:

```console
$ budy t import [OPTIONS]
```

**Options**:

* `-b, --bank TEXT`: The bank to import from. Options: lhv, seb, swedbank  [required]
* `-f, --file FILE`: Path to the CSV file.  [required]
* `--dry-run`: Parse the file but do not save to the database.
* `--help`: Show this message and exit.

## `budy budgets`

Set and manage monthly targets.

**Usage**:

```console
$ budy budgets [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `a`: Add a new budget to the database.
* `add`: Add a new budget to the database.
* `ls`: Display monthly budgets in a table.
* `list`: Display monthly budgets in a table.
* `gen`: Auto-generate monthly budgets based on...
* `generate`: Auto-generate monthly budgets based on...

### `budy budgets a`

Add a new budget to the database.

**Usage**:

```console
$ budy budgets a [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Set the budget target amount.  [1&lt;=x&lt;=9999999; required]
* `-m, --month INTEGER RANGE`: Set the budget target month.  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: Set the budget target year.  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy budgets add`

Add a new budget to the database.

**Usage**:

```console
$ budy budgets add [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Set the budget target amount.  [1&lt;=x&lt;=9999999; required]
* `-m, --month INTEGER RANGE`: Set the budget target month.  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: Set the budget target year.  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy budgets ls`

Display monthly budgets in a table.

**Usage**:

```console
$ budy budgets ls [OPTIONS]
```

**Options**:

* `-y, --year INTEGER`: Filter by year.  [default: 2025]
* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 12]
* `--help`: Show this message and exit.

### `budy budgets list`

Display monthly budgets in a table.

**Usage**:

```console
$ budy budgets list [OPTIONS]
```

**Options**:

* `-y, --year INTEGER`: Filter by year.  [default: 2025]
* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 12]
* `--help`: Show this message and exit.

### `budy budgets gen`

Auto-generate monthly budgets based on historical transaction data.
Calculates suggestions using recent spending trends and seasonal history.

**Usage**:

```console
$ budy budgets gen [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: The year to generate budgets for.  [1900&lt;=x&lt;=2100]
* `-f, --force`: Overwrite existing budgets without asking.
* `--yes`: Automatically confirm saving suggestions.
* `--help`: Show this message and exit.

### `budy budgets generate`

Auto-generate monthly budgets based on historical transaction data.
Calculates suggestions using recent spending trends and seasonal history.

**Usage**:

```console
$ budy budgets generate [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: The year to generate budgets for.  [1900&lt;=x&lt;=2100]
* `-f, --force`: Overwrite existing budgets without asking.
* `--yes`: Automatically confirm saving suggestions.
* `--help`: Show this message and exit.

## `budy b`

Set and manage monthly targets.

**Usage**:

```console
$ budy b [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `a`: Add a new budget to the database.
* `add`: Add a new budget to the database.
* `ls`: Display monthly budgets in a table.
* `list`: Display monthly budgets in a table.
* `gen`: Auto-generate monthly budgets based on...
* `generate`: Auto-generate monthly budgets based on...

### `budy b a`

Add a new budget to the database.

**Usage**:

```console
$ budy b a [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Set the budget target amount.  [1&lt;=x&lt;=9999999; required]
* `-m, --month INTEGER RANGE`: Set the budget target month.  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: Set the budget target year.  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy b add`

Add a new budget to the database.

**Usage**:

```console
$ budy b add [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Set the budget target amount.  [1&lt;=x&lt;=9999999; required]
* `-m, --month INTEGER RANGE`: Set the budget target month.  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: Set the budget target year.  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy b ls`

Display monthly budgets in a table.

**Usage**:

```console
$ budy b ls [OPTIONS]
```

**Options**:

* `-y, --year INTEGER`: Filter by year.  [default: 2025]
* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 12]
* `--help`: Show this message and exit.

### `budy b list`

Display monthly budgets in a table.

**Usage**:

```console
$ budy b list [OPTIONS]
```

**Options**:

* `-y, --year INTEGER`: Filter by year.  [default: 2025]
* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 12]
* `--help`: Show this message and exit.

### `budy b gen`

Auto-generate monthly budgets based on historical transaction data.
Calculates suggestions using recent spending trends and seasonal history.

**Usage**:

```console
$ budy b gen [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: The year to generate budgets for.  [1900&lt;=x&lt;=2100]
* `-f, --force`: Overwrite existing budgets without asking.
* `--yes`: Automatically confirm saving suggestions.
* `--help`: Show this message and exit.

### `budy b generate`

Auto-generate monthly budgets based on historical transaction data.
Calculates suggestions using recent spending trends and seasonal history.

**Usage**:

```console
$ budy b generate [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: The year to generate budgets for.  [1900&lt;=x&lt;=2100]
* `-f, --force`: Overwrite existing budgets without asking.
* `--yes`: Automatically confirm saving suggestions.
* `--help`: Show this message and exit.

## `budy reports`

View financial insights.

**Usage**:

```console
$ budy reports [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `m`: Show the budget status report for a...
* `month`: Show the budget status report for a...
* `y`: Show the budget status report for a...
* `year`: Show the budget status report for a...

### `budy reports m`

Show the budget status report for a specific month.

**Usage**:

```console
$ budy reports m [OPTIONS]
```

**Options**:

* `-m, --month INTEGER RANGE`: The month to report on (defaults to current).  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: The year to report on (defaults to current).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy reports month`

Show the budget status report for a specific month.

**Usage**:

```console
$ budy reports month [OPTIONS]
```

**Options**:

* `-m, --month INTEGER RANGE`: The month to report on (defaults to current).  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: The year to report on (defaults to current).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy reports y`

Show the budget status report for a specific year.

**Usage**:

```console
$ budy reports y [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: The year to report on (defaults to current).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy reports year`

Show the budget status report for a specific year.

**Usage**:

```console
$ budy reports year [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: The year to report on (defaults to current).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

## `budy r`

View financial insights.

**Usage**:

```console
$ budy r [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `m`: Show the budget status report for a...
* `month`: Show the budget status report for a...
* `y`: Show the budget status report for a...
* `year`: Show the budget status report for a...

### `budy r m`

Show the budget status report for a specific month.

**Usage**:

```console
$ budy r m [OPTIONS]
```

**Options**:

* `-m, --month INTEGER RANGE`: The month to report on (defaults to current).  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: The year to report on (defaults to current).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy r month`

Show the budget status report for a specific month.

**Usage**:

```console
$ budy r month [OPTIONS]
```

**Options**:

* `-m, --month INTEGER RANGE`: The month to report on (defaults to current).  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: The year to report on (defaults to current).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy r y`

Show the budget status report for a specific year.

**Usage**:

```console
$ budy r y [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: The year to report on (defaults to current).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy r year`

Show the budget status report for a specific year.

**Usage**:

```console
$ budy r year [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: The year to report on (defaults to current).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.
