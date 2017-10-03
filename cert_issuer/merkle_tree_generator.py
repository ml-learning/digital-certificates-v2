import hashlib

from chainpoint.chainpoint import MerkleTools
from pycoin.serialize import h2b

from cert_schema import Chain


def hash_byte_array(data):
    hashed = hashlib.sha256(data).hexdigest()
    return hashed


def ensure_string(value):
    if isinstance(value, str):
        return value
    return value.decode('utf-8')


class MerkleTreeGenerator(object):
    def __init__(self):
        self.tree = MerkleTools(hash_type='sha256')

    def populate(self, node_generator):
        """
        Populate Merkle Tree with data from node_generator. This requires that node_generator yield byte[] elements.
        Hashes, computes hex digest, and adds it to the Merkle Tree
        :param node_generator:
        :return:
        """
        for data in node_generator:
            hashed = hash_byte_array(data)
            self.tree.add_leaf(hashed)

    def get_blockchain_data(self):
        """
        Finalize tree and return byte array to issue on blockchain
        :return:
        """
        self.tree.make_tree()
        merkle_root = self.tree.get_merkle_root()
        return h2b(ensure_string(merkle_root))

    def get_proof_generator(self, tx_id, chain=Chain.mainnet):
        """
        Returns a generator (1-time iterator) of proofs in insertion order.

        :param tx_id: blockchain transaction id
        :return:
        """
        root = ensure_string(self.tree.get_merkle_root())
        node_count = len(self.tree.leaves)
        for index in range(0, node_count):
            proof = self.tree.get_proof(index)
            proof2 = []

            for p in proof:
                dict2 = dict()
                for key, value in p.items():
                    dict2[key] = ensure_string(value)
                proof2.append(dict2)
            target_hash = ensure_string(self.tree.get_leaf(index))
            merkle_proof = {
                "type": ['MerkleProof2017', 'Extension'],
                "merkleRoot": root,
                "targetHash": target_hash,
                "proof": proof2,
                "anchors": [{
                    "sourceId": to_source_id(tx_id, chain),
                    "type": to_anchor_type(chain)
                }]}
            yield merkle_proof


def to_source_id(txid, chain):
    if chain == Chain.mainnet or Chain.testnet or Chain.ethmain or Chain.ethrop:
        return txid
    else:
        return 'This has not been issued on a blockchain and is for testing only'


def to_anchor_type(chain):
    """
    Return the anchor type to include in the Blockcert signature. In next version of Blockcerts schema we will be able
    to write XTNOpReturn for testnet
    :param chain:
    :return:
    """
    if chain == Chain.mainnet or chain == Chain.testnet:
        return 'BTCOpReturn'
    # non-standard
    elif chain == Chain.regtest:
        return 'REGOpReturn'
    # non-standard
    elif chain == Chain.mocknet:
        return 'MockOpReturn'
    # non-standard
    elif chain == Chain.ethmain:
        return 'ETHdata'
    # non-standard
    elif chain == Chain.ethrop:
        return 'ETHdataRopsten'
