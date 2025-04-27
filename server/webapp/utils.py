try:
    TimeoutError
except NameError:
    class TimeoutError(Exception):
        """Custom TimeoutError for older compatibility."""
        pass

# Force binding to make sure TimeoutError is globally available
TimeoutError = TimeoutError

__all__ = ["TimeoutError"]

import types
import copy
import re
import threading

# (Other imports and code follow...)

def re_compile(pattern, flags=0):
    """Safe wrapper around re.compile."""
    return re.compile(pattern, flags)

# --- rest of your utils.py code follows ---

try:
    import subprocess
except ImportError:
    subprocess = None

try:
    import datetime
except ImportError:
    pass

try:
    set
except NameError:
    from sets import Set as set

try:
    from threading import local as threadlocal
except ImportError:
    from .python23 import threadlocal

import builtins

class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.
    
        >>> o = storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'
    
    """
    def __getattr__(self, key): 
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value): 
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):     
        return '<Storage ' + dict.__repr__(self) + '>'

storage = Storage
# 2
def storify(mapping, *requireds, **defaults):
    from . import webapi as web
    """
    Creates a storage object from a mapping object with required and default keys.
    
        >>> storify({'foo': 'bar'}, 'foo')
        <Storage {'foo': 'bar'}>
        >>> storify({'foo': 'bar'})
        <Storage {'foo': 'bar'}>
        >>> storify({}, foo='bar')
        <Storage {'foo': 'bar'}>
    """
    data = Storage(defaults)
    for k in requireds:
        if k not in mapping:
            raise KeyError(k)
        data[k] = mapping[k]
    for k, v in mapping.items():
        if k not in data:
            data[k] = v
    return data

class Counter(object):
    """
    Counts things.
    
        >>> c = counter()
        >>> c.next()
        0
        >>> c.next()
        1
    """
    def __init__(self): 
        self.n = 0
    
    def __call__(self): 
        self.n += 1
        return self.n - 1

    def next(self): 
        return self.__call__()

counter = Counter

iters = (list, tuple)

if hasattr(builtins, 'set'):
    iters += (set,)

if hasattr(builtins, 'frozenset'):
    iters += (frozenset,)

try:
    from sets import Set
    iters += (Set,)
except ImportError:
    pass

class IterBetter:
    """
    Turns an iterable into something better.

        >>> nums = iterbetter(range(5))
        >>> nums[0]
        0
        >>> nums[2]
        2
    """
    def __init__(self, iterable):
        self.i, self.c = iter(iterable), []

    def __iter__(self): 
        for v in self.c: 
            yield v
        while True:
            try:
                v = next(self.i)
                self.c.append(v)
                yield v
            except StopIteration:
                return

    def __getitem__(self, i):
        while len(self.c) <= i:
            try:
                v = next(self.i)
                self.c.append(v)
            except StopIteration:
                raise IndexError(i)
        return self.c[i]

iterbetter = IterBetter
# 3
def group(seq, size):
    """
    Groups a sequence into lists of a specified size.

        >>> group([1,2,3,4,5,6,7], 3)
        [[1, 2, 3], [4, 5, 6], [7]]
    """
    return [seq[i:i+size] for i in range(0, len(seq), size)]

def uniq(seq):
    """
    Returns a list of unique elements in the order they appear.

        >>> uniq([1,2,3,1,2,3,4,5])
        [1, 2, 3, 4, 5]
    """
    seen = set()
    result = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def iterview(iterable, size):
    """
    Yields lists of a specified size from an iterable.

        >>> list(iterview(range(10), 3))
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    iterable = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(size):
                chunk.append(next(iterable))
        except StopIteration:
            pass
        if chunk:
            yield chunk
        else:
            break

def rstrips(text, remove):
    """
    Removes `remove` characters from the right side of `text`.

        >>> rstrips('foobarfoo', 'foo')
        'foobar'
    """
    if text.endswith(remove):
        return text[:-len(remove)]
    else:
        return text

def lstrips(text, remove):
    """
    Removes `remove` characters from the left side of `text`.

        >>> lstrips('foobarfoo', 'foo')
        'barfoo'
    """
    if text.startswith(remove):
        return text[len(remove):]
    else:
        return text

def strips(text, remove):
    """
    Removes `remove` characters from both sides of `text`.

        >>> strips('foobarfoo', 'foo')
        'bar'
    """
    return lstrips(rstrips(text, remove), remove)
# 4
def safeunicode(obj, encoding='utf-8'):
    from . import webapi as web
    """
    Converts any object to a unicode string safely.

        >>> safeunicode('hello')
        'hello'
    """
    if isinstance(obj, str):
        return obj
    if isinstance(obj, bytes):
        return obj.decode(encoding)
    return str(obj)

def safestr(obj, encoding='utf-8'):
    from . import webapi as web
    """
    Converts any object to a byte string safely.

        >>> safestr('hello')
        b'hello'
    """
    if isinstance(obj, bytes):
        return obj
    if isinstance(obj, str):
        return obj.encode(encoding)
    return str(obj).encode(encoding)

utf8 = safestr

def datestr(then, now=None):
    """
    Formats a datetime object as a human-readable relative date.

        >>> import datetime
        >>> datestr(datetime.datetime.utcnow() - datetime.timedelta(seconds=5))
        'just now'
    """
    if not now:
        now = datetime.datetime.utcnow()
    diff = now - then
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return f"{second_diff} seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return f"{second_diff//60} minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return f"{second_diff//3600} hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return f"{day_diff} days ago"
    if day_diff < 31:
        return f"{day_diff//7} weeks ago"
    if day_diff < 365:
        return f"{day_diff//30} months ago"
    return f"{day_diff//365} years ago"

def numify(string):
    """
    Converts a string to an int or float if possible.

        >>> numify('34')
        34
        >>> numify('3.14')
        3.14
        >>> numify('abc')
        'abc'
    """
    try:
        return int(string)
    except (ValueError, TypeError):
        try:
            return float(string)
        except (ValueError, TypeError):
            return string
# 5
def denumify(obj):
    """
    Converts numbers to strings in an object.

        >>> denumify([1, 2, 3])
        ['1', '2', '3']
    """
    if isinstance(obj, list):
        return [denumify(x) for x in obj]
    if isinstance(obj, tuple):
        return tuple(denumify(x) for x in obj)
    if isinstance(obj, dict):
        return {k: denumify(v) for k, v in obj.items()}
    if isinstance(obj, (int, float)):
        return str(obj)
    return obj

def commify(n):
    """
    Adds commas to an integer n.

        >>> commify(1000)
        '1,000'
    """
    if isinstance(n, (int, float)):
        n = str(n)
    elif not isinstance(n, str):
        return n
    r = ''
    while n and n[-1].isdigit():
        r = n[-1] + r
        n = n[:-1]
    if r:
        r = ','.join([r[max(i - 3, 0):i] for i in range(len(r), 0, -3)][::-1])
    return n + r

def listget(lst, ind, default=None):
    """
    Returns lst[ind] if it exists, otherwise returns default.

        >>> listget([1,2,3], 5, 'foo')
        'foo'
    """
    try:
        return lst[ind]
    except IndexError:
        return default

def intget(d, key, default=None):
    from . import webapi as web
    """
    Returns int(d[key]) if it exists, otherwise returns default.

        >>> intget({'a': '1'}, 'a')
        1
        >>> intget({}, 'a', 5)
        5
    """
    try:
        return int(d[key])
    except (KeyError, ValueError, TypeError):
        return default

def dictreverse(mapping):
    """
    Returns a dictionary mapping values to keys.

        >>> dictreverse({'a': 1, 'b': 2})
        {1: 'a', 2: 'b'}
    """
    return {v: k for k, v in mapping.items()}

def dictfind(mapping, value):
    """
    Finds the first key with a given value.

        >>> dictfind({'a': 1, 'b': 2}, 2)
        'b'
    """
    for k, v in mapping.items():
        if v == value:
            return k

def dictfindall(mapping, value):
    """
    Returns all keys with a given value.

        >>> dictfindall({'a': 1, 'b': 2, 'c': 2}, 2)
        ['b', 'c']
    """
    return [k for k, v in mapping.items() if v == value]

def dictincr(mapping, key, delta=1):
    """
    Increments a value in a dictionary.

        >>> d = {}
        >>> dictincr(d, 'a')
        >>> d
        {'a': 1}
    """
    mapping[key] = mapping.get(key, 0) + delta

def dictadd(mapping, key, value):
    """
    Adds a value to a list in a dictionary.

        >>> d = {}
        >>> dictadd(d, 'a', 1)
        >>> d
        {'a': [1]}
    """
    if key not in mapping:
        mapping[key] = []
    mapping[key].append(value)
# 6
def requeue(queue, item):
    """
    Puts an item back into the queue.

        >>> q = [1,2,3]
        >>> requeue(q, 1)
        >>> q
        [2, 3, 1]
    """
    try:
        queue.remove(item)
    except ValueError:
        pass
    queue.append(item)

def restack(stack, item):
    """
    Puts an item on top of the stack.

        >>> s = [1,2,3]
        >>> restack(s, 2)
        >>> s
        [1, 3, 2]
    """
    try:
        stack.remove(item)
    except ValueError:
        pass
    stack.append(item)

def nthstr(n):
    """
    Converts an integer into its ordinal string.

        >>> nthstr(1)
        '1st'
        >>> nthstr(2)
        '2nd'
        >>> nthstr(3)
        '3rd'
        >>> nthstr(4)
        '4th'
    """
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

def cond(condition, a, b):
    """
    A functional version of a ternary conditional.

        >>> cond(True, 1, 2)
        1
        >>> cond(False, 1, 2)
        2
    """
    if condition:
        return a
    else:
        return b

def autoassign(self, locals):
    """
    Automatically assigns local variables to self.

        >>> class Foo:
        ...     def __init__(self, a, b):
        ...         autoassign(self, locals())
        >>> f = Foo(1,2)
        >>> f.a, f.b
        (1, 2)
    """
    for k, v in locals.items():
        if k != 'self':
            setattr(self, k, v)

def to36(q):
    """
    Converts an integer to a base-36 string.

        >>> to36(35)
        'z'
        >>> to36(36)
        '10'
    """
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    if q < 0:
        return '-' + to36(-q)
    r = ''
    while q >= 36:
        q, rem = divmod(q, 36)
        r = chars[rem] + r
    return chars[q] + r
# 7
def safemarkdown(text):
    """
    Converts Markdown text safely to HTML.
    Requires the `markdown` package.

        >>> safemarkdown("*hello*")
        '<p><em>hello</em></p>'
    """
    try:
        import markdown
    except ImportError:
        return text
    return markdown.markdown(text)

def sendmail(from_address, to_addresses, subject, message, headers=None, server='localhost'):
    """
    Sends an email.

        >>> sendmail('from@example.com', 'to@example.com', 'Subject', 'Message')
    """
    import smtplib
    from email.mime.text import MIMEText

    if isinstance(to_addresses, str):
        to_addresses = [to_addresses]
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = ", ".join(to_addresses)
    
    if headers:
        for k, v in headers.items():
            msg[k] = v

    s = smtplib.SMTP(server)
    s.sendmail(from_address, to_addresses, msg.as_string())
    s.quit()

class CaptureStdout:
    """
    Captures everything written to stdout.

        >>> import sys
        >>> sys.stdout = CaptureStdout()
        >>> print("hello")
        >>> sys.stdout.getvalue().strip()
        'hello'
    """
    def __init__(self):
        import io
        self.buf = io.StringIO()
    
    def write(self, s):
        self.buf.write(s)
    
    def flush(self):
        return

    def getvalue(self):
        return self.buf.getvalue()

capturestdout = CaptureStdout

class Profile:
    """
    A simple way to profile blocks of code.

        >>> with Profile():
        ...     sum(range(1000))
    """
    def __enter__(self):
        import cProfile
        self.profiler = cProfile.Profile()
        self.profiler.enable()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.profiler.disable()
        import pstats
        p = pstats.Stats(self.profiler)
        p.strip_dirs().sort_stats('cumulative').print_stats(20)

profile = Profile
# 8
def tryall(functions, *args, **keywords):
    """
    Tries a list of functions until one succeeds without raising an exception.

        >>> tryall([int, float], '123')
        123
        >>> tryall([int, float], '3.14')
        3.14
        >>> tryall([int, float], 'abc')
        'abc'
    """
    for func in functions:
        try:
            return func(*args, **keywords)
        except Exception:
            pass
    return args and args[0]

class ThreadedDict:
    """
    A thread-safe dictionary where each thread sees a different value.

        >>> d = threadeddict()
        >>> d.x = 1
        >>> d.x
        1
    """
    def clear(self):
        """Clear all thread-specific keys."""
        self._threadlocal.__dict__.clear()

    @classmethod
    def clear_all(cls):
        """Clear all thread-local storages (not implemented)."""
        # In real code, clearing ALL threads' locals is almost impossible safely.
        # So we leave this as a no-op for compatibility.
        pass

    def __init__(self):
        self._threadlocal = threading.local()

    def __getattr__(self, key):
        return getattr(self._threadlocal, key)

    def __setattr__(self, key, value):
        if key == '_threadlocal':
            object.__setattr__(self, key, value)
        else:
            setattr(self._threadlocal, key, value)

    def __delattr__(self, key):
        delattr(self._threadlocal, key)

    def __getitem__(self, key):
        return getattr(self._threadlocal, key)

    def __setitem__(self, key, value):
        setattr(self._threadlocal, key, value)

    def __delitem__(self, key):
        delattr(self._threadlocal, key)


    def items(self):
        """Return thread-specific items() like a dict."""
        return self._threadlocal.__dict__.items()

    def keys(self):
        """Return thread-specific keys() like a dict."""
        return self._threadlocal.__dict__.keys()

    def values(self):
        """Return thread-specific values() like a dict."""
        return self._threadlocal.__dict__.values()

    def get(self, key, default=None):
        """Return thread-specific get() like a dict."""
        return self._threadlocal.__dict__.get(key, default)

threadeddict = ThreadedDict

def safeiter(it):
    """
    Iterates safely over an iterator, catching and ignoring StopIteration.

        >>> list(safeiter([1,2,3]))
        [1, 2, 3]
    """
    try:
        for x in it:
            yield x
    except Exception:
        pass

def safewrite(filename, text, mode='w', encoding='utf-8'):
    """
    Safely writes text to a file.

        >>> safewrite('testfile.txt', 'hello')
        >>> open('testfile.txt').read()
        'hello'
    """
    with open(filename, mode, encoding=encoding) as f:
        f.write(text)

def re_subm(pat, repl, string):
    """Like re.sub, but returns a match object."""
    regex = re.compile(pat)
    m = regex.search(string)
    if not m:
        return None, string
    return m, regex.sub(repl, string)

        
# Final doctest trigger
if __name__ == "__main__":
    import doctest
    doctest.testmod()

