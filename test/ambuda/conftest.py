import pytest
from flask_login import FlaskLoginClient

import ambuda.database as db
from ambuda import create_app
from ambuda.consts import TEXT_CATEGORIES
from ambuda.queries import get_engine, get_session


def initialize_test_db():
    engine = get_engine()
    assert ":memory:" in engine.url

    db.Base.metadata.drop_all(engine)
    db.Base.metadata.create_all(engine)

    session = get_session()

    # Text and parse data
    text = db.Text(slug="pariksha", title="parIkSA")
    session.add(text)
    session.flush()

    # Create stubs for all texts so that texts.index doesn't break
    for category, slugs in TEXT_CATEGORIES.items():
        for slug in slugs:
            t = db.Text(slug=slug, title=slug)
            session.add(t)
            session.flush()

    section = db.TextSection(text_id=text.id, slug="1", title="adhyAyaH 1")
    session.add(section)
    section2 = db.TextSection(text_id=text.id, slug="2", title="adhyAyaH 2")
    session.add(section2)
    session.flush()

    block = db.TextBlock(
        text_id=text.id, section_id=section.id, slug="1.1", xml="<div>agniH</div>", n=1
    )
    session.add(block)
    session.flush()

    parse = db.BlockParse(
        text_id=text.id, block_id=block.id, data="agniH\tagni\tpos=n,g=m,c=1,n=s"
    )
    session.add(parse)

    # Dictionaries
    dictionary = db.Dictionary(slug="test-dict", title="Test Dictionary")
    session.add(dictionary)
    session.flush()

    dictionary_entry = db.DictionaryEntry(
        dictionary_id=dictionary.id, key="agni", value="<div>fire</div>"
    )
    session.add(dictionary_entry)

    # Auth
    rama = db.User(username="ramacandra", email="rama@ayodhya.com")
    rama.set_password("maithili")
    session.add(rama)
    session.flush()

    # Admin
    admin = db.User(username="akprasad", email="arun@ambuda.org")
    admin.set_password("secred password")
    session.add(admin)
    session.flush()

    # Roles
    proofreader_role = db.Role(name=db.SiteRole.P1.value)
    admin_role = db.Role(name=db.SiteRole.ADMIN.value)
    session.add(proofreader_role)
    session.add(admin_role)
    session.flush()

    rama_role_proofreader = db.UserRoles(user_id=rama.id, role_id=proofreader_role.id)
    akprasad_role_proofreader = db.UserRoles(
        user_id=admin.id, role_id=proofreader_role.id
    )
    session.add(rama_role_proofreader)
    session.add(akprasad_role_proofreader)

    akprasad_role_admin = db.UserRoles(user_id=admin.id, role_id=admin_role.id)
    session.add(akprasad_role_admin)

    # Proofreading
    board = db.Board(title="board")
    session.add(board)
    session.flush()

    thread = db.Thread(title="Some thread", author_id=admin.id)
    post = db.Post(content="This is my post.", author_id=admin.id)
    post.board = board
    post.thread = thread
    board.threads = [thread]

    project = db.Project(slug="test-project", title="Test Project", board_id=board.id)
    session.add(project)
    session.flush()

    page_status = db.PageStatus(name="reviewed-0")
    session.add(page_status)
    session.flush()

    page = db.Page(project_id=project.id, slug="1", order=1, status_id=page_status.id)
    session.add(page)

    session.commit()


@pytest.fixture(scope="session")
def flask_app():
    app = create_app("testing")
    app.config.update({"TESTING": True})
    app.test_client_class = FlaskLoginClient

    with app.app_context():
        initialize_test_db()

    yield app


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture()
def rama_client(flask_app):
    session = get_session()
    user = session.query(db.User).filter_by(username="ramacandra").first()
    return flask_app.test_client(user=user)


@pytest.fixture()
def admin_client(flask_app):
    session = get_session()
    user = session.query(db.User).filter_by(username="akprasad").first()
    return flask_app.test_client(user=user)
