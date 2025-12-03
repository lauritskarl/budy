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
* `budgets`: Set and manage monthly targets.
* `reports`: View financial insights.

## `budy transactions`

Manage transaction history.

**Usage**:

```console
$ budy transactions [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add a new transaction to the database.
* `list`: Display transaction history in a table.
* `import`: Import transactions from a bank CSV file.

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

### `budy transactions import`

Import transactions from a bank CSV file.

**Usage**:

```console
$ budy transactions import [OPTIONS]
```

**Options**:

* `-b, --bank [lhv|seb|swedbank]`: The bank to import from.  [required]
* `-f, --file FILE`: Path to the CSV file.  [required]
* `--dry-run / --no-dry-run`: Parse the file but do not save to the database.  [default: no-dry-run]
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

* `add`: Add a new budget to the database.
* `list`: Display monthly budgets in a table.
* `generate`: Auto-generate monthly budgets based on...

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

## `budy reports`

View financial insights.

**Usage**:

```console
$ budy reports [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `month`: Show the budget status report for a...
* `year`: Show the budget status report for a...
* `weekday`: Analyze spending habits by day of the week.
* `volatility`: Analyze spending volatility and outliers.
* `search`: Search transactions by keyword.
* `payees`: Rank payees by total spending.

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

### `budy reports year`

Show the budget status report for a specific year.

**Usage**:

```console
$ budy reports year [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: The year to report on (defaults to current).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy reports weekday`

Analyze spending habits by day of the week.
Shows which days you statistically spend the most money on.

**Usage**:

```console
$ budy reports weekday [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `budy reports volatility`

Analyze spending volatility and outliers.
Shows standard deviation and the largest transactions.

**Usage**:

```console
$ budy reports volatility [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: Filter analysis by year (defaults to all time).  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy reports search`

Search transactions by keyword.
Looks inside the Receiver name and Description.

**Usage**:

```console
$ budy reports search [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: Keyword to search for (in receiver or description).  [required]

**Options**:

* `-l, --limit INTEGER RANGE`: Maximum number of results to display.  [default: 20; x&gt;=1]
* `--help`: Show this message and exit.

### `budy reports payees`

Rank payees by total spending.
Who is getting most of your money?

**Usage**:

```console
$ budy reports payees [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: Filter analysis by year (defaults to all time).  [1900&lt;=x&lt;=2100]
* `-l, --limit INTEGER`: Number of payees to show.  [default: 10]
* `--help`: Show this message and exit.
