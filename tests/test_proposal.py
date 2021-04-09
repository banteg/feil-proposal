import pytest


def test_migrate(core, fei, vault, feil_proposal, Contract):
    core.grantRole(core.PCV_CONTROLLER_ROLE(), feil_proposal)
    core.grantRole(core.BURNER_ROLE(), feil_proposal)
    supply_before = fei.totalSupply()
    feil_proposal.rug_pull()
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
    core.grantRole(core.PCV_CONTROLLER_ROLE(), feil_proposal)
    core.grantRole(core.BURNER_ROLE(), feil_proposal)
    fei.unpause({"from": timelock})
    feil_proposal.rug_pull()

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
