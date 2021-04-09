# Feil Proposal 🌲

## Abstract

Migrate all ETH from Fei protocol-controlled value into Yearn ETH Vault.

Allow redemptions of outstanding FEI for yvETH.

At current system state, 1 FEI would be redeemable for approximately $1.9123.

## How to propose 🚧

A detailed guide will appear here when the proposal is deemed ready.

The proposal needs the following permissions:
1. `core.grantRole(core.PCV_CONTROLLER_ROLE(), proposal)` to migrate PCV,
2. `core.grantRole(core.BURNER_ROLE(), proposal)` to burn FEI,
3. `fei.unpause()` to burn FEI, as pause prevents burning,
4. `proposal.rug_pull()` to migrate all ETH and deposit into yvETH.

## How to redeem 💰

### Redeem using allowance

1. `fei.approve(proposal, 2^256-1)`
2. `proposal.let_me_out()` or `proposal.let_me_out(amount)`

### Redeem using permit

1. Generate a Fei Permit with FeilProposal as spender and with the amount you want to redeem.
2. `proposal.let_me_out_i_have_permit(owner, spender, amount, deadline, v, r, s)`

## Tests

Run `brownie test -v` to simulate the migration and see the current outstanding debt and redemption rate.
