# @version 0.2.11
# @author banteg
# @notice Withdraw PCV from Fei, deposit into WETH yVault and allow redeeming Fei for yvWETH.
from vyper.interfaces import ERC20

interface PCV:
    def totalValue() -> uint256: view
    def withdraw(to: address, amount: uint256): nonpayable

interface WETH:
    def deposit(): payable

interface Vault:
    def deposit(): nonpayable
    def withdraw(): nonpayable
    def pricePerShare() -> uint256: view

interface Fei:
    def burnFrom(account: address, amount: uint256): nonpayable

event Deposit:
    sender: indexed(address)
    amount: uint256

core: constant(address) = 0x8d5ED43dCa8C2F7dFB20CF7b53CC7E593635d7b9
pcv_deposit: constant(address) = 0x9b0C6299D08fe823f2C0598d97A1141507e4ad86
fei: constant(address) = 0x956F47F50A910163D8BF957Cf5846D573E7f87CA
fei_tribe: constant(address) = 0x9928e4046d7c6513326cCeA028cD3e7a91c7590A
weth: constant(address) = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
vault: constant(address) = 0xa9fE4601811213c340e850ea305481afF02f5b28
rugged: public(bool)


@payable
@external
def __default__():
    log Deposit(msg.sender, msg.value)


@external
def rug_pull():
    # assert core.isPCVController(self)
    PCV(pcv_deposit).withdraw(self, PCV(pcv_deposit).totalValue())
    WETH(weth).deposit(value=self.balance)
    ERC20(weth).approve(vault, MAX_UINT256)
    Vault(vault).deposit()
    self.rugged = True

@view
@internal
def _remaining_fei() -> uint256:
    return ERC20(fei).totalSupply() - ERC20(fei).balanceOf(fei_tribe)

@view
@internal
def _remaining_eth() -> uint256:
    return ERC20(vault).balanceOf(self)


@view
@external
def remaining_fei() -> uint256:
    return self._remaining_fei()


@view
@external
def remaining_eth() -> uint256:
    return ERC20(vault).balanceOf(self) * Vault(vault).pricePerShare() / 10 ** 18


@view
@external
def eth_per_fei() -> uint256:
    return ERC20(vault).balanceOf(self) * Vault(vault).pricePerShare() / self._remaining_fei()


@internal
def _redeem(owner: address, amount: uint256):
    assert self.rugged, "not rugged yet"
    assets: uint256 = ERC20(vault).balanceOf(self)
    debt: uint256 = self._remaining_fei()
    burn: uint256 = min(amount, ERC20(fei).balanceOf(owner))
    refund: uint256 = assets * burn / debt
    assert ERC20(fei).allowance(owner, self) >= burn  # otherwise the burner role could burn anyone
    Fei(fei).burnFrom(owner, burn)
    assert ERC20(vault).transfer(owner, refund)


@external
def let_me_out(amount: uint256 = MAX_UINT256):
    self._redeem(msg.sender, min(amount, ERC20(fei).balanceOf(msg.sender)))


@external
def let_me_out_i_have_permit(
    owner: address, spender: address, amount: uint256, deadline: uint256, v: uint256, r: bytes32, s: bytes32
):
    # NOTE: Vyper doesn't support uint8 type, so we encode by hand
    raw_call(fei, concat(
        method_id("permit(address,address,uint256,uint256,uint8,bytes32,bytes32)"),
        convert(owner, bytes32),
        convert(spender, bytes32),
        convert(amount, bytes32),
        convert(v, bytes32),
        r,
        s
    ))
    self._redeem(owner, amount)
