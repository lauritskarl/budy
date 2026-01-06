# budy todos

- [x] add update and delete functions
- [ ] publish to PyPI

- [ ] **Transaction Categories** (Feature)
  - [ ] Create `Category` model (`id`, `name`, `color`) in `src/budy/schemas.py`
  - [ ] Add `category_id` Foreign Key to `Transaction` model
  - [ ] Implement startup check in `src/budy/__init__.py` to safely add the column to existing DBs (SQLite `ALTER TABLE`)
  - [ ] Add service functions: `create_category`, `delete_category`, `list_categories`
  - [ ] Add CLI group `budy categories` with `list`, `add`, `delete` commands
  - [ ] Update `budy transactions add` and `update` commands to support `--category`

- [ ] **Data Export** (Feature)
  - [ ] Create `export_transactions` service using Polars
  - [ ] Add `budy transactions export` command (supports CSV and JSON)

- [ ] **Auto-Categorization** (Feature)
  - [ ] Create `CategoryRule` model (`id`, `pattern`, `category_id`)
  - [ ] Add `budy categories rules` command to manage keyword mappings
  - [ ] Update `import_transactions` logic to apply rules during bank CSV import
