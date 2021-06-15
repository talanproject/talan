#!/usr/bin/env python3
# Copyright (c) 2015-2016 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *
from test_framework.script import *
from test_framework.mininode import *
from test_framework.talan import *
from test_framework.talanconfig import *
import sys


class CallContractTest(BitcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 1
        self.extra_args = [['-txindex=1']]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    # Verifies that the fallback function is correctly called
    def callcontract_fallback_function_test(self):
        connect_nodes(self.nodes[0], 1)
        self.node = self.nodes[0]
        """
        pragma solidity ^0.4.10;
        contract Temp {
            function () payable {}
        }
        """
        contract_data = self.node.createcontract("60606040523415600b57fe5b5b60398060196000396000f30060606040525b600b5b5b565b0000a165627a7a72305820ab715c5850033f4aa2f2c4b1b9e49922655f93b642c16890f84624a0af8f29020029", 1000000, TALAN_MIN_GAS_PRICE_STR)
        contract_address = contract_data['address']
        self.node.generate(1)
        ret = self.node.callcontract(contract_address, "00")
        assert(ret['address'] == contract_address)
        assert(ret['executionResult']['gasUsed'] == 21037)
        assert(ret['executionResult']['excepted'] == "None")
        assert(ret['executionResult']['newAddress'] == contract_address)
        assert(ret['executionResult']['output'] == "")
        assert(ret['executionResult']['codeDeposit'] == 0)
        assert(ret['executionResult']['gasRefunded'] == 0)
        assert(ret['executionResult']['depositSize'] == 0)
        assert(ret['executionResult']['gasForDeposit'] == 0)
        assert(ret['transactionReceipt']['gasUsed'] == 21037)
        assert(ret['transactionReceipt']['bloom'] == "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
        assert(ret['transactionReceipt']['log'] == [])

    # Verifies that the function in the abi is correctly called function is correctly called
    def callcontract_abi_function_signature_test(self):
        """
        contract test {
            
            uint a;
            
            function test() payable {
                a = 13;
            }
            
            function add() payable returns (uint){
                a += 13;
                return a;
            }
            
            function () payable {}
        }
        """
        contract_data = self.node.createcontract("60606040525b600d6000819055505b5b60a98061001d6000396000f30060606040523615603d576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680634f2be91f146045575b60435b5b565b005b604b6061565b6040518082815260200191505060405180910390f35b6000600d60006000828254019250508190555060005490505b905600a165627a7a72305820fd0deb11ff6c6a06f612b5fb04e7312f22eacec75d677c0fbc0194d86772d2d70029", 1000000, TALAN_MIN_GAS_PRICE_STR)
        contract_address = contract_data['address']
        self.node.generate(1)
        # call add()
        ret = self.node.callcontract(contract_address, "4f2be91f")
        assert(ret['address'] == contract_address)
        assert(ret['executionResult']['gasUsed'] == 26878)
        assert(ret['executionResult']['excepted'] == "None")
        assert(ret['executionResult']['newAddress'] == contract_address)
        assert(ret['executionResult']['output'] == "000000000000000000000000000000000000000000000000000000000000001a")
        assert(ret['executionResult']['codeDeposit'] == 0)
        assert(ret['executionResult']['gasRefunded'] == 0)
        assert(ret['executionResult']['depositSize'] == 0)
        assert(ret['executionResult']['gasForDeposit'] == 0)
        assert(ret['transactionReceipt']['gasUsed'] == 26878)
        assert(ret['transactionReceipt']['bloom'] == "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
        assert(ret['transactionReceipt']['log'] == [])


    # Verifies that the function in the abi is correctly called function is correctly called
    def callcontract_verify_subcall_and_logs_test(self):
        """
        contract LogTest {
           uint num;
           /// Create a new ballot with $(_numProposals) different proposals.
           function LogTest() {
               CallTest();
           }
           function CallTest() public{
               num++; //not a constant function.. 
               MakeLogs();
           }
           function MakeLogs() constant public{
               //0x72ba7d8e73fe8eb666ea66babc8116a41bfb10e2
               //0x0000000000000000000000000000000000000000
                log1("0", 0x0000000000000000000000000000000000000000000000000000000000000000);
                log1("1", 0x50cb9fe53daa9737b786ab3646f04d0150dc50ef4e75f59509d83667ad5adb20);
                log1("2", 0x0000000000000000000000000000000000000000000000000000000000004021);
                log1("3", "string test");
                log1("4", "123456");
                log4("5", "topic 1", "topic 2", "topic 3", "topic 4");
                log1("6", 0x4142430000000000000000000000000000000000000000000000000000004021);
                log1("7", 0x4142050000000000000000000000000000000000000000000000000000004021);
                log1(0x41424300, "test");
                log1(0x41420500, "test");
           }
           
           function uintToBytes(uint v) constant returns (bytes32 ret) {
               if (v == 0) {
                   ret = '0';
               }
               else {
                   while (v > 0) {
                       ret = bytes32(uint(ret) / (2 ** 8));
                       ret |= bytes32(((v % 10) + 48) * 2 ** (8 * 31));
                       v /= 10;
                   }
               }
               return ret;
           }
        }
        """
        contract_data = self.node.createcontract("6060604052341561000c57fe5b5b61002861002e6401000000000261015c176401000000009004565b5b6103d2565b60006000815480929190600101919050555061005b61005e64010000000002610179176401000000009004565b5b565b600060010260405180807f3000000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f50cb9fe53daa9737b786ab3646f04d0150dc50ef4e75f59509d83667ad5adb2060010260405180807f3100000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a161402160010260405180807f3200000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f737472696e67207465737400000000000000000000000000000000000000000060405180807f3300000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f313233343536000000000000000000000000000000000000000000000000000060405180807f3400000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f746f7069632034000000000000000000000000000000000000000000000000007f746f7069632033000000000000000000000000000000000000000000000000007f746f7069632032000000000000000000000000000000000000000000000000007f746f70696320310000000000000000000000000000000000000000000000000060405180807f3500000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a47f414243000000000000000000000000000000000000000000000000000000402160010260405180807f3600000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f414205000000000000000000000000000000000000000000000000000000402160010260405180807f3700000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f74657374000000000000000000000000000000000000000000000000000000006341424300604051808260010260001916815260200191505060405180910390a17f74657374000000000000000000000000000000000000000000000000000000006341420500604051808260010260001916815260200191505060405180910390a15b565b610519806103e16000396000f30060606040526000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806394e8767d14610051578063b717cfe61461008d578063f7e52d581461009f575bfe5b341561005957fe5b61006f60048080359060200190919050506100b1565b60405180826000191660001916815260200191505060405180910390f35b341561009557fe5b61009d61015c565b005b34156100a757fe5b6100af610179565b005b600060008214156100e4577f30000000000000000000000000000000000000000000000000000000000000009050610153565b5b60008211156101525761010081600190048115156100ff57fe5b0460010290507f01000000000000000000000000000000000000000000000000000000000000006030600a8481151561013457fe5b06010260010281179050600a8281151561014a57fe5b0491506100e5565b5b8090505b919050565b600060008154809291906001019190505550610176610179565b5b565b600060010260405180807f3000000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f50cb9fe53daa9737b786ab3646f04d0150dc50ef4e75f59509d83667ad5adb2060010260405180807f3100000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a161402160010260405180807f3200000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f737472696e67207465737400000000000000000000000000000000000000000060405180807f3300000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f313233343536000000000000000000000000000000000000000000000000000060405180807f3400000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f746f7069632034000000000000000000000000000000000000000000000000007f746f7069632033000000000000000000000000000000000000000000000000007f746f7069632032000000000000000000000000000000000000000000000000007f746f70696320310000000000000000000000000000000000000000000000000060405180807f3500000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a47f414243000000000000000000000000000000000000000000000000000000402160010260405180807f3600000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f414205000000000000000000000000000000000000000000000000000000402160010260405180807f3700000000000000000000000000000000000000000000000000000000000000815250600101905060405180910390a17f74657374000000000000000000000000000000000000000000000000000000006341424300604051808260010260001916815260200191505060405180910390a17f74657374000000000000000000000000000000000000000000000000000000006341420500604051808260010260001916815260200191505060405180910390a15b5600a165627a7a7230582017fdc5538aa6e8bee9c493bc151eddd0d68855da214d76a4e58025020c4b312c0029", 1000000, TALAN_MIN_GAS_PRICE_STR)
        contract_address = contract_data['address']
        self.node.generate(1)
        # call CallTest()
        ret = self.node.callcontract(contract_address, "b717cfe6")
        expected_log = [
            {
            "address": contract_address,
            "topics": [
              "0000000000000000000000000000000000000000000000000000000000000000"
            ],
            "data": "30"
          }, 
          {
            "address": contract_address,
            "topics": [
              "50cb9fe53daa9737b786ab3646f04d0150dc50ef4e75f59509d83667ad5adb20"
            ],
            "data": "31"
          }, 
          {
            "address": contract_address,
            "topics": [
              "0000000000000000000000000000000000000000000000000000000000004021"
            ],
            "data": "32"
          }, 
          {
            "address": contract_address,
            "topics": [
              "737472696e672074657374000000000000000000000000000000000000000000"
            ],
            "data": "33"
          }, 
          {
            "address": contract_address,
            "topics": [
              "3132333435360000000000000000000000000000000000000000000000000000"
            ],
            "data": "34"
          }, 
          {
            "address": contract_address,
            "topics": [
              "746f706963203100000000000000000000000000000000000000000000000000", 
              "746f706963203200000000000000000000000000000000000000000000000000", 
              "746f706963203300000000000000000000000000000000000000000000000000", 
              "746f706963203400000000000000000000000000000000000000000000000000"
            ],
            "data": "35"
          }, 
          {
            "address": contract_address,
            "topics": [
              "4142430000000000000000000000000000000000000000000000000000004021"
            ],
            "data": "36"
          }, 
          {
            "address": contract_address,
            "topics": [
              "4142050000000000000000000000000000000000000000000000000000004021"
            ],
            "data": "37"
          }, 
          {
            "address": contract_address,
            "topics": [
              "7465737400000000000000000000000000000000000000000000000000000000"
            ],
            "data": "0000000000000000000000000000000000000000000000000000000041424300"
          }, 
          {
            "address": contract_address,
            "topics": [
              "7465737400000000000000000000000000000000000000000000000000000000"
            ],
            "data": "0000000000000000000000000000000000000000000000000000000041420500"
          }
        ]

        assert(ret['address'] == contract_address)
        assert(ret['executionResult']['gasUsed'] == 36501)
        assert(ret['executionResult']['excepted'] == "None")
        assert(ret['executionResult']['newAddress'] == contract_address)
        assert(ret['executionResult']['output'] == "")
        assert(ret['executionResult']['codeDeposit'] == 0)
        assert(ret['executionResult']['gasRefunded'] == 0)
        assert(ret['executionResult']['depositSize'] == 0)
        assert(ret['executionResult']['gasForDeposit'] == 0)
        assert(ret['transactionReceipt']['gasUsed'] == 36501)
        assert(ret['transactionReceipt']['bloom'] != "")
        assert(ret['transactionReceipt']['log'] == expected_log)


    def run_test(self):
        self.nodes[0].generate(COINBASE_MATURITY+100)
        self.callcontract_fallback_function_test()
        self.callcontract_abi_function_signature_test()
        self.callcontract_verify_subcall_and_logs_test()

if __name__ == '__main__':
    CallContractTest().main()
