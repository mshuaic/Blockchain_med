#### 07/09/2018
- Scalability test  
Use 100, 500, 2500 records to test the scalability. _Maybe should use equal scale
instead??_
![scalability test](benchmark_img/scales.png)  

- Reimplement baseline3 using Unique-ID approach. See [06/28/2018](#06-28-2018)
development log (baseline2 chart interpretation).   
When the querying result is large (number of record is large), the Unique-ID approach
needs additional N times query (N = number of record). The Unique-ID saves about
20% space, but the average querying time increases 10 times.
![baseline3uid](benchmark_img/benchmark3UID.png)

- (Doing) Use database normalization techniques to reduce blockchain size

#### 07/05/2018
- (Done) Baseline3  
  - Using multiple streams to insert data to Blockchain:  
one line in log data -> one transaction, and the transaction will add data to
multiple streams(tables) atomically. It reduces the number of transactions to 1/7
(7 is the number of attributes). As a result, the insertion time and storage are
both decreased dramatically. See figure blow.
  - Build an indexing solution for timestamp:  
    - Retrieve all timestamps from Blockchain
    - Build a sorted list for the timestamps  

    Now, we are able to do fast range query, however, **this solution builds an index
  table in memory which is prohibited by the competition**. We just use it as
  an experiment for now.
- (Done) Sorting function  
We are able to sort the result of querying. The test only use **400** records, so
it does not show any significant difference in time. We will increase the number
of records later.

- (Doing) Learning indexing techniques
  - [x] B tree
  - [x] K-d tree
  - [ ] R tree
  - [ ] Hierarchy indexing
- (To-do) Build a solution using modern indexing techniques
![benchmark_img](benchmark_img/benchmark3.png)  

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
