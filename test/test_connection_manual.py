#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2018 Snowflake Computing Inc. All right reserved.
#

import pytest

import snowflake.connector
from snowflake.connector.auth import delete_temporary_credential_file

try:
    from parameters import (CONNECTION_PARAMETERS_SSO)
except:
    CONNECTION_PARAMETERS_SSO = {}


@pytest.mark.skip
def test_connect_externalbrowser():
    """
    SSO Id Token Cache tests. This is disabled by default.
    In order to run this test, remove the above pytest.mark.skip annotation
    and run it. It will popup a windows once but the rest connections
    should not create popups.
    """

    delete_temporary_credential_file()

    # change database and schema to non-default one
    print("[INFO] 1st connection gets id token and stores in the cache file. "
            "This popup a browser to SSO login")
    CONNECTION_PARAMETERS_SSO['database'] = 'testdb'
    CONNECTION_PARAMETERS_SSO['schema'] = 'testschema'
    cnx = snowflake.connector.connect(**CONNECTION_PARAMETERS_SSO)
    assert cnx.database == 'TESTDB'
    assert cnx.schema == 'TESTSCHEMA'
    assert cnx.role == 'SYSADMIN'
    assert cnx.warehouse == 'REGRESS'
    ret = cnx.cursor().execute(
        "select current_database(), current_schema(), "
        "current_role(), current_warehouse()").fetchall()
    assert ret[0][0] == 'TESTDB'
    assert ret[0][1] == 'TESTSCHEMA'
    assert ret[0][2] == 'SYSADMIN'
    assert ret[0][3] == 'REGRESS'
    cnx.close()

    print("[INFO] 2nd connection reads the cache file and uses the id token. "
            "This should not popups a browser.")
    cnx = snowflake.connector.connect(**CONNECTION_PARAMETERS_SSO)
    print("[INFO] Running a 60 seconds query. If the session expires in 10 "
          "seconds, the query should renew the token in the middle, "
          "and the current objects should be refreshed.")
    cnx.cursor().execute("select seq8() from table(generator(timelimit=>60))")
    assert cnx.database == 'TESTDB'
    assert cnx.schema == 'TESTSCHEMA'
    assert cnx.role == 'SYSADMIN'
    assert cnx.warehouse == 'REGRESS'
    ret = cnx.cursor().execute(
        "select current_database(), current_schema(), "
        "current_role(), current_warehouse()").fetchall()
    assert ret[0][0] == 'TESTDB'
    assert ret[0][1] == 'TESTSCHEMA'
    assert ret[0][2] == 'SYSADMIN'
    assert ret[0][3] == 'REGRESS'

    print("[INFO] Running a 5 seconds query. ")
    cnx.cursor().execute("select seq8() from table(generator(timelimit=>5))")
    assert cnx.database == 'TESTDB'
    assert cnx.schema == 'TESTSCHEMA'
    assert cnx.role == 'SYSADMIN'
    assert cnx.warehouse == 'REGRESS'
    ret = cnx.cursor().execute(
        "select current_database(), current_schema(), "
        "current_role(), current_warehouse()").fetchall()
    assert ret[0][0] == 'TESTDB'
    assert ret[0][1] == 'TESTSCHEMA'
    assert ret[0][2] == 'SYSADMIN'
    assert ret[0][3] == 'REGRESS'

    del CONNECTION_PARAMETERS_SSO['database']
    del CONNECTION_PARAMETERS_SSO['schema']
    # the following connection will use the session token derived from
    # the id token and the db and schemas are the default.
    for _ in range(2):
        cnx = snowflake.connector.connect(**CONNECTION_PARAMETERS_SSO)
        assert cnx.database == 'TESTDB'
        assert cnx.schema == 'PUBLIC'
        assert cnx.role == 'SYSADMIN'
        assert cnx.warehouse == 'REGRESS'
        ret = cnx.cursor().execute(
            "select current_database(), current_schema(), "
            "current_role(), current_warehouse()").fetchall()
        assert ret[0][0] == 'TESTDB'
        assert ret[0][1] == 'PUBLIC'
        assert ret[0][2] == 'SYSADMIN'
        assert ret[0][3] == 'REGRESS'
        cnx.close()

    # change database and schema again to ensure they are overridden
    CONNECTION_PARAMETERS_SSO['database'] = 'testdb'
    CONNECTION_PARAMETERS_SSO['schema'] = 'testschema'
    cnx = snowflake.connector.connect(**CONNECTION_PARAMETERS_SSO)
    assert cnx.database == 'TESTDB'
    assert cnx.schema == 'TESTSCHEMA'
    assert cnx.role == 'SYSADMIN'
    assert cnx.warehouse == 'REGRESS'
    ret = cnx.cursor().execute(
        "select current_database(), current_schema(), "
        "current_role(), current_warehouse()").fetchall()
    assert ret[0][0] == 'TESTDB'
    assert ret[0][1] == 'TESTSCHEMA'
    assert ret[0][2] == 'SYSADMIN'
    assert ret[0][3] == 'REGRESS'
    cnx.close()
