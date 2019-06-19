import threading
import time
import inspect
import ctypes


class ThreadPool:
    def __init__(self, size: int, timeout: int):
        self._size = size
        self._timeout = timeout

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid,
                                                         ctypes.py_object(
                                                             exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def _stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

    def start(self, func, task: list):
        record = dict()
        while len(task) or len(record) > 0:
            while len(record) < self._size and len(task) > 0:
                item = task.pop()
                t = threading.Thread(target=func, args=(item,))
                t.start()
                record[t.getName()] = {'thread': t, 'time': time.time()}
            dellist = []
            for k, v in record.items():
                print('检测：' + k)
                if v['thread'].isAlive():
                    if time.time() - v['time'] > self._timeout:
                        self._stop_thread(v['thread'])
                        dellist.append(k)
                else:
                    dellist.append(k)
            for dl in dellist:
                del (record[dl])


if __name__ == '__main__':
    def task(name):
        print("输出name", name)
        time.sleep(name)


    t1 = time.time()
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    pool = ThreadPool(4, 3)
    pool.start(task, items)
    t2 = time.time()
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    for i in items:
        task(i)
    t3 = time.time()
    print('多线程统计用时：{} 非多线程统计：{}'.format(t2 - t1, t3 - t2))
