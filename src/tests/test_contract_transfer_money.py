from blockchain_db import FIRST_BLOCK
from core.data_structures.blockchain import Block

example_block = Block.from_dict(FIRST_BLOCK)
contract_to_test = "transfer_money"
contract = example_block.data.contracts[contract_to_test]


class TestContractTransferMoney:

    def test_basic(self):
        executor = "98f595b5044a260e3576278bc632af9656130b79016013265aee0e982390b282effc2e9d9e224241ae25fe4b3e1ccbab"
        destination = "7839727a8ad525465398057f3be1c2999e28522da658c759b5626bd26e11a9f0e9799fb377cacac22c57e170b2820f13"
        amount = 10
        contract(example_block.data, executor, destination,amount )
        print(example_block.data.accounts[destination])
