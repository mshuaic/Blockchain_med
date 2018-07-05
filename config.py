NUM_NODE = 4

config = {
    "rpcuser": 'multichainrpc',
    "rpcpasswd": 'emory',
    "rpchost": '127.0.0.1',
    "rpcport": 8570,
    "chainname": 'chain1'
}

# time, node, ID, ref-ID, user, activity, resource
ATTRIBUTE = ['T', 'N', 'I', 'r', 'U', 'A', 'R']
ATTRIBUTE_NAME = ['Timestamp', 'Node', 'ID',
                  'Ref-ID', 'User', 'Activity', 'Resource']
ATTRIBUTE_TYPE = {'Timestamp': int, 'Node': int, 'ID': int,
                  'Ref-ID': int, 'User': int, 'Activity': str, 'Resource': str}

datadir = './testData/'


FILE_SIZE = 100
