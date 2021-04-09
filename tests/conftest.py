import pytest


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture()
def timelock(accounts):
    return accounts.at("0x639572471f2f318464dc01066a56867130e45E25", force=True)


@pytest.fixture()
def core(Contract, timelock):
    return Contract("0x8d5ED43dCa8C2F7dFB20CF7b53CC7E593635d7b9", owner=timelock)


@pytest.fixture()
def feil_proposal(FeilProposal, accounts):
    return accounts[0].deploy(FeilProposal)


@pytest.fixture()
def whale(accounts):
    return accounts.at("0xaeD7384F03844Af886b830862FF0a7AFce0a632C", force=True)


@pytest.fixture()
def fei(Contract, whale):
    return Contract("0x956F47F50A910163D8BF957Cf5846D573E7f87CA", owner=whale)


@pytest.fixture()
def vault(Contract):
    return Contract("0xa9fE4601811213c340e850ea305481afF02f5b28")
