from web.core.migration import is_latest, migration


def test_is_latest_empty_database_and_metadata(dbsession, empty_metadata):
    result = is_latest(dbsession.connection(), empty_metadata)

    assert result is True


def test_is_latest_after_migration(dbsession, metadata):
    migration(dbsession.connection(), metadata)

    result = is_latest(dbsession.connection(), metadata)

    assert result is True
