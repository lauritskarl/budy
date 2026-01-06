from typer.testing import CliRunner
from sqlmodel import Session, SQLModel, select
from budy import app
from budy.database import engine
from budy.schemas import Category, Transaction

runner = CliRunner()


def reset_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_category_crud():
    reset_db()

    # 1. Add Category
    result = runner.invoke(app, ["categories", "add", "Groceries", "--color", "green"])
    assert result.exit_code == 0
    assert "Added category Groceries" in result.stdout

    # 2. List Categories
    result = runner.invoke(app, ["categories", "list"])
    assert result.exit_code == 0
    assert "Groceries" in result.stdout
    assert "green" in result.stdout

    # 3. Create Transaction with Category
    # Get Category ID
    with Session(engine) as session:
        cat = session.exec(select(Category).where(Category.name == "Groceries")).one()
        cat_id = cat.id

    result = runner.invoke(app, ["transactions", "add", "-a", "50", "-c", str(cat_id)])
    assert result.exit_code == 0

    # Verify Transaction has category
    with Session(engine) as session:
        txn = session.exec(select(Transaction)).one()
        assert txn.category_id == cat_id

    # 4. Update Transaction Category
    # Create another category
    runner.invoke(app, ["categories", "add", "Transport"])
    with Session(engine) as session:
        cat2 = session.exec(select(Category).where(Category.name == "Transport")).one()
        cat2_id = cat2.id

    result = runner.invoke(
        app, ["transactions", "update", str(txn.id), "-c", str(cat2_id)]
    )
    assert result.exit_code == 0

    with Session(engine) as session:
        txn = session.get(Transaction, txn.id)
        assert txn is not None
        assert txn.category_id == cat2_id

    # 5. Delete Category
    result = runner.invoke(app, ["categories", "delete", str(cat_id), "--force"])
    assert result.exit_code == 0

    with Session(engine) as session:
        cat = session.get(Category, cat_id)
        assert cat is None
