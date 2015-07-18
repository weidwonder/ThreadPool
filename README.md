# Introduction
This is a full-block-thread pool.

# API

### class

`thread_pool.ThreadPool(thread_num=cpu_count)`

> Create thread pool by this. `thread_num` represent the max thread number this pool can process at same time, it equals your pc cpu count default.

### functions

Very easy.Only three function.

`process(func, args=None)`

> Put tasks into pool by using this function. The `args` will be passed to func.

> If the pool has been closed, this function will raise `PoolClosedError`

`close()`

> Close poll, no more task can be put into pool.

`join()`

> Make the thread which handle `join()` wait till pool finish all tasks.

> Attition! The pool must be closed before `join()`, otherwise `JoinWithoutClosedError` will be raised.