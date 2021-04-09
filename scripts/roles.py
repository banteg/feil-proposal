from brownie import Contract
from brownie.utils.output import build_tree


def main():
    core = Contract("0x8d5ED43dCa8C2F7dFB20CF7b53CC7E593635d7b9")
    roles = {
        name: getattr(core, name)()
        for name in [x for x in core.__dict__ if x.endswith("_ROLE")]
    }
    names = {str(roles[name]): name for name in roles}
    tree = []
    for name in roles:
        role = roles[name]
        size = core.getRoleMemberCount(role)
        if size == 0:
            tree.append([name])
        else:
            tree.append(
                [
                    name,
                    ["admin", names[str(core.getRoleAdmin(role))]],
                    [
                        "members",
                        *[str(core.getRoleMember(role, i)) for i in range(size)],
                    ],
                ]
            )

    print(build_tree(tree))
