import threading
from multiprocessing import cpu_count


class JoinWithoutClosedError(RuntimeError):
	def __init__(self):
		return RuntimeError('Pool joined without closed.')

class PoolClosedError(Exception):
	def __init__(self):
		return Exception('Pool is closed, no more task accepted.')


class ThreadPool(object):

	def __init__(self, thread_num=cpu_count()):
		self.thread_num = thread_num
		self._current_thread_num = 0
		self.cond = threading.Condition()
		self.pool_active = False
		self.closing = False
		self.joincond = threading.Condition()

	def sync(processor):
		"""
		Synchronize new process query.If pool is full, make it wait.
		If pool is close.raise PoolClosedError.
		"""
		def _sync_func(*args, **kws):
			self = args[0]
			if self.closing:
				raise PoolClosedError()
			self.cond.acquire()
			self.pool_active = True
			#Here is reason of using '>=': self.close() function in order to close 
			#the poll, put the thread_num = 0 to make sure no more request income.
			while self._current_thread_num >= self.thread_num:
				self.cond.wait()
			self._current_thread_num += 1
			self.cond.release()
			rtn = processor(*args, **kws)
			return rtn
		return _sync_func

	def pool_thread(self, func):
		"""
		Decorating func with this function to reduce _current_thread_num of pool.
		"""
		def _func(*args, **kws):
			rtn = func(*args, **kws)
			self.cond.acquire()
			self._current_thread_num -= 1
			self.cond.notify()
			if self._current_thread_num == 0:
				self.pool_active = False
			if self.thread_num == 0 and self._current_thread_num == 0 and not self.pool_active:
				self.joincond.acquire()
				self.joincond.notify()
				self.joincond.release()
			self.cond.release()
			return rtn
		return _func

	@sync
	def process(self, func, args=None):
		"""
		Use multiprocessing to execute function.
		"""
		func = self.pool_thread(func)
		t = threading.Thread(target=func, args=args)
		t.start()

	def close(self):
		"""
		Close the pool, no more task will be put in pool.
		"""
		self.closing = True
		self.cond.acquire()
		self.thread_num = 0
		self.cond.release()

	def join(self):
		"""
		Waiting all threads in pool to finish.
		Attention:MUST MAKE SURE THE POOL IS CLOSED!
		"""
		if not self.closing:
			raise JoinWithoutClosedError()
		self.joincond.acquire()
		while self.pool_active:
			self.joincond.wait()
		self.joincond.release()