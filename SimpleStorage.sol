// SPDX-Licensen-Identifier: MIT

pragma solidity >=0.6.0 <0.9.0;

import "./SimplestorageofSol.sol";

contract StorageFactory is SimpleStorage {
    SimpleStorage[] public simpleStorageArray;

    function createSimpleStorage() public {
        SimpleStorage simpleStorage = new SimpleStorage();
        simpleStorageArray.push(simpleStorage);
    }

    function sfStore(uint256 _simpleStorageNumber, uint256 _simpleStorageIndex)
        public
    {
        //Address
        //ABI
        SimpleStorage(address(simpleStorageArray[_simpleStorageIndex])).store(
            _simpleStorageNumber
        );
    }

    function sfRetrieve(uint256 _simpleStorageIndex)
        public
        view
        returns (uint256)
    {
        return
            SimpleStorage(address(simpleStorageArray[_simpleStorageIndex]))
                .retrieve();
    }
}
