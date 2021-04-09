import brownie
import pytest
from scripts.roles import main as show_roles

REVOKE_ROLES = {
    "MINTER_ROLE": {
        "0xe1578B4a32Eaefcd563a9E6d0dc02a4213f673B7": "EthBondingCurve",
        "0xEf1a94AF192A88859EAF3F3D8C1B9705542174C5": "FeiRewardsDistributor",
        "0x7a165F8518A9Ec7d5DA15f4B77B1d7128B5D9188": "EthUniswapPCVController",
        "0x7D809969f6A04777F0A87FF94B57E56078E5fE0F": "IDO",
        "0x9b0C6299D08fe823f2C0598d97A1141507e4ad86": "EthUniswapPCVDeposit",
    },
    "BURNER_ROLE": {
        "0x7D809969f6A04777F0A87FF94B57E56078E5fE0F": "IDO",
    },
    "GUARDIAN_ROLE": {
        "0xB8f482539F2d3Ae2C9ea6076894df36D1f632775": "2/3 multisig",
    },
    "PCV_CONTROLLER_ROLE": {
        "0x7a165F8518A9Ec7d5DA15f4B77B1d7128B5D9188": "EthUniswapPCVController",
    },
    "GOVERN_ROLE": {
        "0x80f17b512780F313F265dC4CeEDb89D1079D67F4": "init contract",
    },
}


def migrate(core, fei, timelock, feil_proposal):
    # show_roles()
    # revoke roles
    for name in REVOKE_ROLES:
        role = getattr(core, name)()
        for addr in REVOKE_ROLES[name]:
            core.revokeRole(role, addr)
    # grant the needed roles to proposal
    core.grantRole(core.PCV_CONTROLLER_ROLE(), feil_proposal)
    core.grantRole(core.BURNER_ROLE(), feil_proposal)
    fei.unpause({"from": timelock})
    feil_proposal.rug_pull()
    # show_roles()


def test_migrate(core, fei, vault, timelock, feil_proposal, Contract):
    supply_before = fei.totalSupply()
    migrate(core, fei, timelock, feil_proposal)
    supply_after = fei.totalSupply()
    vault_balance = vault.balanceOf(feil_proposal)
    print(f"fei supply: {supply_before / 1e18} -> {supply_after / 1e18}")
    print(f"vault balance: {vault_balance / 1e18}")
    eth_usd = Contract("eth-usd.data.eth").latestAnswer() / 1e8
    print(f"eth/fei: {feil_proposal.eth_per_fei() / 1e18}")
    print(f"usd/fei: {feil_proposal.eth_per_fei() / 1e18 * eth_usd}")
    print(f"remaining fei: {feil_proposal.remaining_fei() / 1e18}")
    print(f"remaining eth: {feil_proposal.remaining_eth() / 1e18}")

    assert vault_balance > "100_000 ether"
    assert supply_after < supply_before / 2


@pytest.mark.parametrize("full", [True, False])
def test_redeem(core, fei, timelock, vault, feil_proposal, whale, full):
    migrate(core, fei, timelock, feil_proposal)

    supply_before = fei.totalSupply()
    fei_before = fei.balanceOf(whale)
    vault_before = vault.balanceOf(whale)
    rate_before = feil_proposal.eth_per_fei()

    fei.approve(feil_proposal, 2 ** 256 - 1)
    if full:
        feil_proposal.let_me_out({"from": whale})
    else:
        feil_proposal.let_me_out(fei.balanceOf(whale) / 10, {"from": whale})

    supply_after = fei.totalSupply()
    fei_after = fei.balanceOf(whale)
    vault_after = vault.balanceOf(whale)
    rate_after = feil_proposal.eth_per_fei()

    print(f"fei supply: {supply_before / 1e18} -> {supply_after / 1e18}")
    print(f"whale fei: {fei_before / 1e18} -> {fei_after / 1e18}")
    print(f"whale yveth: {vault_before / 1e18} -> {vault_after / 1e18}")
    print(f"eth/fei: {rate_before / 1e18} -> {rate_after / 1e18}")

    assert supply_after < supply_before
    assert fei_after < fei_before
    assert vault_after > vault_before


def test_no_curve_minting(core, fei, timelock, feil_proposal, Contract, accounts):
    user = accounts[0]
    migrate(core, fei, timelock, feil_proposal)
    curve = Contract("0xe1578B4a32Eaefcd563a9E6d0dc02a4213f673B7")
    with brownie.reverts("CoreRef: Caller is not a minter"):
        curve.purchase(user, "100 ether", {"amount": "100 ether", "from": user})
