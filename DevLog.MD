#### 06/28/2018
* (Done) Baseline2 and Baseline2.1
  * Baseline2:
    * First, we store the record as key = SHA1 hash of record, value = plaintext of record.
    * Then, we store its k attributes info as key = hash of i-th attributes, value = SHA1 hash of the record; hence, the hash of this record (instead of the plaintext) is duplicated k times.
  * Baseline2.1:
    * Using (Node# + ID) as key. Pro: eliminate the risk of hashing collision
* (Done) Benchmark Plotting tool.
* (Doing) Learning indexing techniques
  - [x] B tree
  - [ ] K-d tree
  - [ ] R tree
  - [ ] Cutting tree
* (TO-DO) Build a solution using modern indexing techniques

![benchmark_img](benchmark_img/benchmark2.png)

Chart interpretation:  
* Point Query: (using Node attribute as an example)
  * Baseline1: query once, and returns all record
  * Baseline2: the first query gets all pointers, and the second N times query( N =  number of pointers from the first query) get the actual record.  
  Since Node attribute returns the largest number of record, it takes the longest time.
* Range Query: The most query results are _None_, so two baselines have approximately same Performance  
* And Query: Baseline2: The intersection of **2** _And_ is large(number of query is large), so
the second query(pointer-> actual value) takes very long time.
* Insertion time: reason explained above.
* Storage: total size = sum(transactions), transaction size = some constant content( sender address, receiver address, script,...) + actual data. The constant part size is way larger than the actual data size, so it mitigates the effort of hashing(saving storage).



#### 06/20/2018
- (Done) Shell script for automatically creating nodes and blockchain
- (Done) Performance evaluation program Single field query
  - Multiple field query and AND operation
  - Range query
- (Done) Baseline implementation version 0.1
  - Insertion: insert n (n = number of attribute) times copy to blockchain, using attribute
  as key and entire line as value
  - Range query: query from start time, and increase timestamp by 1 every time till end time. The total number of query needed is (start - end)
  - And operation: query using single attribute and do AND operation locally
